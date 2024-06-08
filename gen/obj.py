import bpy, bmesh
from random import random, uniform

X, Y, Z = 40, 20, 10

obstacles = bpy.data.objects.new("Obstacles", bpy.data.meshes.new("Obstacles") )
bpy.context.collection.objects.link(obstacles)

for x in range(X):
    for y in range(Y):
        if random() <= 0.5:
            bpy.ops.mesh.primitive_cube_add(size=1, location=(x+0.5, y+0.5, 0))
            cube = bpy.context.active_object
            height = uniform(1, Z)
            cube.scale[2] = height
            cube.location[2] += height / 2

            cube.select_set(True)
            obstacles.select_set(True)
            bpy.context.view_layer.objects.active = obstacles
            bpy.ops.object.join()
            obstacles.select_set(False)

bpy.ops.mesh.primitive_cube_add(size=X)
box = bpy.context.active_object # floor & walls
box.location = (X / 2, Y / 2, Z/2)
box.scale = (1, Y / X, Z / X)

# Remove top face of box
bm = bmesh.new(); bm.from_mesh(box.data)
bmesh.ops.delete(bm, \
    geom=[f for f in bm.faces if f.normal.z > 0.9], context='FACES')
bm.to_mesh(box.data)
bm.free()

bpy.context.view_layer.update()