"""Firecrawl integration — web scraping and screenshot capture."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any

import httpx
import structlog
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from config.settings import get_settings

log = structlog.get_logger(__name__)

_BASE = "https://api.firecrawl.dev/v1"
_TIMEOUT = 60.0


@dataclass
class ScrapeResult:
    url: str
    markdown: str
    html: str
    screenshot_base64: str | None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CrawlResult:
    url: str
    pages: list[ScrapeResult] = field(default_factory=list)


def _headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {get_settings().firecrawl_api_key}"}


@retry(
    retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True,
)
async def scrape(url: str, *, screenshot: bool = True) -> ScrapeResult:
    """Scrape a single URL. Always requests screenshot when screenshot=True."""
    log.info("firecrawl.scrape.start", url=url, screenshot=screenshot)
    formats = ["markdown", "html"]
    if screenshot:
        formats.append("screenshot@fullPage")

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.post(
            f"{_BASE}/scrape",
            headers=_headers(),
            json={"url": url, "formats": formats},
        )
        resp.raise_for_status()

    data = resp.json().get("data", {})
    result = ScrapeResult(
        url=url,
        markdown=data.get("markdown", ""),
        html=data.get("html", ""),
        screenshot_base64=data.get("screenshot"),
        metadata=data.get("metadata", {}),
    )
    log.info("firecrawl.scrape.done", url=url, has_screenshot=result.screenshot_base64 is not None)
    return result


@retry(
    retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True,
)
async def crawl(
    url: str,
    *,
    max_depth: int = 1,
    max_pages: int = 5,
    screenshot: bool = True,
) -> CrawlResult:
    """Crawl a site; poll until complete. Returns images, never plain text."""
    log.info("firecrawl.crawl.start", url=url, max_depth=max_depth, max_pages=max_pages)
    formats = ["markdown", "html"]
    if screenshot:
        formats.append("screenshot@fullPage")

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.post(
            f"{_BASE}/crawl",
            headers=_headers(),
            json={
                "url": url,
                "maxDepth": max_depth,
                "limit": max_pages,
                "scrapeOptions": {"formats": formats},
            },
        )
        resp.raise_for_status()
        job_id = resp.json()["id"]

    log.info("firecrawl.crawl.polling", job_id=job_id)
    pages: list[ScrapeResult] = []

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        for attempt in range(60):  # poll up to 5 minutes
            await asyncio.sleep(5)
            status_resp = await client.get(
                f"{_BASE}/crawl/{job_id}", headers=_headers()
            )
            status_resp.raise_for_status()
            body = status_resp.json()
            if body.get("status") == "completed":
                for item in body.get("data", []):
                    pages.append(
                        ScrapeResult(
                            url=item.get("metadata", {}).get("sourceURL", url),
                            markdown=item.get("markdown", ""),
                            html=item.get("html", ""),
                            screenshot_base64=item.get("screenshot"),
                            metadata=item.get("metadata", {}),
                        )
                    )
                break
            if body.get("status") == "failed":
                raise RuntimeError(f"Firecrawl crawl failed: {body}")

    log.info("firecrawl.crawl.done", url=url, page_count=len(pages))
    return CrawlResult(url=url, pages=pages)
