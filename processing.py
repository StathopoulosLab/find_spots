# processing.py
from typing import List, Dict, Tuple
from enum import Enum

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

    def progressCallback(self) -> Tuple(int, str):
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
        for step, onStep in enumerate(self._steps):
            self._stepName = f"{self.baseStepName}.{step.stepName()}"
            step.setInput(stepData)
            step.run()
            if step.getStatus() != ProcessStatus.COMPLETED:
                self._status = step.getStatus()
                return
            self._endOutputs.append(step.endOutputs())
            stepData = step.stepOutputs()
            status = step.status()
        self._stepOutputs = stepData
        self._status = status
        self._stepName = self.baseStepName

    def progressCallback(self) -> Tuple(int, str):
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

    def __init__(self, steps: List(ProcessStep), params: Dict):
        super().__init__(params)
        self._stepName = "Concurrent"
        self._steps = steps
        self._stepOutputs = [None] * len(self._steps)
        self._endOutputs = [None] * len(self._steps)

    def run(self) -> None:
        """
        Run the steps concurrently, and accumulate the results in a list
        """
        # start with a simple, sequential implementation
        statuses: List(ProcessStatus) = [ProcessStatus.QUEUED] * len(self._steps)
        for step, i in enumerate(self._steps):
            step.setInput(self._inputs[i])
            step.run()
            statuses[i] = self.status()
            self._stepOutputs[i] = step.stepOutputs()
            self._endOutputs[i] = step.endOutputs()
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

    def progressCallback(self) -> Tuple(int, str):
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
        return (totalProgress / divisor, self._stepName)
