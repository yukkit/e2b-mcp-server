![E2B MCP Server Preview Light](/readme-assets/mcp-server-light.png#gh-light-mode-only)
![E2B MCP Server Preview Dark](/readme-assets/mcp-server-dark.png#gh-dark-mode-only)

# E2B MCP Server

[![smithery badge](https://smithery.ai/badge/e2b)](https://smithery.ai/server/e2b)
[![npm version](https://img.shields.io/npm/v/@yukkit/e2b-mcp-server.svg)](https://www.npmjs.com/package/@yukkit/e2b-mcp-server)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Build Status](https://img.shields.io/github/actions/workflow/status/yukkit/e2b-mcp-server/publish_packages.yml?branch=main)](https://github.com/yukkit/e2b-mcp-server/actions)

Production-grade [Model Context Protocol](https://modelcontextprotocol.io) servers that enable AI assistants to execute code securely in isolated [E2B](https://e2b.dev) sandboxes. Bring powerful code interpretation capabilities to Claude Desktop, Cline, and other MCP-compatible clients.

[Demo](https://x.com/mishushakov/status/1863286108433317958) • [JavaScript Docs](packages/js/README.md) • [Python Docs](packages/python/README.md) • [E2B Platform](https://e2b.dev)

## Overview

This repository contains production-ready MCP server implementations in both JavaScript/TypeScript and Python. Each server provides a complete toolkit for AI models to interact with secure, isolated code execution environments.

**What you can do:**

- Execute Python code in Jupyter-style notebooks
- Run shell commands in isolated environments  
- Manage files (read, write, list) within sandboxes
- Expose services running in sandboxes via public URLs
- Manage multiple concurrent sandboxes with automatic cleanup
- Monitor sandbox usage with comprehensive logging

**Key features:**

- **10 Production Tools**: Complete sandbox interaction toolkit
- **Resource Management**: Automatic lifecycle management with configurable limits
- **Type Safety**: Full validation with Zod (JS) and Pydantic (Python)
- **Robust Error Handling**: Clear diagnostics and graceful degradation
- **Production Logging**: Multi-level logging with timestamps
- **Graceful Shutdown**: Proper cleanup on termination signals

## Quick Start

### Manual Installation

#### JavaScript/TypeScript

```bash
# With npx (no installation required)
npx @yukkit/e2b-mcp-server

# Or install globally
npm install -g @yukkit/e2b-mcp-server
```

#### Python

```bash
# With uv (recommended)
uv pip install e2b-mcp-server

# With pip
pip install e2b-mcp-server
```

## Configuration

### Claude Desktop

Add to your Claude Desktop config:

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

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `E2B_API_KEY` | Your E2B API key ([get one here](https://e2b.dev)) | Required |
| `MAX_ACTIVE_SANDBOXES` | Maximum concurrent sandboxes | `10` |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` |

> [!IMPORTANT]
> Get your free E2B API key at [e2b.dev](https://e2b.dev)

## Available Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| **create_sandbox** | Create a new isolated sandbox | `timeoutMs` (optional) |
| **run_code** | Execute Python code in a sandbox | `code`, `sandboxId` (optional) |
| **run_command** | Run shell commands | `command`, `sandboxId`, `background` |
| **read_file** | Read file contents | `filePath`, `sandboxId` |
| **write_file** | Write to a file | `filePath`, `fileContents`, `sandboxId` |
| **list_files** | List directory contents | `folderPath`, `sandboxId` |
| **get_sandbox_url** | Get public URL for a port | `port`, `sandboxId` |
| **get_file_download_url** | Get download URL for a file | `filePath`, `sandboxId` |
| **list_sandbox_ids** | List all active sandboxes | None |
| **kill_sandbox** | Terminate a sandbox | `sandboxId` |

## Language Support

Choose the implementation that fits your stack:

### JavaScript/TypeScript

- Built with TypeScript for type safety
- Uses Zod for input validation
- Compatible with Node.js 20+
- Full documentation: [packages/js/README.md](packages/js/README.md)

**Install:**

```bash
npm install @yukkit/e2b-mcp-server
```

### Python

- Type-safe with full type annotations
- Pydantic models for validation
- Python 3.10+ required
- Full documentation: [packages/python/README.md](packages/python/README.md)

**Install:**

```bash
pip install e2b-mcp-server
```

## Development

This is a monorepo managed with pnpm workspaces.

### Prerequisites

- Node.js 20+
- pnpm 9+
- Python 3.10+ (for Python package)
- Poetry (for Python package)

### Setup

```bash
# Clone the repository
git clone https://github.com/e2b-dev/mcp-server.git
cd mcp-server

# Install dependencies
pnpm install

# Build all packages
pnpm build
```

### Project Structure

```
.
├── packages/
│   ├── js/          # TypeScript/JavaScript implementation
│   │   ├── src/     # Source code
│   │   └── build/   # Compiled output
│   └── python/      # Python implementation
│       └── e2b_mcp_server/  # Package source
├── .changeset/      # Changesets for version management
└── .github/         # CI/CD workflows
```

### Publishing

This project uses [Changesets](https://github.com/changesets/changesets) for version management:

```bash
# Create a changeset
pnpm changeset

# Version packages
pnpm run version

# Publish to npm/PyPI
pnpm run publish
```

## Use Cases

**AI-Powered Code Assistants**: Let AI models write and execute code with immediate feedback

**Data Analysis**: Enable AI to analyze datasets, create visualizations, and generate reports

**DevOps Automation**: Allow AI to interact with systems and run diagnostic commands

**Educational Tools**: Create interactive coding tutorials with safe execution environments

**API Testing**: Let AI test and validate APIs by running actual requests

**Code Generation & Testing**: Generate code and verify it works through execution

## Resources

- [E2B Documentation](https://e2b.dev/docs)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [E2B Code Interpreter](https://github.com/e2b-dev/code-interpreter)
- [MCP TypeScript SDK](https://github.com/modelcontextprotocol/typescript-sdk)
- [Claude Desktop](https://claude.ai/download)
- [Smithery MCP Registry](https://smithery.ai)

## Support

- **Documentation**: Check the [JavaScript](packages/js/README.md) or [Python](packages/python/README.md) READMEs
- **Issues**: [Open an issue](https://github.com/yukkit/e2b-mcp-server/issues)
- **E2B Platform**: [support@e2b.dev](mailto:support@e2b.dev)
- **Discord**: Join the [E2B Community](https://discord.gg/U7KEcGErtQ)

## Security

E2B sandboxes provide secure, isolated execution environments. However, always:

- Keep your E2B API key secure and never commit it to version control
- Use environment variables for sensitive configuration
- Monitor sandbox usage and set appropriate limits
- Review code before execution in production environments

For security concerns, please email [security@e2b.dev](mailto:security@e2b.dev).

## Contributing

Contributions are welcome! Please read our contributing guidelines before submitting PRs.

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Create a changeset: `pnpm changeset`
5. Submit a pull request

## License

Apache 2.0 - See [LICENSE](LICENSE) for details.
