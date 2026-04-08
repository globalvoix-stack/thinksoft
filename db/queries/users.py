"""User queries — raw SQL, typed dataclasses."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

import asyncpg


@dataclass
class User:
    id: UUID
    email: str
    hashed_password: str
    created_at: datetime
    updated_at: datetime


def _row(record: asyncpg.Record) -> User:
    d = dict(record)
    return User(**d)


async def create_user(
    conn: asyncpg.Connection, email: str, hashed_password: str
) -> User:
    row = await conn.fetchrow(
        """
        INSERT INTO users (email, hashed_password)
        VALUES ($1, $2)
        RETURNING *
        """,
        email,
        hashed_password,
    )
    return _row(row)


async def get_user_by_id(conn: asyncpg.Connection, user_id: UUID) -> User | None:
    row = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
    return _row(row) if row else None


async def get_user_by_email(conn: asyncpg.Connection, email: str) -> User | None:
    row = await conn.fetchrow("SELECT * FROM users WHERE email = $1", email)
    return _row(row) if row else None


async def update_password(
    conn: asyncpg.Connection, user_id: UUID, hashed_password: str
) -> None:
    await conn.execute(
        "UPDATE users SET hashed_password = $1 WHERE id = $2",
        hashed_password,
        user_id,
    )
