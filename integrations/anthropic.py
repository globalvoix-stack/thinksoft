"""Anthropic integration — Sonnet 4.6 and Haiku 4.5 clients."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import anthropic
import structlog
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from config.constants import HAIKU_MODEL, SONNET_MODEL
from config.settings import get_settings

log = structlog.get_logger(__name__)


@dataclass
class AnthropicResponse:
    content: str
    model: str
    input_tokens: int
    output_tokens: int
    stop_reason: str
    raw: dict[str, Any] = field(default_factory=dict)


def _client() -> anthropic.AsyncAnthropic:
    return anthropic.AsyncAnthropic(api_key=get_settings().anthropic_api_key)


def _retryable(exc: Exception) -> bool:
    if isinstance(exc, anthropic.RateLimitError):
        return True
    if isinstance(exc, anthropic.APIStatusError) and exc.status_code >= 500:
        return True
    if isinstance(exc, anthropic.APIConnectionError):
        return True
    return False


@retry(
    retry=retry_if_exception_type((anthropic.RateLimitError, anthropic.APIConnectionError)),
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=1, min=2, max=16),
    reraise=True,
)
async def complete(
    messages: list[dict[str, Any]],
    *,
    model: str = SONNET_MODEL,
    system: str | None = None,
    max_tokens: int = 4096,
    tools: list[dict[str, Any]] | None = None,
    temperature: float = 0.7,
) -> AnthropicResponse:
    """Send a chat completion request to Anthropic."""
    log.info("anthropic.complete.start", model=model, message_count=len(messages))

    kwargs: dict[str, Any] = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": messages,
        "temperature": temperature,
    }
    if system:
        kwargs["system"] = system
    if tools:
        kwargs["tools"] = tools

    client = _client()
    resp = await client.messages.create(**kwargs)

    text_blocks = [b.text for b in resp.content if hasattr(b, "text")]
    content = "\n".join(text_blocks)

    result = AnthropicResponse(
        content=content,
        model=resp.model,
        input_tokens=resp.usage.input_tokens,
        output_tokens=resp.usage.output_tokens,
        stop_reason=resp.stop_reason or "",
        raw=resp.model_dump(),
    )
    log.info(
        "anthropic.complete.done",
        model=model,
        input_tokens=result.input_tokens,
        output_tokens=result.output_tokens,
        stop_reason=result.stop_reason,
    )
    return result


async def sonnet(
    messages: list[dict[str, Any]],
    *,
    system: str | None = None,
    max_tokens: int = 4096,
    tools: list[dict[str, Any]] | None = None,
) -> AnthropicResponse:
    """Convenience wrapper for Sonnet 4.6."""
    return await complete(messages, model=SONNET_MODEL, system=system, max_tokens=max_tokens, tools=tools)


async def haiku(
    messages: list[dict[str, Any]],
    *,
    system: str | None = None,
    max_tokens: int = 2048,
    tools: list[dict[str, Any]] | None = None,
) -> AnthropicResponse:
    """Convenience wrapper for Haiku 4.5."""
    return await complete(messages, model=HAIKU_MODEL, system=system, max_tokens=max_tokens, tools=tools)
