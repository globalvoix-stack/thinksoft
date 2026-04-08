"""Stub: LLM registry - removed. Thinksoft manages its own model clients in agents/."""
from typing import Any


class LLMRegistry:
    """Stub: registry for LLM instances."""

    def __init__(self, *args: Any, **kwargs: Any):
        pass

    def subscribe(self, *args: Any, **kwargs: Any) -> None:
        pass

    def get_llm(self, *args: Any, **kwargs: Any) -> Any:
        return None
