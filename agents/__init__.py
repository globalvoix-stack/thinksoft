"""
Thinksoft agent registry.

Available agents:
  orchestrator — Sonnet 4.6, task planning and coordination
  kimi         — Kimi K2.5, visual clone from screenshots
  gemini       — Gemini Flash, UI component generation
  haiku        — Haiku 4.5, simple backend generation
  sonnet       — Sonnet 4.6, complex backend + security
  critic       — Sonnet 4.6, code quality review
"""
from agents.base import AgentInput, AgentOutput, BaseAgent
from agents.critic.agent import CriticAgent
from agents.gemini.agent import GeminiAgent
from agents.haiku.agent import HaikuAgent
from agents.kimi.agent import KimiAgent
from agents.orchestrator.agent import OrchestratorAgent
from agents.sonnet.agent import SonnetAgent

AGENT_REGISTRY: dict[str, type[BaseAgent]] = {
    "orchestrator": OrchestratorAgent,
    "kimi": KimiAgent,
    "gemini": GeminiAgent,
    "haiku": HaikuAgent,
    "sonnet": SonnetAgent,
    "critic": CriticAgent,
}


def get_agent(name: str) -> BaseAgent:
    """Instantiate an agent by name. Raises KeyError for unknown names."""
    cls = AGENT_REGISTRY[name]
    return cls()


__all__ = [
    "AgentInput",
    "AgentOutput",
    "BaseAgent",
    "OrchestratorAgent",
    "KimiAgent",
    "GeminiAgent",
    "HaikuAgent",
    "SonnetAgent",
    "CriticAgent",
    "AGENT_REGISTRY",
    "get_agent",
]
