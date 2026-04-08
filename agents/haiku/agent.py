"""
Simple Backend agent — Haiku 4.5.

Handles straightforward backend tasks: CRUD endpoints, simple schemas,
utility functions, config files. Fast and cost-efficient.
"""
from __future__ import annotations

import json
from typing import Any

import structlog

from agents.base import AgentInput, AgentOutput, BaseAgent
from integrations.anthropic import haiku

log = structlog.get_logger(__name__)

_SYSTEM = """You are a backend developer specializing in FastAPI and Python.
Generate clean, production-ready backend code for simple tasks:
CRUD endpoints, Pydantic schemas, utility functions, config files.

Respond with a JSON object:
{
  "files": [
    {"path": "api/routes/resource.py", "content": "..."},
    ...
  ],
  "summary": "what was generated"
}

Use parameterized queries only. Never hardcode secrets. Use type hints everywhere.
"""


class HaikuAgent(BaseAgent):
    name = "haiku"

    async def run(self, inp: AgentInput) -> AgentOutput:
        self._log_start(inp)

        plan = inp.context.get_artifact("orchestrator_plan", {})
        task_desc = inp.extra.get("task_description", inp.prompt)

        content = (
            f"Project tech stack: {plan.get('tech_stack', 'FastAPI, PostgreSQL')}\n\n"
            f"Task:\n{task_desc}"
        )

        try:
            resp = await haiku(
                [{"role": "user", "content": content}],
                system=_SYSTEM,
                max_tokens=4096,
            )

            try:
                result = json.loads(resp.content)
            except json.JSONDecodeError:
                result = {"files": [{"path": "generated.py", "content": resp.content}], "summary": "Backend generated"}

        except Exception as exc:
            log.error("haiku.run.error", error=str(exc))
            return AgentOutput(agent=self.name, success=False, error=str(exc))

        files = result.get("files", [])
        inp.context.record_decision(self.name, f"generated {len(files)} backend file(s)")
        inp.context.set_artifact("backend_files_simple", files)

        summary = self._trim_summary(
            f"backend_files={len(files)} summary={result.get('summary', '')[:60]}"
        )

        out = AgentOutput(
            agent=self.name,
            success=True,
            result=result,
            summary=summary,
            input_tokens=resp.input_tokens,
            output_tokens=resp.output_tokens,
        )
        self._log_done(out)
        return out
