import bpy as b
from sys import argv as args
import numpy as num
from time import time
from sys import stdout

"""
Uses heights and kinds grids to build each chunk by stretching cubes.

!! requires path to scene data (.npz) and output directory as arguments.
exports to <out>/scene.glb (glTF binary)

See main.py for usage
"""

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

# Make materials as per color dict
mats = {c: b.data.materials.new(name=c) for c in COL}
for c, m in mats.items(): m.diffuse_color = COL[c]

i = args.index("--") + 1
data, out = args[i:i+2]
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
        if cube: # scale to height, apply mat:
            cube.scale[2] = height
            cube.location[2] += height / 2
            cube.data.materials.append(mats[KINDS[grid["k"][y, x]]]) # type: ignore
            cube.select_set(True)

        # Combine into one mesh
        obstacles.select_set(True)
        b.context.view_layer.objects.active = obstacles
        b.ops.object.join()
        obstacles.select_set(False)

# Mesh cleanup (deduplicate vertices)
b.ops.object.editmode_toggle()
b.ops.mesh.select_all(action="SELECT")
b.ops.mesh.remove_doubles()
b.ops.object.editmode_toggle()

b.context.view_layer.update()

b.ops.export_scene.gltf(filepath=f"{out}/scene")
print("1.0") # done
