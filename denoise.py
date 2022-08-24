# denoise.py

"""
    Apply BM3D_SH3D algorithm to denoise and sharpen an image.

    Currently this calls the MatLab wrapper BM3DSHARP until we can reimplement
    it with a direct python wrapper.
"""

import matlab.engine
import numpy as np

class Denoise():
    """
    Class to encapsulate MatLab engine and apply denoise/sharpen to 3D numpy array
    """

    def __init__(self):
        self._eng = matlab.engine.start_matlab('-nodisplay -nosplash -nojvm -nodesktop')
    
    def denoise(self, image: np.ndarray, stddev: float, alpha_sharp: float =1.3):
        denoised_slices = []
        for z in range(image.shape[0]):
            slice = matlab.uint8(image[z,:,:])
            denoised_slices.append(self._eng.BM3DSHARP(slice, stddev, alpha_sharp))
        return np.array(denoised_slices)
