# processing.py
from qtpy.QtWidgets import QApplication
from typing import List, Dict, Tuple, Callable
from enum import Enum
import multiprocessing as mp
from queue import Full
import logging
from os import getpid

class ProcessStatus(Enum):
    NOT_STARTED = 0     # the processing step has not started
    QUEUED = 1          # the processing step is waiting to start
    RUNNING = 2         # the processing step is in progress
    COMPLETED = 3       # the processing step completed successfully
    REJECTED = -1       # the step finished, but the user rejected the results
    CANCELLED = -2      # the processing step was cancelled by the user
    ABORTED = -3        # the processing step failed or aborted

class ProcessStep():
    """
    A processing step abstract class.

    Defined are:
        Action      Callable
        Parameters  Dict
        Inputs      List
        StepOutputs List    # And incremental output from this step
        EndOutputs  List    # A final output (needing) no additional processing
        Status      ProcessStatus enum
    """

    def __init__(self, params: Dict = {}):
        self._app = None
        self._stepName: str = ""
        self._status: ProcessStatus = ProcessStatus.NOT_STARTED
        self._inputs: List = []
        self._stepOutputs: List = []
        self._endOutputs: List = []
        self._params: Dict = params
        self._logger = None

    def setApp(self, app: QApplication):
        self._app = app

    def setLogger(self, logger: logging.Logger):
        self._logger = logger

    def stepName(self) -> str:
        return self._stepName

    def status(self) -> ProcessStatus:
        return self._status

    def setParams(self, params: Dict) -> None:
        """
        Set or update params for the processing step
        """
        self._params = params

    def setInputs(self, inputs: List) -> None:
        """
        This allows outputs from a previous step to be passed
        to this processing step in a generic way.
        """
        self._inputs = inputs

    def stepOutputs(self) -> List:
        """
        This allows this processing step's outputs to be retreived
        and passed to the next processing step in a generic way.
        """
        return self._stepOutputs

    def endOutputs(self) -> List:
        """
        This allows this processing step's end outputs to be
        retrieved.
        """
        return self._endOutputs

    def run(self, progressCallback: Callable[[int, str], None] = None) -> None:
        """
        Run the process step, consuming the inputs and
        producing one or both of two types of outputs

        The derived class must implement this
        """
        raise NotImplementedError()

class ProcessStepSequence(ProcessStep):
    """
    This is a composite processing step that encapuslates
    a sequence of processing steps.
    """

    def __init__(self, steps: List, params: Dict = {}):
        super().__init__(params)
        self._steps = steps
        self.baseStepName = "Sequence"
        self._stepName = self.baseStepName
        self.onStep = 0
        self._stepsCompleted = 0
        self._progressCallback = None

    def progressCallbackWrapper(self, progress: int, stepName: str):
        # Account for process steps already completed when reporting progress
        if self._progressCallback:
            self._progressCallback(
                int((self._stepsCompleted + progress / 100.) / len(self._steps)),
                self.baseStepName + '.' + stepName)

    def run(self, progressCallback: Callable[[int, str], None] = None) -> None:
        self._progressCallback = progressCallback
        self._stepsCompleted = 0
        stepData = self._inputs
        self._status = ProcessStatus.RUNNING
        for onStep, step in enumerate(self._steps):
            step.setApp(self._app)
            step.setLogger(self._logger)
            self._stepName = f"{self.baseStepName}.{step.stepName()}"
            step.setInput(stepData)
            step.run(self.progressCallbackWrapper if progressCallback else None)
            if step.status() != ProcessStatus.COMPLETED:
                self._status = step.status()
                return
            self._endOutputs.append(step.endOutputs())
            stepData = step.stepOutputs()
            status = step.status()
        self._stepOutputs = stepData
        self._status = status
        self._stepName = self.baseStepName
        progressCallback(100, self._stepName)

