from __future__ import annotations

from typing import Optional, Tuple, List

from models.agent_builder import AgentBuilder
from repositories.agent_builder_repo import AgentBuilderRepository
from schemas.agent_builder import (
    AgentBuilderCreate, AgentBuilderUpdate, AgentBuilderRead
)

class AgentBuilderService:
    def __init__(self, repo: AgentBuilderRepository | None = None) -> None:
        self.repo = repo or AgentBuilderRepository()

    async def create(self, payload: AgentBuilderCreate) -> AgentBuilderRead:
        doc = await self.repo.create(
            title=payload.title,
            description=payload.description,
            is_active=payload.is_active,
        )
        return self._to_read(doc)

    async def get(self, agent_id: str) -> Optional[AgentBuilderRead]:
        doc = await self.repo.get_by_agent_id(agent_id)
        if not doc:
            return None
        return self._to_read(doc)

    async def list(
        self,
        page: int = 1,
        limit: int = 10,
        search_text: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> tuple[list[AgentBuilderRead], int, int, int]:
        skip = max(page - 1, 0) * limit
        items, total = await self.repo.list(
            skip=skip, limit=limit, search_text=search_text, is_active=is_active
        )
        return [self._to_read(x) for x in items], total, page, limit

    async def update(self, agent_id: str, payload: AgentBuilderUpdate) -> Optional[AgentBuilderRead]:
        data = payload.model_dump(exclude_none=True)
        # If title is being updated, check for duplicate
        if data.get("title"):
            existing = await self.repo.get_by_title(data["title"])
            if existing and getattr(existing, "agent_id", None) != agent_id:
                raise ValueError("Agent builder with this title already exists.")
        doc = await self.repo.update_by_agent_id(agent_id, data)
        if not doc:
            return None
        return self._to_read(doc)

    async def delete(self, agent_id: str) -> bool:
        return await self.repo.delete_by_agent_id(agent_id)

    @staticmethod
    def _to_read(doc: AgentBuilder) -> AgentBuilderRead:
        return AgentBuilderRead(
            agent_id=doc.agent_id,
            title=doc.title,
            description=doc.description,
            is_active=doc.is_active,
            created_at=doc.created_at,
            updated_at=doc.updated_at,
        )
