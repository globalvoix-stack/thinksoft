"""
Context Bus — shared session state document for multi-agent coordination.

Tracks:
  - Agent statuses (idle / running / done / error)
  - Active job reference
  - Accumulated decisions and artifacts per session
  - Snapshot versioning (every meaningful state change persisted to Neon)

Light mode: read-only. Never writes to context bus from Light mode.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID

import structlog

from db.pool import acquire
from db.queries.context import (
    ContextSnapshot,
    get_latest_snapshot,
    list_session_snapshots,
    save_snapshot,
)

log = structlog.get_logger(__name__)

# Agent status values
AGENT_IDLE = "idle"
AGENT_RUNNING = "running"
AGENT_DONE = "done"
AGENT_ERROR = "error"

_VALID_STATUSES = {AGENT_IDLE, AGENT_RUNNING, AGENT_DONE, AGENT_ERROR}


@dataclass
class ContextBus:
    """
    In-memory context bus for a single session.

    Backed by Neon for persistence and snapshot versioning.
    Serialize/deserialize via to_dict/from_dict.
    """
    project_id: UUID
    session_id: UUID
    job_id: UUID | None = None
    mode: str = "autonomous"
    agent_statuses: dict[str, str] = field(default_factory=dict)
    """agent_name → status"""
    decisions: list[dict[str, Any]] = field(default_factory=list)
    """Chronological list of {agent, decision, timestamp} records."""
    artifacts: dict[str, Any] = field(default_factory=dict)
    """Keyed by artifact name (e.g. 'design_tokens', 'component_tree')."""
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "project_id": str(self.project_id),
            "session_id": str(self.session_id),
            "job_id": str(self.job_id) if self.job_id else None,
            "mode": self.mode,
            "agent_statuses": self.agent_statuses,
            "decisions": self.decisions,
            "artifacts": self.artifacts,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "ContextBus":
        return cls(
            project_id=UUID(d["project_id"]),
            session_id=UUID(d["session_id"]),
            job_id=UUID(d["job_id"]) if d.get("job_id") else None,
            mode=d.get("mode", "autonomous"),
            agent_statuses=d.get("agent_statuses", {}),
            decisions=d.get("decisions", []),
            artifacts=d.get("artifacts", {}),
            metadata=d.get("metadata", {}),
        )

    def set_agent_status(self, agent: str, status: str) -> None:
        if status not in _VALID_STATUSES:
            raise ValueError(f"Invalid agent status: {status!r}. Must be one of {_VALID_STATUSES}")
        self.agent_statuses[agent] = status
        log.debug("context_bus.agent_status", agent=agent, status=status)

    def record_decision(self, agent: str, decision: str, **extra: Any) -> None:
        entry = {
            "agent": agent,
            "decision": decision,
            "timestamp": datetime.utcnow().isoformat(),
            **extra,
        }
        self.decisions.append(entry)
        log.debug("context_bus.decision", agent=agent, decision=decision[:80])

    def set_artifact(self, name: str, value: Any) -> None:
        self.artifacts[name] = value
        log.debug("context_bus.artifact_set", name=name)

    def get_artifact(self, name: str, default: Any = None) -> Any:
        return self.artifacts.get(name, default)

    def all_agents_done(self, expected_agents: list[str]) -> bool:
        return all(
            self.agent_statuses.get(a) in (AGENT_DONE, AGENT_ERROR)
            for a in expected_agents
        )

    def summary(self, max_tokens: int = 100) -> str:
        """
        Return a brief summary of context bus state, capped approximately by token count.
        100 tokens ≈ 400 chars.
        """
        parts = [
            f"mode={self.mode}",
            f"agents={self.agent_statuses}",
            f"decisions={len(self.decisions)}",
            f"artifacts={list(self.artifacts.keys())}",
        ]
        text = " | ".join(parts)
        return text[: max_tokens * 4]


async def load(project_id: UUID, session_id: UUID) -> ContextBus:
    """Load the latest context bus snapshot from Neon, or return a fresh bus."""
    async with acquire() as conn:
        snapshot = await get_latest_snapshot(conn, project_id, session_id)
    if snapshot:
        bus = ContextBus.from_dict(snapshot.snapshot)
        log.info("context_bus.loaded", project_id=str(project_id), session_id=str(session_id))
        return bus
    log.info("context_bus.new", project_id=str(project_id), session_id=str(session_id))
    return ContextBus(project_id=project_id, session_id=session_id)


async def save(bus: ContextBus, *, mode: str) -> ContextSnapshot:
    """
    Persist the current bus state as a new snapshot.

    Raises ValueError if called from Light mode.
    """
    if mode == "light":
        raise ValueError("Light mode must never write to the context bus")

    log.info(
        "context_bus.save",
        project_id=str(bus.project_id),
        session_id=str(bus.session_id),
    )
    async with acquire() as conn:
        snapshot = await save_snapshot(
            conn,
            project_id=bus.project_id,
            session_id=bus.session_id,
            snapshot=bus.to_dict(),
        )
    return snapshot


async def update_agent_status(
    bus: ContextBus,
    agent: str,
    status: str,
    *,
    mode: str,
    persist: bool = True,
) -> None:
    """Update agent status and optionally persist snapshot."""
    bus.set_agent_status(agent, status)
    if persist:
        await save(bus, mode=mode)


async def get_history(
    project_id: UUID, session_id: UUID
) -> list[ContextSnapshot]:
    """Return all snapshots for a session in chronological order."""
    async with acquire() as conn:
        return await list_session_snapshots(conn, project_id, session_id)
