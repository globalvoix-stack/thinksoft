"""
Versioned migration runner for Thinksoft.

Reads *.sql files from db/migrations/sql/ ordered by filename prefix,
tracks applied migrations in schema_migrations, and rolls back on failure.
"""
from __future__ import annotations

import asyncio
from pathlib import Path

import asyncpg
import structlog

from config.settings import get_settings

logger = structlog.get_logger(__name__)

MIGRATIONS_DIR = Path(__file__).parent / "sql"


async def run_migrations(dsn: str | None = None) -> None:
    settings = get_settings()
    conn_dsn = dsn or str(settings.neon_database_url)

    conn = await asyncpg.connect(conn_dsn)
    try:
        # Bootstrap tracking table
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                id SERIAL PRIMARY KEY,
                filename TEXT UNIQUE NOT NULL,
                applied_at TIMESTAMPTZ DEFAULT now()
            )
        """)

        migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
        if not migration_files:
            logger.warning("no migration files found", path=str(MIGRATIONS_DIR))
            return

        applied = 0
        skipped = 0
        for migration_file in migration_files:
            filename = migration_file.name
            exists = await conn.fetchval(
                "SELECT COUNT(*) FROM schema_migrations WHERE filename = $1",
                filename,
            )
            if exists:
                logger.info("skipping migration (already applied)", filename=filename)
                skipped += 1
                continue

            logger.info("applying migration", filename=filename)
            sql = migration_file.read_text(encoding="utf-8")

            async with conn.transaction():
                await conn.execute(sql)
                await conn.execute(
                    "INSERT INTO schema_migrations (filename) VALUES ($1)", filename
                )

            logger.info("migration applied", filename=filename)
            applied += 1

        logger.info(
            "all migrations complete",
            applied=applied,
            skipped=skipped,
            total=len(migration_files),
        )

    except Exception:
        logger.exception("migration failed — transaction rolled back")
        raise
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(run_migrations())
