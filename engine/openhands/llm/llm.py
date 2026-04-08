"""Stub: LLM wrapper - removed. Thinksoft uses direct AI model clients."""
from typing import Any
from engine.openhands.llm.metrics import Metrics
from engine.openhands.core.config.llm_config import LLMConfig


class LLM:
    """Stub: LLM instance wrapper."""

    def __init__(self, config: LLMConfig | None = None, *args: Any, **kwargs: Any):
        self.config = config
        self.metrics = Metrics()
