"""GET|PATCH /v1/memory — memory entries for a project."""
from __future__ import annotations

from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from api.auth import get_current_user_id
from db.pool import acquire
from db.queries.projects import get_project
from memory import delete as memory_delete
from memory import get_recent

log = structlog.get_logger(__name__)
router = APIRouter()


class MemoryEntryResponse(BaseModel):
    id: UUID
    type: str
    content: str
    source: str
    active: bool


class PatchMemoryRequest(BaseModel):
    action: str
    """'delete' is the only supported action"""
    entry_id: UUID


@router.get("/memory", response_model=list[MemoryEntryResponse])
async def list_memory_route(
    project_id: UUID,
    memory_type: str | None = None,
    limit: int = 20,
    user_id: UUID = Depends(get_current_user_id),
) -> list[MemoryEntryResponse]:
    async with acquire() as conn:
        project = await get_project(conn, project_id, user_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    entries = await get_recent(project_id, limit=limit, memory_type=memory_type)
    log.info("api.list_memory", project_id=str(project_id), count=len(entries))

    return [
        MemoryEntryResponse(
            id=e.id,
            type=e.type,
            content=e.content,
            source=e.source,
            active=e.active,
        )
        for e in entries
    ]


@router.patch("/memory")
async def patch_memory_route(
    body: PatchMemoryRequest,
    project_id: UUID,
    user_id: UUID = Depends(get_current_user_id),
) -> dict:
    async with acquire() as conn:
        project = await get_project(conn, project_id, user_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    if body.action == "delete":
        # Use autonomous mode to allow delete (only non-light modes may delete)
        success = await memory_delete(project_id, body.entry_id, mode="autonomous")
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Memory entry not found")
        log.info("api.patch_memory.delete", entry_id=str(body.entry_id))
        return {"deleted": True}

    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unknown action: {body.action}")
