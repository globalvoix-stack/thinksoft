"""
Context bus — shared session state for multi-agent coordination.

Public API:
  load(project_id, session_id)  — load latest snapshot or create fresh bus
  save(bus, mode=)              — persist snapshot; Light mode forbidden
  update_agent_status(...)      — set agent status + optional persist
  get_history(...)              — list all snapshots for a session

  ContextBus                    — the in-memory state document
  AGENT_IDLE / AGENT_RUNNING / AGENT_DONE / AGENT_ERROR  — status constants
"""
from context.bus import (
    AGENT_DONE,
    AGENT_ERROR,
    AGENT_IDLE,
    AGENT_RUNNING,
    ContextBus,
    get_history,
    load,
    save,
    update_agent_status,
)

__all__ = [
    "ContextBus",
    "AGENT_IDLE",
    "AGENT_RUNNING",
    "AGENT_DONE",
    "AGENT_ERROR",
    "load",
    "save",
    "update_agent_status",
    "get_history",
]
