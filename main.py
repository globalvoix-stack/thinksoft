"""
Thinksoft — FastAPI application entrypoint.

Startup:
  1. Configure structured logging
  2. Initialize Sentry (if DSN configured)
  3. Run database migrations
  4. Create DB connection pool
  5. Mount /v1 routes

Shutdown:
  1. Close DB connection pool
"""
from __future__ import annotations

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.settings import configure_logging, get_settings
from integrations import sentry as sentry_client

log = structlog.get_logger(__name__)


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings)

    # Sentry (non-blocking if not configured)
    sentry_client.init()

    app = FastAPI(
        title="Thinksoft API",
        version="0.1.0",
        docs_url="/docs" if settings.app_env != "production" else None,
        redoc_url=None,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.app_env != "production" else [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    async def startup() -> None:
        log.info("app.startup", env=settings.app_env)

        # Run migrations
        from db.migrations.runner import run_migrations
        await run_migrations()

        # Warm up connection pool
        from db.pool import get_pool
        await get_pool()
        log.info("app.startup.complete")

    @app.on_event("shutdown")
    async def shutdown() -> None:
        from db.pool import close_pool
        await close_pool()
        log.info("app.shutdown")

    # Mount API routes
    from api.v1 import router as v1_router
    app.include_router(v1_router)

    @app.get("/health")
    async def health() -> dict:
        return {"status": "ok", "env": settings.app_env}

    return app


app = create_app()
