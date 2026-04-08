"""POST /v1/generate — submit a generation job."""
from __future__ import annotations

from uuid import UUID, uuid4

import structlog
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from pydantic import BaseModel, Field

from api.auth import get_current_user_id
from db.pool import acquire
from db.queries.projects import get_project_by_clerk_user
from modes.router import resolve
from queue.manager import enqueue, fail as job_fail, start as job_start

log = structlog.get_logger(__name__)
router = APIRouter()


class GenerateRequest(BaseModel):
    project_id: str
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    prompt: str = Field(..., min_length=1, max_length=10000)
    mode: str = Field("autonomous", pattern="^(light|autonomous|max)$")
    is_first_prompt: bool = False


class GenerateResponse(BaseModel):
    job_id: str
    mode: str
    mismatch_suggestion: str | None


async def _run_generation(
    project_id: UUID,
    session_id: UUID,
    job_id: UUID,
    prompt: str,
    mode: str,
) -> None:
    try:
        if mode == "light":
            from modes.light.handler import run as light_run
            from queue.manager import complete as job_complete
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
    clerk_user_id: str = Depends(get_current_user_id),
) -> GenerateResponse:
    try:
        project_id = UUID(body.project_id)
        session_id = UUID(body.session_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid ID format")

    async with acquire() as conn:
        project = await get_project_by_clerk_user(conn, project_id, clerk_user_id)
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    decision = resolve(body.mode, body.prompt, is_first_prompt=body.is_first_prompt)
    effective_mode = decision.mode

    log.info("api.generate", project_id=str(project_id), mode=effective_mode, is_first_prompt=body.is_first_prompt)

    if body.is_first_prompt:
        from pipeline.first_prompt import run as first_prompt_run
        job = await enqueue(project_id, session_id, "max")
        await job_start(job.id)
        background_tasks.add_task(first_prompt_run, project_id, session_id, body.prompt)
    else:
        job = await enqueue(project_id, session_id, effective_mode)
        await job_start(job.id)
        background_tasks.add_task(_run_generation, project_id, session_id, job.id, body.prompt, effective_mode)

    return GenerateResponse(
        job_id=str(job.id),
        mode=effective_mode,
        mismatch_suggestion=decision.mismatch_suggestion,
    )
