from __future__ import annotations
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from services.agent_builder_service import AgentBuilderService
from schemas.agent_builder import AgentBuilderCreate, AgentBuilderUpdate, AgentBuilderRead
from schemas.rest_api import (
    SuccessResponse, ErrorResponse, PaginatedSuccessResponse
)
from schemas.rest_api import APIResponse

router = APIRouter(prefix="/{tenant_name}/agent-builder/v1", tags=["Agent Builders"])

app = AgentBuilderService()

@router.get(
    "/agents",
    response_model=PaginatedSuccessResponse[list[AgentBuilderRead]],
    responses={
        200: {"model": PaginatedSuccessResponse[list[AgentBuilderRead]], "description": "List of agent builders"},
        400: {"model": ErrorResponse, "description": "Bad Request"},
        403: {"model": ErrorResponse, "description": "Access forbidden"},
        409: {"model": ErrorResponse, "description": "Conflict"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def list_agent_builders(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=10),
    search: Optional[str] = Query(None, description="Search in title/description"),
    active: Optional[bool] = Query(None, description="Filter by is_active"),
):
    items, total, page, limit = await app.list(
        page=page, limit=limit, search_text=search, is_active=active
    )
    return PaginatedSuccessResponse(message="OK", data=items, total=total, page=page, limit=limit)


@router.get(
    "/agent/{agent_id}",
    response_model=SuccessResponse[AgentBuilderRead],
    responses={
        200: {"model": SuccessResponse[AgentBuilderRead], "description": "Agent builder found"},
        404: {"model": ErrorResponse, "description": "Agent not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def get_agent_builder(agent_id: str):
    found = await app.get(agent_id)
    if not found:
        raise HTTPException(status_code=404, detail="Agent not found")
    return SuccessResponse(message="OK", data=found)


@router.post(
    "/agent",
    response_model=SuccessResponse[AgentBuilderRead],
    responses={
        201: {"model": SuccessResponse[AgentBuilderRead], "description": "Agent builder created"},
        400: {"model": ErrorResponse, "description": "Bad Request"},
        409: {"model": ErrorResponse, "description": "Conflict"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def create_agent_builder(payload: AgentBuilderCreate):
    try:
        created = await app.create(payload)
        return SuccessResponse(message="Created", data=created)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put(
    "/agent/{agent_id}",
    response_model=SuccessResponse[AgentBuilderRead],
    responses={
        200: {"model": SuccessResponse[AgentBuilderRead], "description": "Agent builder updated"},
        400: {"model": ErrorResponse, "description": "Bad Request"},
        404: {"model": ErrorResponse, "description": "Agent not found"},
        409: {"model": ErrorResponse, "description": "Conflict"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def update_agent_builder(agent_id: str, payload: AgentBuilderUpdate):
    try:
        updated = await app.update(agent_id, payload)
        if not updated:
            raise HTTPException(status_code=404, detail="Agent not found")
        return SuccessResponse(message="Updated", data=updated)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete(
    "/agent/{agent_id}",
    response_model=SuccessResponse[None],
    responses={
        200: {"model": SuccessResponse[None], "description": "Agent builder deleted"},
        400: {"model": ErrorResponse, "description": "Bad Request"},
        404: {"model": ErrorResponse, "description": "Agent not found"},
        409: {"model": ErrorResponse, "description": "Conflict"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
    },
)
async def delete_agent_builder(agent_id: str):
    ok = await app.delete(agent_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Agent not found")
    return SuccessResponse(message="Deleted", data=None)
