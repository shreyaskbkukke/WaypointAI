from __future__ import annotations

from typing import Generic, Optional, TypeVar, Literal
from pydantic import BaseModel

T = TypeVar("T")

class APIResponse(BaseModel, Generic[T]):
    message: str
    data: Optional[T] = None
    status: str

class SuccessResponse(APIResponse[T], Generic[T]):
    status: Literal["success"] = "success"
    code: int = 200

class PaginatedSuccessResponse(APIResponse[T], Generic[T]):
    status: Literal["success"] = "success"
    code: int = 200
    total: int
    page: int
    limit: int

class ErrorResponse(APIResponse[None]):
    status: Literal["error"] = "error"
    code: int
