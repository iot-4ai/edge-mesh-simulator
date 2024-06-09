import carb
import omni
import click as args
from os.path import exists
from omni.isaac.kit import SimulationApp
from os.path import dirname as back, abspath as path

CONFIG = {"headless": False, "sync_loads": True}
ROOT = back(back(path(__file__)))

@args.command()
@args.option("--usd", "-u", type=str, required=True, help="Relative path to USD file")
@args.option("--nucleus", "-n", is_flag=True, help="Look in the Isaac Sim assets folder")
@args.option("--headless", "-h", is_flag=True, help="Run Isaac Sim headless")
def sim(usd, nucleus, headless):
	CONFIG["headless"] = headless
	app = SimulationApp(launch_config=CONFIG)

	from omni.isaac.core.utils.nucleus import get_assets_root_path as nucleus_root

	if nucleus:
		global ROOT; ROOT = nucleus_root()
		if not ROOT:
			carb.log_error("Isaac Sim assets folder not found. Is Nuclues running?")
			app.close()
			exit()
	scene = f"{ROOT}/{usd}"
	print(f'Loading stage from "{scene}"...')

	if not exists(scene):
		carb.log_error("Isaac Sim assets folder not found. Is Nuclues running?")
		app.close()
		exit()

	omni.usd.get_context().open_stage(scene)
	app.update(); app.update()

	print("Loading stage...")
	from omni.isaac.core.utils.stage import is_stage_loading

	while is_stage_loading():
		app.update()
	print("Done!")
	omni.timeline.get_timeline_interface().play()
	while app.is_running():
		app.update()	# Run in realtime (no step size)

	omni.timeline.get_timeline_interface().stop()
	app.close()

sim()