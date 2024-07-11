from attrs import define
from typing import *
import numpy as num
from numpy import clip as clamp
from math import inf, dist
from time import time
import matplotlib.pyplot as plot

isType = isinstance

""" 
Bresenham-based supercover algorithm that also reports intersection length
- alternative implementation that supports float coords & may be more extensible
"""
@define
class Line:
    x0: float
    y0: float
    x1: float
    y1: float

    @property
    def slope(self):
        den = (self.x1 - self.x0)
        return (self.y1 - self.y0)/den if den != 0 else inf

    def getX(self, y) -> float | tuple | None:
        ends = self.y0, self.y1
        y = clamp(y, min(*ends), max(*ends))
        # if not (min(*ends) <= y <= max(*ends)): return None
        if self.slope == 0: return (self.x0, self.x1)
        if self.slope == inf: return self.x1
        return (y - self.y1)/self.slope + self.x1

    def getY(self, x) -> float | tuple | None:
        ends = self.x0, self.x1
        x = clamp(x, min(*ends), max(*ends))
        if self.slope == 0: return self.y1
        if self.slope == inf: return (self.y0, self.y1)
        return self.slope*(x - self.x1) + self.y1

    def dump(self):
        return (self.x0, self.y0, self.x1, self.y1)

def showPlot(grid, start, end, obstacles):
    X, Y = grid.shape
    _, ax = plot.subplots()
    ax.imshow(grid, cmap="binary", origin="upper", extent=[0, Y, X, 0])

    ax.set_xticks(num.arange(0, Y, 1))
    ax.set_yticks(num.arange(0, X, 1))
    ax.set_xticks(num.arange(0.5, Y, 1), minor=True)
    ax.set_yticks(num.arange(0.5, X, 1), minor=True)

    ax.grid(which="major", color="lightgray", linestyle=":", linewidth=0.5)
    ax.grid(which="minor", color="gray", linestyle="-", linewidth=0.5)

    ax.set_xlabel("X")
    ax.set_ylabel("Y")

    x0, y0 = start
    x1, y1 = end
    ax.plot([x0, x1], [y0, y1], "lime", linewidth=2)

    ax.plot(x0, y0, "go", markersize=5)
    ax.plot(x1, y1, "go", markersize=5)

    ax.text(x0, y0 - 0.25, f"({x0}, {y0})", ha="center", color="green", fontsize=10)
    ax.text(x1, y1 + 0.25, f"({x1}, {y1})", ha="center", color="green", fontsize=10)

    for x, y, length in obstacles:
        opacity = length/(1.414*2)  # Calculate opacity based on length
        rect = plot.Rectangle(  #type: ignore
            (x - 0.5, y - 0.5), 1, 1, edgecolor="b", facecolor="b", alpha=opacity, linewidth=2
        )
        plot.gca().add_patch(rect)
        plot.text(x, y + 0.25, f"{length:.2f}", ha="center", color="navy", fontsize=10)

        ax.plot(x, y, "bo", markersize=4)
        plot.xlim(-0.5, Y - 0.5)
        plot.ylim(-0.5, X - 0.5)

    plot.tight_layout()
    plot.show()

def obstructions(line: Line, grid):
    x0, y0, x1, y1 = line.dump()
    dir_x, dir_y = num.sign(x1 - x0), num.sign(y1 - y0)
    x, y = round(x0), round(y0)
    # make round exclusive of 0.5
    x1 -= dir_x*0.001 if int(x1) + .5 == x1 else 0
    y1 -= dir_y*0.001 if int(y1) + .5 == y1 else 0

    prev, leaves = (x0, y0), (0, 0)
    X, Y = grid.shape
    obstacles = []
    done = False

    while not done:
        if 0 <= x <= X and 0 <= y <= Y:
            # print(x,y)
            ds: float
            lr, tb = x + dir_x*0.5, y + dir_y*0.5
            exit_x, exit_y = line.getX(tb), line.getY(lr)
            dx, dy, = 0, 0
            # determine which face line exits from (<l|r>, <t|b>)
            for axis, exit_ in {"x": exit_x, "y": exit_y}.items():

                if isType(exit_, tuple):  # slope is 0 or inf
                    leaves = (lr, y1) if axis == "x" else (x1, tb)
                    if axis == "x": dx = dir_x
                    else: dy = dir_y

                elif isType(exit_, float) and abs(locals()[axis] - exit_) <= 0.5:  # noqa: PLR2004
                    if exit_ in (x1, y1): leaves = (x1, y1)
                    else: leaves = (exit_, tb) if axis == "x" else (lr, exit_)
                    if axis == "y": dx = dir_x
                    else: dy = dir_y

            ds = dist(prev, leaves)
            prev = leaves

            if x == round(x1) and y == round(y1):
                # ds = dist(prev, (x1, y1))
                done = True

            # if ds > 0.1:
            obstacles.append((x, y, round(ds, 3)))
            x += dx
            y += dy  # step

    return obstacles

grid = num.ones((10, 10), dtype=bool)  # Y, X

#        X,   Y
start = (0.2, 0.9)
end =   (4.3, 7.8)

line = Line(*start, *end)

try:
    i = time()
    obstacles = obstructions(line, grid)
    f = time()
    plot.rcParams["toolbar"] = "None"
    showPlot(grid, start, end, obstacles)
    print(f"Time: {(f-i)*1000:.4f}ms")
except IndexError:
    print("Node out of bounds")
    exit()
