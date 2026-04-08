"""
Crawler pipeline — Firecrawl + Exa + Wappalyzer + Neon 72h cache.

Public API:
  run(query, ...)         — discover and scrape competitors; always returns screenshots
  scrape_single(url, ...) — scrape one URL with cache
  CompetitorResult        — per-competitor data (screenshots, tech_stack)
  CrawlerPipelineResult   — full result set
"""
from crawler.pipeline import (
    CompetitorResult,
    CrawlerPipelineResult,
    run,
    scrape_single,
)

__all__ = [
    "CompetitorResult",
    "CrawlerPipelineResult",
    "run",
    "scrape_single",
]
