"""Resend integration — transactional email for generated apps."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import httpx
import structlog
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from config.settings import get_settings

log = structlog.get_logger(__name__)

_BASE = "https://api.resend.com"
_TIMEOUT = 15.0


@dataclass
class EmailResult:
    id: str
    success: bool
    error: str | None = None


def _headers() -> dict[str, str]:
    key = get_settings().resend_api_key
    if not key:
        raise RuntimeError("RESEND_API_KEY is not configured")
    return {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}


@retry(
    retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True,
)
async def send_email(
    *,
    from_address: str,
    to: list[str],
    subject: str,
    html: str | None = None,
    text: str | None = None,
    reply_to: str | None = None,
    tags: list[dict[str, str]] | None = None,
) -> EmailResult:
    """Send a transactional email via Resend."""
    log.info("resend.send.start", to=to, subject=subject)

    if not html and not text:
        raise ValueError("Either html or text must be provided")

    payload: dict[str, Any] = {
        "from": from_address,
        "to": to,
        "subject": subject,
    }
    if html:
        payload["html"] = html
    if text:
        payload["text"] = text
    if reply_to:
        payload["reply_to"] = reply_to
    if tags:
        payload["tags"] = tags

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.post(
            f"{_BASE}/emails",
            headers=_headers(),
            json=payload,
        )
        resp.raise_for_status()

    data = resp.json()
    result = EmailResult(id=data.get("id", ""), success=True)
    log.info("resend.send.done", email_id=result.id)
    return result


async def send_template(
    *,
    from_address: str,
    to: list[str],
    template_id: str,
    variables: dict[str, Any],
) -> EmailResult:
    """Send an email using a Resend template."""
    log.info("resend.send_template.start", to=to, template_id=template_id)

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.post(
            f"{_BASE}/emails",
            headers=_headers(),
            json={
                "from": from_address,
                "to": to,
                "template_id": template_id,
                "variables": variables,
            },
        )
        resp.raise_for_status()

    data = resp.json()
    result = EmailResult(id=data.get("id", ""), success=True)
    log.info("resend.send_template.done", email_id=result.id)
    return result
