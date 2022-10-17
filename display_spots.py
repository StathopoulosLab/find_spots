from __future__ import division, print_function

import imageio

# import matplotlib as mpl
# mpl.use('Agg')
import matplotlib.pyplot as plt

from matplotlib import cm

import sys

def read_file(inputFName):
    '''Read in a file with name 'inputFName' and returns (x,y) of triplets
    and conformations of triplets'''
    f = open(inputFName, 'r')
    triplets, conformations = [], []
    for line in f:
        triplets.append([float(line.split()[0]), float(line.split()[1])])
        conformations.append(line.split()[3])
    return triplets, conformations

# Call cmd line args in this order: conformationFile, inImageName, outImageName
confFile = str(sys.argv[1])
inImageName = str(sys.argv[2])
outImageName = str(sys.argv[3])

# Show base image
im = imageio.imread(inImageName)
plt.imshow(im, cmap=cm.gray)

# Plot Triplets Over

colors = {'000':'r', '100':'b', '010':'g', '001':'c', '110':'y', '101':'k',
          '011':'w', '111':'m'}

triplets, conformations = read_file(confFile)

xScale = 0.0990358382936508
yScale = xScale
zScale = 0.36

# Plot triplet centers
for i in range(len(triplets)):
    style = colors[conformations[i]]+'o'
    plt.plot(triplets[i][0]/xScale, triplets[i][1]/yScale, style, markersize=6)
plt.show()

fig = plt.gcf()
ax = plt.gca()
ax.set_xlim((0,2048)) #set plot size
ax.set_ylim((0,2048)) #set plot size
fig.gca().set_aspect('equal')
plt.axis('off')
plt.savefig(outImageName)
plt.clf()
plt.close()