"""Sentry integration — error monitoring auto-wired into generated apps."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import structlog

from config.settings import get_settings

log = structlog.get_logger(__name__)

_initialized = False


def init() -> bool:
    """
    Initialize Sentry SDK for the Thinksoft backend itself.

    Returns True if Sentry was initialized, False if DSN is not configured.
    Called once at application startup.
    """
    global _initialized
    dsn = get_settings().sentry_dsn
    if not dsn:
        log.info("sentry.init.skipped", reason="SENTRY_DSN not set")
        return False

    try:
        import sentry_sdk  # type: ignore[import]
        from sentry_sdk.integrations.asyncio import AsyncioIntegration
        from sentry_sdk.integrations.logging import LoggingIntegration
        from sentry_sdk.integrations.starlette import StarletteIntegration

        sentry_sdk.init(
            dsn=dsn,
            environment=get_settings().app_env,
            integrations=[
                AsyncioIntegration(),
                StarletteIntegration(),
                LoggingIntegration(level=None, event_level=None),
            ],
            traces_sample_rate=0.1,
            send_default_pii=False,
        )
        _initialized = True
        log.info("sentry.init.done", environment=get_settings().app_env)
        return True
    except ImportError:
        log.warning("sentry.not_installed")
        return False


def capture_exception(exc: Exception, **context: Any) -> str | None:
    """Capture an exception to Sentry and return the event ID."""
    if not _initialized:
        return None
    try:
        import sentry_sdk  # type: ignore[import]
        with sentry_sdk.push_scope() as scope:
            for key, value in context.items():
                scope.set_extra(key, value)
            event_id = sentry_sdk.capture_exception(exc)
        log.debug("sentry.captured", event_id=event_id)
        return event_id
    except Exception as inner:
        log.warning("sentry.capture_failed", error=str(inner))
        return None


def capture_message(message: str, level: str = "info", **context: Any) -> str | None:
    """Capture a message to Sentry."""
    if not _initialized:
        return None
    try:
        import sentry_sdk  # type: ignore[import]
        with sentry_sdk.push_scope() as scope:
            for key, value in context.items():
                scope.set_extra(key, value)
            event_id = sentry_sdk.capture_message(message, level=level)
        return event_id
    except Exception as inner:
        log.warning("sentry.message_failed", error=str(inner))
        return None


def generate_client_snippet(dsn: str, environment: str = "production") -> str:
    """
    Generate a Sentry initialization code snippet for a generated frontend app.

    Returns a JS/TS import + init block to embed in generated app code.
    """
    return f"""import * as Sentry from "@sentry/nextjs";

Sentry.init({{
  dsn: "{dsn}",
  environment: "{environment}",
  tracesSampleRate: 0.1,
  replaysSessionSampleRate: 0.1,
  replaysOnErrorSampleRate: 1.0,
}});
"""


def generate_backend_snippet(dsn: str, environment: str = "production") -> str:
    """Generate a Sentry init snippet for a generated Python backend."""
    return f"""import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="{dsn}",
    environment="{environment}",
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
)
"""
