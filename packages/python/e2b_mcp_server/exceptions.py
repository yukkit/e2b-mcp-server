"""
Custom exceptions for E2B MCP Server.
"""


class SandboxError(Exception):
    """Base exception for sandbox-related errors."""

    pass


class SandboxNotFoundError(SandboxError):
    """Raised when a requested sandbox does not exist."""

    pass


class SandboxLimitExceededError(SandboxError):
    """Raised when the maximum number of active sandboxes is exceeded."""

    pass
