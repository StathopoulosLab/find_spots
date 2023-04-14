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
from processing import ProcessStatus, ProcessStep, ProcessStepIterate
from imageCompareDialog import ProcessStepVisualizeDenoise

from logging import INFO
from matplotlib import cm
import multiprocessing as mp
import numpy as np
from os.path import expanduser, splitext
import sys, platform
import tifffile as tiff
import time
from typing import Dict, List

class FindSpotsTool(QMainWindow):

    fileNameNone = '(none)'
    noteProgressChanged = Signal(int, str)

    testSettingsPipeline = [
        (ProcessStepDenoiseConcurrent, [])
    ]
    def __init__(self, app: QApplication):
        super().__init__()

        self._app = app
        self._logger = None

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
        self.ui.sigma647LineEdit.setText(default_sigma)
        self.ui.sigma555LineEdit.setText(default_sigma)
        self.ui.sigma488LineEdit.setText(default_sigma)
        self.ui.sigmaNucleusLineEdit.setText(default_sigma)
        default_alpha_sharp = str(get_param("alpha_sharp", params))
        self.ui.sharpen647LineEdit.setText(default_alpha_sharp)
        self.ui.sharpen555LineEdit.setText(default_alpha_sharp)
        self.ui.sharpen488LineEdit.setText(default_alpha_sharp)
        self.ui.sharpenNucleusLineEdit.setText(default_alpha_sharp)
        default_nucleus_mask_threshold = str(get_param("nucleus_mask_threshold", params))
        self.ui.nucleusMaskingThresholdLineEdit.setText(default_nucleus_mask_threshold)
        default_spot_detect_threshold = str(get_param("spot_detect_threshold", params))
        self.ui.spotDetection647ThresholdLineEdit.setText(default_spot_detect_threshold)
        self.ui.spotDetection555ThresholdLineEdit.setText(default_spot_detect_threshold)
        self.ui.spotDetection488ThresholdLineEdit.setText(default_spot_detect_threshold)
        self.ui.tripletMaxSizeLineEdit.setText(str(get_param("max_triplet_size", params)))
        self.ui.touchingThresholdLineEdit.setText(str(get_param("touching_threshold", params)))
        self.ui.spotProjectionSliceLineEdit.setText(str(get_param("spot_projection_slice", params)))

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

    def setLogger(self, logger):
        self._logger = logger

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
            # params for 647 channel
            {
                'firstSlice': int(self.ui.firstSliceLineEdit.text()),
                'lastSlice': int(self.ui.lastSliceLineEdit.text()),
                'sigma': int(self.ui.sigma647LineEdit.text()),
                'sharpen': float(self.ui.sharpen647LineEdit.text()),
                'spot_detect_threshold': float(self.ui.spotDetection647ThresholdLineEdit.text())
            },
            # params for 555 channel
            {
                'firstSlice': int(self.ui.firstSliceLineEdit.text()),
                'lastSlice': int(self.ui.lastSliceLineEdit.text()),
                'sigma': int(self.ui.sigma555LineEdit.text()),
                'sharpen': float(self.ui.sharpen555LineEdit.text()),
                'spot_detect_threshold': float(self.ui.spotDetection555ThresholdLineEdit.text())
            },
            # params for 488 channel
            {
                'firstSlice': int(self.ui.firstSliceLineEdit.text()),
                'lastSlice': int(self.ui.lastSliceLineEdit.text()),
                'sigma': int(self.ui.sigma488LineEdit.text()),
                'sharpen': float(self.ui.sharpen488LineEdit.text()),
                'spot_detect_threshold': float(self.ui.spotDetection488ThresholdLineEdit.text())
            },
            # params for Nucleus channel
            {
                'firstSlice': int(self.ui.firstSliceLineEdit.text()),
                'lastSlice': int(self.ui.lastSliceLineEdit.text()),
                'sigma': int(self.ui.sigmaNucleusLineEdit.text()),
                'sharpen': float(self.ui.sharpenNucleusLineEdit.text()),
                'nucleus_mask_threshold': int(self.ui.nucleusMaskingThresholdLineEdit.text())

            }
        ]
        tripletsParams: Dict = {
            'max_triplet_size': float(self.ui.tripletMaxSizeLineEdit.text())
        }
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

        stepOutputs = [cf.channel_647(), cf.channel_488(), cf.channel_555(), cf.channel_nucleus()]
        endOutputs = []
        for step in processSequence:
            step.setApp(self._app)
            step.setLogger(self._logger)
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

        # construct a new rgb version of the nucleus image volume and specified slice
        spot_projection_slice = int(self.ui.spotProjectionSliceLineEdit.text())
        spot_projection_slice = max(0, min(spot_projection_slice, cf.channel_nucleus().shape[0]))
        gray_colormap = cm.get_cmap('gray', 256)
        nucleus_3D_rgb = gray_colormap(cf.channel_nucleus(), bytes=True)[:,:,:,0:3]
        nucleus_2D_rgb = gray_colormap(cf.channel_nucleus()[spot_projection_slice], bytes=True)[:,:,0:3]

        # Now plot each of the triplets into the image stack, colored by conformation
        colors = {
            '000': ( 32,  32,  32),     # nothing touching: dark gray
            '100': (255, 255,   0),     # only red touching green: yellow
            '010': (  0, 255, 255),     # only green touching blue: cyan
            '001': (255,   0, 255),     # only blue touching red: magenta
            '110': (  0, 255,   0),     # red touching green, and green touching blue: green
            '011': (  0,   0, 255),     # green touching blue and blue touching red: blue
            '101': (255,   0,   0),     # blue touching red and red touching green: red
            '111': (255, 255, 255)      # all spots touching: white
            }

        for triplet in output:
            x = round(triplet[0] / scale['X'])
            y = round(triplet[1] / scale['Y'])
            z = round(triplet[2] / scale['Z'])
            color = colors[triplet[3]]
            for dx in range(-6,7):
                if x + dx < 0 or x + dx >= nucleus_3D_rgb.shape[1]:
                    continue
                for dy in range(-6, 7):
                    if y + dx < 0 or y + dy >= nucleus_3D_rgb.shape[2]:
                        continue
                    nucleus_2D_rgb[x+dx][y+dy] = color
                    for dz in range(-1, 2):
                        if z + dz < 0 or z + dz >= nucleus_3D_rgb.shape[0]:
                            continue
                        nucleus_3D_rgb[z+dz][x+dx][y+dy] = color
        tiff.imwrite(outStem + "_3D_rgb.tiff", nucleus_3D_rgb)
        tiff.imwrite(outStem + "_2D_rgb.tiff", nucleus_2D_rgb)

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
    if True or platform.system() == "Darwin":
        mp.set_start_method('spawn')
    # Create the Qt Application
    app = QApplication(sys.argv)

    tool = FindSpotsTool(app)
    logger = mp.log_to_stderr()
    logger.setLevel(INFO)
    tool.setLogger(logger)
    tool.screen_center = app.screens()[len(app.screens())-1].availableGeometry().center()
    # spacing = QPoint((window.width() + video.width()) / 4 + 5, 0)
    qr = tool.frameGeometry()
    qr.moveCenter(tool.screen_center)
    tool.move(qr.topLeft())
    tool.show()
    # Run the main Qt loop
    sys.exit(app.exec_())
