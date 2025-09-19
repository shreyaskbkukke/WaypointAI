from typing import Generic, List, Optional, Dict, Tuple, TypeVar
import asyncio
from beanie import Document, WriteRules

ModelType = TypeVar("ModelType", bound=Document)


class BaseRepository(Generic[ModelType]):
    """
    Generic base class for CRUD operations on Beanie documents.
    Subclasses should define the model class and override methods as needed.
    """
    model: type[ModelType]

    async def create(self, **kwargs) -> ModelType:
        """
        Insert a new document. Subclasses should override if needed for specific params.
        """
        doc = self.model(**kwargs)
        return await doc.insert(link_rule=WriteRules.WRITE)

    async def get(self, id: str) -> Optional[ModelType]:
        """
        Fetch one by id.
        """
        return await self.model.get(id)

    async def list(self, skip: int = 0, limit: int = 10, search_text: Optional[str] = None, **kwargs) -> Tuple[List[ModelType], int]:
        """
        Fetch all documents with pagination and optional search.
        Subclasses can override to customize the query.
        """
        query = self._build_list_query(search_text, **kwargs)

        items_coro = self.model.find(query).skip(skip).limit(limit).to_list()
        count_coro = self.model.find(query).count()

        items, total = await asyncio.gather(items_coro, count_coro)
        return items, total

    def _build_list_query(self, search_text: Optional[str] = None, **kwargs) -> Dict:
        """
        Helper to build the query dict. Subclasses override for model-specific fields.
        """
        query = {}
        if search_text:
            query["$or"] = []
        # Ensure kwargs are merged into the query dictionary
        if kwargs:
            if not isinstance(kwargs, dict):
                raise ValueError("Expected kwargs to be a dictionary")
            query.update(kwargs)
        return query

    async def update(self, id: str, data: dict) -> Optional[ModelType]:
        """
        Partial update: only keys in `data`.
        """
        doc = await self.get(id)
        if not doc:
            return None
        for k, v in data.items():
            setattr(doc, k, v)
        await doc.save()
        return doc

    async def delete(self, id: str) -> bool:
        """
        Delete one by id. Returns True if existed.
        """
        doc = await self.get(id)
        if not doc:
            return False
        await doc.delete()
        return True
