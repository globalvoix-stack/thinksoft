"""
SSE streaming — Server-Sent Events for job progress.

Heartbeat every SSE_HEARTBEAT_SECONDS to keep connections alive.
Polls Neon for job status updates and streams events to clients.
"""
from __future__ import annotations

import asyncio
import json
from typing import AsyncGenerator
from uuid import UUID

import structlog

from config.constants import JOB_TIMEOUT_SECONDS, SSE_HEARTBEAT_SECONDS
from queue.manager import get

log = structlog.get_logger(__name__)

_POLL_INTERVAL = 1.0  # seconds between DB polls
_TERMINAL_STATUSES = {"done", "failed"}


def _event(event_type: str, data: dict) -> str:
    """Format a single SSE message."""
    return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"


def _heartbeat() -> str:
    return ": heartbeat\n\n"


async def stream_job(job_id: UUID) -> AsyncGenerator[str, None]:
    """
    Yield SSE events for a job until it reaches a terminal state.

    Events emitted:
      - progress: {job_id, status, progress, current_step}
      - done:     {job_id, result}
      - error:    {job_id, error}
      - heartbeat: comment line every SSE_HEARTBEAT_SECONDS

    Terminates after JOB_TIMEOUT_SECONDS regardless of job state.
    """
    log.info("sse.stream.start", job_id=str(job_id))
    elapsed = 0.0
    last_heartbeat = 0.0

    while elapsed < JOB_TIMEOUT_SECONDS:
        await asyncio.sleep(_POLL_INTERVAL)
        elapsed += _POLL_INTERVAL
        last_heartbeat += _POLL_INTERVAL

        # Heartbeat
        if last_heartbeat >= SSE_HEARTBEAT_SECONDS:
            yield _heartbeat()
            last_heartbeat = 0.0

        job = await get(job_id)
        if job is None:
            yield _event("error", {"job_id": str(job_id), "error": "Job not found"})
            return

        if job.status in _TERMINAL_STATUSES:
            if job.status == "done":
                yield _event("done", {
                    "job_id": str(job_id),
                    "result": job.result or {},
                })
            else:
                yield _event("error", {
                    "job_id": str(job_id),
                    "error": job.error or "Job failed",
                })
            log.info("sse.stream.done", job_id=str(job_id), status=job.status)
            return

        yield _event("progress", {
            "job_id": str(job_id),
            "status": job.status,
            "progress": job.progress,
            "current_step": job.current_step,
        })

    # Timeout guard
    yield _event("error", {
        "job_id": str(job_id),
        "error": f"SSE stream timed out after {JOB_TIMEOUT_SECONDS}s",
    })
    log.warning("sse.stream.timeout", job_id=str(job_id))


async def stream_job_sse_starlette(job_id: UUID) -> AsyncGenerator[dict, None]:
    """
    Yield dicts compatible with sse-starlette's EventSourceResponse.

    Each dict has 'event' and 'data' keys.
    """
    log.info("sse.starlette.start", job_id=str(job_id))
    elapsed = 0.0
    last_heartbeat = 0.0

    while elapsed < JOB_TIMEOUT_SECONDS:
        await asyncio.sleep(_POLL_INTERVAL)
        elapsed += _POLL_INTERVAL
        last_heartbeat += _POLL_INTERVAL

        if last_heartbeat >= SSE_HEARTBEAT_SECONDS:
            yield {"event": "heartbeat", "data": ""}
            last_heartbeat = 0.0

        job = await get(job_id)
        if job is None:
            yield {"event": "error", "data": json.dumps({"error": "Job not found"})}
            return

        if job.status in _TERMINAL_STATUSES:
            if job.status == "done":
                yield {
                    "event": "done",
                    "data": json.dumps({"job_id": str(job_id), "result": job.result or {}}),
                }
            else:
                yield {
                    "event": "error",
                    "data": json.dumps({"job_id": str(job_id), "error": job.error or "failed"}),
                }
            return

        yield {
            "event": "progress",
            "data": json.dumps({
                "job_id": str(job_id),
                "status": job.status,
                "progress": job.progress,
                "current_step": job.current_step,
            }),
        }

    yield {
        "event": "error",
        "data": json.dumps({"error": f"stream timed out after {JOB_TIMEOUT_SECONDS}s"}),
    }
