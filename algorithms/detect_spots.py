# detect_spots
# changed detect_slice_spots so that only the smaller of two
# overlapping spots will be deleted (not both spots, as it was before)

from  __future__ import division, print_function

import numpy as np

import scipy.ndimage
import imageio
import sys
from processing import ProcessStatus, ProcessStep, ProcessStepConcurrent
from typing import Callable, Dict, Tuple
from os import getpid
from multiprocessing import log_to_stderr
from logging import INFO

def distance_2D(point1, point2):
    '''Returns distance between point 1 and point 2 in form [x,y,z]'''
    x1, y1 = point1[0], point1[1]
    x2, y2 = point2[0], point2[1]
    return np.sqrt((x1-x2)**2 + (y1-y2)**2)

def max_depth(files, depth):
    '''Gives the maximum intensity of 'depth' number of slices.'''
    window = []
    newStack = []
    for filename in files:
        print(filename)
        im = imageio.imread(filename)
        im_float = (im.astype(float) - im.min()) / (im.max() - im.min())
        if len(window) < depth:
            window.append(im_float)
        if len(window) == depth:
            newimage = np.zeros((len(im_float), len(im_float[0])))
            for i in range(len(im_float)):
                for j in range(len(im_float[0])):
                    candidates = []
                    for image in window:
                        candidates.append(image[i][j])
                    newimage[i,j] = max(candidates)
            window.pop(0)
            newStack.append(newimage)
    return newStack

def max_depth_np(image: np.ndarray, depth: int) -> np.ndarray:
    '''Gives the maximum intensity of 'depth' number of slices.'''
    newStack = []
    for z in range(image.shape[0]-depth):
        wedge = image[z:z+depth,:,:]
        newStack.append(np.amax(wedge, 0))
    return newStack

def detect_slice_spots(image, sliceIndex, thresh):
    '''Takes an image (floats) & detects the spots within using a Laplacian of
    Gaussian filter and then selecting for maximal response under a threshold
    over physical space and sigma space. Returns a list of tuples (x,y,z,sigma)
    for each point, where z is sliceIndex argument passed to the function.'''
    # Create sigma space of LoG
    LoG = []
    sigmaSpace = np.arange(0.75,3.5,0.25)
    for i in range(len(sigmaSpace)):
        sigma = sigmaSpace[i]
        im_LoG = sigma**2*scipy.ndimage.filters.gaussian_laplace(image,sigma)
        LoG.append(im_LoG)
    LoG = np.array(LoG)

    # Select minima within sigma space
    spots = []
    for z in range(1,len(LoG)-1):
        for y in range(1,len(LoG[z])-1):
            for x in range(1,len(LoG[z][y])-1):
                #This search auto-eliminates minima at highest & lowest sigmas
                searchSpace = LoG[z-1:z+2, y-1:y+2, x-1:x+2]
                if LoG[z][y][x] < thresh:
                    if LoG[z][y][x] == np.min(searchSpace):
                        spots.append((x,y,sliceIndex,sigmaSpace[z]))

    # Kill overlapping spots
    for spotOne in spots[:]:
        otherSpots = [x for x in spots if x != spotOne]
        for spotTwo in otherSpots:
            minDist = (spotOne[-1]+spotTwo[-1]) * np.sqrt(2)
            if distance_2D(spotOne[0:2], spotTwo[0:2]) < minDist:
                # Now we're removing just the smaller spot instead of both
                if spotTwo in spots and spotOne[3] > spotTwo[3]:
                    spots.remove(spotTwo)
                if spotOne in spots and spotOne[3] < spotTwo[3]:
                    spots.remove(spotOne)

    return spots

def searchSlice(sliceSpots, searchSpot):
    '''Given a list sliceSpots of tuples (x,y,z,sigma) and another tuple
    (x,y,z,sigma) searchSpot that is a spot from the slice below, searchSlice
    returns a spot in sliceSpots within searchSpot's radius. (-1,-1,-1,-1) is
    returned if 0 or >1 sliceSpots are within searchSpot's radius.'''
    nextSpot = (-1,-1,-1,-1)
    hits = 0 # counts up number of neighbors in radius of the starting spot
    for spot in sliceSpots:
        radius = searchSpot[-1] * np.sqrt(2)
        if distance_2D(searchSpot[0:2], spot[0:2]) < radius:
            hits += 1
            if hits == 1:
                nextSpot = spot
            else: # exceeded one neighbor
                nextSpot = (-1,-1,-1,-1)
                break
    return nextSpot

def group_slice_spots(imageStack, thresh, printProgress: bool = True):
    '''Given a list of image slices, finds spots in each slice corresponding to
    the same blobs and groups them together. Returns a list of the groupings.'''
    spots3D = []
    growingSpots = []
    for i in range(len(imageStack)):
        if printProgress:
            print('Analyzing image '+str(i))
        sliceSpots = detect_slice_spots(imageStack[i], i, thresh)
        for growing3D in growingSpots[:]:
            searchSpot = growing3D[-1]
            nextSpot = searchSlice(sliceSpots, searchSpot)
            if nextSpot == (-1,-1,-1,-1):
                growingSpots.remove(growing3D)
                if len(growing3D) >= 4: # cull points shorter than some z-depth
                    spots3D.append(growing3D)
            else:
                growingSpots[growingSpots.index(growing3D)].append(nextSpot)
                sliceSpots.remove(nextSpot) #you'll not be able to detect doubles
        if len(sliceSpots) > 0:
            for spot in sliceSpots:
                growingSpots.append([spot])

    # at the end, move everything from growingSpots to spots3D
    for growing3D in growingSpots[:]:
        if len(growing3D) >= 4:
            spots3D.append(growing3D)

    return spots3D

