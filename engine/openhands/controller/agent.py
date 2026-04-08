"""Stub: Agent base class - removed."""
from typing import Any
from abc import ABC


class Agent(ABC):
    """Stub base class for agents. Thinksoft agents live in agents/."""
    AGENT_REGISTRY: dict[str, type] = {}

    @classmethod
    def register(cls, name: str, agent_cls: type) -> None:
        cls.AGENT_REGISTRY[name] = agent_cls

    @classmethod
    def get_cls(cls, name: str) -> type | None:
        return cls.AGENT_REGISTRY.get(name)
