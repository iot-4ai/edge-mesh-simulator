import numpy as np
from math import inf, dist
from time import time
from typing import *
import matplotlib.pyplot as plt
from matplotlib.colors import to_rgba
from collections import defaultdict as dict
from numpy import sign

""" 
Custom 3D supercover algorithm using parametric lines
- reports intersection length and supports float coords
"""
def obstructions(start, end, grid):
    ray = dist(start, end)
    # ~normalize direction vector
    diff = [(e - s)/ray for s, e in zip(start, end)]
    obstacles = dict(float)

    pos = [int(coord) for coord in start]
    step = sign(diff).astype(int) # step direction
    # init: find first voxel boundary along <dx, dy, dz>
    inters = [(int(coord + (s > 0)) - coord)/d if d else inf
        for coord, d, s in zip(start, diff, step)]

    # *how much <dx, dy, dz> must change for a unit increase in t
    deltas = [abs(1/d_) if d_ else inf for d_ in diff]

    t = 0  # [0, ray)
    while t < ray:
        if all(0 <= i < dim for i, dim in zip(pos, grid.shape)):
            exits = min(*inters, ray)
            seg = exits - t
            if seg > 0.01: obstacles[tuple(pos)] = (seg)

            for i, inter in enumerate(inters):  # i = axis of exit dir
                if inter == exits:
                    pos[i] += step[i]  # step into
                    inters[i] += deltas[i]  # next boundary

            t = exits # t @ entry
        else: break

    return obstacles

grid = np.ones((10, 10, 10), dtype=bool)

def showPlot(grid, start, end, obstacles):
    fig = plt.figure(figsize=(12, 10))
    ax = fig.add_subplot(111, projection="3d")
    X, Y, Z = grid.shape

    voxels = np.zeros((X, Y, Z), dtype=bool)
    colors = np.zeros((X, Y, Z, 4))  # RGBA color array

    max_length = max(*obstacles.values())
    for pos, length in obstacles.items():
        voxels[pos] = True
        opacity = min(1, length/max_length)/2  # clamp
        colors[pos] = to_rgba(plt.cm.Reds(opacity))
        colors[*pos, 3] = opacity

    x0, y0, z0 = start; x1, y1, z1 = end

    ax.text(x0, y0, z0 + 0.25, f"({x0}, {y0})", ha="center", color="green", fontsize=10)
    ax.text(x1, y1, z1 + 0.25, f"({x1}, {y1})", ha="center", color="green", fontsize=10)

    ax.voxels(voxels, facecolors=colors, edgecolor="none")
    ax.scatter(*start, color="g", s=25); ax.scatter(*end, color="g", s=25)

    ax.plot(*zip(start, end), color="lime", linewidth=2)

    for (x,y,z), length in obstacles.items():
        ax.text(x + 0.5, y + 0.5, z + 0.5, f"{length:.2f}", color="black", ha="center", fontsize=8)

    ax.set_xlabel("X"); ax.set_ylabel("Y"); ax.set_zlabel("Z")
    ax.set_xlim(0, X); ax.set_ylim(0, Y); ax.set_zlim(0, Z)
    ax.set_box_aspect((X, Y, Z))
    ax.grid(False)
    plt.tight_layout()
    plt.show()

def run(test, start, end):
    try:
        print(f"{test}:")
        i = time()
        obstacles = obstructions(start, end, grid)
        f = time()
        print(f"{start} to {end}")
        print(f"Spans {sum(obstacles.values()):.3f}, expected {dist(start, end):.3f}")
        print(f"Took {(f-i)*1000:.3f}ms\n")
        showPlot(grid, start, end, obstacles)
    except Exception as e: print(f"Error: {e}")

run("Positive slope", (2, 1.5, 1.2), (8, 7.3, 9))
run("Negative slope", (8, 7.3, 9), (2, 1.5, 1.2))
run("Mixed slope", (1, 8, 3), (9, 2, 7))
run("Diagonal", (0, 0, 0), (9, 9, 9))
run("Horizontal", (0, 5, 5), (9, 5, 5))
run("Negative vertical", (7, 7, 8), (7, 7, 0))
