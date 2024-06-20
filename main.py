from gen.proc import *
from gen.place import *
import sim.rep as sim
from typing import *  # type: ignore
from attrs import define, Factory as new
import matplotlib.pyplot as plot
from subprocess import Popen, PIPE, DEVNULL
from numpy import savez_compressed as export
from tempfile import NamedTemporaryFile
from os import getcwd as cwd, path, remove
from contextlib import suppress, asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from time import time
from rich import print
import toml
import uvicorn

config = toml.load("config.toml")

@define
class Timer:
    _start: float = new(time)

    def __str__(self):
        return f"{time() - self._start:.2f}s"

def main(size=(50, 50), n_nodes=0, comm_type="BLE"):
    global W, D
    if size: W, D = size
    sim.TYPE = comm_type
    timer = Timer()
    plot.rcParams["toolbar"] = "None"
    regions = genRegions(W, D, show=False)  # generate warehouse layout
    y, r = "bright_yellow", "bright_red"
    print(f"[{y}][{timer}][/]  Layout generated")

    kinds: Grid = features(W, D, regions, FREQ)  # place features
    print(f"[{y}][{timer}][/]  Features placed")
    nodes: Grid = sim.genPoints(W, D, n=n_nodes)  # scatter nodes

    plot.close()
    sim.init(kinds, nodes, show=False)  # create scene representation in global sim.SCENE
    print(f"[{y}][{timer}][/]  Created internal scene representation")
    plot.pause(0.1)

    tmp = NamedTemporaryFile()
    export(tmp, k=kinds, h=sim.heights)
    print(f"[{y}][{timer}][/]  Saved scene data to {tmp.name}")

    out = path.join(cwd(), "vis", "assets")
    proc = Popen(["blender", "-b", "-P", "gen/obj.py", "--", tmp.name, out],
        stdout=PIPE,
        stderr=DEVNULL)

    from rich.progress import Progress
    with Progress() as prog:
        task = prog.add_task("[yellow]Building...", total=100)

        for line in proc.stdout:  # type: ignore
            perc = line.decode().strip()
            with suppress(ValueError):
                prog.update(task, completed=float(perc)*100)
    ret = proc.wait()
    if ret >= 0: print(f"[{y}][{timer}][/]  Scene object file saved to {out}")
    else: print(f"[{y}][{timer}][/]  [{r}]Interrupted[/]")

    plot.close()
    remove(tmp.name)

# Startup script
@asynccontextmanager  # API
async def lifespan(app: FastAPI):
    main((config["width"], config["height"]), config["nodes"], config["comm"])
    app.MESH = sim.MESH  # type: ignore
    yield

app = FastAPI(lifespan=lifespan)
origins = [
    "http://localhost:8000",  # frontend
    "http://localhost:8001",  # FastAPI
]
# Cross origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@app.get("/")
def get_root():
    return {"message": "Alive"}

@app.get("/controllers")
async def controllers():
    return [x.toJson() for x in app.MESH.values()]  # type: ignore

if __name__ == "__main__":
    uvicorn.run("__main__:app", host="localhost", port=8001, reload=True)
