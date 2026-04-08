"""
Component and asset registry — queryable by agents.

Backed by the project's component_registry JSONB column in Neon.
Provides in-memory catalog of available UI/animation/icon libraries and asset sources.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

import structlog

from config.constants import (
    ANIMATION_LIBRARIES,
    ASSET_SOURCES,
    ICON_LIBRARIES,
    UI_LIBRARIES,
)
from db.pool import acquire
from db.queries.projects import get_project_by_id, update_component_registry

log = structlog.get_logger(__name__)


@dataclass
class RegistryEntry:
    name: str
    category: str
    """One of: ui, animation, icon, asset"""
    version: str | None = None
    description: str | None = None
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


# Static catalog — always available regardless of project config
_STATIC_CATALOG: list[RegistryEntry] = [
    *[RegistryEntry(name=lib, category="ui") for lib in UI_LIBRARIES],
    *[RegistryEntry(name=lib, category="animation") for lib in ANIMATION_LIBRARIES],
    *[RegistryEntry(name=lib, category="icon") for lib in ICON_LIBRARIES],
    *[RegistryEntry(name=src, category="asset") for src in ASSET_SOURCES],
]

_CATALOG_BY_NAME = {e.name: e for e in _STATIC_CATALOG}


def list_all() -> list[RegistryEntry]:
    """Return the full static catalog."""
    return list(_STATIC_CATALOG)


def list_by_category(category: str) -> list[RegistryEntry]:
    """Return all entries in a category (ui, animation, icon, asset)."""
    return [e for e in _STATIC_CATALOG if e.category == category]


def get(name: str) -> RegistryEntry | None:
    """Look up an entry by name."""
    return _CATALOG_BY_NAME.get(name)


def search(query: str) -> list[RegistryEntry]:
    """Case-insensitive substring search across name, category, description, tags."""
    q = query.lower()
    results = []
    for entry in _STATIC_CATALOG:
        if (
            q in entry.name.lower()
            or q in entry.category.lower()
            or (entry.description and q in entry.description.lower())
            or any(q in tag.lower() for tag in entry.tags)
        ):
            results.append(entry)
    return results


async def get_project_registry(project_id: UUID) -> dict[str, Any]:
    """
    Return the project-specific component registry from Neon.

    This stores agent-selected components and design decisions for the project.
    """
    async with acquire() as conn:
        project = await get_project_by_id(conn, project_id)
    return project.component_registry if project else {}


async def set_project_registry(
    project_id: UUID, registry: dict[str, Any]
) -> None:
    """Overwrite the project component registry in Neon."""
    log.info("registry.set_project", project_id=str(project_id))
    async with acquire() as conn:
        await update_component_registry(conn, project_id, registry)


async def merge_project_registry(
    project_id: UUID, updates: dict[str, Any]
) -> dict[str, Any]:
    """Merge updates into the existing project registry and persist."""
    current = await get_project_registry(project_id)
    current.update(updates)
    await set_project_registry(project_id, current)
    log.info("registry.merged", project_id=str(project_id), keys=list(updates.keys()))
    return current


def describe_for_agent() -> str:
    """
    Return a concise text description of the full catalog for agent prompts.
    Stays within ~200 tokens.
    """
    lines = [
        "Available UI libraries: " + ", ".join(UI_LIBRARIES),
        "Animation libraries: " + ", ".join(ANIMATION_LIBRARIES),
        "Icon sets: " + ", ".join(ICON_LIBRARIES),
        "Asset sources: " + ", ".join(ASSET_SOURCES),
    ]
    return "\n".join(lines)
