"""Stub: microagent framework - removed from core. Thinksoft uses its own agent system."""
from typing import Any
from pathlib import Path
from dataclasses import dataclass


class BaseMicroagent:
    """Stub base class for microagents."""
    name: str = ""
    content: str = ""

    def __init__(self, name: str = "", content: str = ""):
        self.name = name
        self.content = content


class KnowledgeMicroagent(BaseMicroagent):
    """Stub: knowledge-based microagent."""
    triggers: list[str] = []


class RepoMicroagent(BaseMicroagent):
    """Stub: repository-specific microagent."""
    pass


def load_microagents_from_dir(path: str | Path) -> tuple[dict, dict, dict]:
    """Stub: loads microagents from a directory. Returns empty dicts."""
    return {}, {}, {}


__all__ = ['BaseMicroagent', 'KnowledgeMicroagent', 'RepoMicroagent', 'load_microagents_from_dir']
