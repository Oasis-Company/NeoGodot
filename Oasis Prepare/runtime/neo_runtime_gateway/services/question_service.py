from uuid import UUID
from typing import Dict, Optional, List
from schemas.question import Question, QuestionAnswer, QuestionType
from services.event_service import EventService

class QuestionService:
    def __init__(self, event_service: EventService):
        self.questions: Dict[UUID, Question] = {}
        self.event_service = event_service

    async def create_question(self, session_id: UUID, task_id: UUID = None, 
                            type: QuestionType = QuestionType.INFORMATION_GAP,
                            title: str = "", description: str = "",
                            default_action: str = "", choices: List[str] = None,
                            affected_resources: List[str] = None,
                            estimated_cost_impact: float = 0.0) -> Question:
        question = Question(
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
        self.questions[question.question_id] = question
        
        await self.event_service.publish_event(
            session_id=session_id,
            event_type="question.raised",
            payload={
                "question_id": str(question.question_id),
                "title": title,
                "type": type.value
            }
        )
        return question

    async def get_question(self, question_id: UUID) -> Optional[Question]:
        return self.questions.get(question_id)

    async def answer_question(self, answer_data: QuestionAnswer) -> Optional[Question]:
        question = self.questions.get(answer_data.question_id)
        if question:
            question.answered = True
            
            await self.event_service.publish_event(
                session_id=question.session_id,
                event_type="question.answered",
                payload={
                    "question_id": str(question.question_id),
                    "answer": answer_data.answer
                }
            )
        return question

    async def list_questions(self, session_id: UUID = None, answered: bool = None) -> List[Question]:
        questions = list(self.questions.values())
        if session_id:
            questions = [q for q in questions if q.session_id == session_id]
        if answered is not None:
            questions = [q for q in questions if q.answered == answered]
        return questions