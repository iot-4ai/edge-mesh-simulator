from gen.proc import *
from gen.place import *
from sim.signal import *
from sim import rep
from gen.build import build
from typing import *  # type: ignore
from attrs import define, Factory as new
import matplotlib.pyplot as plot
from os import getcwd as cwd, path, mkdir
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from time import time
from rich import print
from sys import stderr
from threading import Thread
from uvicorn import run
import toml

config = toml.load("config.toml")

@define
class Timer:
    _start: float = new(time)

    def __str__(self):
        return f"{time() - self._start:.2f}s"

progress = {"value": 0.0, "step": "Initializing"}
timer = Timer()

def updateProgress(value, step=None):
    global progress
    progress["value"] = value
    if step:
        progress["step"] = step
        print(f"[bright_yellow][{timer}][/]  {step}")

def main(width=60, depth=80, n_nodes=None, comm_type="BLE"):
    global W, D
    W, D = width, depth
    rep.TYPE = comm_type
    plot.rcParams["toolbar"] = "None"

    updateProgress(0.0, "Generating layout")
    regions = genRegions(W, D, show=False)  # generate warehouse layout

    try:
        updateProgress(0.05, "Placing features")
        kinds: Grid = features(W, D, regions, FREQ)  # place features

        updateProgress(0.1, "Scattering nodes")
        nodes: Grid = rep.genPoints(W, D, n=n_nodes)  # scatter nodes

        plot.close()
        updateProgress(0.15, "Creating internal representation")
        rep.init(kinds, nodes, show=False)  # create scene rep in global rep.SCENE
        plot.pause(0.1)

        updateProgress(0.2, "Determining signal strength")
        sigStren(rep.cloud, rep.MESH)

        out = path.join(cwd(), "vis", "assets")
        if not path.exists(out): mkdir(out)
        build(rep.cloud, out, lambda v, s=None: updateProgress(0.4 + v*0.6, s))

    except Exception as e:
        print(f"[bright_red][{timer}]  ERROR: {e}[/]", file=stderr)
    finally:
        plot.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    kwargs = {k: config[k] for k in ["width", "depth", "nodes", "comm"] if k in config}
    Thread(target=main, kwargs=kwargs).start()
    app.MESH = rep.MESH  # type: ignore
    yield

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
async def getProgress():
    global progress; return progress

@app.get("/")
def getRoot():
    return {"message": "Alive"}

@app.get("/controllers")
async def controllers():
    return [x.toJson() for x in app.MESH.values()]  # type: ignore

if __name__ == "__main__":
    run("__main__:app", host="localhost", port=8001, reload=False, log_level="critical")
