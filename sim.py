from collections import namedtuple
from attrs import define, field
from random import uniform as randFloat, getrandbits as randBits
from ipaddress import IPv6Address
import matplotlib.pyplot as plot
from perlin_noise import PerlinNoise
from math import sqrt

Coord = namedtuple('Coord', ['x', 'y', 'z'])
type Grid = tuple[tuple[float, ...], ...]

@define
class Space:
    dim: Coord = Coord(100, 100, 10)
    obs: Grid = field()

    @obs.default
    def genObs(self) -> Grid:
        downscale = 10
        w, h = self.dim.x // downscale, self.dim.y // downscale
        fill = w if w < h else h # Fill space dim; noise is a square
        noise, zNoise = PerlinNoise(octaves=sqrt(fill)), PerlinNoise(octaves=sqrt(fill))

        obs = tuple(
            tuple(zNoise([row/fill, col/fill]) if noise([row/fill, col/fill]) > .1 else -1.0
             for col in range(w)) for row in range(h)
        )
        return tuple( # Upscale
            tuple(obs[row//downscale][col//downscale]
             for col in range(self.dim.x)) for row in range(self.dim.y)
        )

@define
class NodeBLE:
    ip: str = field()
    pos: dict[str, Coord] = field()
    orient: dict[str, Coord] = field()
    
    @ip.default
    def genIPv6(self) -> str:
        return str(IPv6Address(randBits(128))).upper()
    
    @pos.default
    def genPos(self) -> Coord:
        global SPACE
        if not SPACE: SPACE = Space()
        while True:
           pos = Coord(randFloat(0, SPACE.dim.x), randFloat(0, SPACE.dim.y), randFloat(0, SPACE.dim.z))
           if SPACE.obs[int(pos.y)][int(pos.x)]/2 + 0.5 <= pos.z/SPACE.dim.z: return pos # normalize

    @orient.default
    def genOrient(self) -> Coord:
        return Coord(randFloat(0, 360), randFloat(0, 360), randFloat(0, 360))

N_NODES = 50
SPACE: Space = Space(Coord(600, 200, 10)); nodes = []
for _ in range(N_NODES): nodes.append(NodeBLE())

plot.scatter(*zip(*[(n.pos.x, n.pos.y, n.pos.z*10) for n in nodes]), c='thistle')
plot.imshow(SPACE.obs, cmap='bone')
plot.show()
