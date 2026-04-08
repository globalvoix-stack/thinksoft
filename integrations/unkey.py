"""Unkey integration — API key management for generated apps."""
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

log = structlog.get_logger(__name__)

_BASE = "https://api.unkey.dev/v1"
_TIMEOUT = 15.0


@dataclass
class ApiKey:
    key_id: str
    key: str
    name: str | None
    owner_id: str | None
    meta: dict[str, Any] = field(default_factory=dict)
    expires: int | None = None
    remaining: int | None = None


@dataclass
class VerifyResult:
    valid: bool
    key_id: str | None
    owner_id: str | None
    meta: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    code: str | None = None


def _headers(root_key: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {root_key}",
        "Content-Type": "application/json",
    }


@retry(
    retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=8),
    reraise=True,
)
async def create_key(
    root_key: str,
    api_id: str,
    *,
    name: str | None = None,
    owner_id: str | None = None,
    meta: dict[str, Any] | None = None,
    expires_in_ms: int | None = None,
    remaining: int | None = None,
    prefix: str | None = None,
) -> ApiKey:
    """Create a new API key in an Unkey API."""
    log.info("unkey.create_key.start", api_id=api_id, owner_id=owner_id)

    payload: dict[str, Any] = {"apiId": api_id}
    if name:
        payload["name"] = name
    if owner_id:
        payload["ownerId"] = owner_id
    if meta:
        payload["meta"] = meta
    if expires_in_ms:
        payload["expires"] = expires_in_ms
    if remaining is not None:
        payload["remaining"] = remaining
    if prefix:
        payload["prefix"] = prefix

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.post(
            f"{_BASE}/keys.createKey",
            headers=_headers(root_key),
            json=payload,
        )
        resp.raise_for_status()

    data = resp.json()
    result = ApiKey(
        key_id=data.get("keyId", ""),
        key=data.get("key", ""),
        name=name,
        owner_id=owner_id,
        meta=meta or {},
    )
    log.info("unkey.create_key.done", key_id=result.key_id)
    return result


@retry(
    retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=8),
    reraise=True,
)
async def verify_key(root_key: str, key: str, *, api_id: str | None = None) -> VerifyResult:
    """Verify an API key."""
    log.info("unkey.verify.start")

    payload: dict[str, Any] = {"key": key}
    if api_id:
        payload["apiId"] = api_id

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.post(
            f"{_BASE}/keys.verifyKey",
            headers=_headers(root_key),
            json=payload,
        )
        data = resp.json()
        # Unkey returns 200 even for invalid keys; validity is in payload
        valid = data.get("valid", False)

    result = VerifyResult(
        valid=valid,
        key_id=data.get("keyId"),
        owner_id=data.get("ownerId"),
        meta=data.get("meta", {}),
        error=data.get("error"),
        code=data.get("code"),
    )
    log.info("unkey.verify.done", valid=result.valid)
    return result


@retry(
    retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=8),
    reraise=True,
)
async def revoke_key(root_key: str, key_id: str) -> bool:
    """Revoke an API key by ID."""
    log.info("unkey.revoke.start", key_id=key_id)

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.post(
            f"{_BASE}/keys.deleteKey",
            headers=_headers(root_key),
            json={"keyId": key_id},
        )
        resp.raise_for_status()

    log.info("unkey.revoke.done", key_id=key_id)
    return True


def generate_middleware_snippet(api_id: str) -> str:
    """
    Generate an Unkey key verification middleware snippet for generated Next.js apps.
    """
    return f"""import {{ verifyKey }} from "@unkey/api";

export async function middleware(request: Request) {{
  const key = request.headers.get("Authorization")?.replace("Bearer ", "");
  if (!key) return new Response("Unauthorized", {{ status: 401 }});

  const {{ result, error }} = await verifyKey({{ key, apiId: "{api_id}" }});
  if (error || !result?.valid) return new Response("Forbidden", {{ status: 403 }});

  return undefined; // pass through
}}
"""
