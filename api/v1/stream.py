"""GET /v1/stream/{job_id} — SSE job progress stream."""
from __future__ import annotations

from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sse_starlette.sse import EventSourceResponse  # type: ignore[import]

from api.auth import get_current_user_id
from db.pool import acquire
from db.queries.jobs import get_job_for_project
from queue.sse import stream_job_sse_starlette

log = structlog.get_logger(__name__)
router = APIRouter()


@router.get("/stream/{job_id}")
async def stream_job_route(
    job_id: UUID,
    project_id: UUID,
    request: Request,
    user_id: UUID = Depends(get_current_user_id),
) -> EventSourceResponse:
    """Stream job progress via SSE. Heartbeat every 15s. Terminates on done/error."""
    async with acquire() as conn:
        job = await get_job_for_project(conn, job_id, project_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    log.info("api.stream.start", job_id=str(job_id), user_id=str(user_id))

    async def event_generator():
        async for event in stream_job_sse_starlette(job_id):
            if await request.is_disconnected():
                log.info("api.stream.client_disconnected", job_id=str(job_id))
                break
            yield event

    return EventSourceResponse(event_generator())
