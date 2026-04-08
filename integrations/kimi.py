"""Kimi K2.5 integration — via OpenAI-compatible Moonshot API."""
from __future__ import annotations

import base64
from dataclasses import dataclass, field
from typing import Any

import structlog
from openai import AsyncOpenAI
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from config.constants import KIMI_MODEL
from config.settings import get_settings

log = structlog.get_logger(__name__)


@dataclass
class KimiResponse:
    content: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    finish_reason: str
    raw: dict[str, Any] = field(default_factory=dict)


def _client() -> AsyncOpenAI:
    s = get_settings()
    return AsyncOpenAI(
        api_key=s.kimi_api_key,
        base_url=s.kimi_base_url,
    )


def _image_content_block(image_base64: str, mime_type: str = "image/png") -> dict[str, Any]:
    return {
        "type": "image_url",
        "image_url": {"url": f"data:{mime_type};base64,{image_base64}"},
    }


@retry(
    retry=retry_if_exception_type(Exception),
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=1, min=2, max=16),
    reraise=True,
)
async def complete(
    messages: list[dict[str, Any]],
    *,
    model: str = KIMI_MODEL,
    system: str | None = None,
    max_tokens: int = 4096,
    temperature: float = 0.7,
) -> KimiResponse:
    """Send a completion request to Kimi via the Moonshot OpenAI-compatible API."""
    log.info("kimi.complete.start", model=model, message_count=len(messages))

    full_messages: list[dict[str, Any]] = []
    if system:
        full_messages.append({"role": "system", "content": system})
    full_messages.extend(messages)

    client = _client()
    resp = await client.chat.completions.create(
        model=model,
        messages=full_messages,
        max_tokens=max_tokens,
        temperature=temperature,
    )

    choice = resp.choices[0]
    result = KimiResponse(
        content=choice.message.content or "",
        model=resp.model,
        prompt_tokens=resp.usage.prompt_tokens if resp.usage else 0,
        completion_tokens=resp.usage.completion_tokens if resp.usage else 0,
        finish_reason=choice.finish_reason or "",
        raw=resp.model_dump(),
    )
    log.info(
        "kimi.complete.done",
        model=model,
        prompt_tokens=result.prompt_tokens,
        completion_tokens=result.completion_tokens,
    )
    return result


async def complete_with_images(
    text_prompt: str,
    images_base64: list[str],
    *,
    system: str | None = None,
    max_tokens: int = 8192,
) -> KimiResponse:
    """
    Send a multimodal completion with raw screenshot images.

    Kimi K2.5 processes base64-encoded images directly.
    images_base64: list of base64-encoded PNG/JPEG strings (no data: prefix).
    """
    content: list[dict[str, Any]] = [{"type": "text", "text": text_prompt}]
    for img in images_base64:
        content.append(_image_content_block(img))

    messages = [{"role": "user", "content": content}]
    return await complete(messages, system=system, max_tokens=max_tokens)
