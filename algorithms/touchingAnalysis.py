# touchingAnalysis.py


from qtpy.QtWidgets import QApplication
from processing import ProcessStatus, ProcessStep

from os import read
import sys
from typing import Callable, Dict, List, Tuple

def distanceSquared(point1, point2):
    '''Returns squared distance between point 1 and point 2 in form [x,y,z]'''
    x1, y1, z1 = point1[0], point1[1], point1[2]
    x2, y2, z2 = point2[0], point2[1], point2[2]
    return (x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2

def ellipsoidalCloseEnough(point1, point2, thresholdSquared: List):
    '''Returns squared distance between point 1 and point 2 in form [x,y,z]'''
    x1, y1, z1 = point1[0], point1[1], point1[2]
    x2, y2, z2 = point2[0], point2[1], point2[2]
    return (((x1-x2)**2)/thresholdSquared[0] + \
        ((y1-y2)**2)/thresholdSquared[1] + \
        ((z1-z2)**2)/thresholdSquared[2]) < 1.

def classify(leftChan, middleChan, rightChan, thresholdSquared):
    '''Classifies given triplet based on distances between 3 point inputs and
    a threshold parameter that gives the cutoff between "near" and "far"'''
    output = [0,0,0]
    if ellipsoidalCloseEnough(leftChan, middleChan, thresholdSquared):
        output[0] = 1
    if ellipsoidalCloseEnough(middleChan, rightChan, thresholdSquared):
        output[1] = 1
    if ellipsoidalCloseEnough(rightChan, leftChan, thresholdSquared):
        output[2] = 1
    return ''.join(str(e) for e in output)

def read_file(inputFName):
    '''Read in a file with name 'inputFName' and returns list of triplets'''
    f = open(inputFName, 'r')
    triplets = [[],[],[]]
    for line in f:
        fl = [float(x) for x in line.split()]
        triplets[0].append(fl[0:3])
        triplets[1].append(fl[3:6])
        triplets[2].append(fl[6:9])
    return triplets

def analyze_inner(points, thresh, read_file_order: bool = False) -> Tuple[List, Dict]:
    '''Given input file of triplet (r_x, r_y, r_z, g_x, g_y, g_z, b_x, b_y, b_z)
    coordinates with units in physical lengths (not pixel widths) and a
    threshold to determine touching, classifies each triplet into one of 8
    conformations based on which spots are close/touching.'''
    # Classify the different points
    conformations = {'000':0, '100':0, '010':0, '001':0, '110':0, '101':0, \
                    '011':0, '111':0}
    thresholdSquared = [v**2 for v in thresh]
    if read_file_order:
        points.append([])
        for i in range(len(points[0])):
            label = classify(points[0][i], points[1][i], points[2][i], thresholdSquared)
            conformations[label] += 1
            points[3].append(label)

    else:
        triplets = [[],[],[],[]]
        for i in range(len(points)):
            label = classify(points[i][0], points[i][1], points[i][2], thresholdSquared)
            conformations[label] += 1
            triplets[0].append(points[i][0])
            triplets[1].append(points[i][1])
            triplets[2].append(points[i][2])
            triplets[3].append(label)
        points = triplets

    return points, conformations

def analyze(inputFile, threshList, outputFile):
    '''Given input file of triplet (b_x, b_y, b_z, r_x, r_y, r_z, g_x, g_y, g_z)
    coordinates with units in physical lengths (not pixel widths) and a
    threshold to determine touching, classifies each triplet into one of 8
    conformations based on which spots are close/touching.'''
    points = read_file(inputFile)
    points, conformations = analyze_inner(points, threshList, True)

    # Display output
    output = generate_output(points)
    write_output(output, outputFile)

    # Print output options
    print(conformations) #number of triplets in each conformation
    print(points[3])  #list each triplet's conformation

def generate_output(points: List) -> List:
    output = []
    for i in range(len(points[0])):
        label = points[3][i]
        output.append([points[1][i][0], points[1][i][1], points[1][i][2], label])
    return output

def write_output(output, outputFileName, nucleusCount: int = None):
    '''Given lines of triplets and their conformations, writes the triplet
    centroid and then the conformation number to a text file outputFileName.'''
    outFile = open(outputFileName, 'w')

    if nucleusCount:
        outFile.write(f'Nucleus count: {nucleusCount}\n')
    for i in range(len(output)):
        outFile.write('%-15s %-15s %-15s %s\n'%(output[i][0], output[i][1], output[i][2], output[i][3]))
    outFile.close()

class ProcessStepAnalyzeTouching(ProcessStep):
    """
    A process step to do touching analysis.
    """

    def __init__(self, params: Dict = {}):
        super().__init__(params)
        self._stepName = "AnalyzeTouching"

    def run(self, progressCallback: Callable[[int, str], None] = None):
        assert isinstance(self._inputs, list) and len(self._inputs) == 1
        assert 'touching_threshold' in self._params
        self._status = ProcessStatus.RUNNING
        triplets = self._inputs[0]
        self._stepOutputs = []
        self._endOutputs = []
        touching_threshold = self._params['touching_threshold']
        triplets, conformations = analyze_inner(triplets, touching_threshold)
        self._endOutputs.append(conformations)
        output = generate_output(triplets)
        self._stepOutputs.append(output)
        if progressCallback:
            # this step runs fast, so don't bother reporting intermediate progress
            progressCallback(100, self._stepName)
        if self._app:
            self._app.processEvents()
        self._status = ProcessStatus.COMPLETED


if __name__ == "__main__":
    # Enter command line arguments as: inputFile threshold outputFile
    inputFile = str(sys.argv[1])
    threshold = float(sys.argv[2])
    thresholdList = [threshold, threshold, threshold]
    outputFile = str(sys.argv[3])
    analyze(inputFile, thresholdList, outputFile)