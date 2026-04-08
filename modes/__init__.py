"""
Mode system — Light / Autonomous / Max.

Public API:
  router.resolve(mode, prompt, is_first_prompt=)  — resolve mode + detect mismatch
  light.run(prompt)                                — fast single-agent response
  autonomous.run(project_id, session_id, job_id, prompt)
  max.run(project_id, session_id, job_id, prompt)

Constants:
  router.LIGHT / AUTONOMOUS / MAX
"""
from modes.router import (
    AUTONOMOUS,
    LIGHT,
    MAX,
    ModeDecision,
    detect_complexity,
    resolve,
)

__all__ = [
    "LIGHT",
    "AUTONOMOUS",
    "MAX",
    "ModeDecision",
    "detect_complexity",
    "resolve",
]
