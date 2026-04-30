from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from schemas.plan import Plan, PlanCreate
from routes.dependencies import get_plan_service, get_session_service
from services.plan_service import PlanService
from services.session_service import SessionService

router = APIRouter(prefix="/plan", tags=["plan"])

@router.post("", response_model=Plan)
async def create_plan(
    plan_data: PlanCreate,
    plan_service: PlanService = Depends(get_plan_service),
    session_service: SessionService = Depends(get_session_service)
):
    session = await session_service.get_session(plan_data.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    plan = await plan_service.create_plan(plan_data)
    return plan

@router.get("/{plan_id}", response_model=Plan)
async def get_plan(
    plan_id: UUID,
    plan_service: PlanService = Depends(get_plan_service)
):
    plan = await plan_service.get_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan

@router.put("/{plan_id}", response_model=Plan)
async def update_plan(
    plan_id: UUID,
    goal: str = None,
    plan_service: PlanService = Depends(get_plan_service)
):
    plan = await plan_service.update_plan(plan_id, goal=goal)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan

@router.delete("/{plan_id}")
async def delete_plan(
    plan_id: UUID,
    plan_service: PlanService = Depends(get_plan_service)
):
    success = await plan_service.delete_plan(plan_id)
    if not success:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {"message": "Plan deleted successfully"}