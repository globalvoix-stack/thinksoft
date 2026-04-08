"""
Asyncpg connection pool with Neon serverless cold-start retry logic.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

import asyncpg
import structlog
from asyncpg import Connection, Pool
from tenacity import (
    before_sleep_log,
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from config.settings import get_settings

logger = structlog.get_logger(__name__)

_pool: Pool | None = None


def _is_retryable(exc: BaseException) -> bool:
    """Neon cold starts and transient connection errors are retryable."""
    if isinstance(exc, (OSError, ConnectionRefusedError)):
        return True
    if isinstance(exc, asyncpg.PostgresConnectionError):
        return True
    if isinstance(exc, asyncpg.TooManyConnectionsError):
        return True
    msg = str(exc).lower()
    return any(kw in msg for kw in ("connection", "timeout", "endpoint is disabled"))


@retry(
    retry=retry_if_exception_type(Exception),
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=1, max=8),
    before_sleep=before_sleep_log(logger, "warning"),
    reraise=True,
)
async def get_pool() -> Pool:
    """Return the shared connection pool, creating it on first call."""
    global _pool
    if _pool is not None and not _pool._closed:  # type: ignore[attr-defined]
        return _pool

    settings = get_settings()
    dsn = str(settings.neon_database_url)

    logger.info("creating database pool")
    _pool = await asyncpg.create_pool(
        dsn,
        min_size=1,
        max_size=10,
        command_timeout=30,
        max_inactive_connection_lifetime=300,  # Neon hibernates after 5 min
        server_settings={"application_name": "thinksoft"},
    )
    logger.info("database pool created", min_size=1, max_size=10)
    return _pool


async def close_pool() -> None:
    """Gracefully close the pool on shutdown."""
    global _pool
    if _pool and not _pool._closed:  # type: ignore[attr-defined]
        await _pool.close()
        _pool = None
        logger.info("database pool closed")


@asynccontextmanager
async def acquire() -> AsyncGenerator[Connection, None]:
    """Async context manager: acquire a connection from the pool.

    Usage:
        async with acquire() as conn:
            await conn.fetch(...)
    """
    pool = await get_pool()
    async with pool.acquire() as conn:
        yield conn
