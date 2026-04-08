"""Stub: conversation stats tracking - removed. Thinksoft tracks via its own db/ layer."""
from typing import Any


class ConversationStats:
    """Stub: tracks per-conversation statistics."""

    def __init__(self, file_store: Any = None, sid: str = "", user_id: str = ""):
        self.file_store = file_store
        self.sid = sid
        self.user_id = user_id
        self.iteration = 0
        self.total_cost = 0.0

    def register_llm(self, *args: Any, **kwargs: Any) -> None:
        pass

    def update_iteration(self, iteration: int) -> None:
        self.iteration = iteration

    def update_cost(self, cost: float) -> None:
        self.total_cost += cost
