# countNuclei.py

from qtpy.QtWidgets import QApplication
import cv2
from processing import ProcessStatus, ProcessStep
import numpy as np
from typing import Callable, Dict, List
from skimage.feature import blob_log

def count_nuclei(image: np.ndarray, thresh: int) -> int:
    # first, threshold the slice using the same params as for nucleus masking
    _, thresholdedSlice = cv2.threshold(image, thresh, 255, cv2.THRESH_BINARY)
    # now find "blobs" in the same way as we do for spot detection, but in the thresholded nucleus slice
    # This uses a "laplacian of gaussian" operator from SciKit-Image
    # We're using the default parameters for now
    coords = blob_log(thresholdedSlice)
    # finally, just return the number of blobs found
    return len(coords)

class ProcessStepCountNuclei(ProcessStep):
    """
    Count the number of nuclei in the nucleus channel, on the numbered slice given in the params.
    """

    def __init__(self, params: Dict = {}):
        super().__init__(params)
        self._stepName = "CountNuclei"

    def run(self, progressCallback: Callable[[int, str], None] = None):
        assert isinstance(self._inputs, list) and len(self._inputs) > 1
        assert 'nucleus_slice' in self._params
        assert 'nucleus_mask_threshold' in self._params
        self._status = ProcessStatus.RUNNING
        nucleusSlice = int(self._params.get('nucleus_slice'))
        nucleus_mask_threshold = int(self._params.get('nucleus_mask_threshold'))
        self._stepOutputs = self._inputs    # copy across
        self._endOutputs = []
        maskImage = self._inputs[-1]
        if maskImage.dtype != np.uint8:
            maskImage = np.uint8(maskImage)
        if progressCallback:
            progressCallback(0, self._stepName)
        if self._app:
            self._app.processEvents()
        maskImageSlice = maskImage[nucleusSlice]
        numNuclei = count_nuclei(maskImageSlice, nucleus_mask_threshold)
        self._endOutputs.append(numNuclei)
        if self._app:
            self._app.processEvents()
        self._status = ProcessStatus.COMPLETED


