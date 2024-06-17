from gen.proc import *; from gen.place import *
# from sim.rep import *
import sim.rep as sim

from typing import *
import matplotlib.pyplot as plot
from subprocess import getoutput as run
from numpy import savez_compressed as export
from tempfile import NamedTemporaryFile 


plot.rcParams["toolbar"] = "None"

regions = genRegions(W, D, show=True) # generate warehouse layout
plot.pause(1)

kinds: Grid = features(W, D, regions, FREQ) # place features
nodes: Grid = sim.genPoints(W, D) # scatter nodes

plot.close()
sim.init(kinds, nodes, show=True) # create scene representation in global sim.SCENE
plot.pause(1)
plot.close()

tmp = NamedTemporaryFile(delete=False)
export(tmp, k=kinds, h=sim.heights)

out = run(f"blender -b -P b.py -- {tmp.name}")
