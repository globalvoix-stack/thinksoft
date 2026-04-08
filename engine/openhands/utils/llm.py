"""Stub: LiteLLM utility functions - removed. Thinksoft uses direct AI model clients."""
from typing import Any


def is_openhands_model(model: str | None) -> bool:
    """Check if the model uses the OpenHands provider."""
    return bool(model and model.startswith('openhands/'))


def get_provider_api_base(model: str) -> str | None:
    """Stub: get API base URL for a model."""
    return None


def get_supported_llm_models(config: Any) -> list[str]:
    """Stub: returns empty list. Thinksoft manages its own model registry."""
    return []
