from pydantic import BaseModel, Field
from uuid import UUID
from enum import Enum
from typing import List

class ResourceType(str, Enum):
    IMAGE = "image"
    AUDIO = "audio"
    SCENE = "scene"
    SCRIPT = "script"
    MATERIAL = "material"
    OTHER = "other"

class ImportRequest(BaseModel):
    session_id: UUID
    files: List[str] = Field(..., description="List of file paths to import")
    resource_type: ResourceType
    target_directory: str = Field("res://ai_generated/", description="Target directory in Godot project")
    metadata: dict = Field(default_factory=dict)

class ImportResult(BaseModel):
    success: bool
    imported_paths: List[str] = Field(default_factory=list)
    failed_paths: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)
    message: str = ""