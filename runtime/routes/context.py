from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging
import uuid
from context_engine import ContextManager, ProjectContext

router = APIRouter(prefix="/v1/context", tags=["context"])
logger = logging.getLogger("neogodot-runtime.context")
context_manager = ContextManager()


class BuildContextRequest(BaseModel):
    project_path: str = Field(..., description="Path to the Godot project root directory")


class QueryContextRequest(BaseModel):
    project_path: str = Field(..., description="Path to the Godot project root directory")
    query: str = Field(..., description="Search query for relevant context")
    context_type: Optional[str] = Field(None, description="Type of context to search (code/scene/resource)")
    limit: int = Field(10, ge=1, le=50, description="Maximum number of results to return")


@router.post("/build")
async def build_context(request: BuildContextRequest, http_request: Request):
    """Build complete project context."""
    trace_id = getattr(http_request.state, "trace_id", str(uuid.uuid4()))

    project_path = Path(request.project_path)

    if not project_path.exists():
        raise HTTPException(status_code=404, detail=f"Project path not found: {request.project_path}")

    if not project_path.is_dir():
        raise HTTPException(status_code=400, detail=f"Path is not a directory: {request.project_path}")

    logger.info(
        f"Building project context",
        extra={
            "trace_id": trace_id,
            "project_path": str(project_path),
        },
    )

    try:
        context = await context_manager.build_project_context(project_path)

        logger.info(
            f"Project context built successfully",
            extra={
                "trace_id": trace_id,
                "total_files": context.stats.total_files,
                "code_files": context.stats.total_code_files,
            },
        )

        return {
            "success": True,
            "trace_id": trace_id,
            "project_name": context.project_name,
            "project_path": context.project_path,
            "stats": {
                "total_files": context.stats.total_files,
                "code_files": context.stats.total_code_files,
                "scene_files": context.stats.total_scene_files,
                "resources": context.stats.total_resources,
                "symbols": context.stats.total_symbols,
                "lines_of_code": context.stats.total_lines_of_code,
            },
            "is_fully_indexed": context.is_fully_indexed,
        }

    except Exception as e:
        logger.error(
            f"Failed to build project context: {str(e)}",
            extra={"trace_id": trace_id, "error": str(e)},
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=f"Failed to build context: {str(e)}")


@router.post("/query")
async def query_context(request: QueryContextRequest, http_request: Request):
    """Query for relevant project context."""
    trace_id = getattr(http_request.state, "trace_id", str(uuid.uuid4()))

    project_path = Path(request.project_path)

    if not project_path.exists():
        raise HTTPException(status_code=404, detail=f"Project path not found: {request.project_path}")

    logger.info(
        f"Querying project context",
        extra={
            "trace_id": trace_id,
            "project_path": str(project_path),
            "query": request.query,
        },
    )

    try:
        results = await context_manager.get_relevant_context(
            project_path=project_path,
            query=request.query,
            context_type=request.context_type,
            limit=request.limit,
        )

        logger.info(
            f"Context query completed",
            extra={
                "trace_id": trace_id,
                "result_count": len(results),
            },
        )

        return {
            "success": True,
            "trace_id": trace_id,
            "query": request.query,
            "results": [
                {
                    "content": item.content,
                    "file_path": item.source_path,
                    "line_start": item.metadata.get("start_line"),
                    "line_end": item.metadata.get("end_line"),
                    "score": item.relevance_score,
                    "metadata": item.metadata,
                }
                for item in results
            ],
        }

    except Exception as e:
        logger.error(
            f"Failed to query project context: {str(e)}",
            extra={"trace_id": trace_id, "error": str(e)},
            exc_info=True,
        )
        raise HTTPException(status_code=500, detail=f"Failed to query context: {str(e)}")
