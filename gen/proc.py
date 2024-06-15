import matplotlib.pyplot as plot
from matplotlib.patches import Rectangle
from random import uniform, getrandbits as choose
from attrs import define, Factory as new
from itertools import cycle

COL = cycle("rgbcmk")
W, D, MIN = 150, 200, 30
CUTOFF = MIN/4

@define
class Partition:
    x: int
    y: int
    width: int
    height: int
    children: list = new(list)

    def isLeaf(self):
        return len(self.children) == 0

def _cutHori(node):
    if node.height > MIN:
        cutY = int(uniform(node.y, node.y + node.height))

        topHeight = cutY - node.y -1
        botHeight = node.height - (cutY - node.y)-1
        if topHeight > CUTOFF:
            node.children.append(Partition(node.x, node.y, node.width, topHeight))
        if botHeight > CUTOFF:
            node.children.append(Partition(node.x, cutY+1, node.width, botHeight))

def _cutVert(node):
    if node.width > MIN:
        cutX = int(uniform(node.x, node.x + node.width))

        leftWidth = cutX - node.x -1
        rightWidth = node.width - (cutX - node.x)-1
        if leftWidth > CUTOFF:
            node.children.append(Partition(node.x, node.y, leftWidth, node.height))
        if rightWidth > CUTOFF:
            node.children.append(Partition(cutX+1, node.y, rightWidth, node.height))

def _divide(node, depth=0):
    if node.width <= MIN and node.height <= MIN:
        return  # No need to divide further

    # Randomly decide to cut horizontally or vertically
    if node.width == W: _cutVert(node)
    elif node.height == D: _cutHori(node)
    else:
        _cutHori(node) if choose(1) else _cutVert(node)

    for child in node.children: # Recursively parition
        _divide(child, depth + 1)

def _printRegions(node, depth=0):
    print(
        " " * depth * 2
        + f"Node: x={node.x}, y={node.y}, width={node.width}, height={node.height}"
    )
    for child in node.children:
        _printRegions(child, depth + 1)

def _drawRegions(ax, node):
    if node.isLeaf():
        rect = Rectangle(
            (node.x, node.y),
            node.width,
            node.height,
            edgecolor="none",
            facecolor=next(COL)
        )
        ax.add_patch(rect)
    else:
        for child in node.children:
            _drawRegions(ax, child)

def genRegions(width, height, show=False, save=False, debug = False):
    AQT = Partition(0, 0, width, height)
    _divide(AQT)
    if show: _showFig(AQT)
    if save: _saveFig(AQT)
    if debug: _printRegions(AQT)
    return AQT

def _figSetup(AQT):
    _, ax = plot.subplots(1, figsize=(8, 8))
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_xlabel(f"W = {W}"); ax.set_ylabel(f"D = {D}")
    ax.set_xlim(0, AQT.width); ax.set_ylim(0, AQT.height)
    ax.set_aspect("equal")
    plot.gca().invert_yaxis()
    plot.tight_layout()
    return ax

def _showFig(AQT):
    ax = _figSetup(AQT)
    _drawRegions(ax, AQT)
    plot.show(block=False)

def _saveFig(AQT, name=None):
    ax = _figSetup(AQT)
    _drawRegions(ax, AQT)
    if not name: name = "fig"
    plot.savefig(name)
