import bpy
import bmesh
import numpy as num
from mathutils import Vector, Matrix
from time import time

# Cleanup scene
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()

# Obtain a reference to the mesh
mesh = bpy.data.meshes.new("Obstacles")
obj = bpy.data.objects.new("Obstacles", mesh)
bpy.context.collection.objects.link(obj)

bm = bmesh.new()

path = "/tmp/tmpr5am5ojs"
grid = num.load(path)

start = time()
# Iterate over your grid and create cubes at the non-empty locations
rows, cols = grid["k"].shape
for x in range(rows):
    print(f"{x/rows:.2%}")
    for y in range(cols):
        if grid["k"][y, x] == "empty": continue
        height = grid["h"][y, x]

        bmesh.ops.create_cube(bm, size=1.0, matrix=Matrix.Translation((x + 0.5, y + 0.5, 0)))

        new = bm.verts[-8:]  # Get the last 8 vertices (cube)
        bmesh.ops.scale(bm, vec=(1, 1, height), verts=new)
        bmesh.ops.translate(bm, verts=new, vec=Vector((0.0, 0.0, height / 2)))
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.1)


# Convert the BMesh to a mesh
bm.to_mesh(mesh)
bm.free()  # Always remember to free the BMesh to prevent memory leaks

# Update the mesh with new geometry
mesh.update()

end = time()
print(f"Took {end-start:.2f}s")

