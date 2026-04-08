"""
Visual Clone / UI agent — Kimi K2.5.

Processes raw competitor screenshots (base64 PNG) and produces a
structured visual analysis + React component scaffold.
Always receives images — never plain text descriptions.
"""
from __future__ import annotations

import json
from typing import Any

import structlog

from agents.base import AgentInput, AgentOutput, BaseAgent
from context import bus as ctx_bus
from integrations.kimi import complete_with_images
from registry import describe_for_agent

log = structlog.get_logger(__name__)

_SYSTEM = """You are a world-class UI engineer specializing in pixel-perfect React clones.
You receive screenshots of competitor/reference websites and produce:
1. Visual analysis (colors, typography, spacing, layout)
2. Component breakdown
3. React + Tailwind implementation scaffold

Respond with a JSON object:
{
  "visual_analysis": {
    "primary_color": str,
    "secondary_color": str,
    "typography": str,
    "layout_type": str,
    "key_sections": [str]
  },
  "components": [{"name": str, "description": str, "props": [str]}],
  "scaffold": "React JSX code string"
}
"""


class KimiAgent(BaseAgent):
    name = "kimi"

    async def run(self, inp: AgentInput) -> AgentOutput:
        self._log_start(inp)

        screenshots: list[str] = inp.extra.get("screenshots", [])
        if not screenshots:
            return AgentOutput(
                agent=self.name,
                success=False,
                error="KimiAgent requires screenshots in extra.screenshots",
            )

        registry_desc = describe_for_agent()
        text_prompt = (
            f"Available libraries:\n{registry_desc}\n\n"
            f"Task:\n{inp.prompt}\n\n"
            f"Analyze the provided screenshot(s) and produce the component scaffold."
        )

        try:
            resp = await complete_with_images(
                text_prompt,
                screenshots,
                system=_SYSTEM,
                max_tokens=8192,
            )

            # Try to parse JSON; fall back to raw content
            try:
                result = json.loads(resp.content)
            except json.JSONDecodeError:
                result = {"scaffold": resp.content}

        except Exception as exc:
            log.error("kimi.run.error", error=str(exc))
            return AgentOutput(agent=self.name, success=False, error=str(exc))

        inp.context.record_decision(
            self.name,
            f"visual_clone: {len(screenshots)} screenshot(s) analyzed",
        )
        inp.context.set_artifact("visual_analysis", result.get("visual_analysis", {}))
        inp.context.set_artifact("kimi_components", result.get("components", []))

        summary = self._trim_summary(
            f"components={len(result.get('components', []))} "
            f"layout={result.get('visual_analysis', {}).get('layout_type', '')}"
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
