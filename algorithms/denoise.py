# denoise.py

"""
    Apply BM3D_SH3D algorithm to denoise and sharpen an image.

    Currently this calls the MatLab wrapper BM3DSHARP until we can reimplement
    it with a direct python wrapper.
"""

import numpy as np
from bm4d import BM4DProfile, BM4DProfileBM3D, bm4d, BM4DStages
# import multiprocessing as mp
# from concurrent.futures import ProcessPoolExecutor

# import matlab.engine
# class Denoise():
#     """
#     Class to encapsulate MatLab engine and apply denoise/sharpen to 3D numpy array
#     """

#     def __init__(self):
#         self._eng = matlab.engine.start_matlab('-nodisplay -nosplash -nojvm -nodesktop')

#     def denoise(self, image: np.ndarray, stddev: float, alpha_sharp: float =1.3):
#         denoised_slices = []
#         for z in range(image.shape[0]):
#             slice = matlab.uint8(image[z,:,:])
#             denoised_slices.append(self._eng.BM3DSHARP(slice, stddev, alpha_sharp))
#         return np.array(denoised_slices)

#     def denoise3d(self, volume: np.ndarray, stddev: float = 0., alpha_sharp: float = 1.3):
#         # in this version, alpha_sharp is ignored
#         return np.array(self._eng.bm4d(matlab.uint8(volume), "Gauss", stddev, 'np', True, False))

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

"""
def denoise_concurrent_inner(slice: np.ndarray, stddev: float, alpha_sharp: float = 1.3):
    profile = BM4DProfileBM3D()
    profile.set_sharpen(alpha_sharp)
    return bm4d(slice, stddev, profile, stage_arg=BM4DStages.HARD_THRESHOLDING)[:,:,0]

def denoise_concurrent(image: np.ndarray, stddev: float, alpha_sharp: float = 1.3):
    max_workers = min(image.shape[0], mp.cpu_count - 2)
    with ProcessPoolExecutor(max_workers: max_workers) as executor:
        executor.map(denoise_concurrent_inner, [image[z, :, :] for z in range(image.shape[0])], stddev, alpha_sharp)
"""