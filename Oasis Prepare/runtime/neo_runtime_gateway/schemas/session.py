from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum

class SessionStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class SessionCreate(BaseModel):
    project_path: str = Field(..., description="Godot project path")
    mode: str = Field("default", description="Session mode")
    budget_usd: float = Field(10.0, description="Maximum budget in USD")
    selected_models: list[str] = Field(default_factory=list, description="Selected model names")

class Session(BaseModel):
    session_id: UUID = Field(default_factory=uuid4)
    project_path: str
    mode: str
    budget_usd: float
    remaining_budget_usd: float
    selected_models: list[str]
    status: SessionStatus = SessionStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    def update_budget(self, cost_usd: float):
        self.remaining_budget_usd = max(0, self.remaining_budget_usd - cost_usd)
        self.updated_at = datetime.now()