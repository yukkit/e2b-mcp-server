# E2B MCP Server

[![npm version](https://img.shields.io/npm/v/@yukkit/e2b-mcp-server.svg)](https://www.npmjs.com/package/@yukkit/e2b-mcp-server)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
![Node version](https://img.shields.io/node/v/@yukkit/e2b-mcp-server.svg)
[![TypeScript](https://img.shields.io/badge/TypeScript-blue?logo=typescript&logoColor=white)](https://www.typescriptlang.org)

A production-grade Model Context Protocol server that provides secure code execution capabilities through [E2B](https://e2b.dev) sandboxes. This implementation enables AI models and assistants to execute code, manage files, and interact with isolated development environments safely.

## Overview

This server implements the [Model Context Protocol (MCP)](https://modelcontextprotocol.io) to expose E2B's secure sandbox infrastructure as a set of tools that can be used by AI models like Claude. It features a robust architecture with resource management, comprehensive error handling, and production-ready logging.

**Key capabilities:**

- Execute Python code in isolated sandboxes with configurable timeouts
- Run shell commands (foreground and background modes)
- Manage files (read, write, list) within sandbox environments
- Expose sandbox services via public URLs
- Automatic resource cleanup and lifecycle management
- Support for multiple concurrent sandboxes with configurable limits

## Features

- **10 Production-Ready Tools**: Complete toolkit for sandbox interaction
- **Resource Management**: Automatic sandbox lifecycle management with configurable limits (default: 10 concurrent sandboxes)
- **Robust Error Handling**: Custom error classes for clear diagnostics (SandboxError, SandboxNotFoundError, SandboxLimitExceededError)
- **Production Logging**: Multi-level logging system (DEBUG, INFO, WARNING, ERROR) with timestamps
- **Input Validation**: Comprehensive Zod schemas for all tool inputs
- **Graceful Shutdown**: Proper cleanup on SIGINT/SIGTERM signals
- **Zero Configuration**: Works out of the box with sensible defaults

## Installation

### Quick Start with npx

The fastest way to use the server is with npx:

```bash
npx @yukkit/e2b-mcp-server
```

### Global Installation

```bash
npm install -g @yukkit/e2b-mcp-server
```

### Project Installation

```bash
npm install @yukkit/e2b-mcp-server
```

## Usage

### With Claude Desktop

Add the server configuration to your Claude Desktop config file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "e2b": {
      "command": "npx",
      "args": ["-y", "@yukkit/e2b-mcp-server"],
      "env": {
        "E2B_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

> [!IMPORTANT]
> You need an E2B API key to use this server. Get one for free at [e2b.dev](https://e2b.dev).

### With Other MCP Clients

Any MCP-compatible client can use this server by running:

```bash
E2B_API_KEY=your-api-key-here e2b-mcp-server
```

### Configuration

Configure the server using environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `E2B_API_KEY` | Your E2B API key (required) | - |
| `MAX_ACTIVE_SANDBOXES` | Maximum concurrent sandboxes | `10` |
| `LOG_LEVEL` | Logging verbosity (DEBUG, INFO, WARNING, ERROR) | `INFO` |

Example with custom configuration:

```bash
E2B_API_KEY=your-key MAX_ACTIVE_SANDBOXES=5 LOG_LEVEL=DEBUG e2b-mcp-server
```

## Available Tools

### 1. create_sandbox

Create a new isolated code execution sandbox.

**Parameters:**

- `secure` (optional): Whether to create a secure sandbox (default: true)
- `timeoutMs` (optional): Sandbox timeout in milliseconds (default: 300000, max: 3600000)

### 2. run_code

Execute Python code in a sandbox.

**Parameters:**

- `code`: Python code to execute
- `sandboxId` (optional): Target sandbox ID. If not provided, creates a temporary sandbox.

### 3. run_command

Execute a shell command in a sandbox.

**Parameters:**

- `command`: Shell command to run
- `sandboxId`: Target sandbox ID
- `background`: Run in background (default: false)

### 4. read_file

Read file contents from a sandbox.

**Parameters:**

- `filePath`: Path to the file
- `sandboxId`: Target sandbox ID

### 5. write_file

Write content to a file in a sandbox.

**Parameters:**

- `filePath`: Path to the file
- `fileContents`: Content to write
- `sandboxId`: Target sandbox ID

### 6. list_files

List files in a directory within a sandbox.

**Parameters:**

- `folderPath`: Directory path to list
- `sandboxId`: Target sandbox ID

### 7. get_sandbox_url

Get a public URL for accessing a service running in a sandbox.

**Parameters:**

- `port`: Port number (1-65535)
- `sandboxId`: Target sandbox ID

### 8. get_file_download_url

Get a download URL for a file in the sandbox.

**Parameters:**

- `filePath`: Path to the file
- `sandboxId`: Target sandbox ID
- `useSignatureExpiration` (optional): Signature expiration in milliseconds (default: 300000 / 5 minutes)

### 9. list_sandbox_ids

List all active sandbox IDs and get sandbox statistics.

**Parameters:**

None

**Returns:**

- `sandbox_ids`: Array of active sandbox IDs
- `active_sandboxes`: Current number of active sandboxes
- `max_sandboxes`: Maximum allowed sandboxes

### 10. kill_sandbox

Terminate a sandbox and clean up resources.

**Parameters:**

- `sandboxId`: Target sandbox ID

## Development

### Prerequisites

- Node.js >= 20
- pnpm (recommended) or npm

### Setup

Clone the repository and install dependencies:

```bash
git clone https://github.com/yukkit/e2b-mcp-server.git
cd e2b-mcp-server/packages/js
pnpm install
```

### Building

Build the TypeScript source:

```bash
pnpm build
```

For development with automatic rebuilding:

```bash
pnpm watch
```

### Debugging

Since MCP servers communicate over stdio, debugging can be challenging. Use the [MCP Inspector](https://github.com/modelcontextprotocol/inspector) for interactive debugging:

```bash
pnpm inspector
```

This will start the inspector and provide a URL to access debugging tools in your browser.

## Architecture

The server is built with a modular architecture:

- **SandboxManager**: Handles sandbox lifecycle and resource limits
- **Logger**: Provides structured logging with multiple levels
- **Error Classes**: Custom exceptions for clear error handling
- **Zod Schemas**: Input validation for all tools
- **MCP Server**: Standard MCP protocol implementation

## Troubleshooting

### "Need to provide E2B_API_KEY"

Set your E2B API key as an environment variable. Get one at [e2b.dev](https://e2b.dev).

### "Maximum number of active sandboxes reached"

The default limit is 10 concurrent sandboxes. Increase it with `MAX_ACTIVE_SANDBOXES` or terminate unused sandboxes with the `kill_sandbox` tool.

### Connection Issues

Ensure your firewall allows outbound connections to E2B's API endpoints.

## Resources

- [E2B Documentation](https://e2b.dev/docs)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)
- [Claude Desktop](https://claude.ai/download)
