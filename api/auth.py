"""
Auth middleware — Clerk JWT verification.

Clerk issues RS256-signed JWTs. We verify them using Clerk's JWKS endpoint,
cached in memory with a 1-hour TTL to avoid hammering the endpoint.
"""
from __future__ import annotations

import time
from typing import Any
from uuid import UUID

import httpx
import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from config.settings import get_settings

log = structlog.get_logger(__name__)

_bearer = HTTPBearer(auto_error=True)

# Simple in-process JWKS cache
_jwks_cache: dict[str, Any] = {}
_jwks_fetched_at: float = 0.0
_JWKS_TTL = 3600.0  # 1 hour


async def _get_jwks() -> dict[str, Any]:
    global _jwks_cache, _jwks_fetched_at
    now = time.monotonic()
    if _jwks_cache and (now - _jwks_fetched_at) < _JWKS_TTL:
        return _jwks_cache

    frontend_api = get_settings().clerk_frontend_api.rstrip("/")
    url = f"{frontend_api}/.well-known/jwks.json"
    log.info("auth.jwks.fetch", url=url)

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url)
        resp.raise_for_status()

    _jwks_cache = resp.json()
    _jwks_fetched_at = now
    log.info("auth.jwks.cached", key_count=len(_jwks_cache.get("keys", [])))
    return _jwks_cache


def _decode_token(token: str, jwks: dict[str, Any]) -> dict[str, Any]:
    from jose import JWTError, jwt  # type: ignore[import]
    from jose.exceptions import ExpiredSignatureError

    try:
        # Let python-jose select the key from the JWKS by `kid`
        payload: dict[str, Any] = jwt.decode(
            token,
            jwks,
            algorithms=["RS256"],
            options={"verify_aud": False},
        )
        return payload
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as exc:
        log.warning("auth.jwt_invalid", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> dict[str, Any]:
    """FastAPI dependency — returns Clerk JWT payload for the authenticated user."""
    jwks = await _get_jwks()
    return _decode_token(credentials.credentials, jwks)


async def get_current_user_id(
    payload: dict[str, Any] = Depends(get_current_user),
) -> str:
    """FastAPI dependency — returns the Clerk user ID string (e.g. 'user_2abc...')."""
    sub = payload.get("sub")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user identifier (sub)",
        )
    return str(sub)
