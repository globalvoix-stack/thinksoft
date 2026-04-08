"""
Orchestrator agent — Sonnet 4.6.

Coordinates multi-agent pipelines: breaks down the task, assigns sub-agents,
accumulates results into the context bus, and produces the final plan.
"""
from __future__ import annotations

import json
from typing import Any

import structlog

from agents.base import AgentInput, AgentOutput, BaseAgent
from context import bus as ctx_bus
from integrations.anthropic import sonnet
from memory import read as memory_read

log = structlog.get_logger(__name__)

_SYSTEM = """You are the Orchestrator for Thinksoft — a senior software architect.
Your job: analyze the user request, break it into tasks for specialist agents,
and produce a structured execution plan.

Respond with a JSON object:
{
  "intent": "brief description of what the user wants",
  "industry": "detected industry or null",
  "complexity": 1|2|3,
  "tasks": [
    {"agent": "kimi|gemini|haiku|sonnet|critic", "description": "what to do", "depends_on": []}
  ],
  "design_direction": "visual direction and style notes",
  "tech_stack": "recommended stack"
}
"""


class OrchestratorAgent(BaseAgent):
    name = "orchestrator"

    async def run(self, inp: AgentInput) -> AgentOutput:
        self._log_start(inp)

        # Retrieve relevant memory
        memories = await memory_read(inp.project_id, inp.prompt, limit=5)
        memory_context = "\n".join(f"- [{m.source}] {m.content}" for m in memories)

        context_summary = inp.context.summary()

        user_content = (
            f"Project context:\n{context_summary}\n\n"
            f"Relevant memory:\n{memory_context or 'none'}\n\n"
            f"User request:\n{inp.prompt}"
        )

        try:
            resp = await sonnet(
                [{"role": "user", "content": user_content}],
                system=_SYSTEM,
                max_tokens=1024,
            )

            plan = json.loads(resp.content)
        except (json.JSONDecodeError, Exception) as exc:
            log.error("orchestrator.parse_error", error=str(exc))
            return AgentOutput(
                agent=self.name,
                success=False,
                error=f"Orchestrator failed: {exc}",
            )

        # Record plan in context bus
        inp.context.record_decision(
            self.name,
            f"intent={plan.get('intent', '')} complexity={plan.get('complexity', 1)}",
        )
        inp.context.set_artifact("orchestrator_plan", plan)

        summary = self._trim_summary(
            f"intent={plan.get('intent','')} tasks={len(plan.get('tasks', []))}"
        )

        out = AgentOutput(
            agent=self.name,
            success=True,
            result=plan,
            summary=summary,
            input_tokens=resp.input_tokens,
            output_tokens=resp.output_tokens,
        )
        self._log_done(out)
        return out
