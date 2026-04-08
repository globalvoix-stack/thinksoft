"""
Thinksoft verification script — Session 2.
Confirms the full backend stack is importable and DB tables/indexes/routes exist.
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))


def check(label: str, fn) -> bool:
    try:
        fn()
        print(f"  [OK] {label}")
        return True
    except Exception as e:
        print(f"  [FAIL] {label}: {e}")
        return False


async def acheck(label: str, coro_fn) -> bool:
    try:
        await coro_fn()
        print(f"  [OK] {label}")
        return True
    except Exception as e:
        print(f"  [FAIL] {label}: {e}")
        return False


def import_check(module_path: str):
    def _check():
        import importlib
        importlib.import_module(module_path)
    return _check


def main():
    print("\n=== Thinksoft Engine Verification ===\n")
    failures = []

    # ── Thinksoft core modules ────────────────────────────────────────────────
    print("[ Core Module Imports ]")
    for mod in [
        "engine", "engine.execution", "engine.filesystem", "engine.sandbox", "engine.tools",
        "config", "db", "db.migrations",
        "integrations.firecrawl", "integrations.exa", "integrations.wappalyzer",
        "integrations.voyage", "integrations.anthropic", "integrations.gemini",
        "integrations.kimi", "integrations.semgrep", "integrations.e2b",
        "integrations.composio", "integrations.resend", "integrations.sentry",
        "integrations.unkey",
        "memory", "context",
        "agents", "agents.orchestrator", "agents.kimi", "agents.gemini",
        "agents.haiku", "agents.sonnet", "agents.critic",
        "modes", "modes.light", "modes.autonomous", "modes.max",
        "crawler", "registry", "security", "queue",
        "pipeline", "api",
    ]:
        ok = check(f"import {mod}", import_check(mod))
        if not ok:
            failures.append(f"import:{mod}")

    # ── Engine core ───────────────────────────────────────────────────────────
    print("\n[ Engine Core (OpenHands runtime) ]")
    for mod in [
        "engine.openhands.core.exceptions",
        "engine.openhands.core.schema",
        "engine.openhands.events",
        "engine.openhands.events.action",
        "engine.openhands.events.observation",
        "engine.openhands.llm.metrics",
        "engine.openhands.llm.llm_registry",
        "engine.openhands.integrations",
        "engine.openhands.microagent",
        "engine.openhands.security",
        "engine.openhands.io",
        "engine.openhands.mcp",
    ]:
        ok = check(f"import {mod}", import_check(mod))
        if not ok:
            failures.append(f"engine:{mod}")

    # ── Config constants ──────────────────────────────────────────────────────
    print("\n[ Config Constants ]")

    def check_constants():
        from config.constants import (
            KIMI_MODEL, GEMINI_FLASH_MODEL, HAIKU_MODEL, SONNET_MODEL,
            VOYAGE_MODEL, VOYAGE_EMBEDDING_DIM,
            COMPLEXITY_THRESHOLD, MEMORY_RELEVANCE_THRESHOLD,
            MAX_MEMORY_ENTRIES_PER_CALL, JOB_TIMEOUT_SECONDS,
            SSE_HEARTBEAT_SECONDS, SECURITY_REVIEW_TRIGGERS,
            CONTEXT_BUS_SUMMARY_MAX_TOKENS, MEMORY_CONFLICT_THRESHOLD,
            MEMORY_SOURCE_PRIORITY, UI_LIBRARIES, ANIMATION_LIBRARIES,
            ICON_LIBRARIES, ASSET_SOURCES,
        )
        assert KIMI_MODEL == "kimi-k2.5"
        assert SONNET_MODEL == "claude-sonnet-4-6"
        assert HAIKU_MODEL == "claude-haiku-4-5-20251001"
        assert GEMINI_FLASH_MODEL == "gemini-1.5-flash"
        assert VOYAGE_MODEL == "voyage-3"
        assert VOYAGE_EMBEDDING_DIM == 1024
        assert COMPLEXITY_THRESHOLD == 2
        assert MEMORY_RELEVANCE_THRESHOLD == 0.75
        assert MEMORY_CONFLICT_THRESHOLD == 0.90
        assert CONTEXT_BUS_SUMMARY_MAX_TOKENS == 100
        assert SSE_HEARTBEAT_SECONDS == 15
        assert "auth" in SECURITY_REVIEW_TRIGGERS
        assert "heroui" in UI_LIBRARIES
        assert "framer-motion" in ANIMATION_LIBRARIES
        assert len(MEMORY_SOURCE_PRIORITY) == 3

    ok = check("config.constants values", check_constants)
    if not ok:
        failures.append("config.constants")

    # ── Settings schema ───────────────────────────────────────────────────────
    print("\n[ Settings Schema ]")

    def check_settings():
        import tempfile, pathlib
        test_env = (
            "NEON_DATABASE_URL=postgresql://user:pass@localhost:5432/test\n"
            "ANTHROPIC_API_KEY=sk-ant-test\n"
            "GOOGLE_AI_API_KEY=test-google-key\n"
            "KIMI_API_KEY=test-kimi-key\n"
            "VOYAGE_AI_API_KEY=test-voyage-key\n"
            "FIRECRAWL_API_KEY=test-firecrawl-key\n"
            "E2B_API_KEY=test-e2b-key\n"
            "BETTER_AUTH_SECRET=test-secret\n"
            "BETTER_AUTH_URL=http://localhost:8000\n"
        )
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(test_env)
            tmp = f.name
        try:
            from pydantic_settings import BaseSettings
            from pydantic import PostgresDsn

            class T(BaseSettings):
                neon_database_url: PostgresDsn
                anthropic_api_key: str
                google_ai_api_key: str
                kimi_api_key: str
                kimi_base_url: str = "https://api.moonshot.ai/v1"
                voyage_ai_api_key: str
                firecrawl_api_key: str
                exa_api_key: str = ""
                e2b_api_key: str
                better_auth_secret: str
                better_auth_url: str
                sentry_dsn: str = ""
                resend_api_key: str = ""
                app_env: str = "development"
                app_port: int = 8000
                log_level: str = "info"
                class Config:
                    env_file = tmp
                    case_sensitive = False
            s = T()
            assert s.app_env == "development"
            assert s.kimi_base_url == "https://api.moonshot.ai/v1"
        finally:
            pathlib.Path(tmp).unlink(missing_ok=True)

    ok = check("config.settings schema", check_settings)
    if not ok:
        failures.append("config.settings")

    # ── Structlog ─────────────────────────────────────────────────────────────
    print("\n[ Structured Logging ]")

    def check_structlog():
        import structlog
        logger = structlog.get_logger("verify")
        logger.info("structlog_ok", check="verify")

    ok = check("structlog works", check_structlog)
    if not ok:
        failures.append("structlog")

    # ── Directory structure ───────────────────────────────────────────────────
    print("\n[ Directory Structure ]")
    import pathlib
    root = pathlib.Path(__file__).parent

    for d in [
        "engine/execution", "engine/filesystem", "engine/sandbox", "engine/tools",
        "agents/orchestrator", "agents/kimi", "agents/gemini",
        "agents/haiku", "agents/sonnet", "agents/critic",
        "modes/light", "modes/autonomous", "modes/max",
        "memory", "context", "security", "queue", "crawler",
        "registry", "integrations", "pipeline", "api/v1",
        "db/migrations/sql", "config", "tests",
    ]:
        p = root / d.replace(".", "/")
        ok = check(f"dir {d}/", lambda p=p: None if p.is_dir() else (_ for _ in ()).throw(FileNotFoundError(str(p))))
        if not ok:
            failures.append(f"dir:{d}")

    # ── DB tables and indexes (async) ─────────────────────────────────────────
    print("\n[ Database Tables & Indexes ]")

    async def check_db():
        from db.pool import acquire, get_pool

        await get_pool()

        required_tables = [
            "users", "projects", "memory_entries", "context_bus_snapshots",
            "jobs", "generated_files", "crawler_cache",
        ]
        required_indexes = [
            "idx_memory_project_active",
            "idx_jobs_project",
            "idx_jobs_status",
            "idx_context_project",
            "idx_crawler_url",
        ]
        required_triggers = [
            "update_projects_updated_at",
            "update_generated_files_updated_at",
        ]

        async with acquire() as conn:
            for table in required_tables:
                row = await conn.fetchval(
                    "SELECT COUNT(*) FROM information_schema.tables WHERE table_name=$1 AND table_schema='public'",
                    table,
                )
                if row == 0:
                    raise AssertionError(f"Table missing: {table}")

            for idx in required_indexes:
                row = await conn.fetchval(
                    "SELECT COUNT(*) FROM pg_indexes WHERE indexname=$1", idx
                )
                if row == 0:
                    raise AssertionError(f"Index missing: {idx}")

            for trigger in required_triggers:
                row = await conn.fetchval(
                    "SELECT COUNT(*) FROM information_schema.triggers WHERE trigger_name=$1",
                    trigger,
                )
                if row == 0:
                    raise AssertionError(f"Trigger missing: {trigger}")

        from db.pool import close_pool
        await close_pool()

    async def run_db_checks():
        db_ok = await acheck("DB tables, indexes, triggers", check_db)
        return db_ok

    db_ok = asyncio.run(run_db_checks())
    if not db_ok:
        failures.append("database")

    # ── API routes registered ─────────────────────────────────────────────────
    print("\n[ API Routes ]")

    def check_routes():
        from api.v1 import router
        paths = {r.path for r in router.routes}
        required_paths = [
            "/v1/projects",
            "/v1/generate",
            "/v1/stream/{job_id}",
            "/v1/files",
            "/v1/memory",
            "/v1/context",
            "/v1/scan",
        ]
        for path in required_paths:
            if path not in paths:
                raise AssertionError(f"Route missing: {path}")

    ok = check("all /v1 routes registered", check_routes)
    if not ok:
        failures.append("api.routes")

    # ── Agent registry ────────────────────────────────────────────────────────
    print("\n[ Agent Registry ]")

    def check_agents():
        from agents import AGENT_REGISTRY, get_agent
        for name in ["orchestrator", "kimi", "gemini", "haiku", "sonnet", "critic"]:
            agent = get_agent(name)
            assert agent.name == name, f"Agent name mismatch: {agent.name} != {name}"

    ok = check("all 6 agents registered", check_agents)
    if not ok:
        failures.append("agents.registry")

    # ── Mode router ───────────────────────────────────────────────────────────
    print("\n[ Mode Router ]")

    def check_mode_router():
        from modes.router import resolve, LIGHT, AUTONOMOUS, MAX
        # First prompt always max
        d = resolve(LIGHT, "build a saas app", is_first_prompt=True)
        assert d.mode == MAX
        # Complex request in light mode → mismatch
        d2 = resolve(LIGHT, "build a full authentication system with JWT", is_first_prompt=False)
        assert d2.mismatch_suggestion is not None

    ok = check("mode router logic", check_mode_router)
    if not ok:
        failures.append("modes.router")

    # ── Integration clients initialize ────────────────────────────────────────
    print("\n[ Integration Client Imports ]")

    def check_integrations():
        import integrations.firecrawl as fc
        import integrations.exa as exa
        import integrations.voyage as v
        import integrations.anthropic as ant
        import integrations.gemini as gem
        import integrations.kimi as kimi
        import integrations.semgrep as sg
        import integrations.e2b as e2b
        import integrations.sentry as sentry
        import integrations.resend as resend
        import integrations.unkey as unkey
        import integrations.wappalyzer as wapp
        import integrations.composio as comp
        assert hasattr(fc, "scrape")
        assert hasattr(exa, "search_competitors")
        assert hasattr(v, "embed")
        assert hasattr(ant, "sonnet")
        assert hasattr(gem, "flash")
        assert hasattr(kimi, "complete_with_images")
        assert hasattr(sg, "scan_code")
        assert hasattr(sentry, "init")
        assert hasattr(resend, "send_email")
        assert hasattr(unkey, "create_key")

    ok = check("all 13 integration modules load correctly", check_integrations)
    if not ok:
        failures.append("integrations")

    # ── Memory system ─────────────────────────────────────────────────────────
    print("\n[ Memory System ]")

    def check_memory():
        import memory
        assert hasattr(memory, "write")
        assert hasattr(memory, "read")
        assert hasattr(memory, "override")
        assert hasattr(memory, "delete")
        assert hasattr(memory, "get_recent")
        # Light mode write must raise
        import asyncio
        from uuid import uuid4
        async def _test():
            try:
                await memory.write(uuid4(), uuid4(), "test", "user_explicit", "decision", mode="light")
                raise AssertionError("Expected ValueError for light mode write")
            except ValueError:
                pass  # Expected
        asyncio.run(_test())

    ok = check("memory system API + light mode guard", check_memory)
    if not ok:
        failures.append("memory")

    # ── Context bus ───────────────────────────────────────────────────────────
    print("\n[ Context Bus ]")

    def check_context_bus():
        from context.bus import ContextBus, AGENT_IDLE, AGENT_RUNNING, AGENT_DONE, AGENT_ERROR
        from uuid import uuid4
        bus = ContextBus(project_id=uuid4(), session_id=uuid4())
        bus.set_agent_status("test_agent", AGENT_RUNNING)
        assert bus.agent_statuses["test_agent"] == AGENT_RUNNING
        bus.record_decision("test_agent", "test decision")
        assert len(bus.decisions) == 1
        summary = bus.summary()
        assert len(summary) <= 400  # 100 tokens * 4 chars

    ok = check("context bus in-memory logic", check_context_bus)
    if not ok:
        failures.append("context_bus")

    # ── Security scanner ──────────────────────────────────────────────────────
    print("\n[ Security Layer ]")

    def check_security():
        from security import scan, SecurityFinding, SecurityScanResult
        assert callable(scan)

    ok = check("security module API", check_security)
    if not ok:
        failures.append("security")

    # ── Final ─────────────────────────────────────────────────────────────────
    print()
    if failures:
        print(f"[WARN] {len(failures)} check(s) failed: {', '.join(failures)}")
        print("\nThinksoft engine partially ready — see failures above")
        sys.exit(1)
    else:
        print("Thinksoft engine ready")


if __name__ == "__main__":
    main()
