from gen.proc import *; from gen.place import *
from sim.rep import *

from typing import *
import matplotlib.pyplot as plot

plot.rcParams["toolbar"] = "None"

regions = genRegions(W, D, show=True) # generate warehouse layout
plot.pause(1)

kinds: Grid = features(W, D, regions, FREQ) # place features
nodes: Grid = genPoints(W, D) # scatter nodes

plot.close()
init(kinds, nodes, show=True) # create scene representation
plot.pause(1)
