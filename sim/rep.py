from collections import namedtuple as data
from attrs import define, field
from ipaddress import IPv6Address
from random import randint as randInt, random as rand, \
getrandbits as choose

import numpy as num
from typing import *

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
    ip: str = field()
    pos: Coord|None = None
    orient: Rot|None = None
    signal: Signal|None = None

    @ip.default # type: ignore
    def genIPv6(self) -> str:
        return str(IPv6Address(choose(128))).upper()

@define
class Chunk:
    height: int
    node: List[str]
    inside: bool

X = Y = 100; Z = 10
SCENE = num.zeros((X, Y), dtype=object) 
N_NODES = 10
mesh: Dict[str, Controller] = {}

for n in range(N_NODES): # TODO
    name = f"C{n+1:03}"
    c = Controller(name, BLE()) #type: ignore
    mesh[c.ip] = c
    x, y = randInt(0, X), randInt(0, Y)

    # 50/50 chance of being mounted to wall
    z = 0 if choose(1) else randInt(0, Z)

    SCENE[x, y] = Chunk(z, [c.ip], inside=True)
    c.pos = Coord(x, y, z)
    if z != 0: c.orient = Rot(rand()*360, rand()*360, rand()*360)
    else: c.orient = Rot(rand()*360, rand()*360, rand()*360)

for c in mesh.values(): # test
    print(f"Controller {c.name}:")
    print(f"\tType: {c.comm}")
    print(f"\tPosition: {c.pos}")
    print(f"\tFacing: {c.orient}")
    print(f"\tSignal: {c.signal}", end="\n\n")
