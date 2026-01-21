"""
Pydantic schemas for E2B MCP Server tool validation.
"""

from typing import Optional
from pydantic import BaseModel, Field

from .constants import MAX_SANDBOX_TIMEOUT_MS


class RunCodeSchema(BaseModel):
    """Schema for running Python code in a sandbox."""

    code: str = Field(..., description="Python code to execute", min_length=1)
    sandboxId: Optional[str] = Field(
        None,
        description="Optional sandbox ID. If not provided, a temporary sandbox will be created.",
    )


class CreateSandboxSchema(BaseModel):
    """Schema for creating a new sandbox."""

    timeoutMs: Optional[int] = Field(
        None, description="Timeout in milliseconds", ge=1000, le=MAX_SANDBOX_TIMEOUT_MS
    )


class RunCommandSchema(BaseModel):
    """Schema for running a shell command in a sandbox."""

    command: str = Field(..., description="Shell command to execute", min_length=1)
    sandboxId: str = Field(..., description="Sandbox ID")
    background: bool = Field(False, description="Run command in background")


class ReadFileSchema(BaseModel):
    """Schema for reading a file from a sandbox."""

    filePath: str = Field(..., description="Path to the file", min_length=1)
    sandboxId: str = Field(..., description="Sandbox ID")


class WriteFileSchema(BaseModel):
    """Schema for writing content to a file in a sandbox."""

    filePath: str = Field(..., description="Path to the file", min_length=1)
    sandboxId: str = Field(..., description="Sandbox ID")
    fileContents: str = Field(..., description="Content to write to the file")


class ListFilesSchema(BaseModel):
    """Schema for listing files in a directory."""

    sandboxId: str = Field(..., description="Sandbox ID")
    folderPath: str = Field(..., description="Path to the folder", min_length=1)


class GetSandboxUrlSchema(BaseModel):
    """Schema for getting a sandbox URL."""

    port: int = Field(..., description="Port number", ge=1, le=65535)
    sandboxId: str = Field(..., description="Sandbox ID")


class GetFileDownloadUrlSchema(BaseModel):
    """Schema for getting a file download URL."""

    filePath: str = Field(..., description="Path to the file", min_length=1)
    sandboxId: str = Field(..., description="Sandbox ID")


class KillSandboxSchema(BaseModel):
    """Schema for killing a sandbox."""

    sandboxId: str = Field(..., description="Sandbox ID")
