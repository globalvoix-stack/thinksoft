"""Base agent interface — all agents inherit from this."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

import structlog

from config.constants import CONTEXT_BUS_SUMMARY_MAX_TOKENS
from context.bus import ContextBus

log = structlog.get_logger(__name__)


@dataclass
class AgentInput:
    project_id: UUID
    session_id: UUID
    job_id: UUID
    prompt: str
    context: ContextBus
    mode: str
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentOutput:
    agent: str
    success: bool
    result: dict[str, Any] = field(default_factory=dict)
    summary: str = ""
    """Short summary capped at CONTEXT_BUS_SUMMARY_MAX_TOKENS for context bus."""
    error: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0


class BaseAgent(ABC):
    name: str = "base"

    def _trim_summary(self, text: str) -> str:
        """Cap summary at ~CONTEXT_BUS_SUMMARY_MAX_TOKENS tokens (≈4 chars/token)."""
        max_chars = CONTEXT_BUS_SUMMARY_MAX_TOKENS * 4
        return text[:max_chars] if len(text) > max_chars else text

    @abstractmethod
    async def run(self, inp: AgentInput) -> AgentOutput:
        """Execute the agent and return its output."""
        ...

    def _log_start(self, inp: AgentInput) -> None:
        log.info(
            f"{self.name}.start",
            project_id=str(inp.project_id),
            session_id=str(inp.session_id),
            job_id=str(inp.job_id),
            mode=inp.mode,
        )

    def _log_done(self, out: AgentOutput) -> None:
        log.info(
            f"{self.name}.done",
            success=out.success,
            input_tokens=out.input_tokens,
            output_tokens=out.output_tokens,
        )
