from os import path
import click as args
import numpy as num

from omni.isaac.kit import SimulationApp

PATH = path.dirname(path.abspath(__file__))
TILE_CONF = PATH + "/config/tile_config.yaml"
TILE_GEN  = PATH + "/config/tile_generation.yaml"
CONSTRS   = PATH + "/config/constraints.yaml"

@args.command()
@args.option("--make", type=int, default=1, help="Number of scenes to generate")
@args.option("--rows", type=int, default=11, help="Effective scene width in tiles")
@args.option("--cols", type=int, default=15, help="Effective scene depth in tiles")
@args.option("--show", is_flag=True, help="Show the grid solving process")
@args.option("--seed", type=int)
def gen(make, rows, cols, show, seed):
	app = SimulationApp()

	from omni.isaac.core import World
	from omni.isaac.core.utils.stage import close_stage
	from omni.isaac.scene_blox.generation.scene_generator import SceneGenerator
	from omni.isaac.scene_blox.grid_utils import config
	from omni.isaac.scene_blox.grid_utils.grid import Grid
	from omni.isaac.scene_blox.grid_utils.grid_constraints import GridConstraints
	from omni.isaac.scene_blox.grid_utils.tile import tile_loader
	from omni.isaac.scene_blox.grid_utils.tile_superposition import TileSuperposition

	tiles, weights = tile_loader(TILE_CONF)
	constrs = GridConstraints.from_yaml(CONSTRS, rows, cols) if CONSTRS else None
	superpos = TileSuperposition(tiles, weights)

	config.GlobalRNG().rng = num.random.default_rng(seed)

	generator = SceneGenerator(TILE_GEN, False) # No collision checking

	grid = Grid(rows, cols, superpos)
	world = World(stage_units_in_meters=1.0)
	for n in range(make):
		success = False
		for tries in range(50): # MAX 50 tries
			if grid.solve(constrs, show):
				success = True; break
			grid.reset(superpos)
			if constrs: constrs.reset()
		if not success:
			print("Couldn't solve grid"); continue
		# if success:
		print(f"Grid {n+1} solved in {tries+1} tr{'ies' if tries else 'y'}")
		out_path = path.join(PATH, f"scene-{n+1}.usd")
		world.reset()
		generator.generate_scene(grid, world, out_path)
		grid.reset(superpos)
		close_stage(); world.clear_instance()

	app.close()

gen()
