"""
E2B MCP Server - Production-grade Model Context Protocol server for E2B sandboxes.

This module provides a robust MCP server implementation that allows AI models to
interact with E2B code execution sandboxes securely and efficiently.
"""

import asyncio
import atexit
import logging
import os
from collections.abc import Sequence
from typing import Any

from dotenv import load_dotenv
from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from pydantic import ValidationError

from .constants import (
    DEFAULT_SANDBOX_TIMEOUT_MS,
    MAX_SANDBOX_TIMEOUT_MS,
    MAX_ACTIVE_SANDBOXES,
    LOG_LEVEL,
)
from .exceptions import SandboxError
from .manager import SandboxManager
from .schemas import (
    CreateSandboxSchema,
    RunCommandSchema,
    ReadFileSchema,
    WriteFileSchema,
    ListFilesSchema,
    RunCodeSchema,
    GetSandboxUrlSchema,
    GetFileDownloadUrlSchema,
    KillSandboxSchema,
    ListSandboxIdsSchema,
)
from .handlers import (
    handle_create_sandbox,
    handle_run_command,
    handle_read_file,
    handle_write_file,
    handle_list_files,
    handle_run_code,
    handle_get_sandbox_url,
    handle_get_file_download_url,
    handle_kill_sandbox,
    handle_list_sandbox_ids,
)


# Load environment variables
load_dotenv()

# Configure logging with production-grade settings
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("e2b-mcp-server")


# Initialize global sandbox manager
sandbox_manager = SandboxManager()


# Register cleanup handler
def cleanup_handler():
    """Cleanup handler for graceful shutdown."""
    try:
        sandbox_manager.cleanup_all()
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")


atexit.register(cleanup_handler)


# Initialize MCP server
app = Server("e2b-code-mcp-server")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="create_sandbox",
            description="Create a new E2B sandbox",
            inputSchema=CreateSandboxSchema.model_json_schema(),
        ),
        Tool(
            name="run_command",
            description="Run a command in the sandbox",
            inputSchema=RunCommandSchema.model_json_schema(),
        ),
        Tool(
            name="read_file",
            description="Read a file from the sandbox",
            inputSchema=ReadFileSchema.model_json_schema(),
        ),
        Tool(
            name="write_file",
            description="Write content to a file in the sandbox",
            inputSchema=WriteFileSchema.model_json_schema(),
        ),
        Tool(
            name="list_files",
            description="List files in a directory",
            inputSchema=ListFilesSchema.model_json_schema(),
        ),
        Tool(
            name="run_code",
            description="Run python code in a secure sandbox by E2B. Using the Jupyter Notebook syntax. Optionally specify sandboxId to use an existing sandbox.",
            inputSchema=RunCodeSchema.model_json_schema(),
        ),
        Tool(
            name="get_sandbox_url",
            description="Get the URL for a sandbox on a specific port",
            inputSchema=GetSandboxUrlSchema.model_json_schema(),
        ),
        Tool(
            name="get_file_download_url",
            description="Get a download URL for a file in the sandbox",
            inputSchema=GetFileDownloadUrlSchema.model_json_schema(),
        ),
        Tool(
            name="kill_sandbox",
            description="Kill a sandbox",
            inputSchema=KillSandboxSchema.model_json_schema(),
        ),
        Tool(
            name="list_sandbox_ids",
            description="List all active sandbox IDs and statistics",
            inputSchema=ListSandboxIdsSchema.model_json_schema(),
        ),
    ]


@app.call_tool()
async def call_tool(
    name: str, arguments: Any
) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """
    Handle tool calls with comprehensive error handling and logging.

    Args:
        name: The name of the tool to execute
        arguments: The arguments for the tool

    Returns:
        Sequence of response content

    Raises:
        ValueError: If tool name is unknown or arguments are invalid
        SandboxError: If sandbox operation fails
    """
    logger.debug(f"Tool called: {name} with arguments: {arguments}")

    try:
        # Route to appropriate handler
        if name == "create_sandbox":
            return await handle_create_sandbox(arguments, sandbox_manager)
        elif name == "run_command":
            return await handle_run_command(arguments, sandbox_manager)
        elif name == "read_file":
            return await handle_read_file(arguments, sandbox_manager)
        elif name == "write_file":
            return await handle_write_file(arguments, sandbox_manager)
        elif name == "list_files":
            return await handle_list_files(arguments, sandbox_manager)
        elif name == "run_code":
            return await handle_run_code(arguments, sandbox_manager)
        elif name == "get_sandbox_url":
            return await handle_get_sandbox_url(arguments, sandbox_manager)
        elif name == "get_file_download_url":
            return await handle_get_file_download_url(arguments, sandbox_manager)
        elif name == "kill_sandbox":
            return await handle_kill_sandbox(arguments, sandbox_manager)
        elif name == "list_sandbox_ids":
            return await handle_list_sandbox_ids(arguments, sandbox_manager)
        else:
            raise ValueError(f"Unknown tool: {name}")

    except ValidationError as e:
        logger.warning(f"Validation error for tool {name}: {e}")
        raise ValueError(f"Invalid arguments: {e}") from e
    except SandboxError as e:
        logger.error(f"Sandbox error in tool {name}: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error executing tool {name}: {e}", exc_info=True)
        raise


async def main():
    """
    Main entry point for the E2B MCP server.

    Sets up the server with proper lifecycle management and graceful shutdown.
    """
    from mcp.server.stdio import stdio_server

    logger.info("=" * 60)
    logger.info("E2B MCP Server - Production Grade")
    logger.info("=" * 60)
    logger.info(f"Max active sandboxes: {MAX_ACTIVE_SANDBOXES}")
    logger.info(f"Default sandbox timeout: {DEFAULT_SANDBOX_TIMEOUT_MS}ms")
    logger.info(f"Max sandbox timeout: {MAX_SANDBOX_TIMEOUT_MS}ms")
    logger.info("=" * 60)

    try:
        async with stdio_server() as (read_stream, write_stream):
            logger.info("Server ready to accept connections")
            await app.run(
                read_stream, write_stream, app.create_initialization_options()
            )
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise
    finally:
        logger.info("Shutting down server...")
        sandbox_manager.cleanup_all()
        logger.info("Server shutdown complete")


if __name__ == "__main__":
    asyncio.run(main())
