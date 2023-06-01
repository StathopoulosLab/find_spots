# czi2tif.py

from algorithms.confocal_file import ConfocalFile
import tifffile as tf
import numpy as np
import os.path
import sys

"""
Converts Zeiss .czi files to multi-channel tif, e.g. for use by
fish_finder MatLab package.
"""

def czi2tif(infile: str):
    stem, ext = os.path.splitext(infile)
    cf = ConfocalFile(infile)
    outimage = np.stack([cf.channel_647(), cf.channel_555(), cf.channel_488(), cf.channel_nucleus()])
    tf.imwrite(stem + '.tif',
        outimage,
        shape=outimage.shape,
        metadata={'axes': "ZXY"}
        )

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: czi2tif <input_file.czi>")
        exit(-1)
    czi2tif(sys.argv[1])
