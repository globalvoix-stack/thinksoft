from dataclasses import dataclass

from engine.openhands.core.schema import ActionType
from engine.openhands.events.action.action import Action


@dataclass
class NullAction(Action):
    """An action that does nothing."""

    action: str = ActionType.NULL

    @property
    def message(self) -> str:
        return 'No action'
