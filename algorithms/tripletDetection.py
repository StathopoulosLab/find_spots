from __future__ import division, print_function

from qtpy.QtWidgets import QApplication
import sys
from processing import ProcessStep, ProcessStatus
from typing import Callable, Dict

def distance(point1, point2):
    '''Returns sq of distance between point 1 and point 2 in form [x,y,z]'''
    x1, y1, z1 = point1[0], point1[1], point1[2]
    x2, y2, z2 = point2[0], point2[1], point2[2]
    return (x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2

def search_space(spot, channel, lim):
    '''Searches space around a spot for a single other spot of a given color
    channel. If zero or more than one such spots are found, then [-1, -1] is
    returned'''
    nextPoint = [-1, -1]
    offColorNeighbors = 0
    for offColorSpot in channel:
        if distance(spot, offColorSpot) < lim:
            offColorNeighbors += 1
            if offColorNeighbors == 1:
                nextPoint = offColorSpot
            else: # exceeded one neighbor
                nextPoint = [-1, -1]
                break
    return nextPoint

def check_triplet(r, g, b, spots, l):
    '''Checks to make sure no other triplets can be formed using one of the RGB
    spots passed to the function. If no other triplets can be formed, then this
    function returns [True, True, True].  Otherwise, the faulty color returns
    False in that list.'''
    chan0ChecksOut, chan1ChecksOut, chan2ChecksOut = True, True, True
    for chan0spot in spots[0]: #check for stray chan0 spots near chan1 & chan2
        if chan0spot!=r and (distance(chan0spot,g)<l or distance(chan0spot,b)<l):
            chan0ChecksOut = False
    for chan1spot in spots[1]: #check for stray chna1 spots near chan2 & chan0
        if chan1spot!=g and (distance(chan1spot,r)<l or distance(chan1spot,b)<l):
            chan1ChecksOut = False
    for chan2spot in spots[2]: #check for stray chan2 spots near chan0 & chan1
        if chan2spot!=b and (distance(chan2spot,r)<l or distance(chan2spot,g)<l):
            chan2ChecksOut = False
    return [chan0ChecksOut, chan1ChecksOut, chan2ChecksOut]

def triplet_selection(spots, l):
    '''
    Finds triplets in a given list of spots for where the spots aren't
    part of another triplet. Triplet boundary is defined as radius of parameter
    lim around each of the three spots composing the triplet.
    Outputs the list of triplets.
    '''
    triplets = []
    for chan0spot in spots[0]:
        pair_0_1 = search_space(chan0spot, spots[1], l) #look for lone chan1 spot around chan0 spot
        pair_0_2 = search_space(chan0spot, spots[2], l) #look for lone chan2 spot around chan0 spot
        if pair_0_1!=[-1,-1] and pair_0_2==[-1,-1]: #if chan1 found but not chan2 around chan0 spot
            pair_1_2 = search_space(pair_0_1, spots[2], l) #look for lone chan3 spot around chan1 spot
            if pair_1_2!=[-1,-1]: #if G found around R around B
                if check_triplet(chan0spot,pair_0_1,pair_1_2,spots,l)==[True,True,True]:
                    triplets.append([chan0spot, pair_0_1, pair_1_2])
        if pair_0_2!=[-1,-1] and pair_0_1==[-1,-1]: #if G found but not R around B
            pair_2_0 = search_space(pair_0_2,spots[1],l) #look for lone R around G
            if pair_2_0!=[-1,-1]: #if R found around G aroud B
                if check_triplet(chan0spot,pair_2_0,pair_0_2,spots,l)==[True,True,True]:
                    triplets.append([chan0spot, pair_2_0, pair_0_2])
        if pair_0_1!=[-1,-1] and pair_0_2!=[-1,-1]: #if R and G found around B
            if check_triplet(chan0spot,pair_0_1,pair_0_2,spots,l)==[True,True,True]:
                triplets.append([chan0spot, pair_0_1, pair_0_2])
    return triplets

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
    # convert to physical dimensions and return as [[chan0],[chan1],[chan2]]
    points = [[],[],[]]
    for i in [0, 1, 2]:
        points[i] = [[0.065*x,0.065*y,0.1*z] for [x,y,z] in ch[i]]
    return points

def select(chan0File, chan1File, chan2File, lim):
    spots = read_input(chan0File, chan1File, chan2File)
    print(len(spots[0]), len(spots[1]), len(spots[2]))
    triplets = triplet_selection(spots, lim**2)
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

def find_best_triplets(chan0Spots, chan1Spots, chan2Spots,
                       xScale: float, yScale: float, zScale: float,
                       app: QApplication = None,
                       progressCallback: Callable[[int, str], None] = None):
    points = []
    points.append([[xScale*x, yScale*y, zScale*z] for [x,y,z] in chan0Spots])
    points.append([[xScale*x, yScale*y, zScale*z] for [x,y,z] in chan1Spots])
    points.append([[xScale*x, yScale*y, zScale*z] for [x,y,z] in chan2Spots])
    max_lim = -1.
    # limits = [x/5+0.1 for x in range(1,16)]
    limits = [2.0]
    max_triplets = []
    if progressCallback:
        progressCallback(0, "FindTriplets")
    if app:
        # let the GUI, if there is one, process pending events
        app.processEvents()
    for i, lim in enumerate(limits):
        triplets = triplet_selection(points, lim**2)
        if len(triplets) > len(max_triplets):
            max_triplets = triplets
            max_lim = lim
        if progressCallback:
            progressCallback(((i+1) * 100) // len(limits), "FindBestTriplets")
        if app:
            # let the GUI, if there is one, process pending events
            app.processEvents()
    return (max_triplets, max_lim)

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
        self._status = ProcessStatus.RUNNING
        self._stepOutputs = []
        self._endOutputs = []
        max_triplets, max_lim = find_best_triplets(
            self._inputs[0],
            self._inputs[1],
            self._inputs[2],
            self._scale['X'],
            self._scale['Y'],
            self._scale['Z'],
            self._app,
            progressCallback)
        self._stepOutputs.append(max_triplets)
        self._endOutputs.append(max_lim)
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
        triplets = select(chan0FileName,chan1FileName,chan2FileName,lim)
        if len(triplets) > len(max_triplets):
            max_triplets = triplets
            max_lim = lim
    print(str(len(max_triplets))+" triplets found at threshold "+str(max_lim))
    write_results(max_triplets, outName)