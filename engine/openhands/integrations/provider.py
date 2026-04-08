"""Stub: provider handler types."""
from typing import Any
from engine.openhands.integrations.service_types import ProviderType

# Type alias for provider tokens: {provider_type: token_string}
PROVIDER_TOKEN_TYPE = dict[str, str]


class ProviderHandler:
    """Stub: handles git provider authentication. To be implemented in Thinksoft."""

    def __init__(self, provider_tokens: PROVIDER_TOKEN_TYPE | None = None, external_auth_token: str | None = None):
        self.provider_tokens = provider_tokens or {}
        self.external_auth_token = external_auth_token

    @staticmethod
    def check_cmd_action_for_provider_token_ref(action: Any) -> bool:
        return False

    def verify_provider(self, *args: Any, **kwargs: Any) -> None:
        pass

    def clone_repository(self, *args: Any, **kwargs: Any) -> Any:
        return None
