from pydantic import BaseModel, Field
from uuid import UUID
from datetime import datetime
from enum import Enum

class EventType(str, Enum):
    TASK_STARTED = "task.started"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    TASK_WAITING = "task.waiting"
    QUESTION_RAISED = "question.raised"
    QUESTION_ANSWERED = "question.answered"
    ARTIFACT_READY = "artifact.ready"
    PLAN_UPDATED = "plan.updated"
    SESSION_CREATED = "session.created"
    SESSION_ENDED = "session.ended"

class Event(BaseModel):
    event_id: str = Field(default_factory=lambda: str(UUID(int=datetime.now().timestamp())))
    session_id: UUID
    task_id: UUID = None
    event_type: EventType
    payload: dict = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)

    def to_dict(self):
        return {
            "event_id": self.event_id,
            "session_id": str(self.session_id),
            "task_id": str(self.task_id) if self.task_id else None,
            "event_type": self.event_type.value,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat()
        }