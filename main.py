from gen.proc import *; from gen.place import *
import sim.rep as sim

from typing import *
import matplotlib.pyplot as plot
from subprocess import Popen, PIPE, DEVNULL
from numpy import savez_compressed as export
from tempfile import NamedTemporaryFile 
from os import getcwd as cwd, path
from contextlib import suppress


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

print(tmp.name)

out = path.join(cwd(), "vis", "assets")
proc = Popen(["blender", "-b", "-P", "gen/obj.py", "--", tmp.name, out], stdout=PIPE, stderr=DEVNULL)

for line in proc.stdout: # type: ignore
    prog = line.decode().strip()
    with suppress(ValueError): print(f"{float(prog):.1%}")
