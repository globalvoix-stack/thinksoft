"""Stub: provider service types."""
from enum import Enum


class ProviderType(str, Enum):
    GITHUB = "github"
    GITLAB = "gitlab"
    AZURE_DEVOPS = "azure_devops"
    BITBUCKET = "bitbucket"


class AuthenticationError(Exception):
    """Raised when authentication fails with a provider."""
    pass
