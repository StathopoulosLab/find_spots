import sys

def distance(point1, point2):
    '''Returns squared distance between point 1 and point 2 in form [x,y,z]'''
    x1, y1, z1 = point1[0], point1[1], point1[2]
    x2, y2, z2 = point2[0], point2[1], point2[2]
    return (x1-x2)**2 + (y1-y2)**2 + (z1-z2)**2
    
def classify(blue, red, green, threshold):
    '''Classifies given triplet based on distances between 3 point inputs and 
    a threshold parameter that gives the cutoff between "near" and "far"'''
    output = [0,0,0]
    if distance(blue, red) < threshold:
        output[0] = 1
    if distance(green, blue) < threshold:
        output[1] = 1
    if distance(red, green) < threshold:
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

def analyze_inner(points, thresh):
    '''Given input file of triplet (b_x, b_y, b_z, r_x, r_y, r_z, g_x, g_y, g_z)
    coordinates with units in physical lengths (not pixel widths) and a 
    threshold to determine touching, classifies each triplet into one of 8
    conformations based on which spots are close/touching.''' 
    # Classify the different points
    conformations = {'000':0, '100':0, '010':0, '001':0, '110':0, '101':0, \
                    '011':0, '111':0}
    points.append([])
    for i in range(len(points[0])):
        label = classify(points[0][i], points[1][i], points[2][i], thresh**2)
        conformations[label] += 1
        points[3].append(label)
    
    # # Hmmm.  The following don't appear to be used anywhere.
    # dist_35, dist_3P, dist_5P = [], [], []
    # for i in range(len(points[0])):
    #     dist_35.append(distance(points[0][i], points[1][i]))
    #     dist_3P.append(distance(points[0][i], points[2][i]))
    #     dist_5P.append(distance(points[1][i], points[2][i]))
    
    return points, conformations
    
def analyze(inputFile, thresh, outputFile):
    '''Given input file of triplet (b_x, b_y, b_z, r_x, r_y, r_z, g_x, g_y, g_z)
    coordinates with units in physical lengths (not pixel widths) and a 
    threshold to determine touching, classifies each triplet into one of 8
    conformations based on which spots are close/touching.''' 
    points = read_file(inputFile)
    points, conformations = analyze_inner(points, thresh)
    
    # Display output
    write_output(points, outputFile)
    
    # Print output options
    print(conformations) #number of triplets in each conformation
    print(points[3])  #list each triplet's conformation
    
def write_output(points, outputFileName):
    '''Given lines of triplets and their conformations, writes the triplet
    centroid and then the conformation number to a text file outputFileName.'''
    outFile = open(outputFileName, 'w')
    
    for i in range(len(points[0])):
        xCentr = (points[0][i][0] + points[1][i][0] + points[2][i][0])/3
        yCentr = (points[0][i][1] + points[1][i][1] + points[2][i][1])/3
        zCentr = (points[0][i][2] + points[1][i][2] + points[2][i][2])/3
        label = points[3][i]
        outFile.write('%-15s %-15s %-15s %s\n'%(xCentr, yCentr, zCentr, label))
    outFile.close()

if __name__ == "__main__":
    # Enter command line arguments as: inputFile threshold outputFile
    inputFile = str(sys.argv[1])
    threshold = float(sys.argv[2])
    outputFile = str(sys.argv[3])
    analyze(inputFile, threshold, outputFile)