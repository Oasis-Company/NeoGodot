from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID, uuid4
from schemas.session import Session, SessionCreate, SessionStatus
from routes.dependencies import get_session_service
from services.session_service import SessionService

router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.post("", response_model=Session)
async def create_session(
    session_data: SessionCreate,
    service: SessionService = Depends(get_session_service)
):
    session = await service.create_session(session_data)
    return session

@router.get("/{session_id}", response_model=Session)
async def get_session(
    session_id: UUID,
    service: SessionService = Depends(get_session_service)
):
    session = await service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.put("/{session_id}", response_model=Session)
async def update_session(
    session_id: UUID,
    session_data: SessionCreate,
    service: SessionService = Depends(get_session_service)
):
    session = await service.update_session(
        session_id,
        project_path=session_data.project_path,
        mode=session_data.mode,
        budget_usd=session_data.budget_usd,
        selected_models=session_data.selected_models
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.delete("/{session_id}")
async def delete_session(
    session_id: UUID,
    service: SessionService = Depends(get_session_service)
):
    success = await service.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"message": "Session deleted successfully"}

@router.get("", response_model=list[Session])
async def list_sessions(
    service: SessionService = Depends(get_session_service)
):
    return await service.list_sessions()