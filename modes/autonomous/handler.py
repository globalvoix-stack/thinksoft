"""
Autonomous mode handler — Orchestrator + context bus + memory.

Pipeline:
  1. Orchestrator (Sonnet 4.6) creates execution plan
  2. Sub-agents run per plan tasks
  3. Critic reviews all output
  4. Results persisted to context bus + memory
"""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

import structlog

from agents import AgentInput, AgentOutput, get_agent
from context import ContextBus, load as load_bus, save as save_bus
from context.bus import AGENT_DONE, AGENT_ERROR, AGENT_RUNNING
from memory import write as memory_write
from queue.manager import progress as job_progress

log = structlog.get_logger(__name__)


@dataclass
class AutonomousResult:
    job_id: UUID
    success: bool
    orchestrator_plan: dict[str, Any] = field(default_factory=dict)
    agent_outputs: dict[str, AgentOutput] = field(default_factory=dict)
    critic_review: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


async def run(
    project_id: UUID,
    session_id: UUID,
    job_id: UUID,
    prompt: str,
) -> AutonomousResult:
    """Run the full Autonomous pipeline."""
    log.info("autonomous.run.start", project_id=str(project_id), job_id=str(job_id))

    bus = await load_bus(project_id, session_id)
    bus.mode = "autonomous"
    bus.job_id = job_id

    base_input = AgentInput(
        project_id=project_id,
        session_id=session_id,
        job_id=job_id,
        prompt=prompt,
        context=bus,
        mode="autonomous",
    )

    # Step 1: Orchestrator
    await job_progress(job_id, 5, "orchestrating")
    orchestrator = get_agent("orchestrator")
    bus.set_agent_status("orchestrator", AGENT_RUNNING)
    orch_out = await orchestrator.run(base_input)
    bus.set_agent_status("orchestrator", AGENT_DONE if orch_out.success else AGENT_ERROR)

    if not orch_out.success:
        await save_bus(bus, mode="autonomous")
        return AutonomousResult(job_id=job_id, success=False, error=orch_out.error)

    plan = orch_out.result
    tasks = plan.get("tasks", [])
    await job_progress(job_id, 15, "plan_ready")

    # Step 2: Run sub-agents per plan
    agent_outputs: dict[str, AgentOutput] = {"orchestrator": orch_out}
    total_tasks = len(tasks)

    for idx, task in enumerate(tasks):
        agent_name = task.get("agent", "haiku")
        task_desc = task.get("description", prompt)

        if agent_name not in ("kimi", "gemini", "haiku", "sonnet"):
            log.warning("autonomous.unknown_agent", agent=agent_name)
            continue

        pct = 15 + int((idx + 1) / max(total_tasks, 1) * 60)
        await job_progress(job_id, pct, f"running {agent_name}")

        agent = get_agent(agent_name)
        agent_input = AgentInput(
            project_id=project_id,
            session_id=session_id,
            job_id=job_id,
            prompt=prompt,
            context=bus,
            mode="autonomous",
            extra={"task_description": task_desc},
        )
        bus.set_agent_status(agent_name, AGENT_RUNNING)
        out = await agent.run(agent_input)
        bus.set_agent_status(agent_name, AGENT_DONE if out.success else AGENT_ERROR)
        agent_outputs[agent_name] = out

    # Step 3: Critic
    await job_progress(job_id, 80, "reviewing")
    critic = get_agent("critic")
    bus.set_agent_status("critic", AGENT_RUNNING)
    critic_out = await critic.run(base_input)
    bus.set_agent_status("critic", AGENT_DONE if critic_out.success else AGENT_ERROR)
    agent_outputs["critic"] = critic_out

    # Step 4: Persist memory (non-light mode)
    try:
        summary = bus.summary()
        await memory_write(
            project_id,
            session_id,
            content=f"Generation: {prompt[:200]}. Result: {summary}",
            source="agent_decision",
            memory_type="decision",
            mode="autonomous",
        )
    except Exception as exc:
        log.warning("autonomous.memory_write_failed", error=str(exc))

    await save_bus(bus, mode="autonomous")
    await job_progress(job_id, 100, "done")

    return AutonomousResult(
        job_id=job_id,
        success=True,
        orchestrator_plan=plan,
        agent_outputs=agent_outputs,
        critic_review=critic_out.result if critic_out.success else {},
    )
