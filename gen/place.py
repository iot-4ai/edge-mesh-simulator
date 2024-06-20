from typing import * # type: ignore
import numpy as num
from nptyping import NDArray
from numpy.random import choice as choose
from random import randrange as randRange, random
from collections import deque
from math import sqrt


FREQ = {0: 0, 1: 50, 2: 40, 3: 10}
rects = []

def _normFreq(FREQ):
    ele = list(FREQ.keys()); prob = list(FREQ.values())
    val = sum(prob); ret = [v / val for v in prob]
    return ele, ret

def _pickFreq(FREQ):
    ele, prob = _normFreq(FREQ)
    return choose(ele, p=prob)

def _dist(p1, p2):
    y1, x1, y2, x2 = p1[0], p1[1], p2[0], p2[1]
    return sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

# chooses distribution of "close" nodes from start as a pile
def _weightedBFS(start, bounds, target, weight=1.0):
    queue = deque([start])
    visited = set(); visited.add(start)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    result = [start]

    while queue and len(result) < target:
        current = queue.popleft()
        if current != start and random() < (weight / _dist(current, start)):
            result.append(current)
        if len(result) >= target: break
        row, col = current
        for r, c in directions:
            new_row, new_col = row + r, col + c
            if (
                bounds[0] <= new_row < bounds[1]
                and bounds[2] <= new_col < bounds[3]
                and (new_row, new_col) not in visited
            ):
                queue.append((new_row, new_col))
                visited.add((new_row, new_col))
    while len(result) < target:
        for node in visited:
            if node != start and random() < (weight / _dist(node, start)):
                result.append(node)
    return result

def _placeChunk(grid, chunks, code):
    for chunk in chunks: grid[chunk[0], chunk[1]] = code

# finds placement max_dist
def _peekRegion(grid, dim, start, flag):
    y, x = start; y_max, x_max = dim
    ret = 0
    if flag:
        for i in range(y, y_max):
            if grid[i, x] == 0: ret += 1
            else: break
    else:
        for i in range(x, x_max):
            if grid[y, i] == 0: ret += 1
            else: break
    return ret

def _addRectsHori(grid,i,x,cur):
    started = False
    for j in range(x, x + cur):
        if grid[i, j] == 1:
            if not started: started = True; rect_x = j; w = 1
            else: w += 1
        elif started:
            rects.append(("Shelf", i, rect_x, 1, w))
            started = False

def _horiShelf(grid, dim, start, options):
    y, x = start; y_max = dim[0]; min_dist, min_gap = 3, 2
    spacing, gap, extra, p = options
    i = y; flag = extra
    while i < y_max:
        cur = _peekRegion(grid, dim, (i, x), 0)
        if cur > min_dist: grid[i, x : x + cur] = 1
        for loc in range(x + gap, x + cur, gap):
            if random() < p: grid[i, loc - gap : loc + 1] = 0
            elif x + cur - loc > min_gap: grid[i, loc] = 0
        _addRectsHori(grid,i,x,cur)
        if extra and flag: i += 1; flag = False
        else: i += spacing; flag = extra

def _addRectsVert(grid,i,y,cur):
    started = False
    for j in range(y, y + cur):
        if grid[j, i] == 1:
            if not started: started = True; rect_y = j; h = 1
            else: h += 1
        elif started:
            rects.append(("Shelf", rect_y, i, h, 1))
            started = False

def _vertShelf(grid, dim, start, options):
    y, x = start; x_max = dim[1]; min_dist, min_gap = 3, 2
    spacing, gap, extra, p = options
    i = x; flag = extra
    while i < x_max:
        cur = _peekRegion(grid, dim, (y, i), 1)
        if cur > min_dist: grid[y : y + cur, i] = 1
        for loc in range(y + gap, y + cur, gap):
            if random() < p: grid[loc - gap : loc + 1, i] = 0
            elif y + cur - loc > min_gap: grid[loc, i] = 0
        _addRectsVert(grid,i,y,cur)
        if extra and flag: i += 1; flag = False
        else: i += spacing; flag = extra

def _shelves(grid, dim, start):
    y, x, y_max, x_max = start[0], start[1], dim[0], dim[1]
    spacing = choose([2, 3, 4]); gap = choose([5, 6, 7])
    extra_w = choose([0, 1], p=[0.75, 0.25])
    spacing += extra_w
    if min(y_max - y, x_max - x) == y_max - y:
        _vertShelf(grid, dim, start, (spacing, gap, extra_w, 0.075))
    else:
        _horiShelf(grid, dim, start, (spacing, gap, extra_w, 0.075))

def _pile(grid, dim, start, num):
    y, x, y_max, x_max, p = start[0], start[1], dim[0], dim[1], 0.45
    for i in range(3):
        if i > 0 and random() >= p: continue
        y_range, x_range = randRange(y, y_max), randRange(x, x_max)
        bounds = [y, y_max - 1, x, x_max - 1]
        target = 20
        vals = _weightedBFS((y_range, x_range), bounds, target, weight=1.25)
        _placeChunk(grid, vals, num)
    _shelves(grid, dim, start)

def _pillars(grid, start, end):
    y_start, x_start, y_end, x_end = start[0], start[1], end[0], end[1]
    grid[y_start, x_start] = 3 # top-left corner
    grid[y_start, x_end - 1] = 3 # top-right corner
    grid[y_end - 1, x_start] = 3 # bottom-left corner
    grid[y_end - 1, x_end - 1] = 3 # bottom-right corner

type Grid[T] = NDArray[(int, int), T] # type: ignore

def features(width, height, root, FREQ) -> Grid:
    grid: Grid = num.zeros((height, width), dtype=int)

    def populate(node, num):
        y, x = node.y, node.x
        dim = (y + node.height, x + node.width)
        match num:
            case 1: _shelves(grid, dim, (y, x))
            case 2: _pile(grid, dim, (y, x), num)
            case 3: 
                grid[y : dim[0], x : dim[1]] = num
                rects.append(("Block", y, x, dim[0], dim[1]))

        _pillars(grid, (y, x), dim)

    def fillRegions(node):
        if node.isLeaf():
            populate(node, _pickFreq(FREQ))
        else:
            for c in node.children: fillRegions(c)

    fillRegions(root)
    return grid