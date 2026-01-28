"""
Tool handler functions for E2B MCP Server.
"""

import logging
from typing import Any

from e2b import CommandHandle, CommandResult
from e2b_code_interpreter import Sandbox
from mcp.types import TextContent

from .constants import DEFAULT_SANDBOX_TIMEOUT_MS
from .exceptions import SandboxError
from .manager import SandboxManager
from .schemas import (
    CreateSandboxSchema,
    GetFileDownloadUrlSchema,
    GetSandboxUrlSchema,
    KillSandboxSchema,
    ListFilesSchema,
    ListSandboxIdsSchema,
    ReadFileSchema,
    RunCodeSchema,
    RunCommandSchema,
    WriteFileSchema,
)
from .utils import create_success_response

logger = logging.getLogger("e2b-mcp-server")


async def handle_create_sandbox(
    arguments: Any, sandbox_manager: SandboxManager
) -> list[TextContent]:
    """Handle create_sandbox tool call."""
    args = CreateSandboxSchema.model_validate(arguments)

    sandbox_id, _ = sandbox_manager.create_sandbox(args.secure, args.timeoutMs)
    timeout = args.timeoutMs if args.timeoutMs else DEFAULT_SANDBOX_TIMEOUT_MS

    result = {
        "sandboxId": sandbox_id,
        "message": f"Sandbox created successfully with timeout {timeout}ms",
    }
    return create_success_response(result)


async def handle_run_command(
    arguments: Any, sandbox_manager: SandboxManager
) -> list[TextContent]:
    """Handle run_command tool call."""
    args = RunCommandSchema.model_validate(arguments)

    sbx = sandbox_manager.get_sandbox(args.sandboxId)

    try:
        result = sbx.commands.run(cmd=args.command, background=args.background)

        if args.background and isinstance(result, CommandHandle):
            response = {
                "message": "Command started in background",
                "pid": result.pid,
                "sandboxId": args.sandboxId,
            }
        elif not args.background and isinstance(result, CommandResult):
            response = {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.exit_code,
                "sandboxId": args.sandboxId,
            }
        else:
            raise ValueError(f"Unexpected result type: {type(result)}")

        logger.info(
            f"Command executed in sandbox {args.sandboxId}: "
            f"background={args.background}"
        )
        return create_success_response(response)
    except Exception as e:
        logger.error(f"Error running command in sandbox {args.sandboxId}: {e}")
        raise SandboxError(f"Failed to run command: {e}") from e


async def handle_read_file(
    arguments: Any, sandbox_manager: SandboxManager
) -> list[TextContent]:
    """Handle read_file tool call."""
    args = ReadFileSchema.model_validate(arguments)

    sbx = sandbox_manager.get_sandbox(args.sandboxId)

    try:
        content = sbx.files.read(args.filePath)
        result = {
            "filePath": args.filePath,
            "content": content,
            "sandboxId": args.sandboxId,
        }
        logger.info(f"Read file {args.filePath} from sandbox {args.sandboxId}")
        return create_success_response(result)
    except Exception as e:
        logger.error(f"Error reading file {args.filePath}: {e}")
        raise SandboxError(f"Failed to read file: {e}") from e


async def handle_write_file(
    arguments: Any, sandbox_manager: SandboxManager
) -> list[TextContent]:
    """Handle write_file tool call."""
    args = WriteFileSchema.model_validate(arguments)

    sbx = sandbox_manager.get_sandbox(args.sandboxId)

    try:
        sbx.files.write(args.filePath, args.fileContents)
        result = {
            "filePath": args.filePath,
            "message": "File written successfully",
            "sandboxId": args.sandboxId,
            "size": len(args.fileContents),
        }
        logger.info(
            f"Wrote file {args.filePath} to sandbox {args.sandboxId} "
            f"({len(args.fileContents)} bytes)"
        )
        return create_success_response(result)
    except Exception as e:
        logger.error(f"Error writing file {args.filePath}: {e}")
        raise SandboxError(f"Failed to write file: {e}") from e


async def handle_list_files(
    arguments: Any, sandbox_manager: SandboxManager
) -> list[TextContent]:
    """Handle list_files tool call."""
    args = ListFilesSchema.model_validate(arguments)

    sbx = sandbox_manager.get_sandbox(args.sandboxId)

    try:
        files = sbx.files.list(args.folderPath)
        result = {
            "folderPath": args.folderPath,
            "files": [{"name": f.name, "type": f.type} for f in files],
            "sandboxId": args.sandboxId,
            "count": len(files),
        }
        logger.info(
            f"Listed {len(files)} files in {args.folderPath} "
            f"from sandbox {args.sandboxId}"
        )
        return create_success_response(result)
    except Exception as e:
        logger.error(f"Error listing files in {args.folderPath}: {e}")
        raise SandboxError(f"Failed to list files: {e}") from e


