"""
Light mode handler — Gemini Flash or Haiku 4.5.

Constraints:
- Sub-5 second synchronous response
- Never touches context bus
- Never reads or writes memory
- Uses Gemini Flash for UI, Haiku for backend changes
- Single-agent, no pipeline
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

import structlog

from integrations.anthropic import haiku
from integrations.gemini import flash

log = structlog.get_logger(__name__)

_UI_TRIGGERS = ["component", "style", "css", "tailwind", "color", "layout", "ui", "button", "form"]

_UI_SYSTEM = "You are a React/Tailwind expert. Return only the changed file content."
_BACKEND_SYSTEM = "You are a Python/FastAPI expert. Return only the changed code. No explanations."


@dataclass
class LightModeResult:
    content: str
    model_used: str
    input_tokens: int
    output_tokens: int
    files: list[dict[str, Any]] = field(default_factory=list)


def _is_ui_request(prompt: str) -> bool:
    lower = prompt.lower()
    return any(trigger in lower for trigger in _UI_TRIGGERS)


async def run(prompt: str, *, context_hint: str = "") -> LightModeResult:
    """
    Handle a Light mode request synchronously.

    Never reads/writes memory or context bus.
    Routes to Gemini Flash (UI) or Haiku (backend).
    """
    log.info("light.run.start", prompt_length=len(prompt))

    full_prompt = prompt
    if context_hint:
        full_prompt = f"Context:\n{context_hint}\n\nTask:\n{prompt}"

    if _is_ui_request(prompt):
        resp = await flash(full_prompt, system=_UI_SYSTEM, max_tokens=2048)
        result = LightModeResult(
            content=resp.content,
            model_used=resp.model,
            input_tokens=resp.prompt_tokens,
            output_tokens=resp.completion_tokens,
        )
        log.info("light.run.done", model="gemini_flash", tokens=resp.completion_tokens)
    else:
        resp = await haiku(
            [{"role": "user", "content": full_prompt}],
            system=_BACKEND_SYSTEM,
            max_tokens=2048,
        )
        result = LightModeResult(
            content=resp.content,
            model_used=resp.model,
            input_tokens=resp.input_tokens,
            output_tokens=resp.output_tokens,
        )
        log.info("light.run.done", model="haiku", tokens=resp.output_tokens)

    return result
