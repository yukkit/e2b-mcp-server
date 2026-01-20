"""
Sandbox lifecycle manager for E2B MCP Server.
"""

import logging
from typing import Any, Optional

from e2b_code_interpreter import Sandbox

from .constants import (
    DEFAULT_SANDBOX_TIMEOUT_MS,
    MAX_SANDBOX_TIMEOUT_MS,
    MAX_ACTIVE_SANDBOXES,
)
from .exceptions import SandboxError, SandboxNotFoundError, SandboxLimitExceededError

logger = logging.getLogger("e2b-mcp-server")


class SandboxManager:
    """
    Manages E2B sandbox lifecycle with production-grade features.

    Features:
    - Automatic resource cleanup
    - Sandbox limit enforcement
    - Comprehensive logging

    Note: No locks needed as STDIO mode processes requests serially.
    """

    def __init__(self, max_sandboxes: int = MAX_ACTIVE_SANDBOXES):
        """
        Initialize the sandbox manager.

        Args:
            max_sandboxes: Maximum number of concurrent sandboxes
        """
        self._sandboxes: dict[str, Sandbox] = {}
        self._max_sandboxes = max_sandboxes
        logger.info(f"SandboxManager initialized with max_sandboxes={max_sandboxes}")

    def create_sandbox(self, timeout_ms: Optional[int] = None) -> tuple[str, Sandbox]:
        """
        Create a new sandbox with proper error handling.

        Args:
            timeout_ms: Timeout in milliseconds

        Returns:
            Tuple of (sandbox_id, sandbox_instance)

        Raises:
            SandboxLimitExceededError: If max sandboxes limit is reached
        """
        if len(self._sandboxes) >= self._max_sandboxes:
            raise SandboxLimitExceededError(
                f"Maximum number of sandboxes ({self._max_sandboxes}) reached"
            )

        timeout = timeout_ms if timeout_ms else DEFAULT_SANDBOX_TIMEOUT_MS
        timeout = min(timeout, MAX_SANDBOX_TIMEOUT_MS)

        try:
            sbx = Sandbox(timeout=timeout)
            sandbox_id = sbx.sandbox_id
            self._sandboxes[sandbox_id] = sbx
            logger.info(
                f"Sandbox created: {sandbox_id} (timeout={timeout}ms, "
                f"active={len(self._sandboxes)})"
            )
            return sandbox_id, sbx
        except Exception as e:
            logger.error(f"Failed to create sandbox: {e}")
            raise SandboxError(f"Failed to create sandbox: {e}") from e

    def get_sandbox(self, sandbox_id: str) -> Sandbox:
        """
        Get a sandbox by ID.

        Args:
            sandbox_id: The sandbox identifier

        Returns:
            The sandbox instance

        Raises:
            SandboxNotFoundError: If sandbox doesn't exist
        """
        if sandbox_id not in self._sandboxes:
            raise SandboxNotFoundError(f"Sandbox {sandbox_id} not found")
        return self._sandboxes[sandbox_id]

    def kill_sandbox(self, sandbox_id: str) -> None:
        """
        Kill and remove a sandbox.

        Args:
            sandbox_id: The sandbox identifier

        Raises:
            SandboxNotFoundError: If sandbox doesn't exist
        """
        if sandbox_id not in self._sandboxes:
            raise SandboxNotFoundError(f"Sandbox {sandbox_id} not found")

        try:
            sbx = self._sandboxes[sandbox_id]
            sbx.kill()
            del self._sandboxes[sandbox_id]
            logger.info(f"Sandbox killed: {sandbox_id} (active={len(self._sandboxes)})")
        except Exception as e:
            logger.error(f"Error killing sandbox {sandbox_id}: {e}")
            # Still remove it from tracking even if kill fails
            self._sandboxes.pop(sandbox_id, None)
            raise SandboxError(f"Error killing sandbox: {e}") from e

    def cleanup_all(self) -> None:
        """Clean up all active sandboxes. Called during shutdown."""
        sandbox_ids = list(self._sandboxes.keys())
        logger.info(f"Cleaning up {len(sandbox_ids)} sandboxes")

        for sandbox_id in sandbox_ids:
            try:
                sbx = self._sandboxes[sandbox_id]
                sbx.kill()
                logger.info(f"Cleaned up sandbox: {sandbox_id}")
            except Exception as e:
                logger.error(f"Error cleaning up sandbox {sandbox_id}: {e}")

        self._sandboxes.clear()
        logger.info("All sandboxes cleaned up")

    def get_stats(self) -> dict[str, Any]:
        """Get current sandbox statistics."""
        return {
            "active_sandboxes": len(self._sandboxes),
            "max_sandboxes": self._max_sandboxes,
            "sandbox_ids": list(self._sandboxes.keys()),
        }
