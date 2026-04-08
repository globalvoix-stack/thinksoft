"""
UI Generation agent — Gemini Flash.

Fast, cost-efficient UI component generation.
Used for Light mode micro-edits and Autonomous/Max mode bulk component generation.
"""
from __future__ import annotations

import json
from typing import Any

import structlog

from agents.base import AgentInput, AgentOutput, BaseAgent
from integrations.gemini import flash
from registry import describe_for_agent

log = structlog.get_logger(__name__)

_SYSTEM = """You are an expert React/Tailwind UI developer.
Generate clean, production-ready React components with Tailwind CSS.
Use the specified UI library components where appropriate.
Respond with a JSON object:
{
  "files": [
    {"path": "src/components/ComponentName.tsx", "content": "..."},
    ...
  ],
  "summary": "what was generated"
}
"""


class GeminiAgent(BaseAgent):
    name = "gemini"

    async def run(self, inp: AgentInput) -> AgentOutput:
        self._log_start(inp)

        visual_analysis = inp.context.get_artifact("visual_analysis", {})
        kimi_scaffold = inp.context.get_artifact("kimi_components", [])
        registry_desc = describe_for_agent()
        plan = inp.context.get_artifact("orchestrator_plan", {})

        prompt_parts = [
            f"Available libraries:\n{registry_desc}",
            f"\nDesign direction:\n{plan.get('design_direction', inp.prompt)}",
        ]
        if visual_analysis:
            prompt_parts.append(f"\nVisual analysis:\n{json.dumps(visual_analysis, indent=2)}")
        if kimi_scaffold:
            prompt_parts.append(f"\nComponent blueprint:\n{json.dumps(kimi_scaffold, indent=2)}")
        prompt_parts.append(f"\nTask:\n{inp.prompt}")

        full_prompt = "\n".join(prompt_parts)

        try:
            resp = await flash(
                full_prompt,
                system=_SYSTEM,
                max_tokens=8192,
            )

            try:
                result = json.loads(resp.content)
            except json.JSONDecodeError:
                result = {"files": [{"path": "generated.tsx", "content": resp.content}], "summary": "UI generated"}

        except Exception as exc:
            log.error("gemini.run.error", error=str(exc))
            return AgentOutput(agent=self.name, success=False, error=str(exc))

        files = result.get("files", [])
        inp.context.record_decision(
            self.name,
            f"generated {len(files)} UI file(s)",
        )
        inp.context.set_artifact("ui_files", files)

        summary = self._trim_summary(
            f"ui_files={len(files)} summary={result.get('summary', '')[:60]}"
        )

        out = AgentOutput(
            agent=self.name,
            success=True,
            result=result,
            summary=summary,
            input_tokens=resp.prompt_tokens,
            output_tokens=resp.completion_tokens,
        )
        self._log_done(out)
        return out
