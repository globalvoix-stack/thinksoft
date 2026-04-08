"""Wappalyzer integration — tech stack detection via wappalyzer-python."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any

import structlog

log = structlog.get_logger(__name__)


@dataclass
class TechStackResult:
    url: str
    technologies: dict[str, list[str]] = field(default_factory=dict)
    """Category → list of detected technology names."""
    raw: dict[str, Any] = field(default_factory=dict)


async def detect(url: str) -> TechStackResult:
    """
    Detect technologies used by a URL using the Wappalyzer CLI/library.

    Falls back to an empty result if wappalyzer is not installed, so the
    pipeline degrades gracefully rather than crashing.
    """
    log.info("wappalyzer.detect.start", url=url)

    try:
        from Wappalyzer import Wappalyzer, WebPage  # type: ignore[import]
    except ImportError:
        log.warning("wappalyzer.not_installed", url=url)
        return TechStackResult(url=url)

    try:
        loop = asyncio.get_event_loop()
        # Wappalyzer is sync; run in executor to avoid blocking event loop
        wappalyzer = await loop.run_in_executor(None, Wappalyzer.latest)
        webpage = await loop.run_in_executor(None, WebPage.new_from_url, url)
        detected: dict[str, Any] = await loop.run_in_executor(
            None, wappalyzer.analyze_with_categories, webpage
        )
    except Exception as exc:
        log.warning("wappalyzer.detect.error", url=url, error=str(exc))
        return TechStackResult(url=url)

    # Reorganize: {tech_name: {categories: [...], ...}} → {category: [tech_name, ...]}
    categories: dict[str, list[str]] = {}
    for tech_name, meta in detected.items():
        for cat in meta.get("categories", []):
            categories.setdefault(cat, []).append(tech_name)

    result = TechStackResult(url=url, technologies=categories, raw=detected)
    log.info("wappalyzer.detect.done", url=url, tech_count=len(detected))
    return result
