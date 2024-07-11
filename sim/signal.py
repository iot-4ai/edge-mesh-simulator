from math import inf, dist
from typing import *
from numpy import sign
from contextlib import suppress
from .rep import KINDS

def occlusion(start, end, cloud):
    ray = dist(start, end)
    # ~normalize direction vector
    diff = [(e - s)/ray for s, e in zip(start, end)]
    obstacles = []

    pos = [int(coord) for coord in start]
    step = sign(diff).astype(int) # step direction
    # init: find first voxel boundary along <dx, dy, dz>
    inters = [(int(coord + (s > 0)) - coord)/d if d else inf 
        for coord, d, s in zip(start, diff, step)]

    # *how much <dx, dy, dz> must change for a unit increase in t
    deltas = [abs(1/d_) if d_ else inf for d_ in diff]

    t = 0  # [0, ray)
    while t < ray:
        exits = min(*inters, ray)
        seg = exits - t; kind = 0
        with suppress(IndexError): kind = cloud[tuple(pos)]
        if seg > 0.01: obstacles.append((kind, seg))

        for i, inter in enumerate(inters):  # i = axis of exit dir
            if inter == exits:
                pos[i] += step[i]  # step into
                inters[i] += deltas[i]  # next boundary

        t = exits # t @ entry

    return obstacles

density = {
    "empty": 1,  # air: 100m
    "shelf": 2,  # shelf: 50m
    "pile": 3,  # pile: 33m
    "wall": 5   # wall: 20m
}

MAX_STREN = 100

def sigStren(cloud, mesh):
    for cA in mesh.values():
        for cB in mesh.values():
            if cA.name >= cB.name: continue
            if dist(cA.pos, cB.pos) > MAX_STREN: continue
            obstacles = occlusion(cA.pos, cB.pos, cloud)
            loss = sum(density[KINDS[o[0]]]*o[1] for o in obstacles)
            if loss > MAX_STREN: continue
            strength = MAX_STREN - loss

            cA.hears[cB.name] = cB.hears[cA.name] = strength
