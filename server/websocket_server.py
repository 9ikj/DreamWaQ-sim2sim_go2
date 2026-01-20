from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import json
import asyncio
from typing import Set
import uvicorn

app = FastAPI()

# Connected clients
web_clients: Set[WebSocket] = set()
sim_client: WebSocket = None

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global sim_client
    await websocket.accept()

    try:
        # First message identifies client type
        data = await websocket.receive_text()
        msg = json.loads(data)

        if msg.get("type") == "sim_connect":
            sim_client = websocket
            print("Simulation connected")

            # Handle simulation messages
            while True:
                data = await websocket.receive_text()
                msg = json.loads(data)

                # Broadcast state to all web clients
                if msg.get("type") == "state":
                    disconnected = set()
                    for client in web_clients:
                        try:
                            await client.send_text(data)
                        except:
                            disconnected.add(client)
                    web_clients.difference_update(disconnected)

        else:
            # Web client
            web_clients.add(websocket)
            print(f"Web client connected. Total: {len(web_clients)}")

            # Handle web client messages
            while True:
                data = await websocket.receive_text()
                msg = json.loads(data)

                # Forward commands to simulation
                if msg.get("type") == "command" and sim_client:
                    try:
                        await sim_client.send_text(data)
                    except:
                        pass

    except WebSocketDisconnect:
        if websocket == sim_client:
            sim_client = None
            print("Simulation disconnected")
        else:
            web_clients.discard(websocket)
            print(f"Web client disconnected. Total: {len(web_clients)}")

# Serve static files
app.mount("/static", StaticFiles(directory="server/static"), name="static")
app.mount("/assets", StaticFiles(directory="robotics/go2/assets"), name="assets")

@app.get("/")
async def get_index():
    return FileResponse("server/index.html")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
