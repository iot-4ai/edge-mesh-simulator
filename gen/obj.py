import bpy as b, bmesh
from random import random, uniform
from itertools import cycle
from sys import argv as args
import numpy as num
from subprocess import getoutput as run
from time import time

b.ops.object.select_all(action="SELECT")
b.ops.object.delete()
obstacles = b.data.objects.new("Obstacles", b.data.meshes.new("Obstacles") )
b.context.collection.objects.link(obstacles)

colors = {
    "shelf": (0.8039, 0.5216, 0.24706, 1),
    "pile": (0.62745, 0.32157, 0.17647, 1)
}

mats = {c: b.data.materials.new(name=c) for c in colors}
for c, m in mats.items(): m.diffuse_color = colors[c]

# path = args[5] # 1st arg
# run(f"notify-send {path}")
path = "/tmp/tmpr5am5ojs"

grid = num.load(path)
rows, cols = grid["k"].shape

start = time()
for x in range(rows):
    print(f"{x/rows:.2%}")
    for y in range(cols):
        if grid["k"][y, x] == "empty": continue
        b.ops.mesh.primitive_cube_add(size=1, location=(x+0.5, y+0.5, 0))
        cube = b.context.active_object
        height = grid["h"][y, x]
        cube.scale[2] = height
        cube.location[2] += height / 2
        # cube.data.materials.append(next(mats))

        cube.select_set(True)
        obstacles.select_set(True)
        b.context.view_layer.objects.active = obstacles
        b.ops.object.join()
        obstacles.select_set(False)

# b.ops.mesh.primitive_cube_add(size=X)
# walls = b.context.active_object # floor & walls
# walls.location = (X / 2, Y / 2, Z/2)
# walls.scale = (1+0.01, Y / X +0.01, Z / X)
# walls.location[2] -= 0.01
# b.context.active_object.name = "Walls"


# # Remove top face of walls
# bm = bmesh.new(); bm.from_mesh(walls.data)
# bmesh.ops.delete(bm, \
#     geom=[f for f in bm.faces if f.normal.z > 0.9], context='FACES')
# bm.to_mesh(walls.data)
# bm.free()

b.context.view_layer.update()

# n = args[5] # 1st script arg
# b.ops.export_scene.gltf(filepath=f"{cwd()}/scene-{n}")

end = time()

print(f"Took {end-start:.2f}s")
