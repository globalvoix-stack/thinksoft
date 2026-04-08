"""
Memory store — Voyage AI embeddings + Neon persistence.

Four operations: write, read, override, delete.
Conflict detection surfaces conflicts; never resolves silently.
Light mode must never call write/override/delete.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from uuid import UUID

import structlog

from config.constants import (
    MAX_MEMORY_ENTRIES_PER_CALL,
    MEMORY_CONFLICT_THRESHOLD,
    MEMORY_RELEVANCE_THRESHOLD,
    MEMORY_SOURCE_PRIORITY,
)
from db.pool import acquire
from db.queries.memory import (
    MemoryEntry,
    deactivate_all_of_type,
    deactivate_memory,
    get_active_memory,
    get_all_active_with_embeddings,
    write_memory,
)
from integrations.voyage import cosine_similarity, embed, embed_query

log = structlog.get_logger(__name__)


@dataclass
class MemoryConflict:
    """Raised/returned when a new write conflicts with existing memory."""
    existing_entry_id: UUID
    existing_content: str
    existing_source: str
    new_content: str
    new_source: str
    similarity: float


@dataclass
class MemoryWriteResult:
    entry: MemoryEntry
    conflicts: list[MemoryConflict]
    """Non-empty when similarity with existing entries exceeds MEMORY_CONFLICT_THRESHOLD."""


async def write(
    project_id: UUID,
    session_id: UUID,
    content: str,
    source: str,
    memory_type: str,
    *,
    mode: str,
    metadata: dict[str, Any] | None = None,
) -> MemoryWriteResult:
    """
    Write a memory entry with embedding.

    Raises ValueError if called from Light mode.
    Surfaces conflicts without silently resolving them.
    """
    if mode == "light":
        raise ValueError("Light mode must never write memory entries")

    log.info("memory.write.start", project_id=str(project_id), source=source, memory_type=memory_type)

    # Embed the new content
    vectors = await embed([content], input_type="document")
    embedding = vectors[0]

    # Detect conflicts before writing
    conflicts: list[MemoryConflict] = []
    async with acquire() as conn:
        existing = await get_all_active_with_embeddings(conn, project_id)
        for entry in existing:
            if not entry.embedding:
                continue
            sim = cosine_similarity(embedding, entry.embedding)
            if sim >= MEMORY_CONFLICT_THRESHOLD:
                conflicts.append(
                    MemoryConflict(
                        existing_entry_id=entry.id,
                        existing_content=entry.content,
                        existing_source=entry.source,
                        new_content=content,
                        new_source=source,
                        similarity=round(sim, 4),
                    )
                )

        if conflicts:
            log.warning(
                "memory.write.conflicts_detected",
                project_id=str(project_id),
                conflict_count=len(conflicts),
                sources=[c.existing_source for c in conflicts],
            )

        new_entry = await write_memory(
            conn,
            project_id=project_id,
            session_id=session_id,
            content=content,
            source=source,
            memory_type=memory_type,
            embedding=embedding,
            metadata=metadata or {},
        )

    log.info(
        "memory.write.done",
        entry_id=str(new_entry.id),
        conflict_count=len(conflicts),
    )
    return MemoryWriteResult(entry=new_entry, conflicts=conflicts)


async def read(
    project_id: UUID,
    query: str,
    *,
    limit: int = MAX_MEMORY_ENTRIES_PER_CALL,
    memory_type: str | None = None,
) -> list[MemoryEntry]:
    """
    Retrieve relevant memory entries for a query using cosine similarity.

    Returns entries with similarity >= MEMORY_RELEVANCE_THRESHOLD,
    sorted by relevance descending, capped at limit.
    """
    log.info("memory.read.start", project_id=str(project_id), query_length=len(query))

    query_vec = await embed_query(query)

    async with acquire() as conn:
        all_entries = await get_all_active_with_embeddings(conn, project_id)

    scored: list[tuple[float, MemoryEntry]] = []
    for entry in all_entries:
        if memory_type and entry.memory_type != memory_type:
            continue
        if not entry.embedding:
            continue
        sim = cosine_similarity(query_vec, entry.embedding)
        if sim >= MEMORY_RELEVANCE_THRESHOLD:
            scored.append((sim, entry))

    scored.sort(key=lambda x: x[0], reverse=True)
    results = [e for _, e in scored[:limit]]

    log.info("memory.read.done", project_id=str(project_id), result_count=len(results))
    return results


async def override(
    project_id: UUID,
    session_id: UUID,
    content: str,
    source: str,
    memory_type: str,
    *,
    mode: str,
    metadata: dict[str, Any] | None = None,
) -> MemoryWriteResult:
    """
    Deactivate all existing entries of the same type and write a new one.

    Raises ValueError if called from Light mode.
    Used when an agent decision supersedes all previous entries of a type.
    """
    if mode == "light":
        raise ValueError("Light mode must never override memory entries")

    log.info(
        "memory.override.start",
        project_id=str(project_id),
        memory_type=memory_type,
        source=source,
    )

    async with acquire() as conn:
        deactivated = await deactivate_all_of_type(conn, project_id, memory_type)

    log.info("memory.override.deactivated", count=deactivated, memory_type=memory_type)

    return await write(
        project_id,
        session_id,
        content,
        source,
        memory_type,
        mode=mode,
        metadata=metadata,
    )


async def delete(
    project_id: UUID,
    entry_id: UUID,
    *,
    mode: str,
) -> bool:
    """
    Soft-delete (deactivate) a memory entry by ID.

    Raises ValueError if called from Light mode.
    Returns True if the entry was found and deactivated.
    """
    if mode == "light":
        raise ValueError("Light mode must never delete memory entries")

    log.info("memory.delete.start", project_id=str(project_id), entry_id=str(entry_id))

    async with acquire() as conn:
        success = await deactivate_memory(conn, entry_id, project_id)

    log.info("memory.delete.done", entry_id=str(entry_id), success=success)
    return success


async def get_recent(
    project_id: UUID,
    *,
    limit: int = MAX_MEMORY_ENTRIES_PER_CALL,
    memory_type: str | None = None,
) -> list[MemoryEntry]:
    """Return the most recent active memory entries (no embedding needed)."""
    async with acquire() as conn:
        return await get_active_memory(conn, project_id, limit=limit, memory_type=memory_type)
