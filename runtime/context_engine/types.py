
"""Core data models for NeoGodot."""

from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
import hashlib
from pydantic import BaseModel, Field


class SymbolKind(str, Enum):
    """代码符号类型."""
    CLASS = "class"
    FUNCTION = "function"
    VARIABLE = "variable"
    SIGNAL = "signal"
    ENUM = "enum"
    CONSTANT = "constant"
    ANNOTATION = "annotation"
    INNER_CLASS = "inner_class"


class AccessModifier(str, Enum):
    """访问修饰符."""
    PUBLIC = "public"
    PRIVATE = "private"
    PROTECTED = "protected"


class TaskType(str, Enum):
    """任务类型枚举."""
    CODE_GENERATION = "code_generation"
    CODE_COMPLETION = "code_completion"
    SCENE_GENERATION = "scene_generation"
    DEBUGGING = "debugging"
    REFACTORING = "refactoring"
    EXPLANATION = "explanation"
    CHAT = "chat"


class ChangeType(Enum):
    """文件变更类型."""
    CREATED = auto()
    MODIFIED = auto()
    DELETED = auto()
    RENAMED = auto()


class SourceLocation(BaseModel):
    """源码位置."""
    file_path: str
    start_line: int
    start_column: int
    end_line: int
    end_column: int


class SymbolInfo(BaseModel):
    """代码符号信息."""
    name: str
    kind: SymbolKind
    access: AccessModifier
    location: SourceLocation
    docstring: Optional[str] = None
    annotations: List[str] = Field(default_factory=list)
    signature: Optional[str] = None
    type_hint: Optional[str] = None
    default_value: Optional[str] = None
    parent_class: Optional[str] = None


class CodeChunk(BaseModel):
    """代码分块（用于向量检索）."""
    chunk_id: str = Field(default_factory=lambda: str(uuid4()))
    content: str = ""
    chunk_type: str = ""  # function / class / file
    symbol_name: Optional[str] = None
    file_path: str = ""
    start_line: int = 0
    end_line: int = 0
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    @property
    def content_hash(self) -&gt; str:
        """计算内容哈希用于增量更新检测."""
        return hashlib.sha256(self.content.encode()).hexdigest()[:16]


class DependencyInfo(BaseModel):
    """依赖关系信息."""
    source: str
    target: str
    dep_type: str  # extends / preload / call / reference
    target_file: Optional[str] = None
    is_resolved: bool = True


class CodeStructure(BaseModel):
    """文件级代码结构."""
    file_path: str
    file_hash: str = ""
    language: str = "gdscript"
    class_name: Optional[str] = None
    extends: Optional[str] = None
    imports: List[str] = Field(default_factory=list)
    symbols: List[SymbolInfo] = Field(default_factory=list)
    chunks: List[CodeChunk] = Field(default_factory=list)
    dependencies: List[DependencyInfo] = Field(default_factory=list)
    total_lines: int = 0
    source_code: str = ""


class SceneNode(BaseModel):
    """场景节点."""
    node_path: str
    node_type: str
    node_name: str
    parent_path: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)
    script_path: Optional[str] = None
    children: List['SceneNode'] = Field(default_factory=list)


SceneNode.model_rebuild()


class SignalConnection(BaseModel):
    """信号连接."""
    signal_name: str
    source_node: str
    target_node: str
    target_method: str
    flags: List[str] = Field(default_factory=list)


class ExternalResource(BaseModel):
    """外部资源引用."""
    resource_id: str
    resource_type: str
    resource_path: str


class SceneStructure(BaseModel):
    """场景文件结构."""
    scene_path: str
    scene_hash: str = ""
    root_node: Optional[SceneNode] = None
    all_nodes: List[SceneNode] = Field(default_factory=list)
    signal_connections: List[SignalConnection] = Field(default_factory=list)
    node_count: int = 0
    script_bindings: Dict[str, str] = Field(default_factory=dict)
    external_resources: List[ExternalResource] = Field(default_factory=list)


class ResourceInfo(BaseModel):
    """资源信息."""
    resource_path: str
    resource_type: str
    file_size: int = 0
    format: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ProjectStats(BaseModel):
    """项目统计信息."""
    total_files: int = 0
    total_code_files: int = 0
    total_scene_files: int = 0
    total_resources: int = 0
    total_symbols: int = 0
    total_lines_of_code: int = 0
    indexed_at: Optional[datetime] = None


class ProjectContext(BaseModel):
    """项目完整上下文."""
    project_path: str
    project_name: str = ""
    godot_version: Optional[str] = None
    stats: ProjectStats = Field(default_factory=ProjectStats)
    code_structures: Dict[str, CodeStructure] = Field(default_factory=dict)
    scene_structures: Dict[str, SceneStructure] = Field(default_factory=dict)
    resource_index: Dict[str, ResourceInfo] = Field(default_factory=dict)
    symbol_index: Dict[str, List[SymbolInfo]] = Field(default_factory=dict)
    is_fully_indexed: bool = False
    last_updated: Optional[datetime] = None


class RetrievedItem(BaseModel):
    """检索结果项."""
    content: str
    source_type: str  # code / scene / resource / doc
    source_path: str
    relevance_score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class QueryIntent(BaseModel):
    """查询意图."""
    task_type: TaskType
    confidence: float
    entities: List[Dict[str, Any]] = Field(default_factory=list)
    expanded_queries: List[str] = Field(default_factory=list)


class GenerationResult(BaseModel):
    """生成结果."""
    content: str
    model: str
    usage: Dict[str, int] = Field(default_factory=dict)
    finish_reason: str = "stop"
    cached: bool = False
    latency_ms: float = 0.0


class ModelConfig(BaseModel):
    """模型配置."""
    model_id: str
    provider: str
    max_context_length: int
    cost_per_input_token: float
    cost_per_output_token: float
    avg_latency_ms: int
    capabilities: List[str] = Field(default_factory=list)
    enabled: bool = True


class RoutingDecision(BaseModel):
    """路由决策结果."""
    selected_model: str
    fallback_chain: List[str]
    estimated_cost: float
    estimated_latency_ms: int
    routing_reason: str


class FileChangeEvent(BaseModel):
    """文件变更事件."""
    file_path: str
    change_type: ChangeType
    timestamp: datetime
