from fastapi import WebSocket
from typing import Any
import json
import structlog

logger = structlog.get_logger()


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info("ws_client_connected", total=len(self.active_connections))

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info("ws_client_disconnected", total=len(self.active_connections))

    async def broadcast(self, event: str, data: dict[str, Any]):
        message = json.dumps({"event": event, "data": data})
        stale = []
        for conn in self.active_connections:
            try:
                await conn.send_text(message)
            except Exception:
                stale.append(conn)
        for conn in stale:
            self.disconnect(conn)


manager = ConnectionManager()
