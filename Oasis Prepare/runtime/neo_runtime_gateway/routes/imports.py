from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from schemas.import_request import ImportRequest, ImportResult
from routes.dependencies import get_import_service, get_session_service
from services.import_service import ImportService
from services.session_service import SessionService

router = APIRouter(prefix="/import", tags=["import"])

@router.post("", response_model=ImportResult)
async def import_assets(
    request: ImportRequest,
    import_service: ImportService = Depends(get_import_service),
    session_service: SessionService = Depends(get_session_service)
):
    session = await session_service.get_session(request.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    result = await import_service.import_assets(request)
    return result