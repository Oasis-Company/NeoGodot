import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, Set, Optional

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_metadata: Dict[str, dict] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> str:
        connection_id = str(uuid.uuid4())
        
        await websocket.accept()
        
        async with self._lock:
            self.active_connections[connection_id] = websocket
            self.connection_metadata[connection_id] = {
                "connection_id": connection_id,
                "connected_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat(),
                "message_count": 0,
            }
        
        return connection_id

    async def disconnect(self, connection_id: str):
        async with self._lock:
            if connection_id in self.active_connections:
                del self.active_connections[connection_id]
            if connection_id in self.connection_metadata:
                self.connection_metadata[connection_id]["disconnected_at"] = datetime.now().isoformat()

    async def send_message(self, connection_id: str, message: dict):
        websocket = self.active_connections.get(connection_id)
        if websocket:
            try:
                await websocket.send_json(message)
                async with self._lock:
                    if connection_id in self.connection_metadata:
                        self.connection_metadata[connection_id]["message_count"] += 1
                        self.connection_metadata[connection_id]["last_activity"] = datetime.now().isoformat()
            except Exception:
                await self.disconnect(connection_id)

    async def broadcast(self, message: dict):
        disconnected_ids = []
        
        for connection_id, websocket in self.active_connections.items():
            try:
                await websocket.send_json(message)
                async with self._lock:
                    if connection_id in self.connection_metadata:
                        self.connection_metadata[connection_id]["message_count"] += 1
                        self.connection_metadata[connection_id]["last_activity"] = datetime.now().isoformat()
            except Exception:
                disconnected_ids.append(connection_id)
        
        for connection_id in disconnected_ids:
            await self.disconnect(connection_id)

    def get_active_connections(self) -> int:
        return len(self.active_connections)

    def get_connection_info(self, connection_id: str) -> dict:
        return self.connection_metadata.get(connection_id, {})
