"""
First Prompt Pipeline — always Max mode.

Deterministic intent extraction → competitor discovery → visual analysis → full generation.

Steps:
  1. Extract intent deterministically (Sonnet 4.6, structured output)
  2. Run the Max pipeline (crawler + all agents)
  3. Return the job ID for SSE streaming

The first prompt for every project ALWAYS runs Max, regardless of project mode setting.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

import structlog

from config.constants import SONNET_MODEL
from integrations.anthropic import sonnet
from modes.max.handler import MaxResult, run as max_run
from queue.manager import complete as job_complete
from queue.manager import enqueue, fail as job_fail, start as job_start

log = structlog.get_logger(__name__)

_INTENT_SYSTEM = """You are an intent extraction engine.
Given a user's project request, extract structured intent.
Return ONLY a JSON object — no markdown, no explanation:
{
  "product_type": "saas|marketplace|portfolio|landing_page|dashboard|other",
  "industry": str | null,
  "target_audience": str,
  "core_features": [str],
  "design_style": "modern|minimal|bold|playful|corporate|other",
  "competitor_query": "search query to find similar products",
  "is_first_prompt": true
}
"""


@dataclass
class IntentResult:
    product_type: str
    industry: str | None
    target_audience: str
    core_features: list[str]
    design_style: str
    competitor_query: str
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class FirstPromptResult:
    job_id: UUID
    intent: IntentResult
    max_result: MaxResult | None = None
    error: str | None = None


async def extract_intent(prompt: str) -> IntentResult:
    """
    Deterministic intent extraction using Sonnet 4.6.

    Structured output only — no free-form text.
    """
    log.info("first_prompt.extract_intent.start", prompt_length=len(prompt))

    resp = await sonnet(
        [{"role": "user", "content": prompt}],
        system=_INTENT_SYSTEM,
        max_tokens=512,
        temperature=0.0,  # deterministic
    )

    try:
        data = json.loads(resp.content)
    except json.JSONDecodeError:
        log.warning("first_prompt.extract_intent.parse_error", content=resp.content[:200])
        data = {
            "product_type": "other",
            "industry": None,
            "target_audience": "general users",
            "core_features": [],
            "design_style": "modern",
            "competitor_query": prompt[:100],
        }

    intent = IntentResult(
        product_type=data.get("product_type", "other"),
        industry=data.get("industry"),
        target_audience=data.get("target_audience", ""),
        core_features=data.get("core_features", []),
        design_style=data.get("design_style", "modern"),
        competitor_query=data.get("competitor_query", prompt[:100]),
        raw=data,
    )
    log.info(
        "first_prompt.extract_intent.done",
        product_type=intent.product_type,
        industry=intent.industry,
        feature_count=len(intent.core_features),
    )
    return intent


async def run(
    project_id: UUID,
    session_id: UUID,
    prompt: str,
) -> FirstPromptResult:
    """
    Execute the first prompt pipeline for a project.

    Always runs Max mode. Returns a FirstPromptResult with job_id for SSE.
    The job runs to completion synchronously (caller wraps in background task).
    """
    log.info("first_prompt.run.start", project_id=str(project_id))

    # Extract intent first
    intent = await extract_intent(prompt)

    # Create job
    job = await enqueue(
        project_id,
        session_id,
        mode="max",
        metadata={
            "is_first_prompt": True,
            "product_type": intent.product_type,
            "industry": intent.industry,
        },
    )
    job_id = job.id
    log.info("first_prompt.job_created", job_id=str(job_id))

    await job_start(job_id)

    try:
        max_result = await max_run(
            project_id,
            session_id,
            job_id,
            prompt,
            industry=intent.industry,
        )

        if max_result.success:
            await job_complete(job_id, {
                "intent": intent.raw,
                "competitor_count": max_result.competitor_count,
                "critic_passed": max_result.critic_review.get("passed", False),
            })
        else:
            await job_fail(job_id, max_result.error or "Max pipeline failed")

        return FirstPromptResult(job_id=job_id, intent=intent, max_result=max_result)

    except Exception as exc:
        log.error("first_prompt.run.error", job_id=str(job_id), error=str(exc))
        await job_fail(job_id, str(exc))
        return FirstPromptResult(job_id=job_id, intent=intent, error=str(exc))
