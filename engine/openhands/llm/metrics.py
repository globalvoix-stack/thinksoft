"""Stub: LLM metrics types."""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TokenUsage:
    """Tracks token usage for an LLM call."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass
class ResponseLatency:
    """Tracks latency for an LLM call."""
    first_token_latency: float = 0.0
    total_latency: float = 0.0


@dataclass
class Cost:
    """Tracks cost for an LLM call."""
    prompt_cost: float = 0.0
    completion_cost: float = 0.0
    total_cost: float = 0.0


@dataclass
class Metrics:
    """Aggregated LLM metrics."""
    token_usage: list = field(default_factory=list)
    costs: list = field(default_factory=list)
    latencies: list = field(default_factory=list)

    @property
    def accumulated_cost(self) -> float:
        return sum(getattr(c, 'total_cost', 0) for c in self.costs)

    @property
    def accumulated_token_usage(self) -> TokenUsage:
        total = TokenUsage()
        for u in self.token_usage:
            total.prompt_tokens += getattr(u, 'prompt_tokens', 0)
            total.completion_tokens += getattr(u, 'completion_tokens', 0)
            total.total_tokens += getattr(u, 'total_tokens', 0)
        return total
