import json
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class MessageType(str, Enum):
    PING = "ping"
    PONG = "pong"
    GENERATE = "generate"
    GENERATION_COMPLETE = "generation_complete"
    ERROR = "error"


class StreamMessage(BaseModel):
    type: MessageType
    connection_id: Optional[str] = None
    task_id: Optional[str] = None
    payload: Optional[dict] = None
    error: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    trace_id: Optional[str] = None

    class Config:
        use_enum_values = True


def serialize_message(msg: dict) -> str:
    return json.dumps(msg, ensure_ascii=False)


def parse_message(data: str) -> dict:
    try:
        return json.loads(data)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON format"}
