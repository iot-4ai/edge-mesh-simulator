# Edge Mesh Simulator
Simulation of mesh network communications for BLE, 5G, etc.

## Setup (Linux)

[Omniverse + Isaac Sim installation](https://docs.omniverse.nvidia.com/isaacsim/latest/installation/install_workstation.html). Some notes:
- On Fedora: ensure `gnome-terminal` and `libxcrypt-compat` are installed.
- Isaac Sim will install to `~/.local/share/ov/pkg/isaac_sim-<ver>`; for convenience, set this path as an environment variable (how about `$ISAAC`?)
- I've also set one for the workspace root (mine is `$SIM`)
<!-- - [Install Nucleus](https://docs.omniverse.nvidia.com/nucleus/latest/workstation/installation.html) to `edge-mesh-simulator/nucleus`. -->
- If login to your local Nucleus service fails, try 'admin' in both fields

### Workflow
```sh
cd $ISAAC
# Generate scene:
./python.sh "$SIM/scene/gen.py" # optionally with arguments (see --help)
# ???
./python.sh "$SIM/sim/run.py" -u "scene/scene-1.usd" # see --help
