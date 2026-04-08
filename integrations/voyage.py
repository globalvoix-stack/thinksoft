"""Voyage AI integration — memory embeddings."""
from __future__ import annotations

import structlog
import voyageai
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from config.constants import VOYAGE_EMBEDDING_DIM, VOYAGE_MODEL
from config.settings import get_settings

log = structlog.get_logger(__name__)


def _client() -> voyageai.AsyncClient:
    return voyageai.AsyncClient(api_key=get_settings().voyage_ai_api_key)


@retry(
    retry=retry_if_exception_type(Exception),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=8),
    reraise=True,
)
async def embed(texts: list[str], *, input_type: str = "document") -> list[list[float]]:
    """
    Embed a batch of texts.

    input_type: "document" for storage, "query" for retrieval.
    Returns a list of float vectors, each of length VOYAGE_EMBEDDING_DIM.
    """
    if not texts:
        return []

    log.info("voyage.embed.start", count=len(texts), input_type=input_type)
    client = _client()
    result = await client.embed(texts, model=VOYAGE_MODEL, input_type=input_type)
    vectors = result.embeddings

    if any(len(v) != VOYAGE_EMBEDDING_DIM for v in vectors):
        raise ValueError(
            f"Unexpected embedding dimension: expected {VOYAGE_EMBEDDING_DIM}, "
            f"got {[len(v) for v in vectors]}"
        )

    log.info("voyage.embed.done", count=len(vectors))
    return vectors


@retry(
    retry=retry_if_exception_type(Exception),
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=8),
    reraise=True,
)
async def embed_query(text: str) -> list[float]:
    """Embed a single query string for similarity search."""
    vectors = await embed([text], input_type="query")
    return vectors[0]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Pure-Python cosine similarity between two equal-length vectors."""
    if len(a) != len(b):
        raise ValueError(f"Vector length mismatch: {len(a)} vs {len(b)}")
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(x * x for x in b) ** 0.5
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot / (norm_a * norm_b)
