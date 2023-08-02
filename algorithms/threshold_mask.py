# threshold_mask.py

from qtpy.QtWidgets import QApplication
import cv2
from processing import ProcessStatus, ProcessStep
import numpy as np
from scipy.ndimage import gaussian_filter, binary_dilation, binary_erosion
from scipy.ndimage.morphology import binary_fill_holes
from typing import Callable, Dict

def min_max_normalize(img: np.ndarray) -> np.ndarray:
    # Normalizing all values between 0 and 1 for easier thresholding

    min_val = np.min(img)
    max_val = np.max(img)
    normal_image = (img - min_val) / (max_val - min_val)

    return(normal_image)

def generate_nucleus_mask(image: np.ndarray, thresh: float) -> np.ndarray:
    # first, normalize the image between 0. and 1.
    norm_im = min_max_normalize(image)
    # second, flat-field the image
    blur_im = gaussian_filter(norm_im, sigma=50)
    norm_im = norm_im / blur_im
    norm_im = min_max_normalize(norm_im)
    # third, threshold to create a binary mask image
    mask = norm_im > thresh
    # fourth, fill in gaps using binary dilation
    dil = binary_dilation(mask, iterations=3)
    # fifth, fill in the holes
    fill_mask = binary_fill_holes(dil)
    # sixth, erode the mask a bit to remove small spots
    fill_mask = binary_erosion(fill_mask, iterations=4)
    return fill_mask

class ProcessStepThresholdMask(ProcessStep):
    """
    Mask out regions of an image based on a thresholded mask of a different image.
    In spot finding, this can be used to eliminate spots that lie outside the nucleus.
    """

    def __init__(self, params: Dict = {}):
        super().__init__(params)
        self._stepName = "ThresholdMask"

    def run(self, progressCallback: Callable[[int, str], None] = None):
        assert isinstance(self._inputs, list) and len(self._inputs) > 1
        self._endOutputs = []
        assert "do_masking" in self._params
        do_masking = self._params.get('do_masking')
        if not do_masking:
            self._stepOutputs = self._inputs[0:-1]
            self._endOutputs.append([])
            self._status = ProcessStatus.COMPLETED
            return
        assert 'nucleus_mask_threshold' in self._params
        self._status = ProcessStatus.RUNNING
        nucleus_mask_threshold = float(self._params.get('nucleus_mask_threshold'))
        self._stepOutputs = []
        maskImage = self._inputs[-1]
        if maskImage.dtype != np.uint8:
            maskImage = np.uint8(maskImage)
        if progressCallback:
            progressCallback(0, self._stepName)
        if self._app:
            self._app.processEvents()
        for input in self._inputs[0:-1]:
            if input.dtype != np.uint8:
                input = np.uint8(input)
            if len(input.shape) > 2:
                firstSlice = self._params['firstSlice'] if 'firstSlice' in self._params else 0
                lastSlice = self._params['lastSlice'] if 'lastSlice' in self._params else -1
                totalSlices = input.shape[0]
                firstSlice = max(0, min(totalSlices, firstSlice))
                lastSlice = min(totalSlices, totalSlices + lastSlice + 1 if lastSlice < 0 else lastSlice)-1
                slices = [input[i] for i in range(firstSlice, lastSlice+1)]
                maskImageSlices = [maskImage[i] for i in range(firstSlice, lastSlice+1)]
            else:
                slices = input
                maskImageSlices = maskImage
            maskedSlices = []
            thresholdsUsed = []
            for slice, maskImageSlice in zip(slices, maskImageSlices):
                thresholdUsed, maskSlice = generate_nucleus_mask(maskImageSlice, nucleus_mask_threshold)
                thresholdsUsed.append(thresholdUsed)
                maskedSlices.append(np.bitwise_and(slice, maskSlice))
            maskedOutput = np.array(maskedSlices, dtype=np.uint8).squeeze()
            self._stepOutputs.append(maskedOutput)
            self._endOutputs.append(thresholdsUsed)
            if progressCallback:
                progressCallback(int(100 / (len(self._inputs) - 1)), self._stepName)
            if self._app:
                self._app.processEvents()
        self._status = ProcessStatus.COMPLETED

class ProcessStepThresholdMaskConcurrent(ProcessStep):
    """
    """

