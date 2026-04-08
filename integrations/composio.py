"""Composio integration — external platform tool execution."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import structlog
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from config.settings import get_settings

log = structlog.get_logger(__name__)


@dataclass
class ToolExecutionResult:
    action: str
    success: bool
    data: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


def _client():  # type: ignore[return]
    try:
        from composio_openai import ComposioToolSet  # type: ignore[import]
        return ComposioToolSet(api_key=get_settings().composio_api_key if hasattr(get_settings(), "composio_api_key") else "")
    except ImportError:
        raise RuntimeError("composio_openai package not installed")


@retry(
    retry=retry_if_exception_type(Exception),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=8),
    reraise=True,
)
async def execute_action(
    action: str,
    params: dict[str, Any],
    *,
    entity_id: str = "default",
) -> ToolExecutionResult:
    """
    Execute a Composio action for an entity.

    action: Composio action identifier (e.g. "GITHUB_CREATE_ISSUE")
    params: action-specific parameters
    entity_id: the user/entity context for the action
    """
    import asyncio

    log.info("composio.execute.start", action=action, entity_id=entity_id)

    try:
        toolset = _client()
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: toolset.execute_action(
                action=action,
                params=params,
                entity_id=entity_id,
            ),
        )
        log.info("composio.execute.done", action=action, success=True)
        return ToolExecutionResult(action=action, success=True, data=result or {})
    except Exception as exc:
        log.error("composio.execute.error", action=action, error=str(exc))
        return ToolExecutionResult(action=action, success=False, error=str(exc))


async def list_actions(app: str) -> list[str]:
    """List available actions for a Composio app."""
    import asyncio

    log.info("composio.list_actions.start", app=app)
    try:
        toolset = _client()
        loop = asyncio.get_event_loop()
        tools = await loop.run_in_executor(None, lambda: toolset.get_tools(apps=[app]))
        actions = [t.get("name", "") for t in (tools or [])]
        log.info("composio.list_actions.done", app=app, count=len(actions))
        return actions
    except Exception as exc:
        log.error("composio.list_actions.error", app=app, error=str(exc))
        return []
