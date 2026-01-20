"""
Utility functions for E2B MCP Server.
"""

import json
from typing import Any, Optional

from mcp.types import TextContent


def create_success_response(data: dict[str, Any]) -> list[TextContent]:
    """
    Create a standardized success response.

    Args:
        data: Response data dictionary

    Returns:
        List containing a TextContent response
    """
    return [TextContent(type="text", text=json.dumps(data, indent=2))]


def create_error_response(
    error: str, details: Optional[str] = None
) -> list[TextContent]:
    """
    Create a standardized error response.

    Args:
        error: Error message
        details: Optional detailed error information

    Returns:
        List containing a TextContent error response
    """
    response = {"error": error}
    if details:
        response["details"] = details
    return [TextContent(type="text", text=json.dumps(response, indent=2))]
