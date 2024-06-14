import matplotlib.pyplot as plot
from matplotlib.patches import Rectangle
from random import uniform, getrandbits as choose
from attrs import define, Factory as new
from itertools import cycle

@define
class Partition:
    x: int
    y: int
    width: int
    height: int
    children: list = new(list)

    def isLeaf(self):
        return len(self.children) == 0

def cutHori(node):
    if node.height > MIN:
        cutY = int(uniform(node.y, node.y + node.height))

        topHeight = cutY - node.y -1
        botHeight = node.height - (cutY - node.y)-1
        if topHeight > CUTOFF:
            node.children.append(Partition(node.x, node.y, node.width, topHeight))
        if botHeight > CUTOFF:
            node.children.append(Partition(node.x, cutY+1, node.width, botHeight))

def cutVert(node):
    if node.width > MIN:
        cutX = int(uniform(node.x, node.x + node.width))

        leftWidth = cutX - node.x -1
        rightWidth = node.width - (cutX - node.x)-1
        if leftWidth > CUTOFF:
            node.children.append(Partition(node.x, node.y, leftWidth, node.height))
        if rightWidth > CUTOFF:
            node.children.append(Partition(cutX+1, node.y, rightWidth, node.height))

def divide(node, depth=0):
    if node.width <= MIN and node.height <= MIN:
        return  # No need to divide further

    # Randomly decide to cut horizontally or vertically
    if node.width == W: cutVert(node)
    elif node.height == D: cutHori(node)
    else:
        cutHori(node) if choose(1) else cutVert(node)

    for child in node.children: # Recursively parition
        divide(child, depth + 1)

def buildAQT(width, height):
    root = Partition(0, 0, width, height)
    divide(root)
    return root

def printAQT(node, depth=0):
    print(
        " " * depth * 2
        + f"Node: x={node.x}, y={node.y}, width={node.width}, height={node.height}"
    )
    for child in node.children:
        printAQT(child, depth + 1)

def drawAQT(ax, node):
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
            drawAQT(ax, child)

def getDeepest(node, depth=0):
    if node.isLeaf(): return depth
    return max(getDeepest(child, depth + 1) for child in node.children)

# defaults
COL = cycle("rgbcmk")
W, D, MIN = 150, 200, 30
CUTOFF = MIN/4

def setup(AQT):
    # toolbar = plot.get_current_fig_manager().toolbar
    # [toolbar.removeAction(x) for x in toolbar.actions()]

    fig, ax = plot.subplots(1, figsize=(8, 8))
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_xlabel(f"W = {W}"); ax.set_ylabel(f"D = {D}")
    ax.set_xlim(0, AQT.width); ax.set_ylim(0, AQT.height)
    plot.gca().invert_yaxis()
    ax.set_aspect("equal")
    return fig, ax

def run(AQT, debug=False, close=True):
    if debug: printAQT(AQT)
    fig, ax = setup(AQT)

    drawAQT(ax, AQT)
    plot.show(block=False)
    plot.pause(1)
    if close: plot.close()

def save(AQT, filename=None):
    fig, ax = setup(AQT)
    drawAQT(ax, AQT)
    if filename: plot.savefig(filename)
