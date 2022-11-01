# runnableDenoise.py
from re import U
import numpy as np
from qtpy.QtCore import QObject, QRunnable, Signal
from algorithms.denoise import DenoiseBM4D

"""
Wraps a denoiser as a runnable
"""

class WorkerSignals(QObject):
    # Signals
    updateProgress = Signal(int)

class RunnableDenoise(QRunnable):

    def __init__(self):
        super().__init__()
        self.workerSignals = WorkerSignals()
        self._inputImage = None
        self._outputImage = None
        self._firstSlice = 0
        self._lastSlice = -1
        self._stddev = 1.
        self._alpha_sharp = 1.
        self._use3D = False
        self.setAutoDelete(False) # we don't support autoDelete, since we return a value

    def setParams(self, stddev: float, alpha_sharp: float, use3D: bool = False):
        """
        Convenience function to provide all the static parameters at once
        """
        self._stddev = stddev
        self._alpha_sharp = alpha_sharp
        self._use3D = use3D

    def inputImage(self) -> np.ndarray:
        return self._inputImage

    def setInputImage(self, image: np.ndarray):
        self._inputImage = image

    def firstSlice(self) -> int:
        return self._firstSlice

    def setFirstSlice(self, firstSlice: int):
        self._firstSlice = firstSlice

    def lastSlice(self) -> int:
        return self._lastSlice

    def setLastSlice(self, lastSlice: int):
        self._lastSlice = lastSlice

    def stddev(self) -> float:
        return self._stddev

    def setStddev(self, stddev: float):
        self._stddev = stddev

    def alphaSharp(self) -> float:
        return self._alpha_sharp

    def setAlphaSharp(self, alpha_sharp: float):
        self._alpha_sharp = alpha_sharp

    def use3D(self) -> bool:
        return self._use3D

    def setUse3D(self, use3D: bool):
        self._use3D = use3D

    def result(self) -> np.ndarray:
        return self._outputImage

    # QRunnable overrides
    def run(self):
        denoiser = DenoiseBM4D()
        if self._use3D:
            denoiseInstance = denoiser.denoise3d
        else:
            denoiseInstance = denoiser.denoise
        firstSlice = max(self._firstSlice, 0)
        if self._lastSlice >= 0:
            lastSlice = min(self._lastSlice, self._inputImage.shape[0])
        else:
            lastSlice = max(self._inputImage.shape[0]-self._lastSlice, 0)
        self._outputImage = denoiseInstance(self._inputImage[firstSlice:lastSlice], self._stddev, self._alpha_sharp, self.progressCallback)

    # Since we need to return a value, we don't support auto_delete
    def setAutoDelete(self, autoDelete: bool):
        if autoDelete:
            raise NotImplementedError("autoDelete not supported")
        super().setAutoDelete(autoDelete)

    # Progress Callback
    def progressCallback(self, value: int, maxValue: int):
        self.workerSignals.updateProgress.emit(int(value * 100 / maxValue))