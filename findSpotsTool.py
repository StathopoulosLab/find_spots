# findSpotsTool.py
from qtpy.QtCore import Qt, QObject, QRunnable, QThreadPool, QStringListModel, Signal, Slot
from qtpy.QtWidgets import QApplication, QDialog, QDialogButtonBox, QFileDialog, QMainWindow, QMessageBox
from findSpotsTool_ui import Ui_MainWindow
from imageCompareDialog import ImageCompareDialog
from algorithms.countNuclei import ProcessStepCountNuclei
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

        # initialize parameters
        # For now, we don't support saving of params.
        # defaults come from the default_params dict initialized in find_spots.py
        params = {}

        # Initialize dynamic UI contents and connect UI widget Signals to Slots
        # Slice Selection Settings:
        self.ui.firstSliceLineEdit.setText(str(get_param("first_slice", params)))
        self.ui.lastSliceLineEdit.setText(str(get_param("last_slice", params)))
        self.ui.nucleusSliceLineEdit.setText(str(get_param("nucleus_slice", params)))

        # Channel Settings
        for comboBox in [self.ui.leftChannelComboBox,
                         self.ui.middleChannelComboBox,
                         self.ui.rightChannelComboBox]:
            comboBox.addItems(['647','555','488'])
        try:
            self.ui.leftChannelComboBox.setCurrentText(str(get_param('left_channel', params)))
        except ...:
            self.ui.leftChannelComboBox.setCurrentText("647")
        try:
            self.ui.middleChannelComboBox.setCurrentText(str(get_param('middle_channel', params)))
        except ...:
            self.ui.middleChannelComboBox.setCurrentText("488")
        try:
            self.ui.rightChannelComboBox.setCurrentText(str(get_param('right_channel', params)))
        except ...:
            self.ui.rightChannelComboBox.setCurrentText("555")

        # Denoising settings
        self.ui.denoiseCheckBox.clicked.connect(self.changeDenoiseEnableState)
        self.ui.denoiseCheckBox.setChecked(bool(get_param('do_denoising', params)))
        self.changeDenoiseEnableState() # pick up state just set
        self.ui.use3DCheckBox.setChecked(bool(get_param('use_denoise3d', params)))
        default_sigma = str(get_param("sigma", params))
        self.ui.leftSigmaLineEdit.setText(default_sigma)
        self.ui.middleSigmaLineEdit.setText(default_sigma)
        self.ui.rightSigmaLineEdit.setText(default_sigma)
        self.ui.sigmaNucleusLineEdit.setText(default_sigma)
        default_alpha_sharp = str(get_param("alpha_sharp", params))
        self.ui.leftSharpenLineEdit.setText(default_alpha_sharp)
        self.ui.middleSharpenLineEdit.setText(default_alpha_sharp)
        self.ui.rightSharpenLineEdit.setText(default_alpha_sharp)

        # Masking settings
        self.ui.sharpenNucleusLineEdit.setText(default_alpha_sharp)
        self.ui.maskingCheckBox.clicked.connect(self.changeMaskingEnableState)
        self.ui.maskingCheckBox.setChecked(bool(get_param('do_masking', params)))
        self.changeMaskingEnableState() # pick up state just set
        default_nucleus_mask_threshold = str(get_param("nucleus_mask_threshold", params))
        self.ui.nucleusMaskingThresholdLineEdit.setText(default_nucleus_mask_threshold)
        self.ui.countNucleiCheckBox.setChecked(bool(get_param('count_nuclei', params)))

        # Spot detection settings
        default_spot_detect_threshold = str(get_param("spot_detect_threshold", params))
        self.ui.leftSpotDetectionThresholdLineEdit.setText(default_spot_detect_threshold)
        self.ui.middleSpotDetectionThresholdLineEdit.setText(default_spot_detect_threshold)
        self.ui.rightSpotDetectionThresholdLineEdit.setText(default_spot_detect_threshold)
        self.ui.saveDetectedSpotsCheckBox.setChecked(False)

        # Triplet detection settings
        self.ui.tripletMaxSizeLineEdit.setText(str(get_param("max_triplet_size", params)))
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

    def setLogger(self, logger):
        self._logger = logger

    @Slot()
    def changeDenoiseEnableState(self):
        for widget in [self.ui.use3DCheckBox,
                       self.ui.leftDenoiseLabel,
                       self.ui.middleDenoiseLabel,
                       self.ui.rightDenoiseLabel,
                       self.ui.denoiseNucleusLabel,
                       self.ui.sigmaLabel,
                       self.ui.leftSigmaLineEdit,
                       self.ui.middleSigmaLineEdit,
                       self.ui.rightSigmaLineEdit,
                       self.ui.sharpenLabel,
                       self.ui.leftSharpenLineEdit,
                       self.ui.middleSharpenLineEdit,
                       self.ui.rightSharpenLineEdit,
                       self.ui.saveDetectedSpotsCheckBox
                       ]:
            widget.setEnabled(self.ui.denoiseCheckBox.isChecked())

    @Slot()
    def changeMaskingEnableState(self):
        for widget in [self.ui.nucleusMaskingThresholdLabel,
                       self.ui.nucleusMaskingThresholdLineEdit]:
            widget.setEnabled(self.ui.maskingCheckBox.isChecked())

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

        # params for the left channel
        leftChannelParams = {
            'firstSlice': int(self.ui.firstSliceLineEdit.text()),
            'lastSlice': int(self.ui.lastSliceLineEdit.text()),
            'sigma': int(self.ui.leftSigmaLineEdit.text()),
            'sharpen': float(self.ui.leftSharpenLineEdit.text()),
            'spot_detect_threshold': float(self.ui.leftSpotDetectionThresholdLineEdit.text()),
            'save_spot_image': bool(self.ui.saveDetectedSpotsCheckBox.isChecked())
        }
        # params for the middle channel
        middleChannelParams = {
            'firstSlice': int(self.ui.firstSliceLineEdit.text()),
            'lastSlice': int(self.ui.lastSliceLineEdit.text()),
            'sigma': int(self.ui.middleSigmaLineEdit.text()),
            'sharpen': float(self.ui.middleSharpenLineEdit.text()),
            'spot_detect_threshold': float(self.ui.middleSpotDetectionThresholdLineEdit.text()),
            'save_spot_image': bool(self.ui.saveDetectedSpotsCheckBox.isChecked())
        }
        # params for the right channel
        rightChannelParams = {
            'firstSlice': int(self.ui.firstSliceLineEdit.text()),
            'lastSlice': int(self.ui.lastSliceLineEdit.text()),
            'sigma': int(self.ui.rightSigmaLineEdit.text()),
            'sharpen': float(self.ui.rightSharpenLineEdit.text()),
            'spot_detect_threshold': float(self.ui.rightSpotDetectionThresholdLineEdit.text()),
            'save_spot_image': bool(self.ui.saveDetectedSpotsCheckBox.isChecked())
        }
        # params for Nucleus channel
        nucleusChannelParams = {
            'firstSlice': int(self.ui.firstSliceLineEdit.text()),
            'lastSlice': int(self.ui.lastSliceLineEdit.text()),
            'sigma': int(self.ui.sigmaNucleusLineEdit.text()),
            'sharpen': float(self.ui.sharpenNucleusLineEdit.text()),
            'nucleus_mask_threshold': int(self.ui.nucleusMaskingThresholdLineEdit.text()),
            'count_nuclei': bool(self.ui.countNucleiCheckBox.isChecked()),
            'nucleus_slice': int(self.ui.nucleusSliceLineEdit.text())
        }

        tripletsParams: Dict = {
            'max_triplet_size': float(self.ui.tripletMaxSizeLineEdit.text())
        }
        touchingParams: Dict = {
            'touching_threshold': float(self.ui.touchingThresholdLineEdit.text())
        }
        # stepOutputs = [cf.channel_647(), cf.channel_555(), cf.channel_488(), cf.channel_nucleus()]
        channelItemFromString: dict = {
            # map the string to the CZI file channel
            '647': cf.channel_647(),
            '555': cf.channel_555(),
            '488': cf.channel_488()
        }

        # Instantiate the step outputs to be the source images, with matching parameters dicts
        perChannelParamsList = [leftChannelParams, middleChannelParams, rightChannelParams]
        stepOutputs = [channelItemFromString[self.ui.leftChannelComboBox.currentText()],
                       channelItemFromString[self.ui.middleChannelComboBox.currentText()],
                       channelItemFromString[self.ui.rightChannelComboBox.currentText()]]

        if self.ui.maskingCheckBox.isChecked() or self.ui.countNucleiCheckBox.isChecked():
            stepOutputs.append(cf.channel_nucleus())
            perChannelParamsList.append(nucleusChannelParams)

        processSequence: List = []
        # save the index of the step in processSequence that detects spots, so that we can find the results in endOutputs later
        detectSpotsStep: int = 0
        # also save the index of the process step where we count nuclei, so we can get the result later
        countNucleiStep: int = 0
        # Build the sequence of process steps, based on what is selected in the UI and whether we're validating params or not
        if self.ui.denoiseCheckBox.isChecked():
            if validateParams:
                processSequence.append(ProcessStepIterate(ProcessStepVisualizeDenoise, perChannelParamsList))
            else:
                processSequence.append(ProcessStepIterate(ProcessStepDenoiseConcurrent, perChannelParamsList))
            detectSpotsStep += 1
            countNucleiStep += 1

        if self.ui.countNucleiCheckBox.isChecked():
            processSequence.append(ProcessStepCountNuclei(nucleusChannelParams))
            detectSpotsStep += 1

        if self.ui.maskingCheckBox.isChecked():
            processSequence.append(ProcessStepThresholdMask(perChannelParamsList[-1]))
            detectSpotsStep += 1
        processSequence.extend([
                ProcessStepDetectSpotsConcurrent(perChannelParamsList),
                ProcessStepFindTriplets(scale, tripletsParams),
                ProcessStepAnalyzeTouching(touchingParams)
            ])

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
        nucleusCount = endOutputs[countNucleiStep] if self.ui.countNucleiCheckBox.isChecked() else None

        outStem, _ = splitext(fileToRun)
        write_output(output, outStem + "_results.txt", nucleusCount)

        # construct a new rgb version of the nucleus image volume and specified slice
        spot_projection_slice = int(self.ui.nucleusSliceLineEdit.text())
        spot_projection_slice = max(0, min(spot_projection_slice, cf.channel_nucleus().shape[0]))
        gray_colormap = cm.get_cmap('gray', 256)
        nucleus_3D_rgb = gray_colormap(cf.channel_nucleus(), bytes=True)[:,:,:,0:3]
        nucleus_2D_rgb = gray_colormap(cf.channel_nucleus()[spot_projection_slice], bytes=True)[:,:,0:3]

        # Now plot each of the triplets into the image stack, colored by conformation
        colors = {
            '000': ( 64,  64,  64),     # nothing touching: dark gray
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
                    if y + dy < 0 or y + dy >= nucleus_3D_rgb.shape[2]:
                        continue
                    nucleus_2D_rgb[x+dx][y+dy] = color
                    for dz in range(-1, 2):
                        if z + dz < 0 or z + dz >= nucleus_3D_rgb.shape[0]:
                            continue
                        nucleus_3D_rgb[z+dz][x+dx][y+dy] = color
        tiff.imwrite(outStem + "_3D_rgb.tiff", nucleus_3D_rgb)
        tiff.imwrite(outStem + "_2D_rgb.tiff", nucleus_2D_rgb)

        if self.ui.saveDetectedSpotsCheckBox.isChecked() and len(endOutputs) > detectSpotsStep and endOutputs[detectSpotsStep]:
            spots = endOutputs[detectSpotsStep]
            spotColors = [
                (255,   0,   0),     # red
                (  0, 255,   0),     # green
                (  0,   0, 255)      # blue
            ]
            spots_2D_rgb = gray_colormap(cf.channel_nucleus()[spot_projection_slice], bytes=True)[:,:,0:3]
            for ix, ch in enumerate([cf.channel_647(), cf.channel_555(), cf.channel_488()]):
                spots_image = gray_colormap(ch, bytes=True)[:,:,:,0:3]
                color = spotColors[ix]
                for chanSpot in spots[ix]:
                    x = round(chanSpot[0])
                    y = round(chanSpot[1])
                    z = round(chanSpot[2])
                    for dx in range(-6,7):
                        if (
                            x + dx < 0 or x + dx >= spots_image.shape[1] or
                            z < 0 or z >= spots_image.shape[0]
                        ):
                            continue
                        for dy in range(-6, 7):
                            if y + dy < 0 or y + dy >= spots_image.shape[2]:
                                continue
                            if dx in (-6, 6) or dy in (-6, 6):   # draw an open rectangle
                                spots_image[z][x+dx][y+dy] = color
                                spots_2D_rgb[x+dx][y+dy] = color
                tiff.imwrite(outStem + f"_ch{ix}_spots.tiff", spots_image)
            tiff.imwrite(outStem + "_spots_rgb.tiff", spots_2D_rgb)

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
