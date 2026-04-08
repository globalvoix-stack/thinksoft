"""
Max mode handler — full team + competitor scraping + Kimi screenshots.

Pipeline:
  1. Crawler: Exa competitor discovery + Firecrawl scrape with screenshots
  2. Orchestrator: plan with full context
  3. Kimi K2.5: visual analysis from screenshots
  4. Gemini Flash: UI component generation
  5. Sonnet: complex backend
  6. Critic: final review

Always used for the first prompt.
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

import structlog

from agents import AgentInput, AgentOutput, get_agent
from config.constants import MAX_COMPETITORS_SCRAPED
from context import ContextBus, load as load_bus, save as save_bus
from context.bus import AGENT_DONE, AGENT_ERROR, AGENT_RUNNING
from crawler import run as crawl
from memory import write as memory_write
from queue.manager import progress as job_progress

log = structlog.get_logger(__name__)


@dataclass
class MaxResult:
    job_id: UUID
    success: bool
    orchestrator_plan: dict[str, Any] = field(default_factory=dict)
    agent_outputs: dict[str, AgentOutput] = field(default_factory=dict)
    competitor_count: int = 0
    critic_review: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


async def run(
    project_id: UUID,
    session_id: UUID,
    job_id: UUID,
    prompt: str,
    *,
    industry: str | None = None,
) -> MaxResult:
    """Run the full Max pipeline with competitor scraping."""
    log.info("max.run.start", project_id=str(project_id), job_id=str(job_id))

    bus = await load_bus(project_id, session_id)
    bus.mode = "max"
    bus.job_id = job_id

    # Step 1: Competitor discovery + scraping
    await job_progress(job_id, 5, "discovering_competitors")
    screenshots: list[str] = []
    competitor_count = 0

    try:
        crawler_result = await crawl(
            prompt,
            industry=industry,
            max_competitors=MAX_COMPETITORS_SCRAPED,
        )
        competitor_count = len(crawler_result.competitors)
        for competitor in crawler_result.competitors:
            screenshots.extend(competitor.screenshots)

        bus.set_artifact("competitors", [
            {"url": c.url, "tech_stack": c.tech_stack}
            for c in crawler_result.competitors
        ])
        log.info("max.crawler.done", competitor_count=competitor_count, screenshot_count=len(screenshots))
    except Exception as exc:
        log.warning("max.crawler.failed", error=str(exc))
        # Non-fatal: continue without competitor data

    await job_progress(job_id, 20, "orchestrating")

    base_input = AgentInput(
        project_id=project_id,
        session_id=session_id,
        job_id=job_id,
        prompt=prompt,
        context=bus,
        mode="max",
    )

    # Step 2: Orchestrator
    orchestrator = get_agent("orchestrator")
    bus.set_agent_status("orchestrator", AGENT_RUNNING)
    orch_out = await orchestrator.run(base_input)
    bus.set_agent_status("orchestrator", AGENT_DONE if orch_out.success else AGENT_ERROR)

    agent_outputs: dict[str, AgentOutput] = {"orchestrator": orch_out}

    if not orch_out.success:
        await save_bus(bus, mode="max")
        return MaxResult(job_id=job_id, success=False, error=orch_out.error)

    plan = orch_out.result
    detected_industry = plan.get("industry") or industry
    await job_progress(job_id, 30, "visual_analysis")

    # Step 3: Kimi visual analysis (requires screenshots)
    if screenshots:
        kimi = get_agent("kimi")
        kimi_input = AgentInput(
            project_id=project_id,
            session_id=session_id,
            job_id=job_id,
            prompt=prompt,
            context=bus,
            mode="max",
            extra={"screenshots": screenshots[:6]},  # cap at 6 screenshots
        )
        bus.set_agent_status("kimi", AGENT_RUNNING)
        kimi_out = await kimi.run(kimi_input)
        bus.set_agent_status("kimi", AGENT_DONE if kimi_out.success else AGENT_ERROR)
        agent_outputs["kimi"] = kimi_out
    else:
        log.info("max.kimi.skipped", reason="no_screenshots")

    await job_progress(job_id, 50, "generating_ui")

    # Step 4: Gemini UI generation
    gemini = get_agent("gemini")
    bus.set_agent_status("gemini", AGENT_RUNNING)
    gemini_out = await gemini.run(base_input)
    bus.set_agent_status("gemini", AGENT_DONE if gemini_out.success else AGENT_ERROR)
    agent_outputs["gemini"] = gemini_out

    await job_progress(job_id, 70, "generating_backend")

    # Step 5: Sonnet complex backend
    sonnet_agent = get_agent("sonnet")
    sonnet_input = AgentInput(
        project_id=project_id,
        session_id=session_id,
        job_id=job_id,
        prompt=prompt,
        context=bus,
        mode="max",
        extra={"task_description": f"Full backend for: {prompt}"},
    )
    bus.set_agent_status("sonnet", AGENT_RUNNING)
    sonnet_out = await sonnet_agent.run(sonnet_input)
    bus.set_agent_status("sonnet", AGENT_DONE if sonnet_out.success else AGENT_ERROR)
    agent_outputs["sonnet"] = sonnet_out

    await job_progress(job_id, 88, "reviewing")

    # Step 6: Critic review
    critic = get_agent("critic")
    bus.set_agent_status("critic", AGENT_RUNNING)
    critic_out = await critic.run(base_input)
    bus.set_agent_status("critic", AGENT_DONE if critic_out.success else AGENT_ERROR)
    agent_outputs["critic"] = critic_out

    # Persist memory
    try:
        await memory_write(
            project_id,
            session_id,
            content=(
                f"Max generation: {prompt[:200]}. "
                f"Industry: {detected_industry}. "
                f"Competitors: {competitor_count}."
            ),
            source="agent_decision",
            memory_type="decision",
            mode="max",
        )
    except Exception as exc:
        log.warning("max.memory_write_failed", error=str(exc))

    await save_bus(bus, mode="max")
    await job_progress(job_id, 100, "done")

    return MaxResult(
        job_id=job_id,
        success=True,
        orchestrator_plan=plan,
        agent_outputs=agent_outputs,
        competitor_count=competitor_count,
        critic_review=critic_out.result if critic_out.success else {},
    )