async def handle_run_code(
    arguments: Any, sandbox_manager: SandboxManager
) -> list[TextContent]:
    """Handle run_code tool call."""
    args = RunCodeSchema.model_validate(arguments)

    # Determine if we should use an existing sandbox or create a temporary one
    should_cleanup = False
    sbx = None

    try:
        if args.sandboxId:
            sbx = sandbox_manager.get_sandbox(args.sandboxId)
            logger.info(f"Running code in existing sandbox {args.sandboxId}")
        else:
            sbx = Sandbox()
            should_cleanup = True
            logger.info("Running code in temporary sandbox")

        execution = sbx.run_code(args.code)

        result: dict[str, Any] = {
            "stdout": execution.logs.stdout,
            "stderr": execution.logs.stderr,
        }

        if args.sandboxId:
            result["sandboxId"] = args.sandboxId
        else:
            result["message"] = "Executed in temporary sandbox"

        logger.info(
            f"Code execution completed: "
            f"stdout={len(execution.logs.stdout)} chars, "
            f"stderr={len(execution.logs.stderr)} chars"
        )
        return create_success_response(result)

    except Exception as e:
        logger.error(f"Error running code: {e}")
        raise SandboxError(f"Failed to run code: {e}") from e
    finally:
        if should_cleanup and sbx:
            try:
                sbx.kill()
                logger.info("Temporary sandbox cleaned up")
            except Exception as e:
                logger.warning(f"Error cleaning up temporary sandbox: {e}")


async def handle_get_sandbox_url(
    arguments: Any, sandbox_manager: SandboxManager
) -> list[TextContent]:
    """Handle get_sandbox_url tool call."""
    args = GetSandboxUrlSchema.model_validate(arguments)

    sbx = sandbox_manager.get_sandbox(args.sandboxId)

    try:
        url = sbx.get_host(args.port)
        result = {
            "sandboxId": args.sandboxId,
            "port": args.port,
            "url": url,
        }
        logger.info(f"Got URL for sandbox {args.sandboxId} on port {args.port}: {url}")
        return create_success_response(result)
    except Exception as e:
        logger.error(f"Error getting sandbox URL: {e}")
        raise SandboxError(f"Failed to get sandbox URL: {e}") from e


async def handle_get_file_download_url(
    arguments: Any, sandbox_manager: SandboxManager
) -> list[TextContent]:
    """Handle get_file_download_url tool call."""
    args = GetFileDownloadUrlSchema.model_validate(arguments)

    sbx = sandbox_manager.get_sandbox(args.sandboxId)

    try:
        url = sbx.download_url(
            args.filePath, use_signature_expiration=args.useSignatureExpiration
        )
        result = {
            "sandboxId": args.sandboxId,
            "filePath": args.filePath,
            "url": url,
        }
        logger.info(
            f"Got download URL for file {args.filePath} in sandbox {args.sandboxId}"
        )
        return create_success_response(result)
    except Exception as e:
        logger.error(f"Error getting file download URL: {e}")
        raise SandboxError(f"Failed to get file download URL: {e}") from e


async def handle_kill_sandbox(
    arguments: Any, sandbox_manager: SandboxManager
) -> list[TextContent]:
    """Handle kill_sandbox tool call."""
    args = KillSandboxSchema.model_validate(arguments)

    sandbox_manager.kill_sandbox(args.sandboxId)

    result = {
        "sandboxId": args.sandboxId,
        "message": "Sandbox killed successfully",
        "stats": sandbox_manager.get_stats(),
    }
    return create_success_response(result)


async def handle_list_sandbox_ids(
    arguments: Any, sandbox_manager: SandboxManager
) -> list[TextContent]:
    """Handle list_sandbox_ids tool call."""
    ListSandboxIdsSchema.model_validate(arguments)

    stats = sandbox_manager.get_stats()
    result = {
        "sandbox_ids": stats["sandbox_ids"],
        "active_sandboxes": stats["active_sandboxes"],
        "max_sandboxes": stats["max_sandboxes"],
    }
    logger.info(f"Listed {stats['active_sandboxes']} active sandboxes")
    return create_success_response(result)
