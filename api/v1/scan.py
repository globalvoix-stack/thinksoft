"""POST /v1/scan — trigger security scan on code."""
from __future__ import annotations

from typing import Any
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from api.auth import get_current_user_id
from security import SecurityFinding, scan

log = structlog.get_logger(__name__)
router = APIRouter()


class ScanRequest(BaseModel):
    code: str
    language: str
    scope: str = ""
    deep: bool = False


class FindingResponse(BaseModel):
    severity: str
    category: str
    description: str
    recommendation: str
    source: str
    line_hint: int | None = None


class ScanResponse(BaseModel):
    passed: bool
    tiers_run: list[str]
    finding_count: int
    findings: list[FindingResponse]


@router.post("/scan", response_model=ScanResponse, status_code=status.HTTP_200_OK)
async def scan_route(
    body: ScanRequest,
    user_id: UUID = Depends(get_current_user_id),
) -> ScanResponse:
    log.info(
        "api.scan",
        language=body.language,
        scope=body.scope,
        deep=body.deep,
        code_length=len(body.code),
    )

    result = await scan(body.code, body.language, scope=body.scope, deep=body.deep)

    return ScanResponse(
        passed=result.passed,
        tiers_run=result.tiers_run,
        finding_count=len(result.findings),
        findings=[
            FindingResponse(
                severity=f.severity,
                category=f.category,
                description=f.description,
                recommendation=f.recommendation,
                source=f.source,
                line_hint=f.line_hint,
            )
            for f in result.findings
        ],
    )
