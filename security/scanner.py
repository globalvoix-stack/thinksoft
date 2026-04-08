"""
Security scanner — three-tier analysis pipeline.

Tier 1 — Semgrep static scan: runs on every code generation automatically.
Tier 2 — AI review (Sonnet 4.6): triggered only for auth/payment/new route scopes.
Tier 3 — Deep scan: only when explicitly requested by the user.

Never silently passes risky code. Surfaces all findings.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import structlog

from config.constants import SECURITY_REVIEW_TRIGGERS, SONNET_MODEL
from integrations import semgrep as semgrep_client
from integrations.semgrep import SemgrepFinding

log = structlog.get_logger(__name__)

_AI_REVIEW_SYSTEM = """You are a senior application security engineer.
Review the provided code for security vulnerabilities.
Focus on: authentication/authorization flaws, injection risks, data exposure,
insecure cryptography, SSRF, path traversal, and OWASP Top 10.
Return a JSON array of findings. Each finding: {"severity": "critical|high|medium|low",
"category": str, "line_hint": int|null, "description": str, "recommendation": str}.
If no issues found, return [].
"""


@dataclass
class SecurityFinding:
    severity: str
    category: str
    description: str
    recommendation: str
    source: str
    """'semgrep' | 'ai_review' | 'deep_scan'"""
    rule_id: str | None = None
    line_hint: int | None = None
    file_path: str | None = None


@dataclass
class SecurityScanResult:
    findings: list[SecurityFinding]
    tiers_run: list[str]
    passed: bool
    """True only if no critical/high findings."""


def _semgrep_to_finding(f: SemgrepFinding) -> SecurityFinding:
    return SecurityFinding(
        severity=f.severity or "medium",
        category=f.rule_id,
        description=f.message,
        recommendation="Review and remediate the flagged pattern.",
        source="semgrep",
        rule_id=f.rule_id,
        line_hint=f.start_line or None,
        file_path=f.file_path or None,
    )


async def tier1_semgrep(code: str, language: str) -> list[SecurityFinding]:
    """Run Semgrep static analysis. Always runs."""
    log.info("security.tier1.start", language=language)
    result = await semgrep_client.scan_code(code, language)
    findings = [_semgrep_to_finding(f) for f in result.findings]
    log.info("security.tier1.done", finding_count=len(findings))
    return findings


async def tier2_ai_review(code: str, language: str, scope: str) -> list[SecurityFinding]:
    """
    AI security review with Sonnet 4.6.

    Only called when scope is in SECURITY_REVIEW_TRIGGERS.
    """
    import json

    from integrations.anthropic import sonnet

    log.info("security.tier2.start", scope=scope)

    prompt = f"Language: {language}\nScope: {scope}\n\nCode:\n```{language}\n{code}\n```"
    resp = await sonnet(
        [{"role": "user", "content": prompt}],
        system=_AI_REVIEW_SYSTEM,
        max_tokens=2048,
    )

    findings: list[SecurityFinding] = []
    try:
        raw_list = json.loads(resp.content)
        if isinstance(raw_list, list):
            for item in raw_list:
                findings.append(
                    SecurityFinding(
                        severity=item.get("severity", "medium"),
                        category=item.get("category", "unknown"),
                        description=item.get("description", ""),
                        recommendation=item.get("recommendation", ""),
                        source="ai_review",
                        line_hint=item.get("line_hint"),
                    )
                )
    except (json.JSONDecodeError, TypeError) as exc:
        log.warning("security.tier2.parse_error", error=str(exc))

    log.info("security.tier2.done", finding_count=len(findings))
    return findings


async def tier3_deep_scan(code: str, language: str) -> list[SecurityFinding]:
    """
    Deep scan — Semgrep with comprehensive rulesets.

    Only triggered by explicit user request.
    """
    log.info("security.tier3.start", language=language)

    rulesets = ["p/security-audit", "p/owasp-top-ten", "p/secrets"]
    all_findings: list[SecurityFinding] = []

    for ruleset in rulesets:
        result = await semgrep_client.scan_code(code, language, ruleset=ruleset)
        for f in result.findings:
            finding = _semgrep_to_finding(f)
            finding.source = "deep_scan"
            all_findings.append(finding)

    # Deduplicate by rule_id + line
    seen: set[tuple[str | None, int | None]] = set()
    deduped: list[SecurityFinding] = []
    for f in all_findings:
        key = (f.rule_id, f.line_hint)
        if key not in seen:
            seen.add(key)
            deduped.append(f)

    log.info("security.tier3.done", finding_count=len(deduped))
    return deduped


async def scan(
    code: str,
    language: str,
    *,
    scope: str = "",
    deep: bool = False,
) -> SecurityScanResult:
    """
    Full security scan pipeline.

    Tier 1 always runs.
    Tier 2 runs when scope contains a trigger keyword.
    Tier 3 runs only when deep=True (explicit user request).
    """
    log.info("security.scan.start", language=language, scope=scope, deep=deep)

    all_findings: list[SecurityFinding] = []
    tiers_run: list[str] = []

    # Tier 1 — always
    t1 = await tier1_semgrep(code, language)
    all_findings.extend(t1)
    tiers_run.append("semgrep")

    # Tier 2 — scope triggers
    scope_lower = scope.lower()
    if any(trigger in scope_lower for trigger in SECURITY_REVIEW_TRIGGERS):
        t2 = await tier2_ai_review(code, language, scope)
        all_findings.extend(t2)
        tiers_run.append("ai_review")

    # Tier 3 — explicit request
    if deep:
        t3 = await tier3_deep_scan(code, language)
        all_findings.extend(t3)
        tiers_run.append("deep_scan")

    critical_or_high = {"critical", "high"}
    passed = not any(f.severity.lower() in critical_or_high for f in all_findings)

    if not passed:
        log.warning(
            "security.scan.failed",
            critical_high_count=sum(1 for f in all_findings if f.severity.lower() in critical_or_high),
        )

    return SecurityScanResult(findings=all_findings, tiers_run=tiers_run, passed=passed)
