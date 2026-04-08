"""Exa AI integration — semantic competitor discovery."""
from __future__ import annotations

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

_BASE = "https://api.exa.ai"
_TIMEOUT = 30.0


@dataclass
class ExaResult:
    url: str
    title: str
    score: float
    published_date: str | None
    author: str | None
    text: str | None
    highlights: list[str] = field(default_factory=list)


@dataclass
class ExaSearchResponse:
    query: str
    results: list[ExaResult]
    autoprompt_string: str | None = None


def _headers() -> dict[str, str]:
    settings = get_settings()
    if not settings.exa_api_key:
        raise RuntimeError("EXA_API_KEY is not configured")
    return {
        "x-api-key": settings.exa_api_key,
        "Content-Type": "application/json",
    }


@retry(
    retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True,
)
async def search_competitors(
    query: str,
    *,
    num_results: int = 10,
    include_text: bool = False,
    use_autoprompt: bool = True,
) -> ExaSearchResponse:
    """Semantic search to discover competitor websites."""
    log.info("exa.search.start", query=query, num_results=num_results)

    payload: dict[str, Any] = {
        "query": query,
        "numResults": num_results,
        "useAutoprompt": use_autoprompt,
        "type": "neural",
        "category": "company",
    }
    if include_text:
        payload["contents"] = {"text": {"maxCharacters": 1000}, "highlights": {"numSentences": 2}}

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.post(
            f"{_BASE}/search",
            headers=_headers(),
            json=payload,
        )
        resp.raise_for_status()

    body = resp.json()
    results = [
        ExaResult(
            url=r.get("url", ""),
            title=r.get("title", ""),
            score=r.get("score", 0.0),
            published_date=r.get("publishedDate"),
            author=r.get("author"),
            text=r.get("text"),
            highlights=r.get("highlights", []),
        )
        for r in body.get("results", [])
    ]

    log.info("exa.search.done", query=query, result_count=len(results))
    return ExaSearchResponse(
        query=query,
        results=results,
        autoprompt_string=body.get("autopromptString"),
    )


@retry(
    retry=retry_if_exception_type((httpx.HTTPError, httpx.TimeoutException)),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True,
)
async def find_similar(url: str, *, num_results: int = 5) -> ExaSearchResponse:
    """Find websites similar to the given URL."""
    log.info("exa.similar.start", url=url, num_results=num_results)

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        resp = await client.post(
            f"{_BASE}/findSimilar",
            headers=_headers(),
            json={"url": url, "numResults": num_results},
        )
        resp.raise_for_status()

    body = resp.json()
    results = [
        ExaResult(
            url=r.get("url", ""),
            title=r.get("title", ""),
            score=r.get("score", 0.0),
            published_date=r.get("publishedDate"),
            author=r.get("author"),
            text=r.get("text"),
            highlights=r.get("highlights", []),
        )
        for r in body.get("results", [])
    ]

    log.info("exa.similar.done", url=url, result_count=len(results))
    return ExaSearchResponse(query=url, results=results)
