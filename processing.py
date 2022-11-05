# processing.py
from typing import List, Dict, Tuple
from enum import Enum
import multiprocessing as mp
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
        self._stepName: str = ""
        self._status: ProcessStatus = ProcessStatus.NOT_STARTED
        self._inputs: List = []
        self._stepOutputs: List = []
        self._endOutputs: List = []
        self._params: Dict = params

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

    def run(self) -> None:
        """
        Run the process step, consuming the inputs and
        producing one or both of two types of outputs

        The derived class must implement this
        """
        raise NotImplementedError()

    def progressCallback(self) -> Tuple[int, str]:
        """
        Returns a tuple of two items:
            Percent complete (0 - 100)
            The name of the step currently running (or just completed)

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

    def run(self) -> None:
        stepData = self._inputs
        self._status = ProcessStatus.RUNNING
        for onStep, step in enumerate(self._steps):
            self._stepName = f"{self.baseStepName}.{step.stepName()}"
            step.setInput(stepData)
            step.run()
            if step.status() != ProcessStatus.COMPLETED:
                self._status = step.status()
                return
            self._endOutputs.append(step.endOutputs())
            stepData = step.stepOutputs()
            status = step.status()
        self._stepOutputs = stepData
        self._status = status
        self._stepName = self.baseStepName

    def progressCallback(self) -> Tuple[int, str]:
        """
        Return progress percent (0 - 100) and name of processStep
        Calculate progress as follows:
        progress = (100 * stepsCompleted + stepProgress) / totalSteps
        processStep = "Sequential.<substepName>" (Updated within run())
        """
        divisor = len(self._steps)
        stepProgress, _ = self._steps(self.onStep).progressCallback()
        progress = int(100 * self.onStep + stepProgress) / divisor
        return (progress, self._stepName)

class ProcessStepConcurrent(ProcessStep):
    """
    A process step composed of individual steps that can
    be run in parallel.
    """

    def __init__(self, step: ProcessStep, params: Dict = {}):
        super().__init__(params)
        self._stepName = "Concurrent"
        self._step = step

    def setInputs(self, inputs: List) -> None:
        super().setInputs(inputs)
        self._stepOutputs = [None] * len(self._inputs)
        self._endOutputs = [None] * len(self._inputs)

    def runConcurrentInner(self, stepClass: ProcessStep, params: Dict, inQ: mp.Queue, stepOutQ: mp.Queue, endOutQ: mp.Queue) -> None:
        """
        Pull the inputs off the input queue and call the processStep's run() function
        Get the outputs and pushd them on the two output queues.
        """
        while True:
            step = stepClass(params)
            idx, inputs = inQ.get()
            if idx < 0:
                # pass the "poison pill" on and then exit
                stepOutQ.put((idx, None))
                endOutQ.put((idx, None))
                break
            step.setInputs(inputs)
            step.run()
            stepOutQ.put((idx, step.stepOutputs()))
            endOutQ.put((idx, step.endOutputs()))

    def accumulateOutputs(self, workers: int, stepOutQ: mp.Queue, endOutQ: mp.Queue, finalStepOutQ: mp.Queue, finalEndOutQ: mp.Queue) -> None:
        """
        Accumulate the results from the various parallel threads and accumulate them.
        This should be the last step of the pipeline
        We shut down when we've received notice that all the workers have shut down
        i.e. we received the same number of poison pills as workers
        """
        logger = mp.log_to_stderr()
        logger.setLevel(logging.INFO)
        unorderedStepOutputs = []
        unorderedEndOutputs = []
        workersDone = 0
        while workersDone < workers:
            stepIdx, stepOutputs = stepOutQ.get()
            endIdx, endOutputs = endOutQ.get()
            if stepIdx != endIdx:
                workersDone = workers
                raise ValueError(f"stepIdx ({stepIdx}) != endIdx ({endIdx})")
            if stepIdx < 0:
                workersDone += 1
                logger.info(f"{workersDone} workers done so far")
                continue
            unorderedStepOutputs.append((stepIdx, stepOutputs))
            logger.info(f"Appended idx {stepIdx} to step outputs, shape is {stepOutputs[0].shape}")
            unorderedEndOutputs.append((endIdx, endOutputs))
        unorderedStepOutputs.sort(key=lambda item: item[0])
        unorderedEndOutputs.sort(key=lambda item: item[0])
        logger.info(f"len(unorderedEndOutputs): {len(unorderedEndOutputs)}")
        # remove the indices and unwrap each slice before outputting
        finalStepOutQ.put([item[1][0] for item in unorderedStepOutputs])
        finalEndOutQ.put([item[1][0] for item in unorderedEndOutputs])

    def run(self) -> None:
        """
        Run the steps concurrently, accumulating the results in a list

        Doesn't yet support progressCallback updates
        """
        logger = mp.log_to_stderr()
        logger.setLevel(logging.INFO)
        nCores = mp.cpu_count()
        coresToUse = max(2, int(nCores * 3 / 4))
        logger.info(f"Using {coresToUse} cores")
        with mp.Pool(processes=coresToUse) as pool:
            mgr = mp.Manager()
            inQ = mgr.Queue(coresToUse)
            stepOutQ = mgr.Queue(5)
            endOutQ = mgr.Queue(5)
            finalStepOutQ = mgr.Queue(1)
            finalEndOutQ = mgr.Queue(1)
            logger.info("Queues created")
            workers = [pool.apply_async(self.runConcurrentInner, (self._step, self._params, inQ, stepOutQ, endOutQ)) for i in range(coresToUse-1)]
            logger.info(f"Started {len(workers)} Workers with runConcurrentInner")
            accumulator = pool.apply_async(self.accumulateOutputs, (len(workers), stepOutQ, endOutQ, finalStepOutQ, finalEndOutQ))
            logger.info("Started accumulateOutputs Worker")

            for idx, inputs in enumerate(self._inputs):
                logger.info(f"Enqueued idx {idx}")
                inQ.put((idx, inputs))

            for idx in range(len(workers)):
                logger.info(f"Enqueuing poison pill #{idx}")
                inQ.put((-1, None))

            # close the pool's input and wait for everything to finish
            pool.close()
            logger.info("Pool closed")
            pool.join()
            logger.info("Pool joined")
            try:
                self._stepOutputs = finalStepOutQ.get_nowait()
            except mp.queues.Empty as e:
                print(f"runConcurrent: finalStepOutQ was unexpectedly empty")
            try:
                self._endOutputs = finalEndOutQ.get_nowait()
            except mp.queues.Empty as e:
                print(f"runConcurrent: finalEndOutQ was unexpectedly empty")

    def runSequential(self) -> None:
        """
        Run the steps concurrently, and accumulate the results in a list
        """
        # start with a simple, sequential implementation
        statuses: List(ProcessStatus) = [ProcessStatus.QUEUED] * len(self._steps)
        for i, step in enumerate(self._steps):
            step.setInputs([self._inputs[i]])
            step.run()
            statuses[i] = step.status()
            self._stepOutputs[i] = step.stepOutputs()[0]
            self._endOutputs[i] = step.endOutputs()[0]
        if statuses.count(ProcessStatus.COMPLETED) == len(self._steps):
            self._status = ProcessStatus.COMPLETED
        elif statuses.count(ProcessStatus.ABORTED) > 0:
            self._status = ProcessStatus.ABORTED
        elif statuses.count(ProcessStatus.CANCELLED) > 0:
            self._status = ProcessStatus.CANCELLED
        elif statuses.count(ProcessStatus.RUNNING) > 0:
            raise SystemError("Parallel process should not still be running")
        else:
            self._status = ProcessStatus.REJECTED

    def progressCallback(self) -> Tuple[int, str]:
        """
        Return progress percent (0 - 100) and name of processStep
        Calculate progress as follows:
        progress = sum(each step's progress) / totalSteps
        processStep = "Concurrent"
        """
        divisor = len(self._steps)
        totalProgress = 0
        for step in self._steps:
            stepProgress, _ = step.progressCallback()
            totalProgress += stepProgress
        return (int(totalProgress / divisor), self._stepName)