def find_centroids(spots3D):
    '''Given a list of spots detected in a zstack, returns the centroids of the
    spots.'''
    outputSpots = []
    for spot in spots3D:
        (n_tot, x_tot, y_tot, z_tot) = (0, 0, 0, 0)
        for zslice in spot:
            normalizer = 1/(zslice[-1]**2)
            n_tot += normalizer
            x_tot += zslice[0]*normalizer
            y_tot += zslice[1]*normalizer
            z_tot += zslice[2]*normalizer
        (x, y, z) = (x_tot/n_tot, y_tot/n_tot, z_tot/n_tot)
        outputSpots.append((x,y,z))
    return outputSpots

### --- Begin  I/O and Master Functions --- ###

def read_input(inputFileName):
    '''Given a text file with the names of image files to do spot detection on
    listed on separate lines, returns a list of the image file names.'''
    f = open(inputFileName, 'r')
    imagefiles = f.read().splitlines()
    f.close()
    return imagefiles[10:] #ignore first 10 slices

def write_output(spots, outputFileName):
    '''Given a list of (x,y,z) spots detected by the spot detection algorithm,
    writes the results to text file named outputFileName.'''
    f = open(outputFileName, 'w')
    for spot in spots:
        (x, y, z) = spot
        f.write('%-10s %-10s %s\n' %(x,y,z))
    f.close()

def master_function(inputFileName, outputFileName, thresh):
    '''Does spot detection on image files specified in input text file.'''
    print(f"inputFileName: {inputFileName}")
    files = read_input(inputFileName)
    print(f"files: {files}")
    stack = max_depth(files, 5)
    print("Grouping slice spots...")
    spots3D = group_slice_spots(stack, thresh)
    print("Finding centroids...")
    outputSpots = find_centroids(spots3D)
    print(f"Writing output to {outputFileName}")
    write_output(outputSpots, outputFileName)
    print("Done with spot detect")

def detect_spots(image: np.ndarray, thresh: float, printProgress: bool = True):
    logger = log_to_stderr()
    logger.setLevel(INFO)
    if printProgress:
        print("Calculating moving window max")
    logger.info(f"Worker {getpid()}: Calculating moving window max")
    stack = max_depth_np(image, 5)
    if printProgress:
        print("Grouping slice spots...")
    logger.info(f"Worker {getpid()}: Grouping slice spots")
    spots3d = group_slice_spots(stack, thresh, printProgress)
    if printProgress:
        print("Finding centroids...")
    logger.info(f"Worker {getpid()}: Finding centroids")
    outputSpots = find_centroids(spots3d)
    logger.info(f"Worker {getpid()}: Done")
    return(outputSpots)

class ProcessStepDetectSpots(ProcessStep):
    """
    A ProcessStep to detect a list of spots within the input.
    """
    def __init__(self, params: Dict = {}):
        super().__init__(params)
        self._stepName = "DetectSpots"

    def run(self, progressCallback: Callable[..., Tuple[int, str]] = None) -> None:
        assert isinstance(self._inputs, list) and len(self._inputs) == 1
        assert 'spot_detect_threshold' in self._params
        logger = log_to_stderr()
        logger.setLevel(INFO)
        logger.info(f"Worker {getpid()} inside ProcessStepDetectSpots.run()")
        self._stepOutputs = []
        self._endOutputs = []
        spot_detect_threshold = self._params['spot_detect_threshold']
        input = self._inputs
        while isinstance(input, list):
            logger.info(f"Worker {getpid()}: unwrapping ndarray from list")
            input = input[0]
        assert(isinstance(input, np.ndarray))
        self._status = ProcessStatus.RUNNING
        self._stepOutputs.append(detect_spots(input, spot_detect_threshold, False))
        logger.info(f"Worker {getpid()}: outputted a list of length {len(self._stepOutputs[0])}")
        self._endOutputs.append([])
        if progressCallback:
            progressCallback(100, self._stepName)
        self._status = ProcessStatus.COMPLETED

class ProcessStepDetectSpotsConcurrent(ProcessStep):
    """
    A ProcessStep that concurrently detects spots on multiple
    independent channels.
    """

    def __init__(self, params: Dict = {}):
        super().__init__(params)
        self._stepName = "DetectSpotsConcurrent"

    def run(self, progressCallback: Callable[[int, str], None] = None):
        assert isinstance(self._inputs, list) and len(self._inputs) > 0
        self._status = ProcessStatus.RUNNING
        concurrent = ProcessStepConcurrent(ProcessStepDetectSpots, self._params)
        concurrent.setInputs(self._inputs)
        concurrent.run(progressCallback)
        status = concurrent.status()
        if status == ProcessStatus.COMPLETED:
            self._stepOutputs = concurrent.stepOutputs()[0]
            self._endOutputs = concurrent.endOutputs()[0]
        else:
            self._stepOutputs = []
            self._endOutputs = []
        self._status = status

if __name__ == "__main__":
    # Enter command line arguments as: inputFile outputFile thresh
    inputFileName, outputFileName = str(sys.argv[1]), str(sys.argv[2])
    thresh = float(sys.argv[3])
    master_function(inputFileName, outputFileName, thresh)
