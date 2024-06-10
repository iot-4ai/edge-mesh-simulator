import b, bmesh
from random import random, uniform
from itertools import cycle
from sys import argv as args
from os import getcwd as cwd

X, Y, Z = 40, 20, 10

b.ops.object.select_all(action='SELECT')
b.ops.object.delete()
obstacles = b.data.objects.new("Obstacles", b.data.meshes.new("Obstacles") )
b.context.collection.objects.link(obstacles)

cMap = [
    (0.9176, 0.2627, 0.2078, 0.75), # red
    (0.2039, 0.6588, 0.3255, 0.75), # green
    (0.9843, 0.7373, 0.0157, 0.75), # yellow
    (0.2588, 0.5216, 0.9569, 0.75), # blue
    (0.6314, 0.2588, 0.9569, 0.75), # purple
    (0.1412, 0.7569, 0.8784, 0.75)  # cyan
]

mats = []
for i, c in enumerate(cMap):
    m = b.data.materials.new(name=f"M-{i:02}")
    m.diffuse_color = c
    mats.append(m)
mats = cycle(mats)

for x in range(X):
    for y in range(Y):
        if random() <= 0.2:
            b.ops.mesh.primitive_cube_add(size=1, location=(x+0.5, y+0.5, 0))
            cube = b.context.active_object
            height = uniform(1, Z/2)
            cube.scale[2] = height
            cube.location[2] += height / 2
            cube.data.materials.append(next(mats))

            cube.select_set(True)
            obstacles.select_set(True)
            b.context.view_layer.objects.active = obstacles
            b.ops.object.join()
            obstacles.select_set(False)

b.ops.mesh.primitive_cube_add(size=X)
walls = b.context.active_object # floor & walls
walls.location = (X / 2, Y / 2, Z/2)
walls.scale = (1+0.01, Y / X +0.01, Z / X)
walls.location[2] -= 0.01
b.context.active_object.name = "Walls"


# Remove top face of walls
bm = bmesh.new(); bm.from_mesh(walls.data)
bmesh.ops.delete(bm, \
    geom=[f for f in bm.faces if f.normal.z > 0.9], context='FACES')
bm.to_mesh(walls.data)
bm.free()

b.context.view_layer.update()

n = args[5] # 1st script arg
b.ops.export_scene.gltf(filepath=f"{cwd()}/scene-{n}")
