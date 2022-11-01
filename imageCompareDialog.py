# imageCompareDialog.py

from qtpy.QtCore import Qt, Slot
from qtpy.QtGui import QPixmap
from qtpy.QtWidgets import QDialog, QDialogButtonBox

from numpy import ndarray
from imageCompareDialog_ui import Ui_ImageCompareDialog

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