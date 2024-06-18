import bpy as b, bmesh
from random import random, uniform
from itertools import cycle
from sys import argv as args
import numpy as num
from time import time
from sys import stdout

b.ops.object.select_all(action="SELECT")
b.ops.object.delete()
obstacles = b.data.objects.new("Obstacles", b.data.meshes.new("Obstacles") )
b.context.collection.objects.link(obstacles)

KINDS = {
    0: "empty",
    1: "shelf",
    2: "pile",
    3: "wall",
}

COL = {
    "shelf": (0.8039, 0.5216, 0.24706, 1),
    "pile": (0.62745, 0.32157, 0.17647, 1),
    "wall": (0.6, 0.6, 0.6, 1)
}

mats = {c: b.data.materials.new(name=c) for c in COL}
for c, m in mats.items(): m.diffuse_color = COL[c]

data = args[5] # 1st arg
grid = num.load(data)
cols, rows = grid["k"].shape

start = time()
for x in range(rows):
    print(f"{x/rows:.2f}")
    stdout.flush()

    for y in range(cols):
        if KINDS[grid["k"][y, x]] == "empty": continue
        b.ops.mesh.primitive_cube_add(size=1, location=(y+0.5, x+0.5, 0))
        height = grid["h"][y, x]
        cube = b.context.active_object
        if cube:
            cube.scale[2] = height
            cube.location[2] += height / 2
            cube.data.materials.append(mats[KINDS[grid["k"][y, x]]]) # type: ignore

            cube.select_set(True)
        obstacles.select_set(True)
        b.context.view_layer.objects.active = obstacles
        b.ops.object.join()
        obstacles.select_set(False)

b.ops.object.editmode_toggle()
b.ops.mesh.select_all(action="SELECT")
b.ops.mesh.remove_doubles()
b.ops.object.editmode_toggle()

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

out = args[6]
b.ops.export_scene.gltf(filepath=f"{out}/scene")
print("1.0") # done