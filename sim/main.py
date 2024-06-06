from collections import namedtuple as data
from attrs import define, field

Coord = data("Coord", ["x", "y", "z"])
Signal = data("Signal", ["stren", "atten"])

@define
class BLE:
    ver: str = "5.3" 

@define
class Radio:
    mod_type: str = "QAM" 

@define
class WiFi:
    freq_band: str = "<6 GHz" 
    
@define
class Scene:
    space: Coord = Coord(100, 100, 10) # TODO


@define
class Controller:
    name: str
    comm: BLE|Radio|WiFi
    pos: Coord = field()
    orient: Coord = field()
    signal: Signal = field()

    @pos.default
    def genPos(self) -> Coord:
        return Coord(10, 10, 10) # TODO
    
    @orient.default
    def genOrient(self) -> Coord:
        return Coord(360, 360, 360) # TODO

    @signal.default
    def genSignal(self) -> Signal:
        return Signal(80, 5) # TODO


SCENE: Scene = Scene() 
N_NODES = 10; mesh = {}
for n in range(N_NODES):
    name = f"C{n+1:03}"
    mesh[name] = Controller(name, BLE())

for c in mesh.values(): # test
    print(f"Controller {c.name}:")
    print(f"\tType: {c.comm}")
    print(f"\tPosition: {c.pos}")
    print(f"\tFacing: {c.orient}")
    print(f"\tSignal: {c.signal}", end="\n\n")
