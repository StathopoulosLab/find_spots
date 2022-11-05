# denoise.py

"""
    Apply BM3D_SH3D algorithm to denoise and sharpen an image.

    Currently this calls the MatLab wrapper BM3DSHARP until we can reimplement
    it with a direct python wrapper.
"""

import numpy as np
from bm4d import BM4DProfile, BM4DProfileBM3D, bm4d, BM4DStages
from processing import ProcessStatus, ProcessStep, ProcessStepConcurrent
from typing import List, Dict, Tuple
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

    def run(self):
        assert len(self._inputs) > 0 and isinstance(self._inputs[0], np.ndarray)
        assert 'sharpen' in self._params.keys()
        assert 'sigma' in self._params.keys()
        self._stepOutputs = []
        self._endOutputs = []
        profile = BM4DProfileBM3D()
        profile.set_sharpen(self._params['sharpen'])
        self._stepOutputs.append(bm4d(
            self._inputs,
            self._params['sigma'],
            profile,
            stage_arg=BM4DStages.HARD_THRESHOLDING
            ))
        self._endOutputs.append(None)
        self._status = ProcessStatus.COMPLETED

    def progressCallback(self) -> Tuple[int, str]:
        if self._status != ProcessStatus.COMPLETED:
            return (0, self._stepName)
        else:
            return (100, self._stepName)

def MakeProcessStepDenoiseConcurrent(volume: np.ndarray, params: Dict = {}) -> ProcessStepConcurrent:
    """
    Create a ProcessStepConcurrent composed of ProcessTespDenoiseImage steps
    to denoise all the slices of a volume as concurrently as possible.
    """
    # create a processing step for each slice of the volume
    # note that [ProcessStepDenoiseImage(params)] * volume.shape[0] creates references to
    # the same ProcessStep instance, rather than separate ones, like we need
    processSteps = [ProcessStepDenoiseImage(params) for slice in range(volume.shape[0])]
    return ProcessStepConcurrent(processSteps)