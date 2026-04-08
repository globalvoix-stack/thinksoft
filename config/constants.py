# Model identifiers
KIMI_MODEL = "kimi-k2.5"
GEMINI_FLASH_MODEL = "gemini-3-flash"
HAIKU_MODEL = "claude-haiku-4-5"
SONNET_MODEL = "claude-sonnet-4-6"

# Mode thresholds
COMPLEXITY_THRESHOLD = 2  # signals needed to trigger orchestrator

# Memory
MEMORY_RELEVANCE_THRESHOLD = 0.75  # Voyage similarity cutoff
MAX_MEMORY_ENTRIES_PER_CALL = 10

# Crawlee
MAX_COMPETITORS_SCRAPED = 3
CRAWLEE_TIMEOUT_SECONDS = 30

# Jobs
JOB_TIMEOUT_SECONDS = 300
SSE_HEARTBEAT_SECONDS = 15

# Security
SEMGREP_TIMEOUT_SECONDS = 60
