"""
Component and asset registry — queryable by agents.

Public API:
  list_all()                    — full static catalog
  list_by_category(category)    — filter by ui/animation/icon/asset
  get(name)                     — look up by name
  search(query)                 — substring search
  get_project_registry(pid)     — project-specific selections from Neon
  set_project_registry(pid, r)  — overwrite project registry
  merge_project_registry(pid, u)— merge updates into project registry
  describe_for_agent()          — compact text description for prompts
  RegistryEntry                 — entry dataclass
"""
from registry.store import (
    RegistryEntry,
    describe_for_agent,
    get,
    get_project_registry,
    list_all,
    list_by_category,
    merge_project_registry,
    search,
    set_project_registry,
)

__all__ = [
    "RegistryEntry",
    "list_all",
    "list_by_category",
    "get",
    "search",
    "get_project_registry",
    "set_project_registry",
    "merge_project_registry",
    "describe_for_agent",
]
