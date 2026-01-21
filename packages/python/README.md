# E2B MCP Server (Python)

A production-grade Model Context Protocol server for executing code in secure, isolated [E2B](https://e2b.dev) sandboxes.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![E2B](https://img.shields.io/badge/powered%20by-E2B-orange.svg)](https://e2b.dev)

## ✨ Features

- 🚀 **Production-Ready**: Comprehensive error handling, logging, and resource management
- 🔒 **Secure Isolation**: Each sandbox runs in a separate, secure E2B environment
- 🎯 **Type-Safe**: Full type annotations and Pydantic validation
- 📊 **Observable**: Detailed logging and sandbox statistics
- 🧹 **Auto Cleanup**: Automatic resource cleanup and graceful shutdown
- 📦 **Modular Design**: Clean, maintainable code structure
- ⚡ **Easy to Use**: Simple API with comprehensive documentation

## 🛠️ Available Tools

The server provides 10 powerful tools for sandbox interaction:

| Tool | Description |
|------|-------------|
| `create_sandbox` | Create a new E2B sandbox with configurable timeout |
| `run_code` | Execute Python code using Jupyter notebook syntax |
| `run_command` | Run shell commands in the sandbox |
| `read_file` | Read file contents from the sandbox |
| `write_file` | Write content to files in the sandbox |
| `list_files` | List files in a sandbox directory |
| `get_sandbox_url` | Get URL for accessing sandbox on specific port |
| `get_file_download_url` | Get download URL for a file in the sandbox |
| `list_sandbox_ids` | List all active sandbox IDs and statistics |
| `kill_sandbox` | Terminate and cleanup a sandbox |

## 📋 Requirements

- Python 3.10 or higher
- E2B API key ([Get one here](https://e2b.dev))

## 🚀 Quick Start

### Installation

```bash
# Install with uv (recommended)
uv install

# Or with pip
pip install -e .
```

### Configuration

1. Get your E2B API key from [e2b.dev](https://e2b.dev)
2. Set up environment variables:

```bash
# Copy example config
cp .env.example .env

# Edit .env and add your API key
E2B_API_KEY=your_api_key_here
```

### Running the Server

#### Standalone

```bash
# Run directly
python -m e2b_mcp_server

# Or programmatically
python -c "from e2b_mcp_server import main; import asyncio; asyncio.run(main())"
```

#### With Claude Desktop

Add to your Claude Desktop config:

**MacOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "e2b-mcp-server": {
      "command": "uvx",
      "args": ["e2b-mcp-server"],
      "env": {
        "E2B_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

## ⚙️ Configuration

Environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `E2B_API_KEY` | (required) | Your E2B API key |
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `MAX_ACTIVE_SANDBOXES` | `10` | Maximum concurrent sandboxes |

### Advanced Configuration

The server uses these constants (can be modified in `constants.py`):

- `DEFAULT_SANDBOX_TIMEOUT_MS`: 300000 (5 minutes)
- `MAX_SANDBOX_TIMEOUT_MS`: 3600000 (1 hour)

## 🏗️ Architecture

### Module Structure

```
e2b_mcp_server/
├── constants.py      # Configuration constants
├── exceptions.py     # Custom exception classes
├── schemas.py        # Pydantic validation schemas
├── utils.py          # Utility functions
├── manager.py        # Sandbox lifecycle management
├── handlers.py       # Tool handler implementations
├── server.py         # MCP server setup and routing
└── __init__.py       # Package exports
```

### Design Principles

- **Separation of Concerns**: Each module has a single, clear responsibility
- **Type Safety**: Full type hints and Pydantic validation
- **Error Handling**: Comprehensive exception hierarchy
- **Resource Management**: Automatic cleanup and lifecycle tracking
- **Testability**: Modular design enables easy unit testing

### Key Components

#### SandboxManager (`manager.py`)

Manages E2B sandbox lifecycle:

- Creates and tracks sandboxes
- Enforces resource limits
- Handles cleanup on shutdown

#### Tool Handlers (`handlers.py`)

Implements business logic for each tool:

- Validates inputs using schemas
- Interacts with sandboxes
- Returns standardized responses

#### Schemas (`schemas.py`)

Pydantic models for validation:

- Type checking
- Field validation
- Auto-generated JSON schemas

## 🐛 Debugging

Use the [MCP Inspector](https://github.com/modelcontextprotocol/inspector) for debugging:

```bash
npx @modelcontextprotocol/inspector \
  uv \
  --directory . \
  run \
  e2b-mcp-server
```

The Inspector provides a web interface for:

- Testing tool calls
- Viewing request/response logs
- Debugging connection issues

### Enable Debug Logging

```bash
export LOG_LEVEL=DEBUG
python -m e2b_mcp_server
```

## 🧪 Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/yukkit/e2b-mcp-server
cd mcp-server/packages/python

# Install dependencies
uv install

# Copy environment config
cp .env.example .env
# Edit .env with your E2B_API_KEY
```

### Project Structure

```
packages/python/
├── e2b_mcp_server/       # Main package
│   ├── __init__.py
│   ├── server.py         # MCP server
│   ├── manager.py        # Sandbox management
│   ├── handlers.py       # Tool handlers
│   ├── schemas.py        # Validation schemas
│   ├── constants.py      # Configuration
│   ├── exceptions.py     # Custom exceptions
│   └── utils.py          # Utilities
├── tests/                # Test suite (coming soon)
├── examples/             # Usage examples
├── .env.example          # Environment template
├── pyproject.toml        # Package configuration
└── README.md             # This file
```

### Code Style

The codebase follows:

- PEP 8 style guidelines
- Type hints for all functions
- Comprehensive docstrings
- Modular, testable design

### Running Tests

```bash
# Coming soon
pytest tests/
```

## � Building and Packaging

### Quick Build

```bash
# Method 1: Using Poetry (recommended)
poetry install
poetry build

# Method 2: Using build.sh script
./build.sh

# Generated files in dist/:
# - e2b_mcp_server-0.1.1-py3-none-any.whl
# - e2b_mcp_server-0.1.1.tar.gz
```

### Local Installation Testing

```bash
# Install from built wheel
pip install dist/*.whl

# Test the installation
python -m e2b_mcp_server --help
```

### Publishing to PyPI

```bash
# Configure PyPI token
poetry config pypi-token.pypi YOUR_TOKEN

# Publish
poetry publish

# Or build and publish together
poetry publish --build
```

For detailed packaging instructions, see [PACKAGING.md](PACKAGING.md).

## �📊 Resource Management

The server includes production-grade resource management:

### Sandbox Limits

- Maximum concurrent sandboxes: Configurable (default: 10)
- Automatic limit enforcement
- Clear error messages when limits reached

### Automatic Cleanup

- Graceful shutdown handling
- All sandboxes cleaned up on exit
- Temporary sandboxes auto-cleaned after use

### Monitoring

```python
# Get current statistics
from e2b_mcp_server.manager import sandbox_manager

stats = sandbox_manager.get_stats()
# Returns: {
#   "active_sandboxes": 3,
#   "max_sandboxes": 10,
#   "sandbox_ids": ["sbx_123", "sbx_456", "sbx_789"]
# }
```

## 🔒 Security

- **Isolated Execution**: Each sandbox runs in isolated E2B environment
- **Resource Limits**: Configurable timeout and sandbox limits
- **API Key Protection**: Credentials loaded from environment
- **Input Validation**: All inputs validated with Pydantic

## 📄 API Reference

### Tool Schemas

All tools use Pydantic schemas for validation. See `schemas.py` for details.

#### create_sandbox

```python
{
  "timeoutMs": 300000  # Optional, milliseconds
}
```

#### run_code

```python
{
  "code": "print('hello')",      # Required
  "sandboxId": "sbx_..."          # Optional
}
```

#### run_command

```python
{
  "command": "ls -la",            # Required
  "sandboxId": "sbx_...",         # Required
  "background": false             # Optional
}
```

See inline documentation in `schemas.py` for complete API details.

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests (when available)
5. Submit a pull request

## 📝 License

Apache 2.0 - See LICENSE file for details.

## 🔗 Links

- [E2B Documentation](https://e2b.dev/docs)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [GitHub Repository](https://github.com/yukkit/e2b-mcp-server)
- [Issue Tracker](https://github.com/yukkit/e2b-mcp-server/issues)

## 💬 Support

- 📧 Email: <hello@e2b.dev>
- 💬 Discord: [Join our community](https://discord.gg/U7KEcGErtQ)
- 🐛 Issues: [GitHub Issues](https://github.com/yukkit/e2b-mcp-server/issues)

## 🙏 Acknowledgments

Built with:

- [E2B](https://e2b.dev) - Secure code execution sandboxes
- [MCP](https://modelcontextprotocol.io) - Model Context Protocol
- [Pydantic](https://docs.pydantic.dev) - Data validation
- [Python](https://www.python.org) - Programming language

---

Made with ❤️ by the [E2B team](https://e2b.dev)
