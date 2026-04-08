import logging
import sys
from functools import lru_cache

import structlog
from pydantic import PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    neon_database_url: PostgresDsn

    # AI Models
    anthropic_api_key: str
    google_ai_api_key: str
    kimi_api_key: str
    kimi_base_url: str = "https://api.moonshot.ai/v1"

    # Embeddings
    voyage_ai_api_key: str

    # Crawling
    firecrawl_api_key: str

    # Sandbox
    e2b_api_key: str

    # Auth
    better_auth_secret: str
    better_auth_url: str

    # App
    app_env: str = "development"
    app_port: int = 8000
    log_level: str = "info"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()


def configure_logging(settings: Settings | None = None) -> None:
    """Set up structured logging with structlog.

    JSON format in production, human readable in development.
    Every log entry includes: timestamp, level, and optional context fields
    (session_id, project_id, agent) where available.
    """
    log_level_str = (settings.log_level if settings else "info").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    is_production = (settings.app_env if settings else "development") == "production"

    shared_processors: list = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if is_production:
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=sys.stdout.isatty())

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

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger bound to a module name."""
    return structlog.get_logger(name)
