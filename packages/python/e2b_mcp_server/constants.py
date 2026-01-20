"""
Configuration constants for E2B MCP Server.
"""

import os

# Timeout settings (in milliseconds)
DEFAULT_SANDBOX_TIMEOUT_MS = 300000  # 5 minutes
MAX_SANDBOX_TIMEOUT_MS = 3600000  # 1 hour

# Sandbox management
MAX_ACTIVE_SANDBOXES = int(os.getenv("MAX_ACTIVE_SANDBOXES", "10"))

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
