"""
Mode router — determines and validates mode for a request.

Three modes:
  light      — micro edits, Gemini/Haiku, sub-5s sync response. No context bus. No memory writes.
  autonomous — orchestrator + context bus + memory. Standard multi-agent pipeline.
  max        — full team + competitor scraping + Kimi screenshots. First prompt always max.

Mismatch detection: non-blocking. If the request seems mismatched with the selected mode,
attach a suggestion to the context bus without blocking execution.
"""
from __future__ import annotations

from dataclasses import dataclass

import structlog

from config.constants import COMPLEXITY_THRESHOLD, MISMATCH_SUGGESTION_THRESHOLD

log = structlog.get_logger(__name__)

LIGHT = "light"
AUTONOMOUS = "autonomous"
MAX = "max"

VALID_MODES = {LIGHT, AUTONOMOUS, MAX}

# Signals that suggest a request is too complex for Light mode
_COMPLEXITY_SIGNALS = [
    "build", "create", "generate", "implement", "scaffold", "new project",
    "authentication", "database", "payment", "deploy", "architecture",
]

# Signals that suggest a request is too simple for Max mode
_SIMPLICITY_SIGNALS = [
    "fix typo", "change color", "update text", "rename", "small change",
    "quick edit", "minor", "tweak",
]


@dataclass
class ModeDecision:
    mode: str
    mismatch_suggestion: str | None
    """Non-None when the request seems mismatched with the chosen mode."""
    complexity_score: int
    """0-3: 0=trivial, 1=simple, 2=moderate, 3=complex"""


def detect_complexity(prompt: str) -> int:
    """
    Heuristic complexity scoring: 0–3.
    0 = trivial edit, 3 = full project build.
    """
    lower = prompt.lower()
    signals_hit = sum(1 for s in _COMPLEXITY_SIGNALS if s in lower)
    if signals_hit >= 3:
        return 3
    if signals_hit >= 2:
        return 2
    if signals_hit >= 1:
        return 1
    return 0


def resolve(
    requested_mode: str,
    prompt: str,
    *,
    is_first_prompt: bool = False,
) -> ModeDecision:
    """
    Resolve the effective mode and detect mismatches.

    First prompt is always MAX regardless of requested mode.
    Mismatch detection is non-blocking: suggestion is attached, mode is not overridden.
    """
    if requested_mode not in VALID_MODES:
        log.warning("mode.invalid", requested=requested_mode, fallback=AUTONOMOUS)
        requested_mode = AUTONOMOUS

    # First prompt always runs Max
    if is_first_prompt:
        mode = MAX
        if requested_mode != MAX:
            log.info("mode.first_prompt_override", requested=requested_mode, resolved=MAX)
    else:
        mode = requested_mode

    complexity = detect_complexity(prompt)
    mismatch: str | None = None

    if mode == LIGHT and complexity >= COMPLEXITY_THRESHOLD:
        mismatch = (
            f"This request (complexity={complexity}) may be too complex for Light mode. "
            f"Consider switching to Autonomous mode for better results."
        )
        log.info("mode.mismatch_detected", mode=mode, complexity=complexity, suggestion=mismatch)

    elif mode == MAX:
        lower = prompt.lower()
        simplicity_hits = sum(1 for s in _SIMPLICITY_SIGNALS if s in lower)
        if simplicity_hits >= 1 and complexity == 0:
            mismatch = (
                "This appears to be a simple edit. "
                "Light mode would be faster and cheaper."
            )
            log.info("mode.mismatch_detected", mode=mode, suggestion=mismatch)

    return ModeDecision(mode=mode, mismatch_suggestion=mismatch, complexity_score=complexity)
