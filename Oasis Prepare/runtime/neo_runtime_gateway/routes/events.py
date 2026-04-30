from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from uuid import UUID
from schemas.event import Event
from routes.dependencies import get_event_service, get_session_service
from services.event_service import EventService
from services.session_service import SessionService

router = APIRouter(prefix="/events", tags=["events"])

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: UUID,
    event_service: EventService = Depends(get_event_service),
    session_service: SessionService = Depends(get_session_service)
):
    session = await session_service.get_session(session_id)
    if not session:
        await websocket.close(code=1008, reason="Session not found")
        return
    
    await websocket.accept()
    await event_service.subscribe(session_id, websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        await event_service.unsubscribe(session_id, websocket)

@router.get("/history/{session_id}", response_model=list[Event])
async def get_event_history(
    session_id: UUID,
    limit: int = 100,
    event_service: EventService = Depends(get_event_service),
    session_service: SessionService = Depends(get_session_service)
):
    session = await session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return event_service.get_event_history(session_id, limit)