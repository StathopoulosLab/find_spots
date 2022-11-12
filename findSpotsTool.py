# findSpotsTool.py
from qtpy.QtCore import Qt, QObject, QRunnable, QThreadPool, QStringListModel, Signal, Slot
from qtpy.QtWidgets import QApplication, QDialog, QDialogButtonBox, QFileDialog, QMainWindow, QMessageBox
from findSpotsTool_ui import Ui_MainWindow
from imageCompareDialog import ImageCompareDialog
from algorithms.denoise import ProcessStepDenoiseConcurrent
from algorithms.threshold_mask import ProcessStepThresholdMask
from algorithms.detect_spots import ProcessStepDetectSpotsConcurrent, ProcessStepDetectSpots
from algorithms.tripletDetection import ProcessStepFindTriplets
from algorithms.touchingAnalysis import ProcessStepAnalyzeTouching, write_output
from algorithms.find_spots import get_param
from algorithms.confocal_file import ConfocalFile
from algorithms.detect_spots import detect_spots
from processing import ProcessStatus, ProcessStep, ProcessStepIterate
from imageCompareDialog import ProcessStepVisualizeDenoise
from os.path import expanduser, splitext
import tifffile as tiff
from PIL import Image
from matplotlib import cm
from enum import Enum
import sys, platform
import time
from typing import Dict, List
import multiprocessing as mp

