from collections import namedtuple as data
from attrs import define, field, Factory as default
from ipaddress import IPv6Address
from random import randint as randInt, random as rand, \
getrandbits as choose, choice, shuffle, uniform
import numpy as num
from typing import *
from nptyping import NDArray
from scipy.stats import qmc
import matplotlib.pyplot as plot
from matplotlib.colors import ListedColormap
from functools import partial

Signal = data("Signal", ["stren", "atten"])


@define
class Coord:
    x: int; y: int; z: int

@define
class Rot:
    _trunc = partial(field, converter=lambda x: round(x, 3))
    p: float = _trunc(); y: float = _trunc(); r: float = _trunc()

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

KINDS = {
    0: "empty",
    1: "shelf",
    2: "pile",
    3: "wall",
}
COL = \
[ "white", "peru", "sienna", "dimgray" ]

@define
class Chunk:
    kind: str
    height: int
    nodes: List[str] = default(list)

def _makeHeights(kind: int) -> int:
    return {
        "empty": 0,
        "shelf": H // 2,
        "pile": randInt(1, H // 4),
        "wall": H
    }[KINDS[kind]]

def _makeChunk(kind: int, height: int) -> Chunk:
    return Chunk(KINDS[kind], height)

def _makeNodes(chunk: Chunk, x, y, node: bool):
    free = None; z = 0
    if node:
        match chunk.kind:
            case "empty": 
                z = choice([0, H])
                free = "ciel" if z == H else "floor"
            case "shelf" | "pile" | "wall": 
                # (0, 0) is top left (2D rep)
                dirs = [(0, 1), (0, -1), (1, 0), (-1, 0), "top"]
                shuffle(dirs)
                for d in dirs:
                    if d == "top":
                        if chunk.height < H:
                            z = chunk.height; free = d
                        break
                    pos = tuple(num.add(d, (x,y))) 
                    W, D = _chunks.shape # bounds check (inverted):
                    if not (0 <= pos[0] < W and 0 <= pos[1] < D): continue
                    if chunk.height > _chunks[pos].height: #type: ignore
                        z = randInt(_chunks[pos].height+1, chunk.height) #type: ignore
                        free = d
                        break
    if free: 
        pitch, yaw, roll = 0, 0, rand()*360
        match free:
            case "ciel": pitch, yaw = uniform(60, -240), uniform(60, -240)
            case "floor": pitch, yaw = uniform(-60, 240), uniform(-60, 240)
            case "top": pitch, yaw = uniform(0, 180), uniform(0, 180) 
            case (1, 0): yaw = uniform(-90, 90) # E
            case (0,-1): yaw = uniform(0, 180) # N
            case (-1,0): yaw = uniform(90, 270) # W
            case (0, 1): yaw = uniform(180, 360) # S
        if type(free) is tuple: pitch = uniform(90, 180)

        name = f"C{_makeNodes.nth:0{len(str(_maxN))}d}"
        MESH[name] = Controller(
            name, BLE(), Coord(x, y, z), Rot(pitch, yaw, roll),
        ) # type: ignore
        _makeNodes.nth += 1
        chunk.nodes.append(name)

    return chunk
_makeNodes.nth = 0
_maxN = 0

type Grid[T] = NDArray[(int, int), T] # type: ignore

def genPoints(x, y, r=5, n=None) -> Grid:
    sample = qmc.PoissonDisk(d=2, radius=r / min(x, y)).fill_space()
    sample[:, 0], sample[:, 1] = sample[:, 0] * x, sample[:, 1] * y # scale: fit
    N = len(sample)
    if not n: n = N // 4
    global _maxN; _maxN = n
    indices = num.random.choice(N, min(n, N), replace=False)
    points = sample[indices].astype(int)

    array: Grid = num.zeros((y, x), dtype=bool)
    # Represent points as bool:
    array[points[:, 1], points[:, 0]] = True

    return array

def _showFig(kinds):
    # Get updated nodes from SCENE
    new_nodes = num.argwhere(num.vectorize(lambda x: bool(x.nodes))(SCENE))

    _, ax = plot.subplots(figsize=(8, 8))
    ax.imshow(kinds, cmap=ListedColormap(COL), origin="lower")
    ax.scatter(new_nodes[:, 1], new_nodes[:, 0], color="royalblue", s=10)

    D, W = SCENE.shape
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_xlabel(f"W = {W}"); ax.set_ylabel(f"D = {D}")
    plot.gca().invert_yaxis()
    plot.tight_layout()
    plot.show(block=False)

H = 20
MESH: Dict[str, Controller] = {}
SCENE: Grid[Chunk]; _chunks: Grid[Chunk]; heights: Grid[int]

def init(kinds: Grid[int], nodes: Grid[bool], show=False):
    global SCENE, _chunks, heights
    heights = num.vectorize(_makeHeights)(kinds)
    _chunks = num.vectorize(_makeChunk)(kinds, heights)

    Xs, Ys = num.indices(_chunks.shape) # extract indices
    SCENE = num.vectorize(_makeNodes)(_chunks, Xs, Ys, nodes)

    if show: _showFig(kinds)
