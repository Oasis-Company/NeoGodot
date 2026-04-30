from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from schemas.question import Question, QuestionAnswer, QuestionType
from routes.dependencies import get_question_service, get_session_service
from services.question_service import QuestionService
from services.session_service import SessionService

router = APIRouter(prefix="/questions", tags=["questions"])

@router.post("", response_model=Question)
async def create_question(
    session_id: UUID,
    task_id: UUID = None,
    type: QuestionType = QuestionType.INFORMATION_GAP,
    title: str = "",
    description: str = "",
    default_action: str = "",
    choices: list[str] = None,
    affected_resources: list[str] = None,
    estimated_cost_impact: float = 0.0,
    question_service: QuestionService = Depends(get_question_service),
    session_service: SessionService = Depends(get_session_service)
):
    session = await session_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    question = await question_service.create_question(
        session_id=session_id,
        task_id=task_id,
        type=type,
        title=title,
        description=description,
        default_action=default_action,
        choices=choices or [],
        affected_resources=affected_resources or [],
        estimated_cost_impact=estimated_cost_impact
    )
    return question

@router.get("/{question_id}", response_model=Question)
async def get_question(
    question_id: UUID,
    question_service: QuestionService = Depends(get_question_service)
):
    question = await question_service.get_question(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question

@router.post("/{question_id}/answer", response_model=Question)
async def answer_question(
    question_id: UUID,
    answer: str,
    user_comment: str = None,
    question_service: QuestionService = Depends(get_question_service)
):
    answer_data = QuestionAnswer(
        question_id=question_id,
        answer=answer,
        user_comment=user_comment
    )
    question = await question_service.answer_question(answer_data)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question

@router.get("", response_model=list[Question])
async def list_questions(
    session_id: UUID = None,
    answered: bool = None,
    question_service: QuestionService = Depends(get_question_service)
):
    return await question_service.list_questions(session_id, answered)