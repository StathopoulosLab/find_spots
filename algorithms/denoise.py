# denoise.py

"""
    Apply BM3D_SH3D algorithm to denoise and sharpen an image.

    Currently this calls the MatLab wrapper BM3DSHARP until we can reimplement
    it with a direct python wrapper.
"""

from qtpy.QtWidgets import QApplication
import numpy as np
from bm4d import BM4DProfile, BM4DProfileBM3D, bm4d, BM4DStages
from processing import ProcessStatus, ProcessStep, ProcessStepConcurrent
from typing import Callable, Dict
from os import getpid

class DenoiseBM4D():
    """
    Class to directly call native Python version of BM4D with the same
    interface as Denoise()
    """

    def __init__(self):
        pass

    def denoise(self, image: np.ndarray, stddev: float, alpha_sharp: float = 1.3, progressCallback: object = None):
        profile = BM4DProfileBM3D()
        profile.set_sharpen(alpha_sharp)
        denoised_image = np.zeros(image.shape)
        slices = image.shape[0]
        for z in range(slices):
            if callable(progressCallback):
                progressCallback(z, slices)
            denoised_image[z, :, :] = bm4d(
                image[z, :, :],
                stddev,
                profile,
                stage_arg=BM4DStages.HARD_THRESHOLDING)[:, :, 0]
        if callable(progressCallback):
            progressCallback(slices, slices)
        return denoised_image

    def denoise3d(self, volume: np.ndarray, stddev: float = 0., alpha_sharp: float = 1.3):
        profile = BM4DProfile()
        profile.set_sharpen(alpha_sharp)
        denoised_volume = bm4d(volume, stddev, profile, stage_arg=BM4DStages.HARD_THRESHOLDING)
        return denoised_volume

class ProcessStepDenoiseImage(ProcessStep):
    """
    Processing step to denoise one image, or slice of a volume.
    """

    def __init__(self, params: Dict = {}):
        super().__init__(params)
        self._stepName = "Denoise"

    def run(self, progressCallback: Callable[[int, str], None] = None):
        assert len(self._inputs) > 0 and isinstance(self._inputs[0], np.ndarray)
        assert 'sharpen' in self._params.keys()
        assert 'sigma' in self._params.keys()
        self._stepOutputs = []
        self._endOutputs = []
        profile = BM4DProfileBM3D()
        profile.set_sharpen(self._params['sharpen'])
        self._stepOutputs.append(bm4d(
            self._inputs[0],
            self._params['sigma'],
            profile,
            stage_arg=BM4DStages.HARD_THRESHOLDING
            ))
        self._endOutputs.append(None)
        if progressCallback:
            progressCallback(100, self._stepName)
        self._status = ProcessStatus.COMPLETED

class ProcessStepDenoiseConcurrent(ProcessStep):
    """
    Create a ProcessStepConcurrent composed of ProcessStepDenoiseImage steps
    to denoise all the slices of a volume as concurrently as possible.
    """
    def __init__(self, params: Dict = {}):
        super().__init__(params)
        self._stepName = "DenoiseConcurrent"

    def run(self, progressCallback: Callable[[int, str], None] = None):
        # create a ProcessStepConcurrent of ProcessStepDenoiseImage steps, one per slice
        assert isinstance(self._inputs, list) and len(self._inputs) == 1
        inputVolume = self._inputs[0]
        assert len(inputVolume.shape) == 3
        firstSlice = self._params['firstSlice'] if 'firstSlice' in self._params else 0
        lastSlice = self._params['lastSlice'] if 'lastSlice' in self._params else -1
        totalSlices = inputVolume.shape[0]
        firstSlice = max(0, min(totalSlices, firstSlice))
        lastSlice = min(totalSlices, totalSlices + lastSlice if lastSlice < 0 else lastSlice)
        slices = [inputVolume[i] for i in range(firstSlice, lastSlice+1)]
        self._status = ProcessStatus.RUNNING
        concurrent = ProcessStepConcurrent(ProcessStepDenoiseImage, self._params)
        concurrent.setApp(self._app)
        concurrent.setLogger(self._logger)
        concurrent.setInputs(slices)
        concurrent.run(progressCallback)
        status = concurrent.status()
        if status == ProcessStatus.COMPLETED:
            denoisedVolume = np.array(concurrent.stepOutputs()).squeeze()
            self._stepOutputs = [denoisedVolume]
            self._endOutputs = concurrent.endOutputs()
        else:
            self._stepOutputs = []
            self._endOutputs = []
        self._status = status
