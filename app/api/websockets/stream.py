"""
WebSocket streaming endpoints for real-time agent observability.
"""
import asyncio
import json
import logging
from typing import List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

logger = logging.getLogger("condigence.websockets")

router = APIRouter(tags=["WebSockets"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")


ws_manager = ConnectionManager()


@router.websocket("/ws/agent-stream")
async def websocket_agent_stream(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        await websocket.send_text(json.dumps({"type": "CONNECTION_ESTABLISHED", "message": "Connected to Agent Stream"}))
        while True:
            data = await websocket.receive_text()
            # Echo heartbeat or custom commands
            await websocket.send_text(json.dumps({"type": "PONG", "payload": data}))
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
