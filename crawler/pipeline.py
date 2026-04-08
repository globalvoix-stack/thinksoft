"""
Crawler pipeline — competitor discovery and tech stack detection.

Flow:
  1. Exa AI: semantic competitor discovery (up to MAX_COMPETITORS_SCRAPED URLs)
  2. Neon cache: skip Firecrawl for URLs already cached within 72h
  3. Firecrawl: scrape each uncached URL with full-page screenshots (images only, never plain text)
  4. Wappalyzer: detect tech stack per URL
  5. Cache results in Neon (72h TTL)

Returns images always — screenshots are base64-encoded PNGs.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

import structlog

from config.constants import MAX_COMPETITORS_SCRAPED
from db.pool import acquire
from db.queries.crawler_cache import (
    CrawlerCacheEntry,
    get_cached,
    upsert_cache,
)
from integrations.exa import ExaResult, search_competitors
from integrations.firecrawl import ScrapeResult, scrape
from integrations.wappalyzer import TechStackResult, detect

log = structlog.get_logger(__name__)


@dataclass
class CompetitorResult:
    url: str
    title: str
    screenshots: list[str]
    """Base64-encoded PNG screenshots — always present, never plain text."""
    tech_stack: dict[str, list[str]]
    """Wappalyzer category → [tech names]"""
    cached: bool = False


@dataclass
class CrawlerPipelineResult:
    query: str
    competitors: list[CompetitorResult]
    industry: str | None = None


async def _scrape_and_detect(
    url: str, industry: str | None
) -> tuple[ScrapeResult, TechStackResult]:
    """Scrape + detect in parallel."""
    scrape_task = asyncio.create_task(scrape(url, screenshot=True))
    detect_task = asyncio.create_task(detect(url))
    scrape_result, tech_result = await asyncio.gather(scrape_task, detect_task)
    return scrape_result, tech_result


async def run(
    query: str,
    *,
    industry: str | None = None,
    max_competitors: int = MAX_COMPETITORS_SCRAPED,
) -> CrawlerPipelineResult:
    """
    Discover and scrape competitor websites.

    Always returns screenshots (base64). Skips Firecrawl for cached entries.
    """
    log.info("crawler.pipeline.start", query=query, max_competitors=max_competitors)

    # Step 1: Exa competitor discovery
    exa_response = await search_competitors(query, num_results=max_competitors * 2)
    candidates: list[ExaResult] = exa_response.results[:max_competitors * 2]

    competitors: list[CompetitorResult] = []
    processed = 0

    for candidate in candidates:
        if processed >= max_competitors:
            break
        url = candidate.url
        if not url:
            continue

        log.info("crawler.pipeline.processing", url=url)

        # Step 2: Check Neon cache
        async with acquire() as conn:
            cached_entry = await get_cached(conn, url)

        if cached_entry:
            log.info("crawler.pipeline.cache_hit", url=url)
            competitors.append(
                CompetitorResult(
                    url=url,
                    title=candidate.title,
                    screenshots=cached_entry.screenshots,
                    tech_stack=cached_entry.tech_stack,
                    cached=True,
                )
            )
            processed += 1
            continue

        # Step 3 + 4: Firecrawl scrape + Wappalyzer detect
        try:
            scrape_result, tech_result = await _scrape_and_detect(url, industry)
        except Exception as exc:
            log.warning("crawler.pipeline.scrape_failed", url=url, error=str(exc))
            continue

        screenshots = (
            [scrape_result.screenshot_base64]
            if scrape_result.screenshot_base64
            else []
        )

        # Step 5: Cache to Neon
        async with acquire() as conn:
            await upsert_cache(
                conn,
                url=url,
                industry=industry,
                screenshots=screenshots,
                tech_stack=tech_result.technologies,
            )

        competitors.append(
            CompetitorResult(
                url=url,
                title=candidate.title,
                screenshots=screenshots,
                tech_stack=tech_result.technologies,
                cached=False,
            )
        )
        processed += 1

    log.info(
        "crawler.pipeline.done",
        query=query,
        competitor_count=len(competitors),
        cached=sum(1 for c in competitors if c.cached),
    )
    return CrawlerPipelineResult(query=query, competitors=competitors, industry=industry)


async def scrape_single(url: str, *, industry: str | None = None) -> CompetitorResult:
    """Scrape a single URL, using cache if available."""
    log.info("crawler.scrape_single.start", url=url)

    async with acquire() as conn:
        cached = await get_cached(conn, url)

    if cached:
        return CompetitorResult(
            url=url,
            title="",
            screenshots=cached.screenshots,
            tech_stack=cached.tech_stack,
            cached=True,
        )

    scrape_result, tech_result = await _scrape_and_detect(url, industry)
    screenshots = [scrape_result.screenshot_base64] if scrape_result.screenshot_base64 else []

    async with acquire() as conn:
        await upsert_cache(conn, url=url, industry=industry, screenshots=screenshots, tech_stack=tech_result.technologies)

    return CompetitorResult(
        url=url,
        title="",
        screenshots=screenshots,
        tech_stack=tech_result.technologies,
        cached=False,
    )
