from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from schemas.task import Task, TaskSpec, TaskStatus
from routes.dependencies import get_task_service, get_session_service
from services.task_service import TaskService
from services.session_service import SessionService

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("", response_model=Task)
async def create_task(
    task_spec: TaskSpec,
    task_service: TaskService = Depends(get_task_service),
    session_service: SessionService = Depends(get_session_service)
):
    session = await session_service.get_session(task_spec.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    task = await task_service.create_task(task_spec)
    return task

@router.get("/{task_id}", response_model=Task)
async def get_task(
    task_id: UUID,
    task_service: TaskService = Depends(get_task_service)
):
    task = await task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("/{task_id}/execute", response_model=Task)
async def execute_task(
    task_id: UUID,
    task_service: TaskService = Depends(get_task_service)
):
    task = await task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = await task_service.execute_task(task_id)
    return task

@router.get("", response_model=list[Task])
async def list_tasks(
    session_id: UUID = None,
    task_service: TaskService = Depends(get_task_service)
):
    return await task_service.list_tasks(session_id)

@router.put("/{task_id}/status")
async def update_task_status(
    task_id: UUID,
    status: TaskStatus,
    task_service: TaskService = Depends(get_task_service)
):
    task = await task_service.update_task(task_id, status=status)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task