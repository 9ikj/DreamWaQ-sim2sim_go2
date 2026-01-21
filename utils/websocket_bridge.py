import asyncio
import websockets
import json
import time
from typing import Optional, Callable
import threading

class WebSocketBridge:
    def __init__(self, uri: str):
        self.uri = uri
        self.websocket = None
        self.command_callback: Optional[Callable] = None
        self.running = False
        self.loop = None
        self.thread = None

    def set_command_callback(self, callback: Callable):
        self.command_callback = callback

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def _run_loop(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.run_until_complete(self._connect())

    async def _connect(self):
        while self.running:
            try:
                async with websockets.connect(self.uri) as websocket:
                    self.websocket = websocket
                    # Identify as simulation
                    await websocket.send(json.dumps({"type": "sim_connect"}))
                    print("Connected to WebSocket server")

                    # Receive commands
                    while self.running:
                        try:
                            data = await asyncio.wait_for(websocket.recv(), timeout=0.1)
                            msg = json.loads(data)
                            if msg.get("type") == "command" and self.command_callback:
                                self.command_callback(msg)
                        except asyncio.TimeoutError:
                            continue

            except Exception as e:
                print(f"WebSocket error: {e}")
                self.websocket = None
                await asyncio.sleep(1)

    def send_state(self, base_pos, base_quat, joint_pos, joint_vel=None):
        if self.websocket and self.loop:
            msg = {
                "type": "state",
                "timestamp": int(time.time() * 1000),
                "base_pos": base_pos.tolist(),
                "base_quat": base_quat.tolist(),
                "joint_pos": joint_pos.tolist(),
                "joint_vel": joint_vel.tolist() if joint_vel is not None else [0.0] * 12,
                "joint_names": ["FL_hip", "FL_thigh", "FL_calf", "FR_hip", "FR_thigh", "FR_calf",
                                "RL_hip", "RL_thigh", "RL_calf", "RR_hip", "RR_thigh", "RR_calf"]
            }
            asyncio.run_coroutine_threadsafe(
                self.websocket.send(json.dumps(msg)),
                self.loop
            )

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
