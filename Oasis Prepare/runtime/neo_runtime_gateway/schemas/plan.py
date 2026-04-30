from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from typing import List, Optional

class PlanTask(BaseModel):
    task_id: UUID
    kind: str
    description: str
    dependencies: List[UUID] = Field(default_factory=list)
    risk_level: str = "medium"
    estimated_cost_usd: float = 0.0

class PlanCreate(BaseModel):
    session_id: UUID
    goal: str
    context: Optional[str] = None
    constraints: Optional[dict] = None
    existing_artifacts: Optional[List[str]] = None

class Plan(BaseModel):
    plan_id: UUID = Field(default_factory=uuid4)
    session_id: UUID
    goal: str
    context: Optional[str] = None
    tasks: List[PlanTask] = Field(default_factory=list)
    risk_points: List[str] = Field(default_factory=list)
    questions: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)