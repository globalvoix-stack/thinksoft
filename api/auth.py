"""
Auth middleware — JWT verification via Better Auth (HS256).

Better Auth is JS-native; we verify HS256 tokens on the Python side
using python-jose. The secret is better_auth_secret from settings.
"""
from __future__ import annotations

from uuid import UUID

import structlog
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from config.constants import JWT_ALGORITHM
from config.settings import get_settings

log = structlog.get_logger(__name__)

_bearer = HTTPBearer(auto_error=True)


def _decode_token(token: str) -> dict:
    from jose import JWTError, jwt  # type: ignore[import]
    secret = get_settings().better_auth_secret
    try:
        payload = jwt.decode(token, secret, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError as exc:
        log.warning("auth.jwt_invalid", error=str(exc))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
) -> dict:
    """FastAPI dependency — returns JWT payload dict for the authenticated user."""
    return _decode_token(credentials.credentials)


def get_current_user_id(
    payload: dict = Depends(get_current_user),
) -> UUID:
    """FastAPI dependency — returns the UUID user ID from the JWT payload."""
    sub = payload.get("sub") or payload.get("userId") or payload.get("user_id")
    if not sub:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing user identifier",
        )
    try:
        return UUID(str(sub))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user identifier in token",
        )
