from gen.proc import *; from gen.place import *
import sim.rep as sim

from typing import *
from click import command as args, option, Choice, IntRange
from attrs import define, Factory as new
import matplotlib.pyplot as plot
from subprocess import Popen, PIPE, DEVNULL
from numpy import savez_compressed as export
from tempfile import NamedTemporaryFile 
from os import getcwd as cwd, path, remove
from contextlib import suppress
from time import time
from rich import print

@define
class Timer:
    _start: float = new(time)

    def __str__(self):
        return f"{time() - self._start:.2f}s"

@args()
@option("-s", "--size", 
        nargs=2, type=IntRange(50, 500, clamp=True), help="Scene dimensions <width> <depth>")
@option("-n", "--nodes", "n_nodes",
        type=IntRange(3, 10000, clamp=True), default=None, help="Number of nodes in the scene")
@option("-t", "--type", "comm_type", type=Choice(["BLE", "WiFi", "Radio"],
        case_sensitive=False), default="BLE", help="Communication type <BLE|WiFi|Radio>")
def main(size, n_nodes, comm_type):
    global W, D
    if size: W, D = size
    sim.TYPE = comm_type
    timer = Timer()
    plot.rcParams["toolbar"] = "None"
    regions = genRegions(W, D, show=False) # generate warehouse layout
    y, r = "bright_yellow", "bright_red"
    print(f"[{y}][{timer}][/]  Layout generated")

    kinds: Grid = features(W, D, regions, FREQ) # place features
    print(f"[{y}][{timer}][/]  Features placed")
    nodes: Grid = sim.genPoints(W, D, n=n_nodes) # scatter nodes

    plot.close()
    sim.init(kinds, nodes, show=True) # create scene representation in global sim.SCENE
    print(f"[{y}][{timer}][/]  Created internal scene representation")
    plot.pause(0.1)

    tmp = NamedTemporaryFile()
    export(tmp, k=kinds, h=sim.heights)
    print(f"[{y}][{timer}][/]  Saved scene data to {tmp.name}")

    out = path.join(cwd(), "vis", "assets")
    proc = Popen(["blender", "-b", "-P", "gen/obj.py", "--", tmp.name, out], stdout=PIPE, stderr=DEVNULL)

    from rich.progress import Progress
    with Progress() as prog:
        task = prog.add_task("[yellow]Building...", total=100)
        
        for line in proc.stdout:  # type: ignore
            perc = line.decode().strip()
            with suppress(ValueError):
                prog.update(task, completed=float(perc) * 100)

    ret = proc.wait()
    if ret >= 0: print(f"[{y}][{timer}][/]  Scene object file saved to {out}")
    else: print(f"[{y}][{timer}][/]  [{r}]Interrupted[/]")

    plot.close()
    remove(tmp.name)

if __name__ == "__main__": main()
