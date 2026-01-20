@echo off
set PYTHONPATH=%~dp0
uv run python server\websocket_server.py