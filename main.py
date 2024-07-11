from gen.proc import *
from gen.place import *
import sim.rep as sim
from typing import *  # type: ignore
from attrs import define, Factory as new
import matplotlib.pyplot as plot
from subprocess import Popen, PIPE, DEVNULL
from numpy import savez_compressed as export
from tempfile import NamedTemporaryFile
from os import getcwd as cwd, path, remove, mkdir
from contextlib import suppress, asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from time import time
from rich import print
from rich.progress import Progress
from sys import stderr
import threading
import uvicorn
import toml

config = toml.load("config.toml")

@define
class Timer:
    _start: float = new(time)

    def __str__(self):
        return f"{time() - self._start:.2f}s"

proc, progress = None, 0.0

def blender(tmp, out):
    global proc, progress
    proc = Popen(["blender", "-b", "-P", "gen/obj.py", "--", tmp.name, out],
        stdout=PIPE,
        stderr=DEVNULL)

    with Progress() as bar:
        task = bar.add_task("[yellow]Building...", total=100)

        for line in proc.stdout:  # type: ignore
            status = line.decode().strip()
            with suppress(ValueError):
                progress = float(status)
                bar.update(task, completed=progress*100)

    ret = proc.wait()
    if ret >= 0: print(f"[bright_yellow][{Timer()}][/]  Scene object file saved to {out}")
    else: raise InterruptedError("Interrupted")

def main(width=60, depth=80, n_nodes=None, comm_type="BLE"):
    global W, D
    W, D = width, depth
    sim.TYPE = comm_type
    timer = Timer()
    tmp = NamedTemporaryFile(delete=False)
    plot.rcParams["toolbar"] = "None"
    regions = genRegions(W, D, show=False)  # generate warehouse layout
    y, r = "bright_yellow", "bright_red"
    print(f"[{y}][{timer}][/]  Layout generated")

    try:
        kinds: Grid = features(W, D, regions, FREQ)  # place features
        print(f"[{y}][{timer}][/]  Features placed")
        nodes: Grid = sim.genPoints(W, D, n=n_nodes)  # scatter nodes

        plot.close()
        sim.init(
            kinds, nodes, show=False
        )  # create scene representation in global sim.SCENE
        print(f"[{y}][{timer}][/]  Created internal scene representation")
        plot.pause(0.1)

        export(tmp, k=kinds, h=sim.heights)
        print(f"[{y}][{timer}][/]  Saved scene data to {tmp.name}")

        out = path.join(cwd(), "vis", "assets")
        if not path.exists(out): mkdir(out)

        # Start Blender process in a separate thread
        thread = threading.Thread(target=blender, args=(tmp, out))
        thread.start()

    except Exception as e:
        print(f"[{y}][{timer}][/]  [{r}]{e}[/]", file=stderr)
    finally:
        plot.close()

    return thread

@asynccontextmanager
async def lifespan(app: FastAPI):
    global proc
    kwargs = {k: config[k] for k in ["width", "depth", "nodes", "comm"] if k in config}
    thread = main(**kwargs)
    app.MESH = sim.MESH  # type: ignore
    yield
    thread.join()
    if proc: proc.terminate()

app = FastAPI(lifespan=lifespan)
origins = [
    "http://localhost:8000",  # frontend
    "http://localhost:8001",  # FastAPI
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@app.get("/progress")
async def get_progress():
    global progress
    return {"progress": progress}

@app.get("/")
def get_root():
    return {"message": "Alive"}

@app.get("/controllers")
async def controllers():
    return [x.toJson() for x in app.MESH.values()]  # type: ignore

if __name__ == "__main__":
    uvicorn.run(
        "__main__:app", host="localhost", port=8001, reload=False, log_level="critical"
    )
