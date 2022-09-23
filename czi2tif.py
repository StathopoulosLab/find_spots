# czi2tif.py

from confocal_file import ConfocalFile
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
    outimage = np.stack([cf.channel_3CRM(), cf.channel_PPE(), cf.channel_5CRM(), cf.channel_antibody()])
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
