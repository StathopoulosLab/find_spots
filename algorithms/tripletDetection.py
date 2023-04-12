from __future__ import division, print_function

from qtpy.QtWidgets import QApplication
import sys
from processing import ProcessStep, ProcessStatus
from typing import Callable, Dict, List, Tuple

def distanceSquared(point1, point2):
    '''Returns sq of distance between point 1 and point 2 in form [x,y,z]'''
    x1, y1, z1 = point1[0], point1[1], point1[2]
    x2, y2, z2 = point2[0], point2[1], point2[2]
    return (x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2

def read_file(filename):
    '''Read in a file with name 'filename' and returns list of (x,y,z) spots'''
    f = open(filename, 'r')
    spots = []
    for line in f:
        spots.append([float(x) for x in line.split()])
    return spots

def read_input(chan0File, chan1File, chan2File):
    '''Reads in three text files, one for each color channel. Outputs 3 lists
    of points corresponding to each channel.'''
    # Read in text files
    chan0Spots = read_file(chan0File)
    chan1Spots = read_file(chan1File)
    chan2Spots = read_file(chan2File)
    ch = [chan0Spots, chan1Spots, chan2Spots]
    return ch

def select(chan0File, chan1File, chan2File, lim):
    spots = read_input(chan0File, chan1File, chan2File)
    print(len(spots[0]), len(spots[1]), len(spots[2]))
    triplets = find_best_triplets(
        spots[0], spots[1], spots[2],
        0.065, 0.065, 0.1,
        1.5
    )
    print(str(len(triplets))+" Triplets Detected")
    return triplets

def write_results(triplets, outputFileName):
    '''Writes triplet spot coordinates to a text file.'''
    f = open(outputFileName, 'w')
    for triplet in triplets:
        [[x0,y0,z0],[x1,y1,z1],[x2,y2,z2]] = triplet
        f.write('%-5s %-5s %-5s %-5s %-5s %-5s %-5s %-5s %s\n' \
                %(x0,y0,z0,x1,y1,z1,x2,y2,z2))
    f.close()

def find_triplet_spot(spot0, otherChanSpots, otherChanPointUsed, maxTripletSize) -> int:
    # find any spots in otherChanSpots that are close enough to spot0
    candidateSpotIx = []
    for ix, spot in enumerate(otherChanSpots):
        if otherChanPointUsed[ix]:
            return -1
        if distanceSquared(spot0, spot) < maxTripletSize**2:
            candidateSpotIx.append(ix)
    if not candidateSpotIx:
        # no spot close enough
        return -1
    # find the candidate spot1 that's closest to spot0
    bestIdx = candidateSpotIx[0]
    if len(candidateSpotIx) > 1:
        bestDist = distanceSquared(spot0, otherChanSpots[bestIdx])
        for idx in range(1,len(candidateSpotIx)):
            thisDist = distanceSquared(spot0, otherChanSpots[idx])
            if thisDist < bestDist:
                bestDist = thisDist
                bestIdx = idx
    return bestIdx

def find_best_triplets(chan0Spots, chan1Spots, chan2Spots,
                       xScale: float, yScale: float, zScale: float,
                       maxTripletSize: float,
                       app: QApplication = None,
                       progressCallback: Callable[[int, str], None] = None) -> List:
    points = []
    pointUsed = []
    points.append([[xScale*x, yScale*y, zScale*z] for [x,y,z] in chan0Spots])
    pointUsed.append([False] * len(points[0]))
    points.append([[xScale*x, yScale*y, zScale*z] for [x,y,z] in chan1Spots])
    pointUsed.append([False] * len(points[1]))
    points.append([[xScale*x, yScale*y, zScale*z] for [x,y,z] in chan2Spots])
    pointUsed.append([False] * len(points[2]))

    if progressCallback:
        progressCallback(0, "FindTriplets")
    if app:
        # let the GUI, if there is one, process pending events
        app.processEvents()

    triplets = []

    for i0, spot0 in enumerate(points[0]):
        # get the closest chan1 spot, if any
        i1 = find_triplet_spot(spot0, points[1], pointUsed[1], maxTripletSize)
        if i1 < 0:
            # nothing close enough, so no triplet is possible for spot0
            continue

        # get the closest chan2 spot, if any
        i2 = find_triplet_spot(spot0, points[2], pointUsed[2], maxTripletSize)
        if i2 < 0:
            # nothing close enough, so no triplet is possible
            continue

        # found a triplet!
        triplets.append((spot0, points[1][i1], points[2][i1]))
        pointUsed[0][i0] = True
        pointUsed[1][i1] = True
        pointUsed[2][i2] = True

        if progressCallback:
            progressCallback(((i+1) * 100) // len(points[0]), "FindBestTriplets")
        if app:
            # let the GUI, if there is one, process pending events
            app.processEvents()
    return triplets

class ProcessStepFindTriplets(ProcessStep):
    """
    A ProcessStep to find the best triplets, given three sets of spots.
    """
    def __init__(self, scale: Dict, params: Dict = {}):
        super().__init__(params)
        self._scale = scale
        self._stepName = "FindTriplets"

    def run(self, progressCallback: Callable[[int, str], None] = None):
        assert 'X' in self._scale
        assert 'Y' in self._scale
        assert 'Z' in self._scale
        assert isinstance(self._inputs, list) and len(self._inputs) == 3
        assert 'max_triplet_size' in self._params
        self._status = ProcessStatus.RUNNING
        self._stepOutputs = []
        self._endOutputs = []
        max_triplet_size = self._params['max_triplet_size']
        triplets = find_best_triplets(
            self._inputs[0],
            self._inputs[1],
            self._inputs[2],
            self._scale['X'],
            self._scale['Y'],
            self._scale['Z'],
            max_triplet_size,
            self._app,
            progressCallback)
        self._stepOutputs.append(triplets)
        self._endOutputs.append([])
        self._status = ProcessStatus.COMPLETED

if __name__ == "__main__":
    # Enter command line arguments as: bluefile redfile greenfile lim outputfile
    chan0FileName, chan1FileName, chan2FileName = str(sys.argv[1]), \
                            str(sys.argv[2]), str(sys.argv[3])
    max_lim = -1
    parameter = [x/5+0.1 for x in list(range(1,16))]
    outName = str(sys.argv[4])
    max_triplets = []
    for lim in parameter:
        print('Running script with detection threshold of %.1f um' %lim)
        triplets = select(chan0FileName, chan1FileName, chan2FileName, lim)
        if len(triplets) > len(max_triplets):
            max_triplets = triplets
            max_lim = lim
    print(str(len(max_triplets))+" triplets found at threshold "+str(max_lim))
    write_results(max_triplets, outName)