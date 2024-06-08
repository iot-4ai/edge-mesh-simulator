import numpy as np
import matplotlib.pyplot as plot
from matplotlib.patches import Rectangle
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
        midY = node.y + node.height / 2
        rangeY = node.height / 4  # Define a range around the middle for randomness
        cutY = int(
            np.clip(
                midY + np.random.uniform(-rangeY, rangeY),
                node.y + MIN,
                node.y + node.height - MIN,
            )
        )

        topHeight = cutY - node.y -1
        botHeight = node.height - (cutY - node.y)-1 
        if topHeight > MIN/3:
            node.children.append(Partition(node.x, node.y, node.width, topHeight))
        if botHeight > MIN/3:
            node.children.append(Partition(node.x, cutY+1, node.width, botHeight))

def cutVert(node):
    if node.width > MIN:
        midX = node.x + node.width / 2
        rangeX = node.width / 4  # Define a range around the middle for randomness
        cutX = int(
            np.clip(
                midX + np.random.uniform(-rangeX, rangeX),
                node.x + MIN,
                node.x + node.width - MIN,
            )
        )
        leftWidth = cutX - node.x -1
        rightWidth = node.width - (cutX - node.x)-1
        if leftWidth > MIN/3:
            node.children.append(Partition(node.x, node.y, leftWidth, node.height))
        if rightWidth > MIN/3:
            node.children.append(Partition(cutX+1, node.y, rightWidth, node.height))

def divide(node, depth=0):
    if node.width <= MIN and node.height <= MIN:
        return  # No need to divide further

    # Randomly decide to cut horizontally or vertically
    if np.random.rand() > 0.5: cutHori(node)
    else: cutVert(node)

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
            facecolor=next(colors)
        )
        ax.add_patch(rect)
    else:
        for child in node.children:
            drawAQT(ax, child)

def getDeepest(node, depth=0):
    if node.isLeaf(): return depth
    return max(getDeepest(child, depth + 1) for child in node.children)

width, height, MIN = 150, 200, 20
AQT = buildAQT(width, height)

colors = cycle('rgbcmk')
printAQT(AQT)

fig, ax = plot.subplots(1, figsize=(8, 8))
ax.set_xticks([]); ax.set_yticks([])
ax.set_xlim(0, width); ax.set_ylim(0, height)
ax.set_aspect("equal")

toolbar = plot.get_current_fig_manager().toolbar
[toolbar.removeAction(x) for x in toolbar.actions()]

drawAQT(ax, AQT)
plot.gca().invert_yaxis()
plot.show()
