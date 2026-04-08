"""
Critic agent — Sonnet 4.6.

Reviews all generated code for quality, consistency, correctness, and security.
Always runs last in the pipeline. Surfaces issues without silently patching them.
"""
from __future__ import annotations

import json
from typing import Any

import structlog

from agents.base import AgentInput, AgentOutput, BaseAgent
from integrations.anthropic import sonnet

log = structlog.get_logger(__name__)

_SYSTEM = """You are a senior code reviewer with expertise in React, FastAPI, and security.
Review the provided generated code artifacts and produce a structured critique.

Respond with a JSON object:
{
  "overall_score": 1-10,
  "passed": true|false,
  "issues": [
    {
      "severity": "critical|high|medium|low",
      "category": "security|correctness|style|performance|consistency",
      "file": str|null,
      "description": str,
      "suggestion": str
    }
  ],
  "summary": "brief overall assessment"
}

passed=true only if no critical or high severity issues exist.
Be thorough. Surface all issues — do not silently ignore problems.
"""


class CriticAgent(BaseAgent):
    name = "critic"

    async def run(self, inp: AgentInput) -> AgentOutput:
        self._log_start(inp)

        # Collect all generated files from context
        ui_files = inp.context.get_artifact("ui_files", [])
        backend_simple = inp.context.get_artifact("backend_files_simple", [])
        backend_complex = inp.context.get_artifact("backend_files_complex", [])
        security_scans = inp.context.get_artifact("security_scans", [])

        all_files = ui_files + backend_simple + backend_complex
        if not all_files:
            return AgentOutput(
                agent=self.name,
                success=True,
                result={"overall_score": 10, "passed": True, "issues": [], "summary": "No files to review"},
                summary="no files to review",
            )

        # Build review payload (cap at ~6000 chars to stay within token budget)
        file_summaries = []
        total_chars = 0
        for f in all_files:
            content = f.get("content", "")[:1500]  # truncate long files
            total_chars += len(content)
            file_summaries.append(f"### {f.get('path', 'unknown')}\n```\n{content}\n```")
            if total_chars > 6000:
                break

        security_summary = ""
        if security_scans:
            failed = [s for s in security_scans if not s.get("passed")]
            if failed:
                security_summary = f"\nSecurity scan failures: {json.dumps(failed, indent=2)}"

        review_content = (
            f"Generated code to review:\n\n"
            + "\n\n".join(file_summaries)
            + security_summary
        )

        try:
            resp = await sonnet(
                [{"role": "user", "content": review_content}],
                system=_SYSTEM,
                max_tokens=2048,
            )

            try:
                result = json.loads(resp.content)
            except json.JSONDecodeError:
                result = {
                    "overall_score": 5,
                    "passed": False,
                    "issues": [{"severity": "medium", "category": "style", "file": None,
                                "description": "Could not parse critic response", "suggestion": "Manual review needed"}],
                    "summary": resp.content[:200],
                }

        except Exception as exc:
            log.error("critic.run.error", error=str(exc))
            return AgentOutput(agent=self.name, success=False, error=str(exc))

        issues = result.get("issues", [])
        critical_issues = [i for i in issues if i.get("severity") in ("critical", "high")]

        if critical_issues:
            log.warning(
                "critic.critical_issues",
                count=len(critical_issues),
                issues=[i.get("description", "")[:80] for i in critical_issues],
            )

        inp.context.record_decision(
            self.name,
            f"score={result.get('overall_score')} passed={result.get('passed')} issues={len(issues)}",
        )
        inp.context.set_artifact("critic_review", result)

        summary = self._trim_summary(
            f"score={result.get('overall_score')} issues={len(issues)} "
            f"critical={len(critical_issues)} passed={result.get('passed')}"
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
