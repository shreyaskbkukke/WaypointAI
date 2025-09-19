from __future__ import annotations

from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class AgentBuilderCreate(BaseModel):
    title: str
    description: Optional[str] = None
    is_active: bool = True

class AgentBuilderUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class AgentBuilderRead(BaseModel):
    agent_id: str
    title: str
    description: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
