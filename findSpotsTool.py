# findSpotsTool.py
from qtpy.QtCore import QStringListModel, Signal, Slot, QThreadPool
from qtpy.QtWidgets import (QApplication, QFileDialog, QMainWindow, QMessageBox,
                            QLabel, QLineEdit, QGroupBox, QGridLayout)
from findSpotsTool_ui import Ui_MainWindow
from algorithms.countNuclei import ProcessStepCountNuclei
from algorithms.denoise import ProcessStepDenoiseConcurrent
from algorithms.threshold_mask import ProcessStepThresholdMask
from algorithms.detect_spots import ProcessStepDetectSpotsConcurrent
from algorithms.tripletDetection import ProcessStepFindTriplets, distanceSquared
from algorithms.touchingAnalysis import ProcessStepAnalyzeTouching, write_output
from algorithms.nuclear_morphology import ProcessStepNuclearMorphology, compute_spot_boundary_distances
from algorithms.filter_spots import (filter_triplets, filter_doublets,
                                     write_filtered_csv, generate_filtered_html)
from algorithms.find_spots import get_param
from algorithms.confocal_file import ConfocalFile
from spots_io.plot_spots import plot_spots_2D, plot_spots_3D
from processing import ProcessStatus, ProcessStepIterate
from imageCompareDialog import ProcessStepVisualizeDenoise

