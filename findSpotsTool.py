# findSpotsTool.py
from qtpy.QtCore import Qt, QObject, QRunnable, QThreadPool, QStringListModel, Signal, Slot
from qtpy.QtWidgets import QApplication, QDialog, QDialogButtonBox, QFileDialog, QMainWindow, QMessageBox
from findSpotsTool_ui import Ui_MainWindow
from imageCompareDialog import ImageCompareDialog
from runnables.runnableDenoise import RunnableDenoise
from algorithms.find_spots import get_param
from algorithms.confocal_file import ConfocalFile
from os.path import expanduser
from enum import Enum
import sys
import time

class Worker(QRunnable):
    """
    Class to execute image processing currently with UI
    """

    def __init__(self, function, *args, **kwargs):
        super().__init__()
        self.function = function
        self.args = args
        self.kargs = kwargs

    def run(self):
        self.function(self.args, self.kwargs)

class FindSpotsTool(QMainWindow):

    # class ProcessingState(Enum):
    #     STOPPED = 0
    #     RUNNING = 1
    #     CANCEL = 2
    #     ACCEPT = 3
    #     RETRY = 4

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

        # initialize default parameters
        params = {} # for now
        self.ui.firstSliceLineEdit.setText(str(get_param("first_slice", params)))
        self.ui.lastSliceLineEdit.setText(str(get_param("last_slice", params)))
        self.ui.use3DCheckBox.setChecked(get_param('use_denoise3d', params))
        default_sigma = str(get_param("sigma", params))
        self.ui.sigma3CRMLineEdit.setText(default_sigma)
        self.ui.sigmaPPELineEdit.setText(default_sigma)
        self.ui.sigma5CRMLineEdit.setText(default_sigma)
        default_alpha_sharp = str(get_param("alpha_sharp", params))
        self.ui.sharpen3CRMLineEdit.setText(default_alpha_sharp)
        self.ui.sharpenPPELineEdit.setText(default_alpha_sharp)
        self.ui.sharpen5CRMLineEdit.setText(default_alpha_sharp)
        default_spot_detect_threshold = str(get_param("spot_detect_threshold", params))
        self.ui.spotDetection3CRMThresholdLineEdit.setText(default_spot_detect_threshold)
        self.ui.spotDetectionPPEThresholdLineEdit.setText(default_spot_detect_threshold)
        self.ui.spotDetection5CRMThresholdLineEdit.setText(default_spot_detect_threshold)
        self.ui.touchingThresholdLineEdit.setText(str(get_param("touching_threshold", params)))

        # connect various widgets to actions
        self.ui.addFilesButton.clicked.connect(self.addFiles)
        self.ui.clearCompletedFilesPushButton.clicked.connect(self.clearCompletedFiles)
        self.ui.quitPushButton.clicked.connect(self.quit)
        self.ui.testSettingsPushButton.clicked.connect(self.testSettings)
        self.ui.runBatchPushButton.clicked.connect(self.runBatch)

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

    def simulateProcessing(self):
        self.ui.progressBar.setRange(0, 5)
        for t in range(5):
            self.ui.progressBar.setValue(t)
            time.sleep(3)   # 3 seconds per "step"
        self.ui.progressBar.setValue(5)

    @Slot(bool)
    def testSettings(self, checked: bool = False):
        return self.processNextFile(True)

    @Slot(bool)
    def runBatch(self, checked: bool = False):
        while len(self.pendingFilesModel.stringList()) > 0:
            self.processNextFile(False)

    def processNextFile(self, validateParams: bool):
        pendingFilesList = self.pendingFilesModel.stringList()
        if self.running or len(pendingFilesList) == 0:
            return
        fileToRun = pendingFilesList[0]
        self.ui.activeFileLineEdit.setText(fileToRun)
        pendingFilesList = pendingFilesList[1:]
        self.pendingFilesModel.setStringList(pendingFilesList)

        # open confocal file and get image
        try:
            cf = ConfocalFile(fileToRun)
        except Exception as e:
            QMessageBox.warning(self, "Invalid File", f"Image file {fileToRun} could not be opened.  Error was: {e}")
            return

        self.processingPhase = "Denoising"
        imageNames = ["3'CRM Channel", "PPE Channel", "5'CRM Channel"]
        inputImages = [cf.channel_3CRM(), cf.channel_PPE(), cf.channel_5CRM()]
        sigmaWidgets = [self.ui.sigma3CRMLineEdit, self.ui.sigmaPPELineEdit, self.ui.sigma5CRMLineEdit]
        sharpenWidgets = [self.ui.sharpen3CRMLineEdit, self.ui.sharpenPPELineEdit, self.ui.sharpen5CRMLineEdit]
        outputImages = [None, None, None]
        i = 0
        self.pool = QThreadPool.globalInstance()
        self.pool.setMaxThreadCount(1)
        processingDone = False
        while not processingDone:
            inputImage = inputImages[i]
            myTask = RunnableDenoise()
            myTask.setAutoDelete(False)
            myTask.setInputImage(inputImage)
            firstSlice = int(self.ui.firstSliceLineEdit.text())
            firstSlice = max(firstSlice, 0)
            lastSlice = int(self.ui.lastSliceLineEdit.text())
            if lastSlice >= 0:
                lastSlice = min(lastSlice, inputImage.shape[0])
            else:
                lastSlice = max(inputImage.shape[0]-lastSlice, 0)
            myTask.setFirstSlice(firstSlice)
            myTask.setLastSlice(lastSlice)
            myTask.setStddev(float(sigmaWidgets[i].text()))
            myTask.setAlphaSharp(float(sharpenWidgets[i].text()))

            # set up the progress bar
            self.ui.progressBar.setMinimum(0)
            self.ui.progressBar.setMaximum(100)
            self.ui.progressBar.setValue(0)
            myTask.workerSignals.updateProgress.connect(self.ui.progressBar.setValue)

            self.running = True
            self.pool.start(myTask)
            self.pool.waitForDone()
            outputImages[i] = myTask.result()
            self.running = False

            if validateParams:
                self.icd = ImageCompareDialog()
                self.icd.setLeftImageVolume(inputImage[firstSlice:lastSlice])
                self.icd.setRightImageVolume(outputImages[i])    # only has the selected slices
                result = self.icd.exec()
                if result == QDialog.Accepted:
                    i = i + 1
                    if i >= len(inputImages):
                        processingDone = True
                    continue
                elif result == QDialog.Rejected:
                    processingDone = True
                    continue
                elif result == ImageCompareDialog.DiscardResults:
                    #TODO: need to figure out the best way to allow the user to
                    # adjust parameters before continuing where we left off
                    # (as opposed to starting over).  Need to save some state.
                    continue
                else:
                    raise ValueError(f"Unexpected return value: {result}")
            else:
                i = i + 1
                if i >= len(inputImages):
                    processingDone = True
                continue

        completedFilesList = self.completedFilesModel.stringList()
        completedFilesList.append(fileToRun)
        self.ui.activeFileLineEdit.setText("(none)")
        self.ui.progressBar.reset()
        self.completedFilesModel.setStringList(completedFilesList)
        self.running = False


    @Slot()
    def clearCompletedFiles(self):
        self.completedFilesModel.setStringList([])

    @Slot()
    def quit(self):
        self.close()

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
