# findSpotsTool.py
from qtpy.QtCore import QStringListModel, Signal, Slot
from qtpy.QtWidgets import QApplication, QFileDialog, QMainWindow, QMessageBox
from findSpotsTool_ui import Ui_MainWindow
from algorithms.countNuclei import ProcessStepCountNuclei
from algorithms.denoise import ProcessStepDenoiseConcurrent
from algorithms.threshold_mask import ProcessStepThresholdMask
from algorithms.detect_spots import ProcessStepDetectSpotsConcurrent
from algorithms.tripletDetection import ProcessStepFindTriplets, write_doublets, distanceSquared
from algorithms.touchingAnalysis import ProcessStepAnalyzeTouching, write_output
from algorithms.find_spots import get_param
from algorithms.confocal_file import ConfocalFile
from spots_io.plot_spots import plot_spots_2D, plot_spots_3D
from processing import ProcessStatus, ProcessStepIterate
from imageCompareDialog import ProcessStepVisualizeDenoise

from logging import INFO
from math import sqrt
from matplotlib import cm
import multiprocessing as mp
import numpy as np
from math import nan
from os.path import expanduser, splitext
import sys, platform
import tifffile as tiff
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
        self.ui.maskingCheckBox.setChecked(get_param('do_masking', params))
        self.changeMaskingEnableState() # pick up state just set
        default_nucleus_mask_threshold = str(get_param("nucleus_mask_threshold", params))
        self.ui.nucleusMaskingThresholdLineEdit.setText(default_nucleus_mask_threshold)
        self.ui.countNucleiCheckBox.setChecked(get_param('count_nuclei', params))

        # Spot detection settings
        default_spot_detect_threshold = str(get_param("spot_detect_threshold", params))
        self.ui.leftSpotDetectionThresholdLineEdit.setText(default_spot_detect_threshold)
        self.ui.middleSpotDetectionThresholdLineEdit.setText(default_spot_detect_threshold)
        self.ui.rightSpotDetectionThresholdLineEdit.setText(default_spot_detect_threshold)
        self.ui.saveDetectedSpotsCheckBox.setChecked(False)

        # Triplet detection settings
        self.ui.findDoubletsCheckBox.setChecked(get_param("find_doublets", params))
        self.ui.tripletLMMRMaxSizeLineEdit.setText(str(get_param("max_triplet_size", params)))
        self.ui.tripletLRMaxSizeLineEdit.setText(str(get_param("max_triplet_LR_size", params)))
        self.ui.xTouchingThresholdLineEdit.setText(str(get_param("touching_threshold_x", params)))
        self.ui.yTouchingThresholdLineEdit.setText(str(get_param("touching_threshold_y", params)))
        self.ui.zTouchingThresholdLineEdit.setText(str(get_param("touching_threshold_z", params)))

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
                       self.ui.sigmaNucleusLineEdit,
                       self.ui.sharpenLabel,
                       self.ui.leftSharpenLineEdit,
                       self.ui.middleSharpenLineEdit,
                       self.ui.rightSharpenLineEdit,
                       self.ui.sharpenNucleusLineEdit
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

    def write_distances(self, triplets, leftDoublets, rightDoublets, leftRigthDoublets, outName):
        """
        Write out the distances and the coordinates
        Order inside the triplet is {left, middle, right}
        """
        with open(outName, "w") as f:
            f.write("Xleft,Yleft,Zleft,Xmiddle,Ymiddle,Zmiddle,Xright,Yright,Zright,leftDist,rightDist,leftRightDist\n")
            for triplet in triplets:
                leftDist = sqrt(distanceSquared(triplet[0], triplet[1]))
                rightDist = sqrt(distanceSquared(triplet[1], triplet[2]))
                leftRightDist = sqrt(distanceSquared(triplet[0], triplet[2]))
                f.write(f"{triplet[0][0]},{triplet[0][1]},{triplet[0][2]}," +
                        f"{triplet[1][0]},{triplet[1][1]},{triplet[1][2]}," +
                        f"{triplet[2][0]},{triplet[2][1]},{triplet[2][2]}," +
                        f"{leftDist},{rightDist},{leftRightDist}\n")
            for leftDoublet in leftDoublets:
                leftDist = sqrt(distanceSquared(leftDoublet[0], leftDoublet[1]))
                f.write(f"{leftDoublet[0][0]},{leftDoublet[0][1]},{leftDoublet[0][2]}," +
                        f"{leftDoublet[1][0]},{leftDoublet[1][1]},{leftDoublet[1][2]}," +
                        f"{nan},{nan},{nan}," +
                        f"{leftDist},{nan},{nan}\n")
            for rightDoublet in rightDoublets:
                rightDist = sqrt(distanceSquared(rightDoublet[0], rightDoublet[1]))
                f.write(f"{nan},{nan},{nan}," +
                        f"{rightDoublet[0][0]},{rightDoublet[0][1]},{rightDoublet[0][2]}," +
                        f"{rightDoublet[1][0]},{rightDoublet[1][1]},{rightDoublet[1][2]}," +
                        f"{nan},{rightDist},{nan}\n")
            for leftRightDoublet in leftRigthDoublets:
                leftRightDist = sqrt(distanceSquared(leftRightDoublet[0], leftRightDoublet[1]))
                f.write(f"{leftRightDoublet[0][0]},{leftRightDoublet[0][1]},{leftRightDoublet[0][2]}," +
                        f"{nan},{nan},{nan}," +
                        f"{leftRightDoublet[1][0]},{leftRightDoublet[1][1]},{leftRightDoublet[1][2]}," +
                        f"{nan},{nan},{leftRightDist}\n")

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
            'save_spot_image': self.ui.saveDetectedSpotsCheckBox.isChecked()
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
            'nucleus_mask_threshold': float(self.ui.nucleusMaskingThresholdLineEdit.text()),
            'count_nuclei': bool(self.ui.countNucleiCheckBox.isChecked()),
            'nucleus_slice': int(self.ui.nucleusSliceLineEdit.text())
        }

        tripletsParams: Dict = {
            'find_doublets': self.ui.findDoubletsCheckBox.isChecked(),
            'max_triplet_size': float(self.ui.tripletLMMRMaxSizeLineEdit.text()),
            'max_triplet_LR_size': float(self.ui.tripletLRMaxSizeLineEdit.text())
        }
        touchingThresholdList = [
            float(self.ui.xTouchingThresholdLineEdit.text()),
            float(self.ui.yTouchingThresholdLineEdit.text()),
            float(self.ui.zTouchingThresholdLineEdit.text())
        ]
        touchingParams: Dict = {
            'touching_threshold': touchingThresholdList
        }

        # map the string to the CZI file channel
        channelItemFromString: dict = {
            '647': cf.channel_647(),
            '555': cf.channel_555(),
            '488': cf.channel_488()
        }

        # Instantiate the step outputs to be the source images, with matching parameters dicts
        # Note: stepOutputs is the output of a given step that is used as the input to the next step.
        #       The first processing step, like all the later ones, gets its input from the stepOutputs
        #       of the previous step, so the initial input data is put in stepOutputs.
        # Note: endOutputs is used by each step to provide step-specific additional outputs.
        #       A list element is appended to endOutputs for each processing step.  If a step doesn't
        #       need to output anything besides stepOutputs, an empty list is appended.

        # We provide all four channels as initial step inputs (in stepOutputs), regardless whether or not
        # masking or nucleus counting is enabled.
        # To reduce the number of channels before actual spot-finding, the masking process step is
        # always included, and it does nothing except remove the nucleus channel if it's disabled.
        # Nucleus counting process step is still included in the sequence if it's active.

        perChannelParamsList = [leftChannelParams, middleChannelParams, rightChannelParams, nucleusChannelParams]
        stepOutputs = [channelItemFromString[self.ui.leftChannelComboBox.currentText()],
                       channelItemFromString[self.ui.middleChannelComboBox.currentText()],
                       channelItemFromString[self.ui.rightChannelComboBox.currentText()],
                       cf.channel_nucleus()]

        processSequence: List = []

        # Save the index of some specific process steps, so that we can get results specific
        # to that step from endOutputs later
        countNucleiStep: int = 0
        detectSpotsStep: int = 0
        tripletDetectionStep: int = 1   # doublets lists

        #
        # Build the sequence of process steps, based on what is selected in the UI and whether we're validating params or not
        if self.ui.denoiseCheckBox.isChecked():
            if validateParams:
                processSequence.append(ProcessStepIterate(ProcessStepVisualizeDenoise, perChannelParamsList))
            else:
                processSequence.append(ProcessStepIterate(ProcessStepDenoiseConcurrent, perChannelParamsList))
            # since we're adding a process step before CountNuclei and DetectSpots...
            countNucleiStep += 1
            detectSpotsStep += 1
            tripletDetectionStep += 1

        if self.ui.countNucleiCheckBox.isChecked():
            processSequence.append(ProcessStepCountNuclei(nucleusChannelParams))
            # since we're adding a process step before DetectSpots...
            detectSpotsStep += 1
            tripletDetectionStep += 1

        # Include the ThresholdMask process step regardless, since it needs to
        # reduce the number of channels from four to three, but signal
        # whether or not to actually do masking via the params
        nucleusChannelParams['do_masking'] = self.ui.maskingCheckBox.isChecked()
        processSequence.append(ProcessStepThresholdMask(nucleusChannelParams))
        # since we're adding a process step before DetectSpots...
        detectSpotsStep += 1
        tripletDetectionStep += 1

        # Add the rest of the process steps that require no conditional processing
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
        nucleusCoords, nucleusCountImage = endOutputs[countNucleiStep] if self.ui.countNucleiCheckBox.isChecked() else (None, None)
        triplets, leftDoublets, rightDoublets, leftRightDoublets = endOutputs[tripletDetectionStep]

        outStem, _ = splitext(fileToRun)
        self.write_distances(triplets, leftDoublets, rightDoublets, leftRightDoublets, outStem + "_distances.csv")
        write_output(output, outStem + "_results.txt", len(nucleusCoords) if nucleusCoords else None)

        # construct a new rgb version of the nucleus image volume and specified slice
        spot_projection_slice = int(self.ui.nucleusSliceLineEdit.text())
        spot_projection_slice = max(0, min(spot_projection_slice, cf.channel_nucleus().shape[0]))
        gray_colormap = cm.get_cmap('gray', 256)
        nucleus_3D_rgb = gray_colormap(cf.channel_nucleus(), bytes=True)[:,:,:,0:3]
        nucleus_2D_rgb = gray_colormap(cf.channel_nucleus()[spot_projection_slice], bytes=True)[:,:,0:3]

        # For now, always plot nuclei if we counted them
        if self.ui.countNucleiCheckBox.isChecked():
            nuclei_2d_rgb = gray_colormap(nucleusCountImage, bytes=True)[:,:,0:3]
            plot_spots_2D(nuclei_2d_rgb, nucleusCoords, (1., 1., 1.), lambda pos: [255, 255, 0])
            tiff.imwrite(outStem + "_nuclei_rgb.tiff", nuclei_2d_rgb)

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
        scaleTuple = (scale['X'], scale['Y'], scale['Z'])
        plot_spots_2D(nucleus_2D_rgb, output, scaleTuple, lambda pos: colors[pos[3]])
        tiff.imwrite(outStem + "_2D_rgb.tiff", nucleus_2D_rgb)

        plot_spots_3D(nucleus_3D_rgb, output, scaleTuple, lambda pos: colors[pos[3]])
        tiff.imwrite(outStem + "_3D_rgb.tiff", nucleus_3D_rgb)

        if self.ui.findDoubletsCheckBox.isChecked():
            doublet_2D_rgb = gray_colormap(cf.channel_nucleus()[spot_projection_slice], bytes=True)[:,:,0:3]
            # Calculate the left doublet centroids
            leftDoubletCentroids = [((doublet[0][0] + doublet[1][0])/2.,
                                     (doublet[0][1] + doublet[1][0])/2.,
                                     (doublet[0][2] + doublet[1][2])/2.) for doublet in leftDoublets]
            # Plot the left doublet centroids in red
            plot_spots_2D(doublet_2D_rgb, leftDoubletCentroids, scaleTuple, lambda pos: (255, 0, 0))
            # Calculate the right doublet centroids
            rightDoubletCentroids = [((doublet[0][0] + doublet[1][0])/2.,
                                      (doublet[0][1] + doublet[1][0])/2.,
                                      (doublet[0][2] + doublet[1][2])/2.) for doublet in rightDoublets]
            # Plot the right doublet centroids in blue on the same image as the left doublets
            plot_spots_2D(doublet_2D_rgb, rightDoubletCentroids, scaleTuple, lambda pos: (0, 0, 255))
            tiff.imwrite(outStem + "_doublets_rgb.tiff", doublet_2D_rgb)

        if self.ui.saveDetectedSpotsCheckBox.isChecked() and len(endOutputs) > detectSpotsStep and endOutputs[detectSpotsStep]:
            spots = endOutputs[detectSpotsStep]
            spotColors = [
                (255,   0,   0),     # red
                (  0, 255,   0),     # green
                (  0,   0, 255)      # blue
            ]

            spots_2D_rgb = gray_colormap(cf.channel_nucleus()[spot_projection_slice], bytes=True)[:,:,0:3]
            spots_3D_rgb = gray_colormap(ch, bytes=True)[:,:,:,0:3]

            spotsScale = (1., 1., 1.)
            for ix, ch in enumerate([
                    channelItemFromString[self.ui.leftChannelComboBox.currentText()],
                    channelItemFromString[self.ui.middleChannelComboBox.currentText()],
                    channelItemFromString[self.ui.rightChannelComboBox.currentText()]
                    ]):
                spots_image = gray_colormap(ch, bytes=True)[:,:,:,0:3]
                plot_spots_2D(spots_2D_rgb, spots[ix], spotsScale, lambda pos: spotColors[ix], filled=False)
                plot_spots_3D(spots_3D_rgb, spots[ix], spotsScale, lambda pos: spotColors[ix], filled=False)
                plot_spots_3D(spots_image, spots[ix], spotsScale, lambda pos: spotColors[ix], filled=False)
                tiff.imwrite(outStem + f"_ch{ix}_spots.tiff", spots_image)
            tiff.imwrite(outStem + "_spots_3D_rgb.tiff", spots_3D_rgb)
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
    # Run the main Qt event loop, exiting the app when the event loop exits
    sys.exit(app.exec_())
