"""Semgrep integration — static security analysis via subprocess."""
from __future__ import annotations

import asyncio
import json
import tempfile
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import structlog

from config.constants import SEMGREP_TIMEOUT_SECONDS

log = structlog.get_logger(__name__)


@dataclass
class SemgrepFinding:
    rule_id: str
    message: str
    severity: str
    file_path: str
    start_line: int
    end_line: int
    code_snippet: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SemgrepResult:
    findings: list[SemgrepFinding]
    errors: list[str]
    exit_code: int


async def scan_code(
    code: str,
    language: str,
    *,
    ruleset: str = "p/security-audit",
) -> SemgrepResult:
    """
    Scan a code string for security issues using Semgrep.

    Writes code to a temp file, runs semgrep, parses JSON output.
    """
    log.info("semgrep.scan.start", language=language, ruleset=ruleset, code_length=len(code))

    ext_map = {
        "python": ".py",
        "javascript": ".js",
        "typescript": ".ts",
        "tsx": ".tsx",
        "jsx": ".jsx",
        "go": ".go",
        "java": ".java",
        "ruby": ".rb",
        "rust": ".rs",
    }
    ext = ext_map.get(language.lower(), ".txt")

    with tempfile.TemporaryDirectory() as tmpdir:
        src_file = Path(tmpdir) / f"target{ext}"
        src_file.write_text(code, encoding="utf-8")

        cmd = [
            "semgrep",
            "--config", ruleset,
            "--json",
            "--no-git-ignore",
            "--timeout", str(SEMGREP_TIMEOUT_SECONDS),
            str(src_file),
        ]

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(), timeout=SEMGREP_TIMEOUT_SECONDS + 5
            )
            exit_code = proc.returncode or 0
        except FileNotFoundError:
            log.warning("semgrep.not_installed")
            return SemgrepResult(findings=[], errors=["semgrep not found in PATH"], exit_code=-1)
        except asyncio.TimeoutError:
            log.warning("semgrep.timeout", timeout=SEMGREP_TIMEOUT_SECONDS)
            return SemgrepResult(findings=[], errors=["semgrep timed out"], exit_code=-1)

        findings: list[SemgrepFinding] = []
        errors: list[str] = []

        try:
            output = json.loads(stdout.decode())
            for r in output.get("results", []):
                findings.append(
                    SemgrepFinding(
                        rule_id=r.get("check_id", ""),
                        message=r.get("extra", {}).get("message", ""),
                        severity=r.get("extra", {}).get("severity", ""),
                        file_path=r.get("path", ""),
                        start_line=r.get("start", {}).get("line", 0),
                        end_line=r.get("end", {}).get("line", 0),
                        code_snippet=r.get("extra", {}).get("lines", ""),
                        metadata=r.get("extra", {}).get("metadata", {}),
                    )
                )
            for e in output.get("errors", []):
                errors.append(e.get("message", str(e)))
        except json.JSONDecodeError:
            errors.append(f"semgrep output parse error: {stdout.decode()[:200]}")

    log.info(
        "semgrep.scan.done",
        language=language,
        finding_count=len(findings),
        error_count=len(errors),
        exit_code=exit_code,
    )
    return SemgrepResult(findings=findings, errors=errors, exit_code=exit_code)


async def scan_directory(
    directory: str | Path,
    *,
    ruleset: str = "p/security-audit",
) -> SemgrepResult:
    """Scan an entire directory."""
    directory = Path(directory)
    log.info("semgrep.scan_dir.start", directory=str(directory), ruleset=ruleset)

    cmd = [
        "semgrep",
        "--config", ruleset,
        "--json",
        "--no-git-ignore",
        "--timeout", str(SEMGREP_TIMEOUT_SECONDS),
        str(directory),
    ]

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(), timeout=SEMGREP_TIMEOUT_SECONDS + 10
        )
        exit_code = proc.returncode or 0
    except FileNotFoundError:
        log.warning("semgrep.not_installed")
        return SemgrepResult(findings=[], errors=["semgrep not found in PATH"], exit_code=-1)
    except asyncio.TimeoutError:
        log.warning("semgrep.timeout")
        return SemgrepResult(findings=[], errors=["semgrep timed out"], exit_code=-1)

    findings: list[SemgrepFinding] = []
    errors: list[str] = []

    try:
        output = json.loads(stdout.decode())
        for r in output.get("results", []):
            findings.append(
                SemgrepFinding(
                    rule_id=r.get("check_id", ""),
                    message=r.get("extra", {}).get("message", ""),
                    severity=r.get("extra", {}).get("severity", ""),
                    file_path=r.get("path", ""),
                    start_line=r.get("start", {}).get("line", 0),
                    end_line=r.get("end", {}).get("line", 0),
                    code_snippet=r.get("extra", {}).get("lines", ""),
                    metadata=r.get("extra", {}).get("metadata", {}),
                )
            )
        for e in output.get("errors", []):
            errors.append(e.get("message", str(e)))
    except json.JSONDecodeError:
        errors.append(f"parse error: {stdout.decode()[:200]}")

    log.info("semgrep.scan_dir.done", finding_count=len(findings))
    return SemgrepResult(findings=findings, errors=errors, exit_code=exit_code)
