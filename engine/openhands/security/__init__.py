"""Stub: security analyzer - removed. Thinksoft has its own security/ layer using semgrep."""
from typing import Any
from abc import ABC


class SecurityAnalyzer(ABC):
    """Stub abstract base for security analyzers."""

    def set_event_stream(self, event_stream: Any) -> None:
        pass

    async def analyze(self, action: Any) -> Any:
        return action


class _SecurityAnalyzers:
    """Registry stub for security analyzers."""
    _analyzers: dict[str, type] = {}

    def get(self, name: str, default: type | None = None) -> type | None:
        return self._analyzers.get(name, default)

    def register(self, name: str, cls: type) -> None:
        self._analyzers[name] = cls


class _Options:
    SecurityAnalyzers = _SecurityAnalyzers()


options = _Options()

__all__ = ['SecurityAnalyzer', 'options']
