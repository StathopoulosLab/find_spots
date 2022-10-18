# findSpotsTool.py
from qtpy.QtCore import QObject, Qt, QStringListModel, Signal, Slot
from qtpy.QtWidgets import QApplication, QFileDialog, QMainWindow
from findSpotsTool_ui import Ui_MainWindow
from os.path import expanduser
import sys
import time

class FindSpotsTool(QMainWindow):

    def __init__(self):
        super().__init__()

        # set up the main window UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # file processing data items
        self.pendingFilesModel = QStringListModel()
        self.ui.pendingFilesListView.setModel(self.pendingFilesModel)
        self.currentlyProcessingFile = None
        self.ui.activeFileLineEdit.insert("(none)")
        self.completedFilesModel = QStringListModel()
        self.ui.completedFilesListView.setModel(self.completedFilesModel)

        # connect various widgets to actions
        self.ui.addFilesButton.clicked.connect(self.addFiles)
        self.ui.clearCompletedFilesPushButton.clicked.connect(self.clearCompletedFiles)
        self.ui.quitPushButton.clicked.connect(self.quit)
        self.ui.testSettingsPushButton.clicked.connect(self.processNextFile)

        # setup some state
        self.running: bool = False

    @Slot()
    def addFiles(self):
        baseDir = expanduser("~")
        file_paths, _ = QFileDialog.getOpenFileNames(
            None,
            "Select confocal microscope files to process",
            baseDir,
            "Confocal files (*.czi)",
            "Confocal files (*.czi)")
        if len(file_paths) > 0:
            files = self.pendingFilesModel.stringList()
            files.extend(file_paths)
            self.pendingFilesModel.setStringList(files)
            self.pendingFilesModel.dataChanged.emit(
                self.pendingFilesModel.index(0),
                self.pendingFilesModel.index(len(files)))

    @Slot()
    def processNextFile(self):
        pendingFilesList = self.pendingFilesModel.stringList()
        if self.running or len(pendingFilesList) == 0:
            return
        fileToRun = pendingFilesList[0]
        self.ui.activeFileLineEdit.setText(fileToRun)
        pendingFilesList = pendingFilesList[1:]
        self.pendingFilesModel.setStringList(pendingFilesList)
        # TODO: for a process to process the file after setting self.running to True
        # But for a mock-up:
        self.running = True
        time.sleep(5)   # 5 seconds
        completedFilesList = self.completedFilesModel.stringList()
        completedFilesList.append(fileToRun)
        self.ui.activeFileLineEdit.setText("(none)")
        self.completedFilesModel.setStringList(completedFilesList)
        self.running = False

    @Slot()
    def clearCompletedFiles(self):
        self.completedFilesModel.setStringList([])

    @Slot()
    def quit(self):
        pass

if __name__ == "__main__":
    # Create the Qt Application
    app = QApplication(sys.argv)

    tool = FindSpotsTool()
    tool.screen_center = app.screens()[len(app.screens())-1].availableGeometry().center()
    # spacing = QPoint((window.width() + video.width()) / 4 + 5, 0)
    qr = tool.frameGeometry()
    qr.moveCenter(tool.screen_center)
    tool.move(qr.topLeft())
    tool.show()
    # Run the main Qt loop
    sys.exit(app.exec_())
