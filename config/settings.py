"""
Thinksoft application settings.

Loaded from environment variables / .env file via pydantic-settings.
Application fails loudly on startup if any required variable is missing.
"""
from __future__ import annotations

import logging
import sys
from functools import lru_cache

import structlog
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Database ─────────────────────────────────────────────────────────
    neon_database_url: PostgresDsn

    # ── AI Models ─────────────────────────────────────────────────────────
    anthropic_api_key: str
    google_ai_api_key: str
    kimi_api_key: str
    kimi_base_url: str = "https://api.moonshot.ai/v1"

    # ── Embeddings ────────────────────────────────────────────────────────
    voyage_ai_api_key: str

    # ── Crawling ──────────────────────────────────────────────────────────
    firecrawl_api_key: str
    exa_api_key: str = ""

    # ── Sandbox ───────────────────────────────────────────────────────────
    e2b_api_key: str

    # ── Auth (Clerk) ──────────────────────────────────────────────────────
    clerk_secret_key: str
    """Clerk secret key — used to fetch JWKS and verify session tokens."""
    clerk_frontend_api: str
    """Clerk frontend API URL, e.g. https://your-app.clerk.accounts.dev"""

    # ── Monitoring ────────────────────────────────────────────────────────
    sentry_dsn: str = ""
    resend_api_key: str = ""

    # ── App ───────────────────────────────────────────────────────────────
    app_env: str = "development"
    app_port: int = 8000
    log_level: str = "info"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


def configure_logging(settings: Settings | None = None) -> None:
    """
    Configure structlog for structured logging.

    JSON format in production; human-readable ConsoleRenderer in development.
    Every entry automatically includes timestamp, level, logger name, and any
    context vars bound via structlog.contextvars (session_id, project_id, agent).
    """
    s = settings or get_settings()
    log_level_str = s.log_level.upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    is_production = s.app_env == "production"

    shared_processors: list = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.ExceptionRenderer(),
    ]

    renderer = (
        structlog.processors.JSONRenderer()
        if is_production
        else structlog.dev.ConsoleRenderer(colors=sys.stdout.isatty())
    )

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(log_level)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Return a structlog logger bound to a module name."""
    return structlog.get_logger(name)
