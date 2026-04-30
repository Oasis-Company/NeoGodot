from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from datetime import datetime
from enum import Enum
from typing import Optional, List

class TaskKind(str, Enum):
    PLAN_COMPILE = "plan.compile"
    RETRIEVE_SEARCH = "retrieve.search"
    TOOL_CALL = "tool.call"
    CODE_EDIT = "code.edit"
    CODE_TEST = "code.test"
    ANSWER_COMPOSE = "answer.compose"
    APPROVAL_REQUEST = "approval.request"
    CRITIC_SAFETY = "critic.safety"
    CRITIC_GROUNDING = "critic.grounding"
    ASSET_IMAGE = "asset.image"
    ASSET_AUDIO = "asset.audio"
    ASSET_3D = "asset.3d"
    SCENE_GENERATE = "scene.generate"
    SCRIPT_GENERATE = "script.generate"

class TaskPriority(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"

class TaskRiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TaskStatus(str, Enum):
    DRAFT = "draft"
    WAITING_APPROVAL = "waiting_approval"
    READY = "ready"
    RUNNING = "running"
    WAITING_USER = "waiting_user"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    RETRYING = "retrying"
    ESCALATED = "escalated"
    IMPORTED = "imported"
    VERIFIED = "verified"

class RetryPolicy(BaseModel):
    max_attempts: int = Field(3, ge=0, le=5)
    backoff: str = Field("exponential", enum=["none", "fixed", "exponential"])
    idempotent: bool = Field(True)

class TaskSpec(BaseModel):
    task_id: UUID = Field(default_factory=uuid4)
    session_id: UUID
    kind: TaskKind
    priority: TaskPriority = TaskPriority.P1
    risk_level: TaskRiskLevel = TaskRiskLevel.MEDIUM
    depends_on: List[UUID] = Field(default_factory=list)
    deadline_ts: Optional[datetime] = None
    timeout_ms: int = Field(60000, ge=1000)
    retry_policy: RetryPolicy = Field(default_factory=RetryPolicy)
    tool_scope: List[str] = Field(default_factory=list)
    budget: dict = Field(default_factory=dict)
    success_criteria: List[str] = Field(default_factory=list)
    evidence_refs: List[str] = Field(default_factory=list)
    metadata: dict = Field(default_factory=dict)

class Task(TaskSpec):
    status: TaskStatus = TaskStatus.DRAFT
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    output_artifacts: List[dict] = Field(default_factory=list)
    cost_usd: float = Field(0.0)
    error_message: Optional[str] = None
    logs: List[str] = Field(default_factory=list)

    def update_status(self, new_status: TaskStatus):
        self.status = new_status
        self.updated_at = datetime.now()