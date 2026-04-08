"""
External tool integrations.

Each module is self-contained with retry logic, typed responses, and structlog.
Import directly from the submodule rather than from this package to keep
startup cost low (avoid importing all SDKs at once).
"""
