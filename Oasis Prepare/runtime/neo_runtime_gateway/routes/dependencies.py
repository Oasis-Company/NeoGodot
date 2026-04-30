from services.session_service import SessionService
from services.task_service import TaskService
from services.plan_service import PlanService
from services.question_service import QuestionService
from services.event_service import EventService
from services.import_service import ImportService
from services.provider_service import ProviderService

event_service = EventService()
provider_service = ProviderService()

session_service = SessionService()
plan_service = PlanService()
task_service = TaskService(event_service, provider_service)
question_service = QuestionService(event_service)
import_service = ImportService(event_service)

def get_session_service() -> SessionService:
    return session_service

def get_task_service() -> TaskService:
    return task_service

def get_plan_service() -> PlanService:
    return plan_service

def get_question_service() -> QuestionService:
    return question_service

def get_event_service() -> EventService:
    return event_service

def get_import_service() -> ImportService:
    return import_service