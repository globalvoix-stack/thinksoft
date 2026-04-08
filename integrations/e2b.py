"""E2B integration — sandboxed code execution."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import structlog
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from config.settings import get_settings

log = structlog.get_logger(__name__)

_DEFAULT_TIMEOUT = 30  # seconds per execution


@dataclass
class ExecutionResult:
    stdout: str
    stderr: str
    exit_code: int
    duration_ms: float
    files: dict[str, str] = field(default_factory=dict)
    """Relative path → file content for any files written during execution."""


@retry(
    retry=retry_if_exception_type(Exception),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=8),
    reraise=True,
)
async def run_code(
    code: str,
    language: str = "python",
    *,
    timeout: int = _DEFAULT_TIMEOUT,
    env_vars: dict[str, str] | None = None,
) -> ExecutionResult:
    """
    Execute code in an E2B sandbox.

    language: "python" | "javascript" | "typescript" | "bash"
    """
    import time

    log.info("e2b.run.start", language=language, code_length=len(code))

    try:
        from e2b_code_interpreter import AsyncSandbox  # type: ignore[import]
    except ImportError:
        log.warning("e2b.not_installed")
        return ExecutionResult(
            stdout="",
            stderr="e2b_code_interpreter package not installed",
            exit_code=-1,
            duration_ms=0,
        )

    start = time.monotonic()
    api_key = get_settings().e2b_api_key

    async with await AsyncSandbox.create(api_key=api_key, timeout=timeout) as sandbox:
        if env_vars:
            for k, v in env_vars.items():
                await sandbox.set_env(k, v)

        execution = await sandbox.run_code(code, language=language, timeout=timeout)

        duration_ms = (time.monotonic() - start) * 1000

        result = ExecutionResult(
            stdout="\n".join(str(o) for o in execution.logs.stdout) if execution.logs else "",
            stderr="\n".join(str(e) for e in execution.logs.stderr) if execution.logs else "",
            exit_code=0 if not execution.error else 1,
            duration_ms=duration_ms,
        )

    log.info(
        "e2b.run.done",
        language=language,
        exit_code=result.exit_code,
        duration_ms=round(result.duration_ms, 1),
    )
    return result


@retry(
    retry=retry_if_exception_type(Exception),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=8),
    reraise=True,
)
async def run_files(
    files: dict[str, str],
    entrypoint: str,
    *,
    language: str = "python",
    timeout: int = _DEFAULT_TIMEOUT,
) -> ExecutionResult:
    """
    Upload files to a sandbox and execute an entrypoint.

    files: {relative_path: content}
    entrypoint: path of the file to run (must be in files)
    """
    import time

    log.info("e2b.run_files.start", file_count=len(files), entrypoint=entrypoint)

    try:
        from e2b_code_interpreter import AsyncSandbox  # type: ignore[import]
    except ImportError:
        log.warning("e2b.not_installed")
        return ExecutionResult(
            stdout="",
            stderr="e2b_code_interpreter package not installed",
            exit_code=-1,
            duration_ms=0,
        )

    start = time.monotonic()
    api_key = get_settings().e2b_api_key

    async with await AsyncSandbox.create(api_key=api_key, timeout=timeout) as sandbox:
        for path, content in files.items():
            await sandbox.files.write(path, content)

        execution = await sandbox.run_code(
            f"exec(open('{entrypoint}').read())",
            language=language,
            timeout=timeout,
        )
        duration_ms = (time.monotonic() - start) * 1000

        result = ExecutionResult(
            stdout="\n".join(str(o) for o in execution.logs.stdout) if execution.logs else "",
            stderr="\n".join(str(e) for e in execution.logs.stderr) if execution.logs else "",
            exit_code=0 if not execution.error else 1,
            duration_ms=duration_ms,
        )

    log.info("e2b.run_files.done", exit_code=result.exit_code)
    return result