class ProcessStepConcurrent(ProcessStep):
    """
    A process step composed of individual steps that can
    be run in parallel.

    params, if supplied, can be either a dict or a list of dicts
    """

    def __init__(self, step: ProcessStep, params = {}):
        assert isinstance(params, (dict, list))
        super().__init__(params)
        self._stepName = "Concurrent"
        self._step = step

    def setInputs(self, inputs: List) -> None:
        super().setInputs(inputs)
        self._stepOutputs = []
        self._endOutputs = []

    def setApp(self, app: QApplication):
        # QApplication objects can't be pickled, so don't store it
        pass

    def runInner(self, stepClass: ProcessStep, params: Dict, inQ: mp.Queue, outQ: mp.Queue) -> None:
        """
        Pull the inputs off the input queue and call the processStep's run() function
        Get the outputs and pushd them on the two output queues.
        """
        try:
            step = stepClass(params)
            step.setLogger(self._logger)
            while True:
                idx, inputs = inQ.get()
                if idx < 0:
                    # pass the "poison pill" on and then exit
                    outQ.put((idx, None))
                    break
                step.setInputs(inputs)
                step.run()
                outQ.put((idx, step.stepOutputs(), step.endOutputs()))
        except Exception as e:
            self._logger.exception(f"Worker {getpid()} got exception {e}")

    def accumulateOutputs(self, nWorkers: int, outQ: mp.Queue) -> None:
        """
        Accumulate the results from the various parallel threads and accumulate them.
        This should be the last step of the pipeline
        We shut down when we've received notice that all the workers have shut down
        i.e. we received the same number of poison pills as workers
        """
        unorderedOutputs = []
        workersDone = 0
        try:
            while workersDone < nWorkers:
                outputs = outQ.get()
                idx = outputs[0]
                if idx < 0:
                    workersDone += 1
                    self._logger.info(f"{workersDone} workers done so far")
                    continue
                unorderedOutputs.append(outputs)
                self._logger.info(f"Appended idx {idx} to outputs")
            unorderedOutputs.sort(key=lambda item: item[0])
            # remove the indices and unwrap each slice before outputting
            # create a tuple of stepOutputs and endOutputs
            return \
                [item[1][0] for item in unorderedOutputs], \
                [item[2][0] for item in unorderedOutputs]
        except Exception as e:
            self._logger.exception(f"accumulateOutputs got exception {e}")

    def run(self, progressCallback: Callable[[int, str], None] = None) -> None:
        """
        Run the steps concurrently, accumulating the results in a list

        Doesn't yet support progressCallback updates
        """
        self._status = ProcessStatus.RUNNING
        self._stepOutputs = []
        self._endOutputs = []
        nCores = mp.cpu_count()
        # We need at least two so that accumulateOutputs can run alongside runInner
        # Use up to 3/4 of the available cores, but no need for more than we have work.
        coresToUse = min(max(2, int(nCores * 3 / 4)), len(self._inputs) + 1)
        nWorkers = coresToUse - 1
        self._logger.info(f"Using {coresToUse} cores")
        with mp.Pool(processes=coresToUse) as pool:
            with mp.Manager() as mgr:
                inQ = mgr.Queue(nWorkers)   # one per worker
                outQ = mgr.Queue(nWorkers)  # contains tuple(stepOutputs, endOutputs) to avoid race with two queues
                self._logger.info("Queues created")
                if isinstance(self._params, dict):
                    self._params = [self._params] * nWorkers
                assert len(self._params) >= nWorkers    # check in case params was passed in as a list
                accumulatorResults = pool.apply_async(self.accumulateOutputs, (nWorkers, outQ))
                self._logger.info("Started accumulateOutputs Worker")
                try:
                    workerResults = [pool.apply_async(self.runInner, (self._step, self._params[i], inQ, outQ)) for i in range(nWorkers)]
                except Exception as e:
                    self._logger.exception(f"Exception trying to start workers with runInner: {e}")
                self._logger.info(f"Started {nWorkers} Workers with runInner")

                for idx, inputs in enumerate(self._inputs):
                    self._logger.info(f"Enqueued idx {idx}")
                    while True:
                        # the queue can fill, at which point inQ.put will block
                        # Set a timeout so that Qt can handle UI events before trying again
                        try:
                            inQ.put((idx, [inputs]), timeout=0.1)
                            break
                        except Full:
                            if self._app:
                                self._app.processEvents()

                for idx in range(nWorkers):
                    self._logger.info(f"Enqueuing poison pill #{idx}")
                    while True:
                        # Let Qt handle UI events, same as above
                        try:
                            inQ.put((-1, None), timeout=0.1)
                            break
                        except Full:
                            if self._app:
                                self._app.processEvents()

                # close the pool's input and wait for everything to finish
                pool.close()
                self._logger.info("Pool closed")
                while True:
                    try:
                        stepOutputs, endOutputs = accumulatorResults.get(0.1)
                        self._logger.info("Got output from accumulateOutputs")
                        break
                    except mp.TimeoutError:
                        # let Qt get in to process UI events.
                        if self._app:
                            self._app.processEvents()
                pool.join()
                self._logger.info("Pool joined")
                self._stepOutputs.append(stepOutputs)
                self._endOutputs.append(endOutputs)
            if progressCallback:
                #TODO: provide a callback mechanism that passes on updates
                # from accumulateOutputs
                progressCallback(100, self._stepName)
            if self._app:
                self._app.processEvents()
            self._status = ProcessStatus.COMPLETED

class ProcessStepIterate(ProcessStep):
    """
    Execute sequentially a set of parallel paths of the overall process
    This accumulates the outputs of each pass over the sequential inputs
    in a list


    """

    def __init__(self, stepClass: ProcessStep, paramsList: List = {}):
        super().__init__(None)
        self._paramsList = paramsList
        self._stepClass: ProcessStep = stepClass
        self._stepName = "Iterate"
        self._stepsCompleted: int = 0
        self._progressCallback = None

    def progressCallbackWrapper(self, progress: int, stepName: str):
        # Account for process steps already completed when reporting progress
        if self._progressCallback:
            self._progressCallback(
                int((self._stepsCompleted + progress / 100.) / len(self._inputs)),
                self._stepName + '.' + stepName)
        if self._app:
            self._app.processEvents()

    def run(self, progressCallback: Callable[[int, str], None] = None) -> None:
        """
        Run the steps sequentially, and accumulate the results in a list
        """
        assert len(self._inputs) == len(self._paramsList)
        self._progressCallback = progressCallback
        self._stepOutputs = []
        self._endOutputs = []
        self._stepsCompleted = 0
        statuses: List(ProcessStatus) = [ProcessStatus.QUEUED] * len(self._inputs)
        for i, input in enumerate(self._inputs):
            step = self._stepClass(self._paramsList[i])
            step.setApp(self._app)
            step.setLogger(self._logger)
            step.setInputs([input])
            step.run(self.progressCallbackWrapper if progressCallback else None)
            statuses[i] = step.status()
            self._stepOutputs.append(step.stepOutputs()[0])
            self._endOutputs.append(step.endOutputs()[0])
            self._stepsCompleted = i+1
        if statuses.count(ProcessStatus.COMPLETED) == len(self._inputs):
            self._status = ProcessStatus.COMPLETED
        elif statuses.count(ProcessStatus.ABORTED) > 0:
            self._status = ProcessStatus.ABORTED
        elif statuses.count(ProcessStatus.CANCELLED) > 0:
            self._status = ProcessStatus.CANCELLED
        elif statuses.count(ProcessStatus.RUNNING) > 0:
            raise SystemError("Parallel process should not still be running")
        else:
            self._status = ProcessStatus.REJECTED
