"""Google Gemini integration — Gemini Flash for UI generation."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import structlog
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from config.constants import GEMINI_FLASH_MODEL
from config.settings import get_settings

log = structlog.get_logger(__name__)


@dataclass
class GeminiResponse:
    content: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    finish_reason: str
    raw: dict[str, Any] = field(default_factory=dict)


def _build_client():  # type: ignore[return]
    import google.generativeai as genai  # type: ignore[import]
    genai.configure(api_key=get_settings().google_ai_api_key)
    return genai


@retry(
    retry=retry_if_exception_type(Exception),
    stop=stop_after_attempt(4),
    wait=wait_exponential(multiplier=1, min=2, max=16),
    reraise=True,
)
async def complete(
    prompt: str,
    *,
    model: str = GEMINI_FLASH_MODEL,
    system: str | None = None,
    max_tokens: int = 4096,
    temperature: float = 0.7,
) -> GeminiResponse:
    """Send a generation request to Gemini."""
    import asyncio

    import google.generativeai as genai  # type: ignore[import]
    import google.generativeai.types as genai_types  # type: ignore[import]

    log.info("gemini.complete.start", model=model)
    genai.configure(api_key=get_settings().google_ai_api_key)

    gen_model = genai.GenerativeModel(
        model_name=model,
        system_instruction=system,
        generation_config=genai_types.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
        ),
    )

    loop = asyncio.get_event_loop()
    resp = await loop.run_in_executor(None, gen_model.generate_content, prompt)

    try:
        content = resp.text
    except Exception:
        content = ""

    usage = getattr(resp, "usage_metadata", None)
    result = GeminiResponse(
        content=content,
        model=model,
        prompt_tokens=getattr(usage, "prompt_token_count", 0) if usage else 0,
        completion_tokens=getattr(usage, "candidates_token_count", 0) if usage else 0,
        finish_reason=str(getattr(resp.candidates[0], "finish_reason", "")) if resp.candidates else "",
        raw={},
    )
    log.info(
        "gemini.complete.done",
        model=model,
        prompt_tokens=result.prompt_tokens,
        completion_tokens=result.completion_tokens,
    )
    return result


async def flash(
    prompt: str,
    *,
    system: str | None = None,
    max_tokens: int = 4096,
) -> GeminiResponse:
    """Convenience wrapper for Gemini Flash."""
    return await complete(prompt, model=GEMINI_FLASH_MODEL, system=system, max_tokens=max_tokens)
