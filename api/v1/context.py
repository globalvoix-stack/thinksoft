"""GET /v1/context — current context bus snapshot for a session."""
from __future__ import annotations

from typing import Any
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from api.auth import get_current_user_id
from context import load as load_bus
from db.pool import acquire
from db.queries.projects import get_project

log = structlog.get_logger(__name__)
router = APIRouter()


class ContextResponse(BaseModel):
    project_id: UUID
    session_id: UUID
    mode: str
    agent_statuses: dict[str, str]
    decision_count: int
    artifact_keys: list[str]


@router.get("/context", response_model=ContextResponse)
async def get_context_route(
    project_id: UUID,
    session_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
) -> ContextResponse:
    async with acquire() as conn:
        project = await get_project(conn, project_id, user_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    bus = await load_bus(project_id, session_id)
    log.info("api.get_context", project_id=str(project_id), session_id=str(session_id))

    return ContextResponse(
        project_id=bus.project_id,
        session_id=bus.session_id,
        mode=bus.mode,
        agent_statuses=bus.agent_statuses,
        decision_count=len(bus.decisions),
        artifact_keys=list(bus.artifacts.keys()),
    )
