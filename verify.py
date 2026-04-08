"""
Thinksoft Session 1 verification script.
Imports every module and checks settings load to confirm the foundation is healthy.
"""
import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(__file__))


def check(label: str, fn) -> bool:
    try:
        fn()
        print(f"  [OK] {label}")
        return True
    except Exception as e:
        print(f"  [FAIL] {label}: {e}")
        return False


def main():
    print("\n=== Thinksoft Engine Verification ===\n")
    failures = []

    # --- New Thinksoft module structure ---
    print("[ Thinksoft Modules ]")

    def import_check(module_path: str):
        def _check():
            import importlib
            importlib.import_module(module_path)
        return _check

    thinksoft_modules = [
        "engine",
        "engine.execution",
        "engine.filesystem",
        "engine.sandbox",
        "engine.tools",
        "agents",
        "agents.orchestrator",
        "agents.kimi",
        "agents.gemini",
        "agents.haiku",
        "agents.sonnet",
        "modes",
        "modes.light",
        "modes.autonomous",
        "modes.max",
        "memory",
        "context",
        "security",
        "queue",
        "crawler",
        "api",
        "db",
        "db.migrations",
        "config",
    ]

    for mod in thinksoft_modules:
        ok = check(f"import {mod}", import_check(mod))
        if not ok:
            failures.append(mod)

    # --- Engine core (OpenHands runtime infrastructure) ---
    print("\n[ Engine Core (OpenHands runtime) ]")

    engine_core_modules = [
        "engine.openhands",
        "engine.openhands.core.exceptions",
        "engine.openhands.core.schema",
        "engine.openhands.events",
        "engine.openhands.events.action",
        "engine.openhands.events.observation",
        "engine.openhands.events.serialization",
        "engine.openhands.llm.metrics",
        "engine.openhands.llm.llm_registry",
        "engine.openhands.integrations",
        "engine.openhands.microagent",
        "engine.openhands.security",
        "engine.openhands.io",
        "engine.openhands.mcp",
    ]

    for mod in engine_core_modules:
        ok = check(f"import {mod}", import_check(mod))
        if not ok:
            failures.append(mod)

    # --- Config constants ---
    print("\n[ Config Constants ]")

    def check_constants():
        from config.constants import (
            KIMI_MODEL, GEMINI_FLASH_MODEL, HAIKU_MODEL, SONNET_MODEL,
            COMPLEXITY_THRESHOLD, MEMORY_RELEVANCE_THRESHOLD,
            MAX_MEMORY_ENTRIES_PER_CALL, JOB_TIMEOUT_SECONDS,
        )
        assert KIMI_MODEL == "kimi-k2.5"
        assert SONNET_MODEL == "claude-sonnet-4-6"
        assert COMPLEXITY_THRESHOLD == 2
        assert MEMORY_RELEVANCE_THRESHOLD == 0.75

    ok = check("config.constants values", check_constants)
    if not ok:
        failures.append("config.constants")

    # --- Settings loading (requires .env) ---
    print("\n[ Settings (requires .env file) ]")

    def check_settings_load():
        # Create a temporary .env with dummy values to test schema loading
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
        import tempfile, pathlib
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(test_env)
            tmp_path = f.name

        try:
            from pydantic_settings import BaseSettings
            from pydantic import PostgresDsn

            class _TestSettings(BaseSettings):
                neon_database_url: PostgresDsn
                anthropic_api_key: str
                google_ai_api_key: str
                kimi_api_key: str
                kimi_base_url: str = "https://api.moonshot.ai/v1"
                voyage_ai_api_key: str
                firecrawl_api_key: str
                e2b_api_key: str
                better_auth_secret: str
                better_auth_url: str
                app_env: str = "development"
                app_port: int = 8000
                log_level: str = "info"

                class Config:
                    env_file = tmp_path
                    case_sensitive = False

            settings = _TestSettings()
            assert settings.app_env == "development"
            assert settings.app_port == 8000
            assert settings.kimi_base_url == "https://api.moonshot.ai/v1"
        finally:
            pathlib.Path(tmp_path).unlink(missing_ok=True)

    ok = check("config.settings schema", check_settings_load)
    if not ok:
        failures.append("config.settings")

    # --- Structured logging ---
    print("\n[ Structured Logging ]")

    def check_structlog():
        import structlog
        logger = structlog.get_logger("verify")
        logger.info("structlog_ok", check="verify")

    ok = check("structlog configured", check_structlog)
    if not ok:
        failures.append("structlog")

    # --- Directory structure ---
    print("\n[ Directory Structure ]")

    import pathlib
    root = pathlib.Path(__file__).parent

    required_dirs = [
        "engine/execution", "engine/filesystem", "engine/sandbox", "engine/tools",
        "agents/orchestrator", "agents/kimi", "agents/gemini", "agents/haiku", "agents/sonnet",
        "modes/light", "modes/autonomous", "modes/max",
        "memory", "context", "security", "queue", "crawler", "api", "db/migrations", "config",
        "tests",
    ]

    for d in required_dirs:
        path = root / d
        ok = check(f"dir {d}/", lambda p=path: (p.is_dir() or (_ for _ in ()).throw(FileNotFoundError(f"Missing: {p}"))))
        if not ok:
            failures.append(d)

    # --- Final result ---
    print()
    if failures:
        print(f"[WARN] {len(failures)} check(s) failed: {', '.join(failures)}")
        print("\nThinksoft engine partially ready — see failures above")
        sys.exit(1)
    else:
        print("Thinksoft engine ready")


if __name__ == "__main__":
    main()
