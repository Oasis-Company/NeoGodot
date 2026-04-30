from uuid import UUID
from typing import Dict, Optional
from schemas.session import Session, SessionCreate, SessionStatus

class SessionService:
    def __init__(self):
        self.sessions: Dict[UUID, Session] = {}

    async def create_session(self, create_data: SessionCreate) -> Session:
        session = Session(
            project_path=create_data.project_path,
            mode=create_data.mode,
            budget_usd=create_data.budget_usd,
            remaining_budget_usd=create_data.budget_usd,
            selected_models=create_data.selected_models
        )
        self.sessions[session.session_id] = session
        return session

    async def get_session(self, session_id: UUID) -> Optional[Session]:
        return self.sessions.get(session_id)

    async def update_session(self, session_id: UUID, **kwargs) -> Optional[Session]:
        session = self.sessions.get(session_id)
        if session:
            for key, value in kwargs.items():
                if hasattr(session, key):
                    setattr(session, key, value)
            session.updated_at = session.__fields__["updated_at"].default_factory()
        return session

    async def delete_session(self, session_id: UUID) -> bool:
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

    async def list_sessions(self) -> list[Session]:
        return list(self.sessions.values())

    async def update_budget(self, session_id: UUID, cost_usd: float) -> bool:
        session = self.sessions.get(session_id)
        if session:
            session.update_budget(cost_usd)
            return True
        return False