class FindSpotsTool(QMainWindow):

    fileNameNone = '(none)'
    noteProgressChanged = Signal(int, str)

    testSettingsPipeline = [
        (ProcessStepDenoiseConcurrent, [])
    ]
    def __init__(self, app: QApplication):
        super().__init__()

        self._app = app

        # set up the main window UI
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # file processing data items
        self.pendingFilesModel = QStringListModel()
        self.ui.pendingFilesListView.setModel(self.pendingFilesModel)
        self.currentlyProcessingFile = None
        self.ui.activeFileLineEdit.insert(self.fileNameNone)
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
        self.ui.sigmaDAPILineEdit.setText(default_sigma)
        default_alpha_sharp = str(get_param("alpha_sharp", params))
        self.ui.sharpen3CRMLineEdit.setText(default_alpha_sharp)
        self.ui.sharpenPPELineEdit.setText(default_alpha_sharp)
        self.ui.sharpen5CRMLineEdit.setText(default_alpha_sharp)
        self.ui.sharpenDAPILineEdit.setText(default_alpha_sharp)
        default_nucleus_mask_threshold = str(get_param("nucleus_mask_threshold", params))
        self.ui.nucleusMaskingThresholdLineEdit.setText(default_nucleus_mask_threshold)
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

        # connect other signals
        self.noteProgressChanged.connect(self.progressChanged)

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

    def processNextFile(self, validateParams: bool) -> None:
        # There may be a file currently being processed, where the user
        # rejected the params for one of the process steps.  We need to
        # restart processing that file with the process step that was
        # rejected.

        def progressCallback(progress: int, stepName: str) -> None:
            self.noteProgressChanged.emit(progress, stepName)

        fileToRun = self.ui.activeFileLineEdit.text()
        if fileToRun == None or fileToRun == "" or fileToRun == self.fileNameNone:
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
        scale = cf.get_scale()

        # set up the progress bar
        self.ui.progressBar.setMinimum(0)
        self.ui.progressBar.setMaximum(100)
        self.ui.progressBar.setValue(0)

        # set up the processing sequence and params
        perChannelParamsList = [
            # params for 3'CRM channel
            {
                'firstSlice': int(self.ui.firstSliceLineEdit.text()),
                'lastSlice': int(self.ui.lastSliceLineEdit.text()),
                'sigma': int(self.ui.sigma3CRMLineEdit.text()),
                'sharpen': float(self.ui.sharpen3CRMLineEdit.text()),
                'spot_detect_threshold': float(self.ui.spotDetection3CRMThresholdLineEdit.text())
            },
            # params for PPE channel
            {
                'firstSlice': int(self.ui.firstSliceLineEdit.text()),
                'lastSlice': int(self.ui.lastSliceLineEdit.text()),
                'sigma': int(self.ui.sigmaPPELineEdit.text()),
                'sharpen': float(self.ui.sharpenPPELineEdit.text()),
                'spot_detect_threshold': float(self.ui.spotDetectionPPEThresholdLineEdit.text())
            },
            # params for 5'CRM channel
            {
                'firstSlice': int(self.ui.firstSliceLineEdit.text()),
                'lastSlice': int(self.ui.lastSliceLineEdit.text()),
                'sigma': int(self.ui.sigma5CRMLineEdit.text()),
                'sharpen': float(self.ui.sharpen5CRMLineEdit.text()),
                'spot_detect_threshold': float(self.ui.spotDetection5CRMThresholdLineEdit.text())
            },
            # params for DAPI channel
            {
                'firstSlice': int(self.ui.firstSliceLineEdit.text()),
                'lastSlice': int(self.ui.lastSliceLineEdit.text()),
                'sigma': int(self.ui.sigmaDAPILineEdit.text()),
                'sharpen': float(self.ui.sharpenDAPILineEdit.text()),
                'nucleus_mask_threshold': int(self.ui.nucleusMaskingThresholdLineEdit.text())

            }
        ]
        tripletsParams: Dict = {}
        touchingParams: Dict = {
            'touching_threshold': float(self.ui.touchingThresholdLineEdit.text())
        }

        processSequence: List[ProcessStep] = [
                ProcessStepIterate(ProcessStepVisualizeDenoise, perChannelParamsList),
                ProcessStepThresholdMask(perChannelParamsList[-1]),
                ProcessStepDetectSpotsConcurrent(perChannelParamsList),
                ProcessStepFindTriplets(scale, tripletsParams),
                ProcessStepAnalyzeTouching(touchingParams)
            ] if validateParams else [
                ProcessStepIterate(ProcessStepDenoiseConcurrent, perChannelParamsList),
                ProcessStepThresholdMask(perChannelParamsList[-1]),
                ProcessStepDetectSpotsConcurrent(perChannelParamsList),
                ProcessStepFindTriplets(scale, tripletsParams),
                ProcessStepAnalyzeTouching(touchingParams)
            ]

        stepOutputs = [cf.channel_3CRM(), cf.channel_PPE(), cf.channel_5CRM(), cf.channel_antibody()]
        endOutputs = []
        for step in processSequence:
            step.setApp(self._app)
            step.setInputs(stepOutputs)
            step.run(progressCallback)
            if step.status() != ProcessStatus.COMPLETED:
                msgBox = QMessageBox()
                msgBox.exec()
                return
            stepOutputs = step.stepOutputs()
            endOutputs.append(step.endOutputs())
        output = stepOutputs[0]
        conformance = endOutputs[-1][0]

        outStem, _ = splitext(fileToRun)
        write_output(output, outStem + "_results.txt")

        # construct a new rgb version of the antibody image volume
        gray_colormap = cm.get_cmap('gray', 256)
        antibody_rgb = gray_colormap(cf.channel_antibody(), bytes=True)[:,:,:,0:3]

        # Now plot each of the triplets into the image stack, colored by conformation
        colors = {
            '000': (255,   0,   0),     # red
            '100': (  0,   0, 255),     # blue
            '010': (  0, 255,   0),     # green
            '001': (  0, 255, 255),     # cyan
            '110': (255, 255,   0),     # yellow
            '101': (  0,   0,   0),     # black
            '011': (255, 255, 255),     # white
            '111': (255,   0, 255)      # magenta
            }

        for triplet in output:
            x = round(triplet[0] / scale['X'])
            y = round(triplet[1] / scale['Y'])
            z = round(triplet[2] / scale['Z'])
            color = colors[triplet[3]]
            for dx in range(-6,7):
                if x + dx < 0 or x + dx >= antibody_rgb.shape[1]:
                    continue
                for dy in range(-6, 7):
                    if y + dx < 0 or y + dy >= antibody_rgb.shape[2]:
                        continue
                    for dz in range(-2, 3):
                        if z + dz < 0 or z + dz >= antibody_rgb.shape[0]:
                            continue
                        antibody_rgb[z+dz][x+dx][y+dy] = color
        tiff.imwrite(outStem + "_rgb.tiff", antibody_rgb)

        completedFilesList = self.completedFilesModel.stringList()
        completedFilesList.append(fileToRun)
        self.ui.activeFileLineEdit.setText(self.fileNameNone)
        self.progressChanged(0, "")
        self.ui.progressBar.reset()
        self.completedFilesModel.setStringList(completedFilesList)
        self.running = False

    @Slot(int, str)
    def progressChanged(self, progress: int, stepName: str) -> None:
        self.ui.progressBar.setValue(progress)
        self.ui.stepNameLineEdit.setText(stepName)

    @Slot()
    def clearCompletedFiles(self):
        self.completedFilesModel.setStringList([])

    @Slot()
    def quit(self):
        self.close()

if __name__ == "__main__":
    if platform.system() == "Darwin":
        mp.set_start_method('spawn')
    # Create the Qt Application
    app = QApplication(sys.argv)

    tool = FindSpotsTool(app)
    tool.screen_center = app.screens()[len(app.screens())-1].availableGeometry().center()
    # spacing = QPoint((window.width() + video.width()) / 4 + 5, 0)
    qr = tool.frameGeometry()
    qr.moveCenter(tool.screen_center)
    tool.move(qr.topLeft())
    tool.show()
    # Run the main Qt loop
    sys.exit(app.exec_())
