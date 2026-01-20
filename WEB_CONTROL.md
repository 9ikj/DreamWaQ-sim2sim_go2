# Web-Based Go2 Robot Control

## Overview
This system provides a web interface to visualize and control the Go2 robot simulation in real-time using WebSocket communication.

## Architecture
- **FastAPI WebSocket Server**: Runs independently on port 8000
- **Simulation**: Connects as WebSocket client, displays in MuJoCo viewer
- **Web Browser**: Connects as WebSocket client, displays 3D visualization with Three.js
- Both MuJoCo viewer and web interface display robot simultaneously
- Keyboard control only from web interface

## Installation

1. Install web dependencies:
```bash
pip install -r requirements_web.txt
```

## Usage

### Step 1: Start the WebSocket Server
Open a terminal and run:
```bash
python server/websocket_server.py
```
Or use the batch file:
```bash
start_server.bat
```

The server will start on `http://localhost:8000`

### Step 2: Start the Simulation
Open another terminal and run:
```bash
python scripts/dreamwaq_go2_web.py
```
Or use the batch file:
```bash
start_web.bat
```

This will:
- Connect to the WebSocket server
- Open the MuJoCo viewer window
- Start sending robot state at 20Hz

### Step 3: Open Web Interface
Open your browser and navigate to:
```
http://localhost:8000
```

You should see:
- 3D visualization of the robot
- Control panel with status and velocity commands
- FPS counter

## Controls

Use keyboard in the **web browser** (not MuJoCo viewer):
- **Arrow Up/Down**: Move forward/backward
- **Arrow Left/Right**: Strafe left/right
- **Q/E**: Rotate left/right

## Data Flow

```
Web Browser (Keyboard) → WebSocket Server → Simulation
Simulation (Joint States) → WebSocket Server → Web Browser (3D View)
```

## Troubleshooting

### "Connection refused" error
- Make sure the WebSocket server is running first
- Check that port 8000 is not in use

### Robot not moving
- Verify keyboard focus is on the web browser window
- Check the control panel shows velocity changes when pressing keys
- Verify "Status: Connected" in the web interface

### Web page shows "Disconnected"
- Ensure the simulation is running
- Check the server terminal for error messages
- Try refreshing the browser page

## Files

- `server/websocket_server.py` - FastAPI WebSocket server
- `server/static/index.html` - Web interface with Three.js
- `scripts/dreamwaq_go2_web.py` - Modified simulation with WebSocket client
- `utils/websocket_bridge.py` - WebSocket communication utilities
- `start_server.bat` - Batch file to start server
- `start_web.bat` - Batch file to start simulation
