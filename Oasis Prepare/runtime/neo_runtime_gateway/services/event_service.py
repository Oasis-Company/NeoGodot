from uuid import UUID
from typing import Dict, List
from schemas.event import Event, EventType

class EventService:
    def __init__(self):
        self.active_connections: Dict[UUID, List] = {}
        self.event_history: List[Event] = []

    async def publish_event(self, session_id: UUID, task_id: UUID = None, 
                         event_type: str = "", payload: dict = None):
        event = Event(
            session_id=session_id,
            task_id=task_id,
            event_type=EventType(event_type),
            payload=payload or {}
        )
        self.event_history.append(event)

        if session_id in self.active_connections:
            for connection in self.active_connections[session_id]:
                await connection.send_json(event.to_dict())

    async def subscribe(self, session_id: UUID, connection):
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(connection)

    async def unsubscribe(self, session_id: UUID, connection):
        if session_id in self.active_connections:
            self.active_connections[session_id].remove(connection)
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]

    def get_event_history(self, session_id: UUID = None, limit: int = 100) -> List[Event]:
        events = self.event_history
        if session_id:
            events = [e for e in events if e.session_id == session_id]
        return events[-limit:] if limit else events