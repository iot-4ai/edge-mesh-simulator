from collections import namedtuple as data
from attrs import define, field, Factory as default
from ipaddress import IPv6Address
from random import randint as randInt, random as rand, \
getrandbits as choose, choice, shuffle, uniform
import numpy as num
from typing import *
from scipy.stats import qmc
from sys import path
path.append("../gen")
import place, proc # type: ignore
import matplotlib.pyplot as plot
from matplotlib.colors import ListedColormap


Signal = data("Signal", ["stren", "atten"])
Coord  = data("Coord", ["x", "y", "z"])
Rot    = data("Rot", ["p", "y", "r"])

@define
class BLE:
    ver: str = "5.3"

@define
class Radio:
    mod_type: str = "QAM"

@define
class WiFi:
    freq_band: str = "<6 GHz"

@define
class Controller:
    name: str
    comm: BLE|Radio|WiFi
    pos: Coord
    orient: Rot
    ip: str = field()
    signal: Signal|None = None

    @ip.default # type: ignore
    def genIPv6(self) -> str:
        return str(IPv6Address(choose(128))).upper()

KIND_MAP = {
    0: "empty",
    1: "shelf",
    2: "pile",
    3: "wall",
}
COL = \
[ "white", "peru", "sienna", "dimgray" ]

@define
class Chunk:
    kind: int
    height: int
    nodes: List[str] = default(list)

def makeChunk(kind: int) -> Chunk:
    height = 0
    match kind:
        case 0: height = 0
        case 1: height = H // 2
        case 2: height = randInt(1, H // 4)
        case 3: height = H
    return Chunk(kind, height)

def makeNodes(chunk: Chunk, x, y, node: bool):
    free = z = None
    if node:
        match chunk.kind:
            case 0: 
                z = choice([0, H])
                free = "ciel" if z == H else "floor"
            case 1|2|3: 
                # (0, 0) is top left (2D rep)
                dirs = [(0, 1), (0, -1), (1, 0), (-1, 0), "top"]
                shuffle(dirs)
                for d in dirs:
                    if d == "top":
                        if chunk.height < H:
                            z = chunk.height; free = d
                        break
                    pos = tuple(num.add(d, (x,y))) # bounds check (inverted): 
                    if not (0 <= pos[0] < proc.D and 0 <= pos[1] < proc.W): continue
                    if chunk.height > chunks[pos].height: #type: ignore
                        z = randInt(chunks[pos].height+1, chunk.height) #type: ignore
                        free = d
                        break
    if free: 
        pitch, yaw, roll = None, None, rand()*360
        match free:
            case "ciel": pitch, yaw = uniform(60, -240), uniform(60, -240)
            case "floor": pitch, yaw = uniform(-60, 240), uniform(-60, 240)
            case "top": pitch, yaw = uniform(0, 180), uniform(0, 180) 
            case (1, 0): yaw = uniform(-90, 90) # E
            case (0,-1): yaw = uniform(0, 180) # N
            case (-1,0): yaw = uniform(90, 270) # W
            case (0, 1): yaw = uniform(180, 360) # S
        if type(free) is tuple: pitch = uniform(90, 180)

        name = f"C{makeNodes.nth:03}"
        MESH[name] = Controller(
            name, BLE(), Coord(x, y, z), Rot(pitch, yaw, roll),
        ) # type: ignore
        makeNodes.nth += 1
        chunk.nodes.append(name)

    return chunk
makeNodes.nth = 0

def genPoints(x, y, r=5, n=None):
    sample = qmc.PoissonDisk(d=2, radius=r / min(x, y)).fill_space()
    sample[:, 0], sample[:, 1] = sample[:, 0] * x, sample[:, 1] * y # scale: fit
    N = len(sample)
    if not n: n = N // 4
    indices = num.random.choice(N, min(n, N), replace=False)
    points = sample[indices].astype(int)

    array = num.zeros((y, x), dtype=bool)
    # Represent points as bool:
    array[points[:, 1], points[:, 0]] = True

    return array

# proc.W, proc.D, proc.MIN = 150, 200, 30
H = 20
# proc.CUTOFF = proc.MIN / 4
# place.FREQ = {0: 0, 1: 50, 2: 40, 3: 10}

regions = proc.buildAQT(proc.W, proc.D)
kinds: num.ndarray = place.gridAQT(proc.W, proc.D, regions, place.FREQ)
nodes: num.ndarray = genPoints(proc.W, proc.D)

MESH: Dict[str, Controller] = {}
chunks: num.ndarray = num.vectorize(makeChunk)(kinds)
Xs, Ys = num.indices(chunks.shape) # extract indices
SCENE: num.ndarray = num.vectorize(makeNodes)(chunks, Xs, Ys, nodes)

for c in MESH.values(): # test
    print(f"Controller {c.name}:")
    print(f"\tType: {c.comm}")
    print(f"\tPosition: {c.pos}")
    print(f"\tFacing: {c.orient}")
    print(f"\tSignal: {c.signal}", end="\n\n")

# Get updated nodes from SCENE
new_nodes = num.argwhere(num.vectorize(lambda x: bool(x.nodes))(SCENE))

fig, ax = plot.subplots(figsize=(8, 8))
ax.imshow(kinds, cmap=ListedColormap(COL), origin="lower")
ax.scatter(new_nodes[:, 1], new_nodes[:, 0], color="royalblue", s=10)

ax.set_xticks([]); ax.set_yticks([])
ax.set_xlabel(f"W = {proc.W}"); ax.set_ylabel(f"D = {proc.D}")
plot.tight_layout()
plot.show()
