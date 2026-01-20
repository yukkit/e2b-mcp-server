"""
E2B MCP Server - Production-grade Model Context Protocol server for E2B sandboxes.

This package provides a robust MCP server implementation that allows AI models to
interact with E2B code execution sandboxes securely and efficiently.
"""

from . import server
import asyncio

__version__ = "1.0.0"


def main():
    """Main entry point for the package."""
    asyncio.run(server.main())


# Expose important items at package level
__all__ = ["main", "server"]
