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

def check_triplet(b, r, g, spots, l):
    '''Checks to make sure no other triplets can be formed using one of the RGB
    spots passed to the function. If no other triplets can be formed, then this
    function returns [True, True, True].  Otherwise, the faulty color returns
    False in that list.'''
    blueChecksOut, redChecksOut, greenChecksOut = True, True, True
    for blue in spots[0]: #check for stray blue spots near red & green
        if blue!=b and (distance(blue,r)<l or distance(blue,g)<l):
            blueChecksOut = False
    for red in spots[1]: #check for stray red spots near blue & green
        if red!=r and (distance(red,b)<l or distance(red,g)<l):
            redChecksOut = False
    for green in spots[2]: #check for stray green spots near blue & red
        if green!=g and (distance(green,r)<l or distance(green,b)<l):
            greenChecksOut = False
    return [blueChecksOut, redChecksOut, greenChecksOut]

def triplet_selection(spots, l):
    '''Finds triplets in a given list of rgb spots far where the spots aren't
    part of another triplet. Triplet boundary is defined as radius of parameter
    lim around each of the three spots composing the triplet.
    Outputs the list of triplets.'''
    triplets = []
    for blue in spots[0]:
        b_red = search_space(blue,spots[1],l) #look for lone red around blue
        b_green = search_space(blue,spots[2],l) #look for lone green around blue
        if b_red!=[-1,-1] and b_green==[-1,-1]: #if R found but not G around B
            r_green = search_space(b_red,spots[2],l) #look for lone G around R
            if r_green!=[-1,-1]: #if G found around R around B
                if check_triplet(blue,b_red,r_green,spots,l)==[True,True,True]:
                    triplets.append([blue, b_red, r_green])
        if b_green!=[-1,-1] and b_red==[-1,-1]: #if G found but not R around B
            g_red = search_space(b_green,spots[1],l) #look for lone R around G
            if g_red!=[-1,-1]: #if R found around G aroud B
                if check_triplet(blue,g_red,b_green,spots,l)==[True,True,True]:
                    triplets.append([blue, g_red, b_green])
        if b_red!=[-1,-1] and b_green!=[-1,-1]: #if R and G found around B
            if check_triplet(blue,b_red,b_green,spots,l)==[True,True,True]:
                triplets.append([blue, b_red, b_green])
    return triplets

def read_file(filename):
    '''Read in a file with name 'filename' and returns list of (x,y,z) spots'''
    f = open(filename, 'r')
    spots = []
    for line in f:
        spots.append([float(x) for x in line.split()])
    return spots

def read_input(blueFile, redFile, greenFile):
    '''Reads in three text files, one for each color channel. Outputs 3 lists
    of points corresponding to each channel.'''
    # Read in text files
    blueSpots = read_file(blueFile)
    redSpots = read_file(redFile)
    greenSpots = read_file(greenFile)
    ch = [blueSpots, redSpots, greenSpots]
    # convert to physical dimensions and return as [[blue],[red],[green]]
    points = [[],[],[]]
    for i in [0, 1, 2]:
        points[i] = [[0.065*x,0.065*y,0.1*z] for [x,y,z] in ch[i]]
    return points

def select(blueFile, redFile, greenFile, lim):
    spots = read_input(blueFile, redFile, greenFile)
    print(len(spots[0]), len(spots[1]), len(spots[2]))
    triplets = triplet_selection(spots, lim**2)
    print(str(len(triplets))+" Triplets Detected")
    return triplets

def write_results(triplets, outputFileName):
    '''Writes triplet spot coordinates to a text file.'''
    f = open(outputFileName, 'w')
    for triplet in triplets:
        [[bx,by,bz],[gx,gy,gz],[rx,ry,rz]] = triplet
        f.write('%-5s %-5s %-5s %-5s %-5s %-5s %-5s %-5s %s\n' \
                %(bx,by,bz,gx,gy,gz,rx,ry,rz))
    f.close()

def find_best_triplets(blueSpots, redSpots, greenSpots,
                       xScale: float, yScale: float, zScale: float,
                       app: QApplication = None,
                       progressCallback: Callable[[int, str], None] = None):
    points = []
    points.append([[xScale*x, yScale*y, zScale*z] for [x,y,z] in blueSpots])
    points.append([[xScale*x, yScale*y, zScale*z] for [x,y,z] in redSpots])
    points.append([[xScale*x, yScale*y, zScale*z] for [x,y,z] in greenSpots])
    max_lim = -1.
    limits = [x/5+0.1 for x in range(1,16)]
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
    blueFileName, redFileName, greenFileName = str(sys.argv[1]), \
                            str(sys.argv[2]), str(sys.argv[3])
    max_lim = -1
    parameter = [x/5+0.1 for x in list(range(1,16))]
    outName = str(sys.argv[4])
    max_triplets = []
    for lim in parameter:
        print('Running script with detection threshold of %.1f um' %lim)
        triplets = select(blueFileName,redFileName,greenFileName,lim)
        if len(triplets) > len(max_triplets):
            max_triplets = triplets
            max_lim = lim
    print(str(len(max_triplets))+" triplets found at threshold "+str(max_lim))
    write_results(max_triplets, outName)