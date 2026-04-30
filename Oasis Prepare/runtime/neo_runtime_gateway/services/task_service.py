from uuid import UUID
from typing import Dict, Optional, List
from schemas.task import Task, TaskSpec, TaskStatus
from services.event_service import EventService
from services.provider_service import ProviderService

class TaskService:
    def __init__(self, event_service: EventService, provider_service: ProviderService):
        self.tasks: Dict[UUID, Task] = {}
        self.event_service = event_service
        self.provider_service = provider_service

    async def create_task(self, spec: TaskSpec) -> Task:
        task = Task(**spec.dict())
        self.tasks[task.task_id] = task
        await self.event_service.publish_event(
            session_id=spec.session_id,
            task_id=task.task_id,
            event_type="task.started",
            payload={"task_id": str(task.task_id), "kind": spec.kind.value}
        )
        return task

    async def get_task(self, task_id: UUID) -> Optional[Task]:
        return self.tasks.get(task_id)

    async def update_task(self, task_id: UUID, **kwargs) -> Optional[Task]:
        task = self.tasks.get(task_id)
        if task:
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            task.updated_at = task.__fields__["updated_at"].default_factory()
        return task

    async def execute_task(self, task_id: UUID) -> Task:
        task = self.tasks.get(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        task.update_status(TaskStatus.RUNNING)
        await self.event_service.publish_event(
            session_id=task.session_id,
            task_id=task.task_id,
            event_type="task.running",
            payload={"task_id": str(task.task_id)}
        )

        try:
            result = await self.provider_service.execute_task(task)
            task.output_artifacts = result.get("artifacts", [])
            task.cost_usd = result.get("cost_usd", 0.0)
            task.update_status(TaskStatus.SUCCEEDED)
            
            await self.event_service.publish_event(
                session_id=task.session_id,
                task_id=task.task_id,
                event_type="task.completed",
                payload={
                    "task_id": str(task.task_id),
                    "artifacts": task.output_artifacts,
                    "cost_usd": task.cost_usd
                }
            )
        except Exception as e:
            task.error_message = str(e)
            task.update_status(TaskStatus.FAILED)
            await self.event_service.publish_event(
                session_id=task.session_id,
                task_id=task.task_id,
                event_type="task.failed",
                payload={
                    "task_id": str(task.task_id),
                    "error": str(e)
                }
            )

        return task

    async def list_tasks(self, session_id: UUID = None) -> List[Task]:
        if session_id:
            return [t for t in self.tasks.values() if t.session_id == session_id]
        return list(self.tasks.values())