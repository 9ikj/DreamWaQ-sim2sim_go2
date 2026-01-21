# DreamWaQ: sim2sim_go2

## Description
This repo contains implementation of the paper [Learning Robust Quadrupedal Locomotion With Implicit Terrain Imagination via Deep Reinforcement Learning](https://arxiv.org/abs/2301.10602)

This project can run on the Windows system. It is recommended to use Mujoco 3.2.7

There are some files in utils that are not actually used – you can ignore them, but some of the contents might be useful to you.

## Sincerely thank the original authors of the repositories:

1. https://github.com/Manaro-Alpha/DreamWaQ
2. https://github.com/ShengqianChen/DreamWaQ_Go2W 
3. https://github.com/LucienJi/MetaRobotics
4. https://github.com/InternRobotics/HIMLoco
5. https://github.com/yusongmin1/My_unitree_go2_gym

## Installation

### Option 1: Full Installation (with Web Interface)
```bash
# Create a Python virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows:
.venv\Scripts\activate
# On Linux/Mac:
# source .venv/bin/activate

# Install all dependencies
pip install -r requirements.txt

# For CUDA support (recommended for faster inference):
pip install torch --index-url https://download.pytorch.org/whl/cu118
```

### Option 2: Minimal Installation (Keyboard Control Only)
```bash
# Create a Python virtual environment
python -m venv .venv

# Activate the virtual environment
.venv\Scripts\activate

# Install minimal dependencies
pip install -r requirements-minimal.txt
```

## How to Use

### Basic Simulation (Keyboard Control)
```bash
# Run directly
python scripts/dreamwaq_go2.py

# Or use the batch file
start.bat
```

**Controls:**
- Arrow keys: Forward/backward and left/right translation
- Q/E keys: Left/right rotation
- F1: Stop keyboard listener

### Web Interface (Browser + Gamepad Support)
```bash
# Start all components at once
start_all.bat

# Or start components separately:
# 1. Start WebSocket server
start_server.bat

# 2. Start simulation
start_web.bat

# 3. Open browser to http://localhost:8000
```

**Controls:**
- **Keyboard**: WASD or arrow keys for movement, Q/E for rotation
- **Gamepad**: Left stick for movement, right stick for rotation

See [WEB_CONTROL.md](WEB_CONTROL.md) for detailed web interface documentation.

## Requirements

### Core Dependencies
- Python 3.8+
- MuJoCo 3.2.7
- PyTorch 2.0+
- NumPy 1.24+
- SciPy 1.10+
- pynput 1.7.6+

### Web Interface Dependencies (Optional)
- FastAPI 0.104+
- Uvicorn 0.24+
- WebSockets 12.0+
