# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a DreamWaQ sim2sim implementation for the Unitree Go2 quadruped robot, based on the paper "Learning Robust Quadrupedal Locomotion With Implicit Terrain Imagination via Deep Reinforcement Learning". The project runs MuJoCo physics simulations on Windows using pre-trained reinforcement learning policies.

## Key Commands

### Running the Simulation
```bash
# Direct execution
python scripts/dreamwaq_go2.py

# Or using the batch file (runs in 'go2' conda environment)
start.bat
```

### Robot Control
- **Arrow keys**: Forward/backward (Up/Down) and left/right translation (Left/Right)
- **Q/E keys**: Left/right rotation
- **F1**: Stop keyboard listener

## Architecture

### Core Control Loop
The main simulation runs in `scripts/dreamwaq_go2.py` with a hierarchical control structure:

1. **High-level policy** (20 Hz, every 4 control steps):
   - Takes observation history (6 frames of 45-dimensional observations)
   - Outputs 12-dimensional action (target joint position offsets)
   - Policy loaded from `policies/dreamwaq/go2/policy_dwaq.pt` as a TorchScript model

2. **Low-level PD controller** (200 Hz, 0.005s timestep):
   - Converts policy actions to joint torques using position + velocity control
   - PD gains: kp=28, kd=0.7 for all 12 joints

### Observation Space (45 dimensions)
- `[0:3]` Command velocities (x, y, angular) - scaled by [2.0, 2.0, 0.5]
- `[3:6]` Angular velocity (scaled by 0.25)
- `[6:9]` Gravity orientation from quaternion
- `[9:21]` Joint position errors (current - default)
- `[21:33]` Joint velocities (scaled by 0.05)
- `[33:45]` Previous action

Frame stacking: 6 consecutive observations → 270 total dimensions

### Action Space
- 12-dimensional continuous actions (one per joint)
- Actions represent offsets from default standing pose
- Scaled by 0.25 before being added to default angles
- Default pose: hip=0.0, thigh=0.8, calf=-1.5 (all 4 legs)

### Configuration Structure
`Sim2simCfg` class contains nested configuration:
- `sim_config`: MuJoCo model path, timestep (0.005s), decimation (4x)
- `robot_config`: PD gains, default joint angles
- `env`: Observation/action dimensions, frame stack size
- `control`: Action scaling
- `normalization`: Observation scaling factors

### Key Files
- `scripts/dreamwaq_go2.py`: Main simulation loop and control logic
- `robotics/go2/scene_terrain.xml`: MuJoCo scene with terrain
- `robotics/go2/go2.xml`: Go2 robot model definition
- `policies/dreamwaq/go2/policy_dwaq.pt`: Pre-trained policy network
- `utils/keyboard_controller.py`: Keyboard input handler (threaded)
- `utils/easy_math.py`: Quaternion/gravity orientation utilities

### Dependencies
- MuJoCo 3.2.7 (physics simulation)
- PyTorch (policy inference)
- NumPy (numerical operations)
- pynput (keyboard input)
- scipy (rotation utilities)

Note: Several utility files in `utils/` are unused legacy code (datacollector, joystick_controller, mocap_collector, etc.)

### Coordinate Conventions
- Quaternions from MuJoCo: `[w, x, y, z]` format
- Gravity orientation calculated directly from quaternion using custom formula (not standard rotation matrix)
- Joint ordering: [FL_hip, FL_thigh, FL_calf, FR_hip, FR_thigh, FR_calf, RL_hip, RL_thigh, RL_calf, RR_hip, RR_thigh, RR_calf]
