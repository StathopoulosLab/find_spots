# detect_spots
# changed detect_slice_spots so that only the smaller of two
# overlapping spots will be deleted (not both spots, as it was before)

import numpy as np

from processing import ProcessStatus, ProcessStep, ProcessStepConcurrent
from typing import Callable, Dict, Tuple
from os import getpid
from logging import Logger
from skimage.feature import blob_log

def detect_spots(image: np.ndarray, thresh: float, logger: Logger = None):
    logger.info(f"Worker {getpid()}: Detecting spots")
    coords = blob_log(image, threshold=thresh)
    outputSpots = [(spot[1], spot[2], spot[0]) for spot in coords]
    return(outputSpots)

class ProcessStepDetectSpots(ProcessStep):
    """
    A ProcessStep to detect a list of spots within the input.
    """
    def __init__(self, params: Dict = {}):
        super().__init__(params)
        self._stepName = "DetectSpots"

    def run(self, progressCallback: Callable[..., Tuple[int, str]] = None) -> None:
        assert isinstance(self._inputs, list) and len(self._inputs) == 1
        assert 'spot_detect_threshold' in self._params
        self._logger.info(f"Worker {getpid()} inside ProcessStepDetectSpots.run()")
        self._stepOutputs = []
        self._endOutputs = []
        spot_detect_threshold = self._params['spot_detect_threshold']
        input = self._inputs
        while isinstance(input, list):
            self._logger.info(f"Worker {getpid()}: unwrapping ndarray from list")
            input = input[0]
        assert(isinstance(input, np.ndarray))
        if input.dtype != np.uint8:
            input = np.array(input, dtype=np.uint8)
        self._status = ProcessStatus.RUNNING
        stepOutputs = detect_spots(input, spot_detect_threshold, False, self._logger)
        self._stepOutputs.append(stepOutputs)
        self._logger.info(f"Worker {getpid()}: outputted a list of length {len(self._stepOutputs[0])}")
        if self._params['save_spot_image']:
            self._endOutputs.append(stepOutputs)
        else:
            self._endOutputs.append([])
        if progressCallback:
            progressCallback(100, self._stepName)
        if self._app:
            self._app.processEvents()
        self._status = ProcessStatus.COMPLETED

class ProcessStepDetectSpotsConcurrent(ProcessStep):
    """
    A ProcessStep that concurrently detects spots on multiple
    independent channels.
    """

    def __init__(self, params: Dict = {}):
        super().__init__(params)
        self._stepName = "DetectSpotsConcurrent"

    def run(self, progressCallback: Callable[[int, str], None] = None):
        assert isinstance(self._inputs, list) and len(self._inputs) > 0
        self._status = ProcessStatus.RUNNING
        concurrent = ProcessStepConcurrent(ProcessStepDetectSpots, self._params)
        concurrent.setApp(self._app)
        concurrent.setLogger(self._logger)
        concurrent.setInputs(self._inputs)
        concurrent.run(progressCallback)
        status = concurrent.status()
        if status == ProcessStatus.COMPLETED:
            self._stepOutputs = concurrent.stepOutputs()[0]
            self._endOutputs = concurrent.endOutputs()[0]
        else:
            self._stepOutputs = []
            self._endOutputs = []
        self._status = status
