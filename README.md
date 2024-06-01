# Edge Mesh Simulator
Simulation of mesh network communications for BLE, 5G, etc.

## Setup (Linux)

[Omniverse + Isaac Sim installation](https://docs.omniverse.nvidia.com/isaacsim/latest/installation/install_workstation.html). Some notes:
- On Fedora: ensure `gnome-terminal` and `libxcrypt-compat` are installed.
- Isaac Sim will install to `~/.local/share/ov/pkg/isaac_sim-<ver>`; for convenience, set this path as an environment variable (how about `$SIM`?)
<!-- - [Install Nucleus](https://docs.omniverse.nvidia.com/nucleus/latest/workstation/installation.html) to `edge-mesh-simulator/nucleus`. -->
- If login to your local Nucleus service fails, try 'admin' in both fields

### Scene Generator
- Run `$SIM/python.sh scene/gen.py`, optionally with arguments (see `--help`)