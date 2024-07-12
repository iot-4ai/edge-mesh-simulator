import numpy as num
import trimesh

KINDS = {
    0: "empty",
    1: "shelf",
    2: "pile",
    3: "wall",
}

COL = {"shelf": (0.8039, 0.5216, 0.24706), "pile": (0.62745, 0.32157, 0.17647), "wall": (0.6, 0.6, 0.6)}

def march(volume, colors, callback):
    faceMap = [
        ([0, 0, 0], [0, 0, 1], [0, 1, 1], [0, 1, 0], [-1, 0, 0]), # left
        ([1, 0, 0], [1, 1, 0], [1, 1, 1], [1, 0, 1], [1, 0, 0]),  # right
        ([0, 0, 0], [1, 0, 0], [1, 0, 1], [0, 0, 1], [0, -1, 0]), # bottom
        ([0, 1, 0], [0, 1, 1], [1, 1, 1], [1, 1, 0], [0, 1, 0]),  # top
        ([0, 0, 0], [0, 1, 0], [1, 1, 0], [1, 0, 0], [0, 0, -1]), # back
        ([0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1], [0, 0, 1])   # front
    ]

    vertices, triangles, normals, mats = [], [], [], []
    count, total = 0, num.prod(volume.shape)

    for (x, y, z), voxel in num.ndenumerate(volume):
        if voxel:
            for face in faceMap:
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

        count += 1
        if count % 1000 == 0:
            progress = count/total
            callback(progress)

    return num.array(vertices), num.array(triangles), num.array(normals), num.array(mats)

def build(cloud, out, callback):
    colors = num.zeros((*cloud.shape, 3))
    for kind, color in COL.items():
        i = list(KINDS.values()).index(kind)
        colors[cloud == i] = color

    callback(0.0, "Marching cubes")
    vertices, triangles, normals, colors = march(cloud, colors, lambda p: callback(p*0.8))

    callback(0.8, "Creating mesh")
    mesh = trimesh.Trimesh(vertices=vertices, faces=triangles, vertex_normals=normals, vertex_colors=colors)

    callback(0.9, "Exporting")
    mesh.export(f"{out}/scene.glb")

    callback(1.0, "Finished")
