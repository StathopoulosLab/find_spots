# Fst3DGraphicsView.py
from qtpy.QtCore import Qt, Signal, Slot
from qtpy.QtGui import QPixmap, QMouseEvent, QWheelEvent
from qtpy.QtWidgets import QGraphicsScene, QGraphicsView
from numpy import ndarray
from qimage2ndarray import gray2qimage

class Fst3DGraphicsView(QGraphicsView):
    """
    Widget class derived from QGraphicsView to specifically support the viewing
    of 3D image data.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.imageVolume = None
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.pixmap = QPixmap()
        self.pixmapItem = self.scene.addPixmap(self.pixmap)
        self.currentSlice = 0
        self.setDragMode(QGraphicsView.ScrollHandDrag)

    def setImageVolume(self, volume: ndarray):
        self.imageVolume = volume
        self.setSlice(0)

    def setSlice(self, slice:int):
        if type(self.imageVolume) != ndarray:
            return
        slice = max(0, min(self.imageVolume.shape[0]-1, slice))
        self.pixmap = QPixmap.fromImage(gray2qimage(self.imageVolume[slice]))
        self.currentSlice = slice
        self.pixmapItem.setPixmap(self.pixmap)
        self.sliceChanged.emit(self.currentSlice)
        # self.fitInView(self.pixmapItem.boundingRect(), mode=Qt.KeepAspectRatio)


    # overrides
    def wheelEvent(self, event: QWheelEvent) -> None:
        steps = int(event.angleDelta().y() / 120)   # 15 deg per step on most mouse wheels; reading is in 1/8 degrees
        self.setSlice(self.currentSlice + steps)
        event.accept()

    # Signals
    sliceChanged = Signal(int)

    # Slots
    @Slot(int)
    def updateSlice(self, slice):
        if slice != self.currentSlice:
            # avoids signal recursion loop
            self.setSlice(slice)