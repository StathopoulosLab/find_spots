from __future__ import division, print_function

import imageio

import sys

def normalize(image):
    imageRange = image.max() - image.min()
    newImage = (image - image.min()) / imageRange * 255
    return newImage.astype(int)

if __name__ == "__main__":
    inputName, outputName = str(sys.argv[1]), str(sys.argv[2])
    im = imageio.imread(inputName)
    im_normalized = normalize(im)
    imageio.imsave(outputName, im_normalized)