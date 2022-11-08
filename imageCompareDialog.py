# imageCompareDialog.py

from qtpy.QtCore import Qt, Slot
from qtpy.QtGui import QPixmap
from qtpy.QtWidgets import QDialog, QDialogButtonBox

from numpy import ndarray
from imageCompareDialog_ui import Ui_ImageCompareDialog

from processing import ProcessStep, ProcessStatus
from typing import Dict

class ImageCompareDialog(QDialog):
    """
    """
    DiscardResults = 2

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_ImageCompareDialog()
        self.ui.setupUi(self)
        # synchronize slice across both sides
        self.ui.leftGraphicsView.sliceChanged.connect(self.ui.rightGraphicsView.updateSlice)
        self.ui.rightGraphicsView.sliceChanged.connect(self.ui.leftGraphicsView.updateSlice)
        self.ui.leftGraphicsView.horizontalScrollBar().valueChanged.connect(self.ui.rightGraphicsView.horizontalScrollBar().setValue)
        self.ui.leftGraphicsView.verticalScrollBar().valueChanged.connect(self.ui.rightGraphicsView.verticalScrollBar().setValue)
        self.ui.rightGraphicsView.horizontalScrollBar().valueChanged.connect(self.ui.leftGraphicsView.horizontalScrollBar().setValue)
        self.ui.rightGraphicsView.verticalScrollBar().valueChanged.connect(self.ui.leftGraphicsView.verticalScrollBar().setValue)
        # make the discard button return a unique value
        self.ui.buttonBox.button(QDialogButtonBox.Discard).clicked.connect(self.discardResults)

    def setLeftImageVolume(self, volume: ndarray):
        self.ui.leftGraphicsView.setImageVolume(volume)

    def setRightImageVolume(self, volume: ndarray):
        self.ui.rightGraphicsView.setImageVolume(volume)

    @Slot()
    def discardResults(self):
        self.done(self.DiscardResults)

class ProcessStepVisualizeDenoise(ProcessStep):
    """
    ProcessStep to visualize the denoising process.

    Inputs:
        List[beforeDenoising, afterDenoising]

    Step Outputs:
        afterDenoising image

    Status:
        Depends on user response, as follows:
        Clicking "Okay" yields ProcessStatus.COMPLETED
        Clicking "Reject/Don't Save" yields ProcessStatus.REJECTED
        Clicking "Cancel" yields ProcessStatus.CANCELLED
        While user is still running the tool, status is ProcessStatus.RUNNING
    """

    def __init__(self, params: Dict = {}):
        super().__init__(params)
        self._stepName = "VisualizeDenoise"

    def run(self):
        assert isinstance(self._inputs, list) and len(self._inputs) == 2
        self._status = ProcessStatus.RUNNING
        viewer = ImageCompareDialog()
        viewer.setLeftImageVolume(self._inputs[0])
        viewer.setRightImageVolume(self._inputs[1])
        result = viewer.exec()
        if result == QDialog.Accepted:
            # The user accepted the current parameters, so we press forward
            self._status = ProcessStatus.COMPLETED
        elif result == QDialog.Rejected:
            # confusingly, this is the Cancel button, so we abort the processing
            self._status = ProcessStatus.ABORTED
        elif result == ImageCompareDialog.DiscardResults:
            # The user didn't like the results and wants to retry with different parameters
            self._status = ProcessStatus.REJECTED
        else:
            raise ValueError(f"Unexpected return value: {result}")
        self._stepOutputs = [self._inputs[0]]
        self._endOutputs = []

