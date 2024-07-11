import numpy as num
from math import inf, hypot
from time import time
import matplotlib.pyplot as plot

""" 
Bresenham-based supercover algorithm that also reports intersection length
"""
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


def obstructions(start, end, grid):
    x0, y0 = start; x1, y1 = end
    dx, dy = x1 - x0, y1 - y0
    x, y = x0, y0
    sx, sy = num.sign(dx), num.sign(dy) # step directions
    diff = abs(dx) - abs(dy)
    dx *= 2; dy *= 2
    length: float

    X, Y = grid.shape
    obstacles = []
    for _ in range(1 + X + Y):
        if 0 <= x <= X and 0 <= y <= Y and grid[y, x] != 0:
            # print(x, y)
            def inter(s, _0, _d):
                return (s - _0) / _d if _d != 0 else inf

            ix = inter(x - 0.5, x0, dx), inter(x + 0.5,  x0, dx)
            iy = inter(y - 0.5, y0, dy), inter(y + 0.5,  y0, dy)

            _max = min(max(*ix), max(*iy))
            _min = max(min(*ix), min(*iy))


            # print(_min, _max)
            if _max >= 0 and _min <= 1: # clamp
                _min = max(0, _min)
                _max = min(1, _max)

                enter_x, enter_y = (x0 + _min * dx, y0 + _min * dy)
                leave_x, leave_y = (x0 + _max * dx, y0 + _max * dy)
                if x == x1 and y == y1: leave_x, leave_y = x, y # fix end +0.5

                length = hypot(leave_x - enter_x, leave_y - enter_y)
            if _min == inf:
                length = 0.5 if (x, y) == (x0, y0) or (x, y) == (x1, y1) else 1.0
            obstacles.append((x, y, length)) # type: ignore

            if x == x1 and y == y1: break

        # next step:
        if diff > 0:
            x += sx
            diff -= abs(dy)
        elif diff == 0: # corner
            x += sx; y += sy
            diff += abs(dx)-abs(dy)
        else:
            y += sy
            diff += abs(dx)

    return obstacles

grid = num.ones((10,10), dtype=bool) # Y, X

#        X, Y
start = (2, 1)
end =   (5, 9)

try:
    i = time()
    obstacles = obstructions(start, end, grid)
    f = time()
    plot.rcParams["toolbar"] = "None"
    showPlot(grid, start, end, obstacles)
    print(f"Time: {(f-i)*1000:.4f}ms")


except IndexError:
    print("Node out of bounds")
    exit()
