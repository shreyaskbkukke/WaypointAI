from __future__ import annotations
from typing import Optional, Dict, Tuple, List
from beanie import PydanticObjectId

from models.agent_builder import AgentBuilder
from repositories.base_repo import BaseRepository

class AgentBuilderRepository(BaseRepository[AgentBuilder]):
    async def get_by_title(self, title: str) -> Optional[AgentBuilder]:
        return await self.model.find_one(self.model.title == title)
    model = AgentBuilder

    async def get_by_agent_id(self, agent_id: str) -> Optional[AgentBuilder]:
        return await self.model.find_one(self.model.agent_id == agent_id)

    def _build_list_query(self, search_text: Optional[str] = None, **kwargs) -> Dict:
        query: Dict = {}
        # optional filter by is_active (bool) if provided
        if "is_active" in kwargs and kwargs["is_active"] is not None:
            query["is_active"] = kwargs["is_active"]

        if search_text:
            # simple $or search across title/description
            query["$or"] = [
                {"title": {"$regex": search_text, "$options": "i"}},
                {"description": {"$regex": search_text, "$options": "i"}},
            ]
        return query

    async def update_by_agent_id(self, agent_id: str, data: dict) -> Optional[AgentBuilder]:
        doc = await self.get_by_agent_id(agent_id)
        if not doc:
            return None
        for k, v in data.items():
            setattr(doc, k, v)
        await doc.save()
        return doc

    async def delete_by_agent_id(self, agent_id: str) -> bool:
        doc = await self.get_by_agent_id(agent_id)
        if not doc:
            return False
        await doc.delete()
        return True
