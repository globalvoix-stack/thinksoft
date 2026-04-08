from dataclasses import dataclass

from engine.openhands.core.schema import ObservationType
from engine.openhands.events.observation.observation import Observation


@dataclass
class LoopDetectionObservation(Observation):
    """Observation for loop recovery state changes.

    This observation is used to notify the UI layer when agent
    is in loop recovery mode.

    This observation is CLI-specific and should only be displayed
    in CLI/TUI mode, not in GUI or other UI modes.
    """

    observation: str = ObservationType.LOOP_DETECTION
