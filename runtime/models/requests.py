from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class GenerateRequest(BaseModel):
    prompt: str = Field(..., description="The prompt for text generation")
    max_tokens: int = Field(default=2048, ge=1, le=8192)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    stream: bool = Field(default=False)
    model: Optional[str] = Field(default=None)
    stop: Optional[List[str]] = Field(default=None)


class ImageGenerateRequest(BaseModel):
    prompt: str = Field(..., description="The prompt for image generation")
    size: str = Field(default="1024x1024")
    quality: str = Field(default="standard")
    model: Optional[str] = Field(default=None)


class ScriptGenerateRequest(BaseModel):
    prompt: str = Field(..., description="The prompt for script generation")
    template_type: str = Field(default="default")
    target_class: Optional[str] = Field(default=None)
    style: Optional[str] = Field(default="gdscript")
