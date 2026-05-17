from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import time


class GenerateResponse(BaseModel):
    success: bool = Field(..., description="Whether the generation was successful")
    trace_id: str = Field(..., description="Trace ID for tracking")
    result: Optional[Dict[str, Any]] = Field(None, description="Generation result")
    error: Optional[str] = Field(None, description="Error message if failed")


class ImageGenerateResponse(BaseModel):
    success: bool = Field(..., description="Whether the image generation was successful")
    trace_id: str = Field(..., description="Trace ID for tracking")
    image_url: Optional[str] = Field(None, description="Generated image URL")
    image_path: Optional[str] = Field(None, description="Generated image path")
    error: Optional[str] = Field(None, description="Error message if failed")


class DependencyStatus(BaseModel):
    name: str = Field(..., description="Dependency name")
    status: str = Field(..., description="Status: connected, disconnected, not_configured")
    model: Optional[str] = Field(None, description="Model name if configured")


class HealthResponse(BaseModel):
    status: str = Field(..., description="Service health status")
    version: str = Field(..., description="Service version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Health check timestamp")
    uptime: float = Field(default=0.0, description="Service uptime in seconds")
    providers: List[DependencyStatus] = Field(default_factory=list, description="AI providers status")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")
    trace_id: Optional[str] = Field(None, description="Trace ID for tracking")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
