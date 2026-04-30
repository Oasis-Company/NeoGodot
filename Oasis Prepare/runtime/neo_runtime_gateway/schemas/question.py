from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum
from typing import List, Optional

class QuestionType(str, Enum):
    INFORMATION_GAP = "information_gap"
    ARCHITECTURE_FORK = "architecture_fork"
    DESTRUCTIVE_CHANGE = "destructive_change"
    COST_JUMP = "cost_jump"
    VALIDATION_FAILURE = "validation_failure"

class Question(BaseModel):
    question_id: UUID = Field(default_factory=uuid4)
    session_id: UUID
    task_id: Optional[UUID] = None
    type: QuestionType
    title: str
    description: str
    default_action: str
    choices: List[str] = Field(default_factory=list)
    affected_resources: List[str] = Field(default_factory=list)
    estimated_cost_impact: float = 0.0
    created_at: datetime = Field(default_factory=datetime.now)
    answered: bool = False

class QuestionAnswer(BaseModel):
    question_id: UUID
    answer: str
    user_comment: Optional[str] = None