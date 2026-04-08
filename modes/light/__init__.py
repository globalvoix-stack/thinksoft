"""Light mode — fast, single-agent, no context bus, no memory writes."""
from modes.light.handler import LightModeResult, run
__all__ = ["run", "LightModeResult"]
