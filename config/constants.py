"""
Thinksoft constants — model names, thresholds, limits.
All tunable values live here; nothing hardcoded in business logic.
"""

# ── Model identifiers ──────────────────────────────────────────────────────
KIMI_MODEL = "kimi-k2.5"
GEMINI_FLASH_MODEL = "gemini-1.5-flash"   # updated; gemini-3-flash not yet GA
HAIKU_MODEL = "claude-haiku-4-5-20251001"
SONNET_MODEL = "claude-sonnet-4-6"

# Voyage AI embedding model
VOYAGE_MODEL = "voyage-3"
VOYAGE_EMBEDDING_DIM = 1024

# ── Mode thresholds ────────────────────────────────────────────────────────
COMPLEXITY_THRESHOLD = 2          # orchestrator signals needed to activate
MISMATCH_SUGGESTION_THRESHOLD = 0.85  # confidence to suggest mode switch

# ── Memory ────────────────────────────────────────────────────────────────
MEMORY_RELEVANCE_THRESHOLD = 0.75   # Voyage cosine similarity cutoff
MAX_MEMORY_ENTRIES_PER_CALL = 10

# Source authority order (highest first)
MEMORY_SOURCE_PRIORITY = ["user_explicit", "user_implicit", "agent_decision"]

MEMORY_CONFLICT_THRESHOLD = 0.90   # cosine similarity → likely conflict

# ── Crawler ───────────────────────────────────────────────────────────────
MAX_COMPETITORS_SCRAPED = 3
CRAWLEE_TIMEOUT_SECONDS = 30
CRAWLER_CACHE_TTL_HOURS = 72

# ── Jobs ──────────────────────────────────────────────────────────────────
JOB_TIMEOUT_SECONDS = 300          # 5 minutes
SSE_HEARTBEAT_SECONDS = 15

# ── Security ──────────────────────────────────────────────────────────────
SEMGREP_TIMEOUT_SECONDS = 60

# Scopes that trigger AI security review
SECURITY_REVIEW_TRIGGERS = frozenset(
    ["auth", "session", "jwt", "payment", "financial", "api_route"]
)

# ── Agent ─────────────────────────────────────────────────────────────────
CONTEXT_BUS_SUMMARY_MAX_TOKENS = 100

# ── Auth ──────────────────────────────────────────────────────────────────
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24   # 24 hours

# ── Registry ──────────────────────────────────────────────────────────────
UI_LIBRARIES = ["heroui", "shadcn", "aceternity", "magic-ui", "radix"]
ANIMATION_LIBRARIES = ["framer-motion", "gsap", "lottie", "auto-animate"]
ICON_LIBRARIES = ["lucide", "phosphor", "iconify"]
ASSET_SOURCES = ["spline", "lottiefiles", "storyset", "undraw"]
