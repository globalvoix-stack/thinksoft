"""Stub: Agent execution state."""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class State:
    """Stub: holds agent execution state."""
    iteration: int = 0
    max_iterations: int = 100
    history: list = field(default_factory=list)
    inputs: dict = field(default_factory=dict)
    outputs: dict = field(default_factory=dict)
    extra_data: dict = field(default_factory=dict)
