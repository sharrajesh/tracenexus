# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TraceNexus is a platform-agnostic MCP (Model Context Protocol) server for LLM observability that provides unified access to traces from multiple platforms (LangSmith, Langfuse). It uses FastMCP 2.0 and supports dual transport protocols for compatibility with different MCP clients.

## Essential Commands

### Development Setup
```bash
# Install development dependencies
make install-dev

# Run development server
make run
# Or directly: python -m tracenexus --host 127.0.0.1 --http-port 52734 --sse-port 52735
```

### Code Quality & Testing
```bash
# Run all formatting, linting, and type checking
make format

# Run tests with coverage
make test

# Run specific test file
pytest tests/test_providers.py -v

# Run async tests
pytest tests/test_mcp_server.py -v
```

### Build & Publish
```bash
# Build package
make build

# Publish to PyPI (requires PYPI_TOKEN)
make publish
```

## Architecture

### Core Components
- **CLI Layer** (`tracenexus/cli.py`): Entry point, handles argument parsing and dual-transport server spawning
- **MCP Server** (`tracenexus/server/mcp_server.py`): FastMCP-based server exposing trace retrieval tools
- **Provider System** (`tracenexus/providers/`): Extensible platform integrations
  - Each provider implements async trace retrieval methods
  - Providers handle authentication and API communication

### Dual Transport Architecture
The server spawns two parallel processes:
1. **Streamable-HTTP** (default port 52734): For Cursor IDE
2. **SSE** (default port 52735): For Windsurf IDE

Both processes share the same MCP server implementation but use different transport layers.

### Adding New Providers
1. Create new provider in `tracenexus/providers/`
2. Implement async `get_trace()` method returning structured data
3. Register tool in `tracenexus/server/mcp_server.py`
4. Add corresponding test in `tests/test_providers.py`

## Testing Approach

- Use `pytest` with `pytest-asyncio` for async tests
- Mock external API calls in provider tests
- Test tool registration and execution in `test_mcp_server.py`
- Ensure coverage with `pytest --cov=tracenexus`

## Environment Configuration

Required environment variables (create `.env` file):
```
LANGSMITH_API_KEY=your_key
LANGFUSE_PUBLIC_KEY=your_key
LANGFUSE_SECRET_KEY=your_key
LANGFUSE_HOST=your_host
```

## Version Management

Version is maintained in two locations (keep synchronized):
- `pyproject.toml`: `version` field
- `tracenexus/__init__.py`: `__version__` variable

## Key Dependencies

- **FastMCP** (^2.3.4): Core MCP framework with dual transport support
- **Pydantic**: Data validation and configuration
- **LangSmith/Langfuse clients**: Platform-specific SDKs
- **Poetry**: Dependency management (use `poetry add` for new deps)

## CI/CD

GitHub Actions workflow (`.github/workflows/ci.yml`) runs on pushes/PRs to main:
1. Runs isort, black, mypy checks
2. Executes full test suite with coverage
3. Tests on Python 3.11

## Development Tips

- Always run `make format` before committing
- Use type hints for all function signatures
- Follow existing provider patterns when adding new integrations
- Test async functions with `pytest-asyncio` fixtures
- Keep dual-transport compatibility in mind when modifying server code