# nuclear_morphology.py
#
# Python replacement for UKC_segment.m and UKC_process_im.m
#
# What this module does:
#   1. Segments nuclei from a fluorescence image (accurate masks/boundaries)
#   2. Extracts per-nucleus morphology features as RAW DATA (for future ML staging)
#   3. Computes spot-to-nearest-boundary distance (signed: negative = inside nucleus)
#
# What this module does NOT do:
#   - Stage classification. The morphology features (area, roundness, etc.)
#     are exported as raw CSV data. A future ML model can be trained on
#     labeled examples to classify nc13/nc14A/nc14C from these features.

import numpy as np
from skimage.filters import threshold_local
from skimage.morphology import disk, binary_opening, binary_dilation, binary_closing
from skimage.morphology import remove_small_objects
from skimage.measure import label, regionprops
from skimage.segmentation import clear_border, find_boundaries
from skimage.transform import rescale, resize
from scipy.ndimage import binary_fill_holes, distance_transform_edt
from processing import ProcessStatus, ProcessStep
from typing import Callable, Dict


# ---------------------------------------------------------------------------
# STEP 1: Segment nuclei (replaces UKC_segment.m)
# ---------------------------------------------------------------------------
#
# What UKC_segment.m did:
#   1. adaptthresh  -> adaptive threshold
#   2. imcomplement -> invert (nuclei are darker than background)
#   3. imopen       -> morphological open with disk(5) to remove noise
#   4. imdilate     -> dilate with disk(5) to reconnect fragments
#   5. imopen       -> open again with disk(10) for smoother shapes
#   6. imfill       -> fill holes
#   7. imclearborder-> remove objects touching the border
#   8. MANUAL INPUT -> user picks bad objects to throw out
#
# Our Python version does the same morphological pipeline but replaces
# the manual input step with automated filtering (remove objects that
# are too small or too large to be real nuclei).

