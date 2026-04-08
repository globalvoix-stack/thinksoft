"""POST /v1/generate — submit a generation job."""
from __future__ import annotations

import asyncio
from uuid import UUID, uuid4

import structlog
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel, Field

from api.auth import get_current_user_id
from db.pool import acquire
from db.queries.projects import get_project
from modes.router import resolve
from pipeline.first_prompt import run as first_prompt_run
from queue.manager import complete as job_complete
from queue.manager import enqueue, fail as job_fail
from queue.manager import run_with_timeout, start as job_start

log = structlog.get_logger(__name__)
router = APIRouter()


class GenerateRequest(BaseModel):
    project_id: UUID
    session_id: UUID = Field(default_factory=uuid4)
    prompt: str = Field(..., min_length=1, max_length=10000)
    mode: str = Field("autonomous", pattern="^(light|autonomous|max)$")
    is_first_prompt: bool = False


class GenerateResponse(BaseModel):
    job_id: UUID
    mode: str
    mismatch_suggestion: str | None


async def _run_generation(
    project_id: UUID,
    session_id: UUID,
    job_id: UUID,
    prompt: str,
    mode: str,
) -> None:
    """Background task: run generation pipeline and update job status."""
    try:
        if mode == "light":
            from modes.light.handler import run as light_run
            result = await light_run(prompt)
            await job_complete(job_id, {"content": result.content, "model": result.model_used})
        elif mode == "autonomous":
            from modes.autonomous.handler import run as autonomous_run
            result = await autonomous_run(project_id, session_id, job_id, prompt)
            if not result.success:
                await job_fail(job_id, result.error or "autonomous pipeline failed")
        elif mode == "max":
            from modes.max.handler import run as max_run
            result = await max_run(project_id, session_id, job_id, prompt)
            if not result.success:
                await job_fail(job_id, result.error or "max pipeline failed")
    except Exception as exc:
        log.error("generate.background.error", job_id=str(job_id), error=str(exc))
        await job_fail(job_id, str(exc))


@router.post("/generate", response_model=GenerateResponse, status_code=status.HTTP_202_ACCEPTED)
async def generate_route(
    body: GenerateRequest,
    background_tasks: BackgroundTasks,
    user_id: UUID = Depends(get_current_user_id),
) -> GenerateResponse:
    # Verify project ownership
    async with acquire() as conn:
        project = await get_project(conn, body.project_id, user_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # Resolve mode and detect mismatch
    decision = resolve(body.mode, body.prompt, is_first_prompt=body.is_first_prompt)
    effective_mode = decision.mode

    log.info(
        "api.generate",
        project_id=str(body.project_id),
        mode=effective_mode,
        is_first_prompt=body.is_first_prompt,
    )

    # For first prompt, use the full pipeline (always max)
    if body.is_first_prompt:
        job = await enqueue(body.project_id, body.session_id, "max")
        await job_start(job.id)
        background_tasks.add_task(
            first_prompt_run,
            body.project_id,
            body.session_id,
            body.prompt,
        )
    else:
        job = await enqueue(body.project_id, body.session_id, effective_mode)
        await job_start(job.id)
        background_tasks.add_task(
            _run_generation,
            body.project_id,
            body.session_id,
            job.id,
            body.prompt,
            effective_mode,
        )

    return GenerateResponse(
        job_id=job.id,
        mode=effective_mode,
        mismatch_suggestion=decision.mismatch_suggestion,
    )
