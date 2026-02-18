"""
Fast test script for nuclear segmentation.
Uses the actual segment_nuclei() function so results always match the pipeline.

Usage:
    python test_segmentation.py <file.czi> [nucleus_slice] [downsample] [threshold_offset]
    python test_segmentation.py test_image/foo.czi 2 2 0.0
"""

import sys
import numpy as np
from os.path import splitext
import tifffile as tiff

from algorithms.confocal_file import ConfocalFile
from algorithms.nuclear_morphology import segment_nuclei
from skimage.segmentation import find_boundaries
from skimage.measure import regionprops


def test_segmentation(czi_path, nucleus_slice=2, downsample=2,
                      threshold_offset=0.0, min_area=500, max_area=50000):

    print(f"Loading {czi_path}...")
    cf = ConfocalFile(czi_path)
    nuc_image = cf.channel_nucleus()
    print(f"  Nucleus volume shape: {nuc_image.shape}, dtype: {nuc_image.dtype}")

    # Extract slice
    if len(nuc_image.shape) == 3:
        nucleus_slice = max(0, min(nucleus_slice, nuc_image.shape[0] - 1))
        slice_2d = nuc_image[nucleus_slice]
    else:
        slice_2d = nuc_image

    if slice_2d.dtype != np.uint8:
        slice_2d = np.uint8(slice_2d)

    print(f"  Slice shape: {slice_2d.shape}, min={slice_2d.min()}, max={slice_2d.max()}")
    outStem, _ = splitext(czi_path)

    # Run the actual segment_nuclei function
    print(f"  Running segment_nuclei(downsample={downsample}, threshold_offset={threshold_offset}, "
          f"min_area={min_area}, max_area={max_area})...")
    label_img, mask = segment_nuclei(slice_2d, min_area=min_area, max_area=max_area,
                                      threshold_offset=threshold_offset, downsample=downsample)

    n_nuclei = label_img.max()
    print(f"  RESULT: {n_nuclei} nuclei detected")

    # Print per-nucleus stats
    props = regionprops(label_img)
    for p in props:
        print(f"    #{p.label}: area={p.area}, solidity={p.solidity:.2f}, "
              f"eccentricity={p.eccentricity:.2f}")

    # Save overlay
    overlay = np.stack([slice_2d, slice_2d, slice_2d], axis=-1)
    boundaries = find_boundaries(label_img, mode='outer')
    overlay[boundaries] = [0, 255, 0]
    tiff.imwrite(outStem + "_debug_10_overlay.tiff", overlay)
    print(f"  Overlay saved to {outStem}_debug_10_overlay.tiff")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_segmentation.py <file.czi> [nucleus_slice] [downsample] [threshold_offset]")
        sys.exit(1)

    czi_path = sys.argv[1]
    nucleus_slice = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    downsample = int(sys.argv[3]) if len(sys.argv) > 3 else 2
    threshold_offset = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0

    test_segmentation(czi_path, nucleus_slice=nucleus_slice,
                      downsample=downsample, threshold_offset=threshold_offset)