def segment_nuclei(image, block_size=51, min_area=500, max_area=50000,
                    threshold_offset=0.0, downsample=1):
    """
    Segment nuclei from a single 2D fluorescence image.

    Parameters
    ----------
    image : 2D numpy array
        Single-channel fluorescence image (e.g., the nucleus channel).
    block_size : int
        Size of the local neighborhood for adaptive thresholding.
        Must be odd. Larger = less sensitive to local variation.
    min_area : int
        Minimum nucleus area in pixels. Objects smaller are discarded.
    max_area : int
        Maximum nucleus area in pixels. Objects larger are discarded.
    threshold_offset : float
        Offset subtracted from the adaptive threshold. Positive values
        make segmentation stricter (fewer/smaller nuclei detected).
        Negative values make it more permissive (more/larger nuclei).
        Default 0.0 (no offset).
    downsample : int
        Downsample factor for segmentation. 1 = no downsampling.
        For large images (e.g. Airyscan 2048+ px), use 2 or 4 for
        ~4-16x speedup. The label image and mask are upscaled back
        to original resolution.

    Returns
    -------
    label_image : 2D numpy array of int
        Each nucleus has a unique ID. Background is 0.
    binary_mask : 2D numpy array of bool
        Binary mask of all nuclei combined.
    """
    original_shape = image.shape

    # Downsample if requested
    if downsample > 1:
        scale_factor = 1.0 / downsample
        im_work = rescale(image.astype(np.float64), scale_factor,
                          anti_aliasing=True, preserve_range=True)
        # Scale area thresholds to match downsampled resolution
        ds_area = downsample * downsample
        min_area_ds = max(1, min_area // ds_area)
        max_area_ds = max_area // ds_area
    else:
        im_work = image.astype(np.float64)
        min_area_ds = min_area
        max_area_ds = max_area

    # Normalize to float [0, 1]
    im = im_work
    im = (im - im.min()) / (im.max() - im.min() + 1e-10)

    # Clamp threshold_offset to valid range for a [0,1] image.
    # Values outside [-0.5, 0.5] are almost certainly a mistake
    # (e.g. user entering a raw intensity value instead of a fraction).
    threshold_offset = max(-0.5, min(0.5, threshold_offset))

    # Ensure block_size is odd and not larger than the image
    bs = min(block_size, min(im.shape[0], im.shape[1]) - 1)
    if bs % 2 == 0:
        bs -= 1
    bs = max(bs, 3)

    # Adaptive threshold (replaces MATLAB adaptthresh + imbinarize)
    # offset is subtracted from the local threshold: positive = stricter
    local_thresh = threshold_local(im, block_size=bs, method='gaussian',
                                   offset=threshold_offset)
    bw = im > local_thresh

    # Invert (replaces MATLAB imcomplement)
    bw = ~bw

    # Scale morphological disk sizes for downsampled image
    if downsample > 1:
        disk_open = max(2, 5 // downsample)
        disk_dilate = max(1, 2 // downsample)
        disk_smooth = max(3, 10 // downsample)
    else:
        disk_open = 5
        disk_dilate = 5
        disk_smooth = 10

    # Morphological cleanup (replaces MATLAB strel/imopen/imdilate chain)
    bw = binary_opening(bw, footprint=disk(disk_open))
    bw = binary_dilation(bw, footprint=disk(disk_dilate))
    bw = binary_opening(bw, footprint=disk(disk_smooth))
    bw = binary_fill_holes(bw)
    bw = clear_border(bw)

    # Automated size and shape filtering (replaces MATLAB's manual input step)
    bw = remove_small_objects(bw, min_size=min_area_ds)
    labeled = label(bw)
    for region in regionprops(labeled):
        if region.area > max_area_ds:
            bw[labeled == region.label] = False
        # Remove non-convex regions (inter-nuclear gaps, not real nuclei)
        elif region.solidity < 0.88:
            bw[labeled == region.label] = False
        # Remove elongated objects: real nuclei are roughly circular,
        # interstitial gaps between nuclei are elongated/irregular.
        elif region.eccentricity > 0.75:
            bw[labeled == region.label] = False
        # Remove objects that aren't round enough (minor/major axis ratio)
        elif (region.major_axis_length > 0 and
              region.minor_axis_length / region.major_axis_length < 0.55):
            bw[labeled == region.label] = False

    # Relative size filter: remove objects much smaller than the median.
    # Inter-nuclear gaps that pass shape checks are typically much smaller
    # than real nuclei, so this catches them adaptively.
    labeled_tmp = label(bw)
    tmp_areas = [r.area for r in regionprops(labeled_tmp)]
    if len(tmp_areas) > 2:
        median_area = np.median(tmp_areas)
        min_relative = 0.25 * median_area
        for region in regionprops(labeled_tmp):
            if region.area < min_relative:
                bw[labeled_tmp == region.label] = False

    # --- Debug: count after size/shape filtering ---
    label_after_shape = label(bw)
    n_after_shape = label_after_shape.max()

    # Save pre-border-filter state for debug overlay
    label_before_border = label_after_shape.copy()

    # Remove nuclei near the image border using clear_border with a buffer.
    # This removes any object that has ANY pixel within buffer_size of the
    # image edge — catches partial edge nuclei that morphological ops
    # shifted inward.  Buffer scales with nucleus size (median radius).
    h_work, w_work = bw.shape
    areas = [r.area for r in regionprops(label_after_shape)]
    if len(areas) > 0:
        median_radius = int(np.sqrt(np.median(areas) / np.pi))
        border_margin = max(15, median_radius // 2)
    else:
        border_margin = 15

    label_image = label(bw)
    label_image = clear_border(label_image, buffer_size=border_margin)
    # Rebuild binary mask from the border-cleared label image
    bw = label_image > 0
    # Relabel sequentially after clearing
    label_image = label(bw)
    n_after_border = label_image.max()

    # Build debug info: figure out which labels were removed
    removed_labels_set = set(np.unique(label_before_border)) - set(np.unique(label_image))
    removed_labels_set.discard(0)
    border_removed = []
    for region in regionprops(label_before_border):
        if region.label in removed_labels_set:
            border_removed.append({
                'label': region.label,
                'centroid': region.centroid,
                'bbox': region.bbox,
                'area': region.area,
            })

    # --- Debug info ---
    debug_info = {
        'image_shape': (h_work, w_work),
        'border_margin_px': border_margin,
        'n_after_size_shape_filter': n_after_shape,
        'n_after_border_filter': n_after_border,
        'n_border_removed': len(border_removed),
        'border_removed': border_removed,
        'label_before_border': label_before_border,
    }

    # Upscale back to original resolution if we downsampled
    if downsample > 1:
        label_image = resize(label_image, original_shape, order=0,
                             preserve_range=True, anti_aliasing=False).astype(label_image.dtype)
        bw = resize(bw.astype(np.uint8), original_shape, order=0,
                    preserve_range=True, anti_aliasing=False).astype(bool)
        debug_info['label_before_border'] = resize(
            label_before_border, original_shape, order=0,
            preserve_range=True, anti_aliasing=False).astype(label_before_border.dtype)

    return label_image, bw, debug_info


# ---------------------------------------------------------------------------
# STEP 2: Extract per-nucleus morphology as raw features
# ---------------------------------------------------------------------------
#
# These features are OUTPUT AS-IS for inspection and future ML training.
# No classification is done here — that requires labeled training data.

def extract_nuclear_morphology(label_image, intensity_image=None):
    """
    Extract morphology features for each labeled nucleus.

    These are raw measurements — use them to build a training dataset
    for ML-based stage classification later.

    Returns
    -------
    nuclei : list of dict
        One dict per nucleus with keys:
        - 'label': int, unique nucleus ID
        - 'centroid': (row, col) tuple
        - 'area': int, number of pixels
        - 'major_axis': float, length of major ellipse axis (pixels)
        - 'minor_axis': float, length of minor ellipse axis (pixels)
        - 'orientation': float, angle of major axis in radians
        - 'eccentricity': float, 0 = circle, 1 = line
        - 'roundness': float, minor/major axis ratio (1 = circle)
        - 'mean_intensity': float (only if intensity_image provided)
    """
    props = regionprops(label_image, intensity_image=intensity_image)

    nuclei = []
    for p in props:
        nuc = {
            'label': p.label,
            'centroid': p.centroid,
            'area': p.area,
            'major_axis': p.major_axis_length,
            'minor_axis': p.minor_axis_length,
            'orientation': p.orientation,
            'eccentricity': p.eccentricity,
            'roundness': (p.minor_axis_length / p.major_axis_length
                          if p.major_axis_length > 0 else 0.0),
        }
        if intensity_image is not None:
            nuc['mean_intensity'] = p.mean_intensity
        nuclei.append(nuc)

    return nuclei


# ---------------------------------------------------------------------------
# STEP 3: Compute summary statistics (for CSV output, NOT for classification)
# ---------------------------------------------------------------------------

def compute_morphology_stats(nuclei):
    """
    Compute summary statistics across all nuclei. Useful for quick
    inspection and as aggregate features for future ML training.

    Returns
    -------
    stats : dict with keys:
        - 'num_nuclei', 'median_area', 'mean_area', 'std_area',
        - 'median_roundness', 'mean_roundness', 'std_roundness'
    """
    if len(nuclei) == 0:
        return {'num_nuclei': 0}

    areas = np.array([n['area'] for n in nuclei])
    roundness = np.array([n['roundness'] for n in nuclei])

    return {
        'num_nuclei': len(nuclei),
        'median_area': float(np.median(areas)),
        'mean_area': float(np.mean(areas)),
        'std_area': float(np.std(areas)),
        'median_roundness': float(np.median(roundness)),
        'mean_roundness': float(np.mean(roundness)),
        'std_roundness': float(np.std(roundness)),
    }


# ---------------------------------------------------------------------------
# STEP 4: Spot-to-boundary distance (SIGNED)
# ---------------------------------------------------------------------------
#
# This is the biologically meaningful measurement:
#   - Negative distance = spot is INSIDE a nucleus (distance to nearest edge)
#   - Zero             = spot is ON the boundary
#   - Positive distance = spot is OUTSIDE all nuclei (distance to nearest edge)
#
# Uses a signed distance transform on the binary mask, which is much more
# accurate than measuring to centroids. A spot near the edge of a large
# nucleus would appear "far" by centroid distance but "close" by boundary
# distance — boundary distance is what matters biologically.

def compute_spot_boundary_distances(spots, binary_mask, label_image, scale=None):
    """
    For each spot, compute the signed distance to the nearest nucleus boundary.

    Parameters
    ----------
    spots : list of tuples
        Detected spots as (x, y, z) from detect_spots.py.
        x and y are in pixel coordinates.
    binary_mask : 2D bool array
        Binary mask from segment_nuclei().
    label_image : 2D int array
        Labeled image from segment_nuclei().
    scale : dict, optional
        Pixel-to-micron scale {'X': float, 'Y': float}.
        If provided, distances are in microns. Otherwise pixels.

    Returns
    -------
    distances : list of dict
        One entry per spot:
        - 'spot': (x, y, z) original coordinates
        - 'distance_to_boundary': float, SIGNED distance
              negative = inside nucleus, positive = outside
        - 'x_dist_to_boundary': float, X-component distance (microns)
        - 'y_dist_to_boundary': float, Y-component distance (microns)
        - 'z_dist_to_boundary': float, always 0 (mask is 2D)
        - 'nearest_nucleus_label': int, which nucleus (0 if outside all)
        - 'inside_nucleus': bool
    """
    if len(spots) == 0 or binary_mask.sum() == 0:
        return []

    # Compute distance transforms with nearest-pixel indices
    # return_indices gives the (row, col) of the nearest boundary pixel
    dist_inside, idx_inside = distance_transform_edt(binary_mask,
                                                      return_indices=True)
    dist_outside, idx_outside = distance_transform_edt(~binary_mask,
                                                        return_indices=True)

    # Signed scalar distance: negative inside, positive outside
    signed_dist = dist_outside.copy()
    signed_dist[binary_mask] = -dist_inside[binary_mask]

    # Nearest boundary pixel indices for every pixel in the image
    # Inside pixels -> nearest outside pixel; outside pixels -> nearest inside pixel
    nearest_row = np.where(binary_mask, idx_inside[0], idx_outside[0])
    nearest_col = np.where(binary_mask, idx_inside[1], idx_outside[1])

    # Scale factors
    if scale:
        pixel_scale = (scale['X'] + scale['Y']) / 2.0
        sx = scale['X']
        sy = scale['Y']
    else:
        pixel_scale = 1.0
        sx = 1.0
        sy = 1.0

    distances = []
    h, w = binary_mask.shape
    for spot in spots:
        spot_x, spot_y = spot[0], spot[1]
        spot_z = spot[2] if len(spot) > 2 else 0

        # Convert spot (x, y) to pixel indices (col, row)
        col = int(round(spot_x))
        row = int(round(spot_y))

        # Clamp to image bounds
        row = max(0, min(row, h - 1))
        col = max(0, min(col, w - 1))

        dist_val = signed_dist[row, col] * pixel_scale
        nuc_label = int(label_image[row, col])  # 0 if outside

        # Per-axis distances to nearest boundary pixel (in microns)
        bnd_row = nearest_row[row, col]
        bnd_col = nearest_col[row, col]
        dx = abs(col - bnd_col) * sx
        dy = abs(row - bnd_row) * sy
        # Z boundary distance is 0 (2D segmentation mask)
        dz = 0.0

        distances.append({
            'spot': (spot_x, spot_y, spot_z),
            'distance_to_boundary': float(dist_val),
            'x_dist_to_boundary': float(dx),
            'y_dist_to_boundary': float(dy),
            'z_dist_to_boundary': float(dz),
            'nearest_nucleus_label': nuc_label,
            'inside_nucleus': bool(binary_mask[row, col]),
        })

    return distances


# ---------------------------------------------------------------------------
# STEP 5: ProcessStep for GUI pipeline integration
# ---------------------------------------------------------------------------
#
# Pipeline position:
#   [Denoise?] → [NuclearMorphology] → [CountNuclei?] → [ThresholdMask] → ...
#                 ^^^ THIS STEP ^^^
#
# What it does:
#   - Segments nuclei on the selected z-slice
#   - Extracts raw morphology features (area, roundness, axes, etc.)
#   - Computes summary stats
#   - Passes all inputs through unchanged so the pipeline continues
#
# What it outputs (in endOutputs):
#   - Summary stats dict (num_nuclei, median_area, etc.)
#   - Per-nucleus feature list (for CSV export)
#   - Label image (for overlay visualization)
#   - Binary mask (for boundary distance computation later)

class ProcessStepNuclearMorphology(ProcessStep):

    def __init__(self, params: Dict = {}):
        super().__init__(params)
        self._stepName = "NuclearMorphology"

    def run(self, progressCallback: Callable[[int, str], None] = None):
        assert isinstance(self._inputs, list) and len(self._inputs) > 1

        self._status = ProcessStatus.RUNNING
        if progressCallback:
            progressCallback(0, self._stepName)

        # Get the nucleus channel (always the last input)
        nucleus_image = self._inputs[-1]

        # Pick the z-slice to analyze, THEN convert only that slice to uint8
        nucleus_slice = int(self._params.get('nucleus_slice', 0))
        if len(nucleus_image.shape) == 3:
            nucleus_slice = max(0, min(nucleus_slice, nucleus_image.shape[0] - 1))
            slice_2d = nucleus_image[nucleus_slice]
        else:
            slice_2d = nucleus_image

        if slice_2d.dtype != np.uint8:
            slice_2d = np.uint8(slice_2d)

        min_area = int(self._params.get('min_nuc_area', 500))
        max_area = int(self._params.get('max_nuc_area', 50000))
        threshold_offset = float(self._params.get('nuc_seg_threshold', 0.0))
        downsample = int(self._params.get('nuc_downsample', 1))

        if progressCallback:
            progressCallback(20, self._stepName)

        # Segment nuclei
        label_img, mask, debug_info = segment_nuclei(
            slice_2d, min_area=min_area, max_area=max_area,
            threshold_offset=threshold_offset, downsample=downsample)

        if progressCallback:
            progressCallback(60, self._stepName)

        # Extract raw morphology features
        nuclei = extract_nuclear_morphology(label_img, intensity_image=slice_2d)

        # Compute summary stats (for logging and CSV header)
        stats = compute_morphology_stats(nuclei)

        if progressCallback:
            progressCallback(80, self._stepName)

        if self._logger:
            self._logger.info(
                f"NuclearMorphology: {stats.get('num_nuclei', 0)} nuclei, "
                f"median_area={stats.get('median_area', 0):.0f}, "
                f"median_roundness={stats.get('median_roundness', 0):.2f}"
            )
            # --- Debug: border filtering details ---
            self._logger.info(
                f"  Segmentation debug: image={debug_info['image_shape']}, "
                f"border_margin={debug_info['border_margin_px']}px, "
                f"after_size_shape={debug_info['n_after_size_shape_filter']}, "
                f"border_removed={debug_info['n_border_removed']}, "
                f"final={debug_info['n_after_border_filter']}"
            )
            for rem in debug_info['border_removed']:
                self._logger.info(
                    f"    Removed border nucleus label={rem['label']}, "
                    f"centroid=({rem['centroid'][0]:.0f},{rem['centroid'][1]:.0f}), "
                    f"bbox={rem['bbox']}, area={rem['area']}"
                )

        # Pass all inputs through unchanged
        self._stepOutputs = self._inputs

        # Store results for the GUI to pick up
        # (stats, nuclei_list, label_image, binary_mask, debug_info)
        self._endOutputs = (stats, nuclei, label_img, mask, debug_info)

        if progressCallback:
            progressCallback(100, self._stepName)
        if self._app:
            self._app.processEvents()

        self._status = ProcessStatus.COMPLETED
