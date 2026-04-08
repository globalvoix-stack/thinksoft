"""
First prompt pipeline — always Max mode with deterministic intent extraction.

Public API:
  extract_intent(prompt) — structured intent from raw user request
  run(project_id, session_id, prompt) — full first-prompt pipeline; returns job_id
  IntentResult           — structured intent dataclass
  FirstPromptResult      — job_id + intent + max pipeline result
"""
from pipeline.first_prompt import (
    FirstPromptResult,
    IntentResult,
    extract_intent,
    run,
)

__all__ = ["FirstPromptResult", "IntentResult", "extract_intent", "run"]
