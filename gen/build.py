from multiprocessing import Pool, cpu_count, Manager
from functools import partial
import numpy as num
import trimesh

KINDS = {
    0: "empty",
    1: "shelf",
    2: "pile",
    3: "wall",
}

COL = {"shelf": (0.8039, 0.5216, 0.24706), "pile": (0.62745, 0.32157, 0.17647), "wall": (0.6, 0.6, 0.6)}

vertices, faces, normals, colors = [], [], [], []
def march(stripData, status):
    ID, (strip, (x0, y0, z0)) = stripData
    vertices, faces, normals, colors = [], [], [], []
    faceMap = [
        ([0, 0, 0], [0, 0, 1], [0, 1, 1], [0, 1, 0], [-1, 0, 0]), # left
        ([1, 0, 0], [1, 1, 0], [1, 1, 1], [1, 0, 1], [1, 0, 0]),  # right
        ([0, 0, 0], [1, 0, 0], [1, 0, 1], [0, 0, 1], [0, -1, 0]), # bottom
        ([0, 1, 0], [0, 1, 1], [1, 1, 1], [1, 1, 0], [0, 1, 0]),  # top
        ([0, 0, 0], [0, 1, 0], [1, 1, 0], [1, 0, 0], [0, 0, -1]), # back
        ([0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1], [0, 0, 1])   # front
    ]

    for (x, y, z), pos in num.ndenumerate(strip):
        if pos:
            for face in faceMap:
                neighbor = x + face[4][0], y + face[4][1], z + face[4][2]  # face[4]: normal to face
                if all(0 <= n < dim for n, dim in zip(neighbor, strip.shape)) and strip[neighbor]:
                    continue  # interior face

                v = len(vertices)
                vertices.extend([(x + dx + x0, y + dy + y0, z + dz + z0) for (dx, dy, dz) in face[:4]])
                faces.extend([[v, v + 1, v + 2], [v, v + 2, v + 3]])
                normals.extend([face[4]]*4)
                colors.extend([COL.get(KINDS[pos], (0, 0, 0))]*4)

    status[ID] = 1
    return vertices, faces, normals, colors

def process(cloud, callback):
    cores = cpu_count()
    stripSize = max(1, cloud.shape[0] // cores)

    strips = []
    for i in range(0, cloud.shape[0], stripSize):
        strip = cloud[i:i+stripSize]
        strips.append((strip, (i, 0, 0)))

    with Manager() as manager:
        status = manager.dict()

        with Pool(cores) as pool:
            fn = partial(march, status=status)
            results = pool.map_async(fn, enumerate(strips))

            while not results.ready():
                completed = sum(status.values())
                callback(completed / cores * 0.8)
                results.wait(0.1)

            results = results.get()

    offset = 0
    for _vertices, _faces, _normals, _colors in results:
        vertices.extend(_vertices)
        faces.extend([[f[0] + offset, f[1] + offset, f[2] + offset] for f in _faces])
        normals.extend(_normals)
        colors.extend(_colors)
        offset += len(_vertices)

def build(cloud, out, callback):
    callback(0.0, "Marching cubes")
    process(cloud, lambda p: callback(p*0.8))

    callback(0.8, "Creating mesh")
    mesh = trimesh.Trimesh(vertices, faces, vertex_normals=normals, vertex_colors=colors)

    callback(0.9, "Exporting")
    mesh.export(f"{out}/scene.glb")

    callback(1.0, "Finished")
