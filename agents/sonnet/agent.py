"""
Complex Backend agent — Sonnet 4.6.

Handles complex backend tasks: authentication, database schemas, payment
integration, complex business logic, API design, security-sensitive code.
"""
from __future__ import annotations

import json
from typing import Any

import structlog

from agents.base import AgentInput, AgentOutput, BaseAgent
from integrations.anthropic import sonnet
from security import scan as security_scan
from config.constants import SECURITY_REVIEW_TRIGGERS

log = structlog.get_logger(__name__)

_SYSTEM = """You are a senior backend architect specializing in FastAPI, PostgreSQL, and security.
Handle complex backend tasks: authentication systems, payment flows, database design,
multi-service orchestration, complex business logic.

Respond with a JSON object:
{
  "files": [
    {"path": "...", "content": "...", "language": "python"},
    ...
  ],
  "summary": "what was generated",
  "security_scope": "auth|payment|api_route|other"
}

Requirements:
- Parameterized queries only (no string interpolation in SQL)
- Type hints on every function
- Never hardcode secrets — use environment variables
- Structured error handling
- Input validation at boundaries
"""


class SonnetAgent(BaseAgent):
    name = "sonnet"

    async def run(self, inp: AgentInput) -> AgentOutput:
        self._log_start(inp)

        plan = inp.context.get_artifact("orchestrator_plan", {})
        task_desc = inp.extra.get("task_description", inp.prompt)

        content = (
            f"Project context: {plan.get('tech_stack', 'FastAPI, PostgreSQL')}\n"
            f"Design direction: {plan.get('design_direction', '')}\n\n"
            f"Task:\n{task_desc}"
        )

        try:
            resp = await sonnet(
                [{"role": "user", "content": content}],
                system=_SYSTEM,
                max_tokens=8192,
            )

            try:
                result = json.loads(resp.content)
            except json.JSONDecodeError:
                result = {
                    "files": [{"path": "generated.py", "content": resp.content, "language": "python"}],
                    "summary": "Complex backend generated",
                    "security_scope": "other",
                }

        except Exception as exc:
            log.error("sonnet.run.error", error=str(exc))
            return AgentOutput(agent=self.name, success=False, error=str(exc))

        # Security scan each generated file
        security_scope = result.get("security_scope", "")
        scan_results = []
        for file_info in result.get("files", []):
            code = file_info.get("content", "")
            lang = file_info.get("language", "python")
            scan = await security_scan(code, lang, scope=security_scope)
            if not scan.passed:
                log.warning(
                    "sonnet.security_scan.failed",
                    file=file_info.get("path", ""),
                    finding_count=len(scan.findings),
                )
            scan_results.append({
                "file": file_info.get("path", ""),
                "passed": scan.passed,
                "finding_count": len(scan.findings),
                "findings": [
                    {"severity": f.severity, "description": f.description}
                    for f in scan.findings[:5]
                ],
            })

        result["security_scans"] = scan_results
        files = result.get("files", [])
        inp.context.record_decision(self.name, f"generated {len(files)} complex backend file(s)")
        inp.context.set_artifact("backend_files_complex", files)
        inp.context.set_artifact("security_scans", scan_results)

        summary = self._trim_summary(
            f"backend_files={len(files)} security_scope={security_scope}"
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
