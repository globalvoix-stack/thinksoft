"""
Security layer — three-tier code analysis.

Tier 1 (semgrep): runs on every code generation.
Tier 2 (ai_review): triggered by auth/payment/route scopes.
Tier 3 (deep_scan): explicit user request only.

Public API:
  scan(code, language, scope=, deep=)  — run the full pipeline
  SecurityFinding                       — individual finding dataclass
  SecurityScanResult                    — aggregate result with passed flag
"""
from security.scanner import (
    SecurityFinding,
    SecurityScanResult,
    scan,
    tier1_semgrep,
    tier2_ai_review,
    tier3_deep_scan,
)

__all__ = [
    "SecurityFinding",
    "SecurityScanResult",
    "scan",
    "tier1_semgrep",
    "tier2_ai_review",
    "tier3_deep_scan",
]
