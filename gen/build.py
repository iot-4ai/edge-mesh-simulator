from time import time
import numpy as np
import trimesh

def march(volume, colors):
    face_map = [
        ([0, 0, 0], [0, 0, 1], [0, 1, 1], [0, 1, 0], [-1, 0, 0]), # left
        ([1, 0, 0], [1, 1, 0], [1, 1, 1], [1, 0, 1], [1, 0, 0]),  # right
        ([0, 0, 0], [1, 0, 0], [1, 0, 1], [0, 0, 1], [0, -1, 0]), # bottom
        ([0, 1, 0], [0, 1, 1], [1, 1, 1], [1, 1, 0], [0, 1, 0]),  # top
        ([0, 0, 0], [0, 1, 0], [1, 1, 0], [1, 0, 0], [0, 0, -1]), # back
        ([0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1], [0, 0, 1])   # front
    ]

    vertices, triangles, normals, mats = [], [], [], []
    for (x, y, z), voxel in np.ndenumerate(volume):
        if voxel:
            for face in face_map:
                # face[4]: normal vector to face
                nx, ny, nz = x + face[4][0], y + face[4][1], z + face[4][2]
                if ( # interior face
                    0 <= nx < volume.shape[0] and 0 <= ny < volume.shape[1] and 0 <= nz < volume.shape[2]
                    and volume[nx, ny, nz]
                ): continue

                v = len(vertices)
                vertices.extend([(x + dx, y + dy, z + dz) for (dx, dy, dz) in face[:4]])
                triangles.extend([[v, v + 1, v + 2], [v, v + 2, v + 3]])
                normals.extend([face[4]]*4)
                mats.extend([colors[x, y, z]]*4)

    return np.array(vertices), np.array(triangles), np.array(normals), np.array(mats)

X, Y, Z, N = 50, 20, 100, 100000
randPoints = np.column_stack([np.random.choice(dim, size=N) for dim in (X, Y, Z)])
randColors = np.random.rand(N, 3)
volume = np.zeros((X, Y, Z), dtype=bool)
colors = np.zeros((X, Y, Z, 3))

for point, color in zip(randPoints, randColors):
    x, y, z = point
    volume[x, y, z] = True
    colors[x, y, z] = color

i = time()
print("Marching...")
args = march(volume, colors)

print("Making mesh...")
mesh = trimesh.Trimesh(*args)

# Export to GLB
print("Exporting...")
mesh.export("test.glb")
f = time()
# mesh.show()

print(f"Completed in {f - i:.2f}s")
