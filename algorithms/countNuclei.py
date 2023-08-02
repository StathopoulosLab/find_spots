# countNuclei.py

from qtpy.QtWidgets import QApplication
import cv2
from processing import ProcessStatus, ProcessStep
from algorithms.threshold_mask import generate_nucleus_mask
import numpy as np
from typing import Callable, Dict
from skimage.feature import blob_log
from scipy.ndimage import gaussian_filter, binary_dilation, binary_erosion
from scipy.ndimage.morphology import binary_fill_holes

def count_nuclei(image: np.ndarray, thresh: float) -> int:
    # first, see if we already have a nucleus mask
    if image.dtype != np.bool:
        # Nope!  Need to generate one from the input
        image = generate_nucleus_mask(image, thresh)
    # Erode the image more to make the nuclei smaller and hopefully separate them
    er = binary_erosion(image, iterations=25)
    # Finally, find "blobs" in the same way as we do for spot detection, but in the thresholded nucleus slice
    # This uses a "laplacian of gaussian" operator from SciKit-Image
    # We're using the default parameters for now
    coords = blob_log(er)
    # finally, just return the coordinates of the blobs found and the eroded image
    return coords, er

class ProcessStepCountNuclei(ProcessStep):
    """
    Count the number of nuclei in the nucleus channel, on the numbered slice given in the params.
    """

    def __init__(self, params: Dict = {}):
        super().__init__(params)
        self._stepName = "CountNuclei"

    def run(self, progressCallback: Callable[[int, str], None] = None):
        """
        Count the number of nuclei in each nucleus plane.
        Return in endOutputs the coordinates of the nuclei and the masked image we counted
        them on for the one where the count is greatest.
        Pass the input images unchanged to stepOutputs.
        """
        assert isinstance(self._inputs, list) and len(self._inputs) > 1
        assert 'nucleus_slice' in self._params
        assert 'nucleus_mask_threshold' in self._params
        self._status = ProcessStatus.RUNNING
        nucleusSlice = int(self._params.get('nucleus_slice'))
        nucleus_mask_threshold = float(self._params.get('nucleus_mask_threshold'))
        self._stepOutputs = self._inputs    # copy across
        self._endOutputs = []
        nucleusImage = self._inputs[-1]
        if nucleusImage.dtype != np.uint8:
            nucleusImage = np.uint8(nucleusImage)
        if progressCallback:
            progressCallback(0, self._stepName)
        if self._app:
            self._app.processEvents()
        bestSlice = None
        bestCount = -1
        bestCoords = []
        for ix, nucleusImageSlice in enumerate(nucleusImage):
            # maskImageSlice = maskImage[nucleusSlice]
            nucleusCoords, maskSlice = count_nuclei(nucleusImageSlice, nucleus_mask_threshold)
            self._logger.info(f"Counted {len(nucleusCoords)} in nucleus slice {ix}")
            if bestCount < len(nucleusCoords):
                bestCount = len(nucleusCoords)
                bestCoords = nucleusCoords
                bestSlice = maskSlice
        self._endOutputs = (bestCoords, bestSlice)
        if self._app:
            self._app.processEvents()
        self._status = ProcessStatus.COMPLETED