from logging import INFO
from math import sqrt
import multiprocessing as mp
import numpy as np
from math import nan
from os.path import expanduser, splitext
import sys, platform
import tifffile as tiff
from typing import Dict, List
from worker import Worker

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
        self.threadPool = QThreadPool()


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

        # --- Nuclear Morphology settings (added programmatically) ---
        # These controls tune the nuclear SEGMENTATION only.
        # No staging classification is done — raw morphology features are
        # exported to CSV for future ML training.
        morphGroup = QGroupBox("Nuclear Segmentation")
        morphLayout = QGridLayout()

        morphLayout.addWidget(QLabel("Threshold:"), 0, 0)
        self.nucSegThresholdLineEdit = QLineEdit("0.0")
        self.nucSegThresholdLineEdit.setToolTip(
            "Adaptive threshold offset for nuclear segmentation.\n"
            "Valid range: -0.5 to 0.5 (clamped if outside).\n"
            "Positive = stricter (fewer/smaller nuclei detected).\n"
            "Negative = more permissive (more/larger nuclei detected).\n"
            "Start at 0.0 and adjust in steps of 0.01-0.05.")
        morphLayout.addWidget(self.nucSegThresholdLineEdit, 0, 1)

        morphLayout.addWidget(QLabel("Min Area (px):"), 1, 0)
        self.minNucAreaLineEdit = QLineEdit("500")
        self.minNucAreaLineEdit.setToolTip(
            "Nuclei smaller than this (in pixels) are removed as noise.\n"
            "Decrease if small nuclei are being dropped. Increase if noise remains.")
        morphLayout.addWidget(self.minNucAreaLineEdit, 1, 1)

        morphLayout.addWidget(QLabel("Max Area (px):"), 1, 2)
        self.maxNucAreaLineEdit = QLineEdit("50000")
        self.maxNucAreaLineEdit.setToolTip(
            "Nuclei larger than this (in pixels) are removed as clumps.\n"
            "Decrease if merged clumps slip through. Increase if large nuclei are dropped.")
        morphLayout.addWidget(self.maxNucAreaLineEdit, 1, 3)

        morphLayout.addWidget(QLabel("Downsample:"), 2, 0)
        self.nucDownsampleLineEdit = QLineEdit("1")
        self.nucDownsampleLineEdit.setToolTip(
            "Downsample factor for nuclear segmentation.\n"
            "1 = no downsampling (default).\n"
            "2 or 4 = faster for large images (e.g. Airyscan).\n"
            "The mask is upscaled back to full resolution.")
        morphLayout.addWidget(self.nucDownsampleLineEdit, 2, 1)

        morphGroup.setLayout(morphLayout)
        # Insert into the left panel, after the masking section
        self.ui.leftVerticalLayout.addWidget(morphGroup)

        # Spot detection settings
        self.ui.leftSpotDetectionThresholdLineEdit.setText(str(get_param("spot_detect_threshold_left", params)))
        self.ui.middleSpotDetectionThresholdLineEdit.setText(str(get_param("spot_detect_threshold_middle", params)))
        self.ui.rightSpotDetectionThresholdLineEdit.setText(str(get_param("spot_detect_threshold_right", params)))
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
        self.ui.runBatchPushButton.clicked.connect(self.toggleRunBatch)

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

    def updateRunBatchButtonText(self, direction: str):
        if direction == "run":
            self.ui.runBatchPushButton.setText("Run Batch")
        elif direction == "kill":
            self.ui.runBatchPushButton.setText("Kill Batch")
        elif direction == "stopping":
            self.ui.runBatchPushButton.setText("Stopping Batch...")
        else:
            raise RuntimeError(f'Expected "run", "stopping" or "kill", got {direction}')

    @Slot(bool)
    def toggleRunBatch(self, checked: bool = False):
        buttonText = self.ui.runBatchPushButton.text()
        if buttonText == "Run Batch":
            self.updateRunBatchButtonText("kill")
            self.runBatch()
        elif buttonText == "Kill Batch":
            if self.workerRunning:
                self.updateRunBatchButtonText("stopping")
            else:
                self.updateRunBatchButtonText("run")
            self.killBatch()
        elif buttonText == "Stopping Batch...":
            # do nothing, we're already stopping
            pass
        else:
            raise RuntimeError(f"Start/Stop pushbutton text is unexpected: {buttonText}")

    def killBatch(self):
        self.keepRunning = False

    def runBatch(self):
        self.keepRunning = True
        self.workerRunning = True
        self.stopBatchProcessing = False
        batchWorker = Worker(self.runBatchJobs)
        batchWorker.signals.finished.connect(self.resetRunBatchButtonText)
        self.threadPool.start(batchWorker)

    def resetRunBatchButtonText(self):
        self.workerRunning = False
        self.updateRunBatchButtonText("run")

    def runBatchJobs(self):
        while self.keepRunning and len(self.pendingFilesModel.stringList()) > 0:
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

    def write_morphology(self, stats, nuclei_list, outName):
        """
        Write raw nuclear morphology features as CSV.
        This is ML training data — each row is one nucleus with all its
        measured features. Add a 'stage' column manually after visual
        inspection to create labeled training data for a classifier.
        """
        with open(outName, "w") as f:
            # Summary stats as comment header (for quick inspection)
            for key, val in stats.items():
                f.write(f"# {key}={val}\n")
            # Column headers — 'stage' column is empty, to be filled in
            # manually after visual inspection of each embryo
            f.write("label,centroid_row,centroid_col,area,major_axis,minor_axis,"
                    "orientation,eccentricity,roundness,stage\n")
            for nuc in nuclei_list:
                f.write(f"{nuc['label']},"
                        f"{nuc['centroid'][0]:.1f},{nuc['centroid'][1]:.1f},"
                        f"{nuc['area']},"
                        f"{nuc['major_axis']:.2f},{nuc['minor_axis']:.2f},"
                        f"{nuc['orientation']:.4f},"
                        f"{nuc['eccentricity']:.4f},"
                        f"{nuc['roundness']:.4f},"
                        f"\n")  # stage column left blank for manual labeling

    def write_spot_boundary_distances(self, spot_boundary_dists, spot_labels,
                                       spot_microns, outName):
        """
        Write spot-to-nearest-boundary distances (signed) for every
        individual spot (left, middle, right) in each triplet/doublet.
        Coordinates are in microns. Distance is signed: negative = inside
        a nucleus, positive = outside.
        """
        with open(outName, "w") as f:
            f.write("group_type,group_index,channel,"
                    "x_microns,y_microns,z_microns,"
                    "distance_to_boundary,"
                    "x_dist_to_boundary_um,y_dist_to_boundary_um,"
                    "z_dist_to_boundary_um,"
                    "nearest_nucleus_label,inside_nucleus\n")
            for entry, label_info, microns in zip(spot_boundary_dists,
                                                   spot_labels, spot_microns):
                group_type, channel, group_idx = label_info
                f.write(f"{group_type},{group_idx},{channel},"
                        f"{microns[0]:.2f},{microns[1]:.2f},{microns[2]:.2f},"
                        f"{entry['distance_to_boundary']:.4f},"
                        f"{entry['x_dist_to_boundary']:.4f},"
                        f"{entry['y_dist_to_boundary']:.4f},"
                        f"{entry['z_dist_to_boundary']:.4f},"
                        f"{entry['nearest_nucleus_label']},"
                        f"{entry['inside_nucleus']}\n")

    def save_nucleus_overlay(self, cf, label_img, nuclei_list, morph_stats, outStem):
        """
        Save a labeled overlay image of the nucleus segmentation.
        Draws colored boundaries around each nucleus and labels them with ID numbers.
        Also adds stage classification text. This is the image you use to verify
        that segmentation thresholds are working correctly.
        """
        from skimage.segmentation import find_boundaries
        from PIL import Image, ImageDraw, ImageFont

        # Get the nucleus slice used for segmentation
        nucleus_slice_idx = int(self.ui.nucleusSliceLineEdit.text())
        nuc_image = cf.channel_nucleus()
        if len(nuc_image.shape) == 3:
            nucleus_slice_idx = max(0, min(nucleus_slice_idx, nuc_image.shape[0] - 1))
            slice_2d = nuc_image[nucleus_slice_idx]
        else:
            slice_2d = nuc_image

        # Create RGB overlay from grayscale nucleus image
        if slice_2d.dtype != np.uint8:
            im_float = slice_2d.astype(np.float32)
            im_float = (im_float - im_float.min()) / (im_float.max() - im_float.min() + 1e-10) * 255
            slice_2d = im_float.astype(np.uint8)
        overlay = np.stack([slice_2d, slice_2d, slice_2d], axis=-1)

        # Draw nucleus boundaries in green
        boundaries = find_boundaries(label_img, mode='outer')
        overlay[boundaries] = [0, 255, 0]

        # Convert to PIL for text drawing
        pil_img = Image.fromarray(overlay)
        draw = ImageDraw.Draw(pil_img)

        # Label each nucleus with its ID and area
        for nuc in nuclei_list:
            row, col = nuc['centroid']
            text = f"{nuc['label']}"
            draw.text((col - 5, row - 5), text, fill=(255, 255, 0))

        # Add summary stats at top-left corner
        num_nuc = morph_stats.get('num_nuclei', 0)
        med_area = morph_stats.get('median_area', 0)
        med_round = morph_stats.get('median_roundness', 0)
        info_text = (f"N={num_nuc} | "
                     f"Med Area={med_area:.0f} | Med Roundness={med_round:.2f}")
        draw.text((10, 10), info_text, fill=(255, 255, 0))

        # Save
        result = np.array(pil_img)
        tiff.imwrite(outStem + "_nuclei_segmentation.tiff", result)

    def save_nucleus_debug_overlay(self, cf, label_img, seg_debug, outStem):
        """
        Save a debug overlay showing border-filtering results:
          - GREEN outlines + labels: nuclei that were KEPT
          - RED outlines + labels:   nuclei REMOVED by border margin filter
          - Yellow text:  summary of filtering counts and border margin
        """
        from skimage.segmentation import find_boundaries
        from PIL import Image, ImageDraw

        # Get the nucleus slice
        nucleus_slice_idx = int(self.ui.nucleusSliceLineEdit.text())
        nuc_image = cf.channel_nucleus()
        if len(nuc_image.shape) == 3:
            nucleus_slice_idx = max(0, min(nucleus_slice_idx, nuc_image.shape[0] - 1))
            slice_2d = nuc_image[nucleus_slice_idx]
        else:
            slice_2d = nuc_image

        if slice_2d.dtype != np.uint8:
            im_float = slice_2d.astype(np.float32)
            im_float = (im_float - im_float.min()) / (im_float.max() - im_float.min() + 1e-10) * 255
            slice_2d = im_float.astype(np.uint8)
        overlay = np.stack([slice_2d, slice_2d, slice_2d], axis=-1)

        # Green boundaries for KEPT nuclei
        kept_boundaries = find_boundaries(label_img, mode='outer')
        overlay[kept_boundaries] = [0, 255, 0]

        # Red boundaries for REMOVED nuclei (from pre-border label image)
        label_before_border = seg_debug.get('label_before_border')
        if label_before_border is not None:
            removed_labels = set(r['label'] for r in seg_debug['border_removed'])
            # Build mask of only removed nuclei
            removed_mask = np.zeros_like(label_before_border, dtype=bool)
            for rl in removed_labels:
                removed_mask |= (label_before_border == rl)
            from skimage.measure import label as sk_label
            removed_labeled = sk_label(removed_mask)
            removed_boundaries = find_boundaries(removed_labeled, mode='outer')
            overlay[removed_boundaries] = [255, 0, 0]

        pil_img = Image.fromarray(overlay)
        draw = ImageDraw.Draw(pil_img)

        # Label kept nuclei in green
        from skimage.measure import regionprops
        for region in regionprops(label_img):
            row, col = region.centroid
            draw.text((col - 5, row - 5), str(region.label), fill=(0, 255, 0))

        # Label removed nuclei in red
        if label_before_border is not None:
            for rem in seg_debug['border_removed']:
                row, col = rem['centroid']
                draw.text((col - 5, row - 5), f"X{rem['label']}", fill=(255, 0, 0))

        # Draw border margin rectangle
        margin = seg_debug['border_margin_px']
        h, w = overlay.shape[:2]
        # Scale margin if debug was computed at downsampled resolution
        if seg_debug['image_shape'] != (h, w):
            ds_h, ds_w = seg_debug['image_shape']
            margin = int(margin * h / ds_h)
        draw.rectangle(
            [margin, margin, w - margin - 1, h - margin - 1],
            outline=(255, 255, 0), width=2)

        # Summary text
        info = (f"Border margin={seg_debug['border_margin_px']}px | "
                f"Before filter={seg_debug['n_after_size_shape_filter']} | "
                f"Removed={seg_debug['n_border_removed']} (red) | "
                f"Kept={seg_debug['n_after_border_filter']} (green)")
        draw.text((10, 10), info, fill=(255, 255, 0))

        result = np.array(pil_img)
        tiff.imwrite(outStem + "_nuclei_debug.tiff", result)

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
            'nucleus_slice': int(self.ui.nucleusSliceLineEdit.text()),
            # Nuclear segmentation params (from the new UI section)
            'nuc_seg_threshold': float(self.nucSegThresholdLineEdit.text()),
            'min_nuc_area': int(self.minNucAreaLineEdit.text()),
            'max_nuc_area': int(self.maxNucAreaLineEdit.text()),
            'nuc_downsample': int(self.nucDownsampleLineEdit.text()),
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
        nuclearMorphologyStep: int = 0
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
            # since we're adding a process step before everything else...
            nuclearMorphologyStep += 1
            countNucleiStep += 1
            detectSpotsStep += 1
            tripletDetectionStep += 1

        # --- Nuclear Morphology step (always runs) ---
        # Segments nuclei, extracts raw morphology features for ML training.
        # Passes all inputs through unchanged so the pipeline continues.
        processSequence.append(ProcessStepNuclearMorphology(nucleusChannelParams))
        # Bump the indices for all steps that come after
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

        # --- Extract nuclear morphology results ---
        morph_stats, nuclei_list, label_img, binary_mask, seg_debug = endOutputs[nuclearMorphologyStep]

        outStem, _ = splitext(fileToRun)
        self.write_distances(triplets, leftDoublets, rightDoublets, leftRightDoublets, outStem + "_distances.csv")
        write_output(output, outStem + "_results.txt", len(nucleusCoords) if nucleusCoords else None)

        # --- Write raw nuclear morphology features (ML training data) ---
        self.write_morphology(morph_stats, nuclei_list, outStem + "_morphology.csv")

        # --- Save labeled nucleus overlay image ---
        # Produces _nuclei_segmentation.tiff: nucleus channel with green
        # outlines and ID labels. Use to verify segmentation quality.
        self.save_nucleus_overlay(cf, label_img, nuclei_list, morph_stats, outStem)

        # --- Save debug overlay: green = kept, red = removed by border filter ---
        self.save_nucleus_debug_overlay(cf, label_img, seg_debug, outStem)

        # --- Compute and write spot-to-BOUNDARY distances ---
        # Signed distance: negative = inside nucleus, positive = outside.
        # Collect every individual spot (left, middle, right) from all
        # triplets and doublets so each gets its own boundary measurement.
        all_spots_px = []    # pixel coords for distance transform lookup
        spot_microns = []    # micron coords for CSV output
        spot_labels = []     # parallel list: (group_type, channel, group_idx)
        group_idx = 0
        for triplet in triplets:
            left, middle, right = triplet[0], triplet[1], triplet[2]
            for channel, spot in [('left', left), ('middle', middle), ('right', right)]:
                all_spots_px.append((spot[0] / scale['X'], spot[1] / scale['Y'],
                                     spot[2] / scale['Z'] if len(spot) > 2 else 0))
                spot_microns.append((spot[0], spot[1], spot[2] if len(spot) > 2 else 0))
                spot_labels.append(('triplet', channel, group_idx))
            group_idx += 1
        for doublet in leftDoublets:
            for channel, spot in [('left', doublet[0]), ('middle', doublet[1])]:
                all_spots_px.append((spot[0] / scale['X'], spot[1] / scale['Y'],
                                     spot[2] / scale['Z'] if len(spot) > 2 else 0))
                spot_microns.append((spot[0], spot[1], spot[2] if len(spot) > 2 else 0))
                spot_labels.append(('left_doublet', channel, group_idx))
            group_idx += 1
        for doublet in rightDoublets:
            for channel, spot in [('middle', doublet[0]), ('right', doublet[1])]:
                all_spots_px.append((spot[0] / scale['X'], spot[1] / scale['Y'],
                                     spot[2] / scale['Z'] if len(spot) > 2 else 0))
                spot_microns.append((spot[0], spot[1], spot[2] if len(spot) > 2 else 0))
                spot_labels.append(('right_doublet', channel, group_idx))
            group_idx += 1
        for doublet in leftRightDoublets:
            for channel, spot in [('left', doublet[0]), ('right', doublet[1])]:
                all_spots_px.append((spot[0] / scale['X'], spot[1] / scale['Y'],
                                     spot[2] / scale['Z'] if len(spot) > 2 else 0))
                spot_microns.append((spot[0], spot[1], spot[2] if len(spot) > 2 else 0))
                spot_labels.append(('lr_doublet', channel, group_idx))
            group_idx += 1
        if binary_mask.any() and len(all_spots_px) > 0:
            spot_boundary_dists = compute_spot_boundary_distances(
                all_spots_px, binary_mask, label_img, scale)
            self.write_spot_boundary_distances(spot_boundary_dists, spot_labels,
                                               spot_microns,
                                               outStem + "_spot_boundary_distances.csv")

        # --- Filter spots: keep only triplets/doublets inside nuclei ---
        # _distances.csv has ALL spots. _filtered_spots.csv has only those
        # where every spot in the triplet/doublet is inside a nucleus.
        if binary_mask.any():
            filt_triplets, n_removed = filter_triplets(triplets, binary_mask, scale)
            filt_left = filter_doublets(leftDoublets, binary_mask, scale)
            filt_right = filter_doublets(rightDoublets, binary_mask, scale)
            filt_lr = filter_doublets(leftRightDoublets, binary_mask, scale)

            if self._logger:
                self._logger.info(
                    f"Filtered spots: kept {len(filt_triplets)}/{len(triplets)} triplets "
                    f"({n_removed} removed as outside nuclei)")

            # Write filtered CSV (same format as _distances.csv)
            write_filtered_csv(filt_triplets, filt_left, filt_right,
                               filt_lr, outStem + "_filtered_spots.csv")

            # HTML generation is deferred until after _spots_rgb is built
            # so we can use it as the background image.

        # construct a new rgb version of the nucleus image volume and specified slice
        spot_projection_slice = int(self.ui.nucleusSliceLineEdit.text())
        spot_projection_slice = max(0, min(spot_projection_slice, cf.channel_nucleus().shape[0] - 1))
        def gray_to_rgb(img_2d):
            """Convert a 2D grayscale image to RGB uint8 (H, W, 3)."""
            if img_2d.dtype != np.uint8:
                im = img_2d.astype(np.float32)
                lo, hi = im.min(), im.max()
                if hi > lo:
                    im = (im - lo) / (hi - lo) * 255.0
                im = np.clip(im, 0, 255).astype(np.uint8)
            else:
                im = img_2d
            return np.stack([im, im, im], axis=-1)

        nucleus_vol = cf.channel_nucleus()
        # Build 3D RGB slice-by-slice to avoid massive memory spike
        nucleus_3D_rgb = np.empty(nucleus_vol.shape + (3,), dtype=np.uint8)
        for zi in range(nucleus_vol.shape[0]):
            nucleus_3D_rgb[zi] = gray_to_rgb(nucleus_vol[zi])
        nucleus_2D_rgb = nucleus_3D_rgb[spot_projection_slice].copy()

        # For now, always plot nuclei if we counted them
        if self.ui.countNucleiCheckBox.isChecked():
            nuclei_2d_rgb = gray_to_rgb(nucleusCountImage)
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
        del nucleus_3D_rgb  # Free ~2-4 GB before allocating more

        if self.ui.findDoubletsCheckBox.isChecked():
            doublet_2D_rgb = gray_to_rgb(nucleus_vol[spot_projection_slice])
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

        spots_2D_rgb = None  # Will be set below if detected-spots image is created
        if self.ui.saveDetectedSpotsCheckBox.isChecked() and len(endOutputs) > detectSpotsStep and endOutputs[detectSpotsStep]:
            spots = endOutputs[detectSpotsStep]
            spotColors = [
                (255,   0,   0),     # red
                (  0, 255,   0),     # green
                (  0,   0, 255)      # blue
            ]

            spots_2D_rgb = gray_to_rgb(nucleus_vol[spot_projection_slice])
            spots_3D_rgb = np.empty(nucleus_vol.shape + (3,), dtype=np.uint8)
            for zi in range(nucleus_vol.shape[0]):
                spots_3D_rgb[zi] = gray_to_rgb(nucleus_vol[zi])

            spotsScale = (1., 1., 1.)
            for ix, ch in enumerate([
                    channelItemFromString[self.ui.leftChannelComboBox.currentText()],
                    channelItemFromString[self.ui.middleChannelComboBox.currentText()],
                    channelItemFromString[self.ui.rightChannelComboBox.currentText()]
                    ]):
                spots_image = np.empty(ch.shape + (3,), dtype=np.uint8)
                for zi in range(ch.shape[0]):
                    spots_image[zi] = gray_to_rgb(ch[zi])
                plot_spots_2D(spots_2D_rgb, spots[ix], spotsScale, lambda pos: spotColors[ix], filled=False)
                plot_spots_3D(spots_3D_rgb, spots[ix], spotsScale, lambda pos: spotColors[ix], filled=False)
                plot_spots_3D(spots_image, spots[ix], spotsScale, lambda pos: spotColors[ix], filled=False)
                tiff.imwrite(outStem + f"_ch{ix}_spots.tiff", spots_image)
                del spots_image
            tiff.imwrite(outStem + "_spots_3D_rgb.tiff", spots_3D_rgb)
            del spots_3D_rgb
            tiff.imwrite(outStem + "_spots_rgb.tiff", spots_2D_rgb)

        # --- Generate interactive HTML overlay of filtered spots ---
        # Uses _spots_rgb as background (if available) so you can see raw
        # detected spots with filtered spots overlaid as filled circles.
        if binary_mask.any():
            spots_bg = spots_2D_rgb.copy() if spots_2D_rgb is not None else None
            nuc_slice_idx = int(self.ui.nucleusSliceLineEdit.text())
            nuc_img = cf.channel_nucleus()
            if len(nuc_img.shape) == 3:
                nuc_slice_idx = max(0, min(nuc_slice_idx, nuc_img.shape[0] - 1))
                nuc_slice_2d = nuc_img[nuc_slice_idx]
            else:
                nuc_slice_2d = nuc_img
            generate_filtered_html(nuc_slice_2d, filt_triplets, scale,
                                   outStem + "_filtered_spots.html",
                                   left_doublets=filt_left,
                                   right_doublets=filt_right,
                                   lr_doublets=filt_lr,
                                   morph_stats=morph_stats,
                                   spots_rgb=spots_bg)

        del nucleus_vol  # Free the raw volume
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
