"""
Memory system — Voyage AI embeddings + Neon persistence.

Public API:
  write(...)    — embed and store; Light mode forbidden; surfaces conflicts
  read(...)     — similarity search against active entries
  override(...) — deactivate all entries of a type, then write new one
  delete(...)   — soft-delete a single entry; Light mode forbidden
  get_recent(...) — retrieve recent entries without embedding
"""
from memory.store import (
    MemoryConflict,
    MemoryWriteResult,
    delete,
    get_recent,
    override,
    read,
    write,
)

__all__ = [
    "MemoryConflict",
    "MemoryWriteResult",
    "write",
    "read",
    "override",
    "delete",
    "get_recent",
]
