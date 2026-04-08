"""
Job queue manager — Neon-backed job lifecycle management.

Jobs move through: pending → running → completed | failed.
Stale jobs (>5 min in running state) are timed out automatically.
"""
from __future__ import annotations

import asyncio
from typing import Any
from uuid import UUID

import structlog

from config.constants import JOB_TIMEOUT_SECONDS
from db.pool import acquire
from db.queries.jobs import (
    Job,
    complete_job,
    create_job,
    fail_job,
    get_job,
    list_project_jobs,
    mark_job_running,
    timeout_stale_jobs,
    update_job_progress,
)

log = structlog.get_logger(__name__)


async def enqueue(
    project_id: UUID,
    session_id: UUID,
    mode: str,
    *,
    metadata: dict[str, Any] | None = None,
) -> Job:
    """Create a new pending job in Neon."""
    async with acquire() as conn:
        job = await create_job(
            conn,
            project_id=project_id,
            session_id=session_id,
            mode=mode,
            metadata=metadata or {},
        )
    log.info("queue.enqueue", job_id=str(job.id), mode=mode, project_id=str(project_id))
    return job


async def start(job_id: UUID) -> Job | None:
    """Transition a job from pending → running."""
    async with acquire() as conn:
        job = await mark_job_running(conn, job_id)
    if job:
        log.info("queue.start", job_id=str(job_id))
    return job


async def progress(job_id: UUID, pct: int, message: str = "") -> None:
    """Update job progress (0–100) and optional status message."""
    async with acquire() as conn:
        await update_job_progress(conn, job_id, pct, message)
    log.debug("queue.progress", job_id=str(job_id), pct=pct, message=message)


async def complete(job_id: UUID, result: dict[str, Any] | None = None) -> Job | None:
    """Mark job as completed with optional result payload."""
    async with acquire() as conn:
        job = await complete_job(conn, job_id, result or {})
    if job:
        log.info("queue.complete", job_id=str(job_id))
    return job


async def fail(job_id: UUID, error: str) -> Job | None:
    """Mark job as failed with error message."""
    async with acquire() as conn:
        job = await fail_job(conn, job_id, error)
    if job:
        log.error("queue.fail", job_id=str(job_id), error=error)
    return job


async def get(job_id: UUID) -> Job | None:
    """Fetch a job by ID."""
    async with acquire() as conn:
        return await get_job(conn, job_id)


async def list_for_project(project_id: UUID, *, limit: int = 20) -> list[Job]:
    """List recent jobs for a project."""
    async with acquire() as conn:
        return await list_project_jobs(conn, project_id, limit=limit)


async def sweep_stale() -> int:
    """
    Timeout jobs that have been running longer than JOB_TIMEOUT_SECONDS.

    Returns the number of jobs timed out.
    Call periodically (e.g. from a background task).
    """
    async with acquire() as conn:
        count = await timeout_stale_jobs(conn, timeout_seconds=JOB_TIMEOUT_SECONDS)
    if count:
        log.warning("queue.sweep_stale", timed_out=count)
    return count


async def run_with_timeout(
    job_id: UUID,
    coro: Any,
    *,
    timeout: int = JOB_TIMEOUT_SECONDS,
) -> Any:
    """
    Run a coroutine with a timeout. Marks the job failed on error or timeout.

    Returns the coroutine result on success.
    """
    try:
        result = await asyncio.wait_for(coro, timeout=timeout)
        return result
    except asyncio.TimeoutError:
        await fail(job_id, f"Job timed out after {timeout} seconds")
        raise
    except Exception as exc:
        await fail(job_id, str(exc))
        raise
