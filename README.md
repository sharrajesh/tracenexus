# TraceNexus

> **⚠️ WORK IN PROGRESS ⚠️**
>
> This project is currently under active development and should be considered experimental. 
> Features may change, and stability is not guaranteed.
>
> Please DM the author if you have any comments, suggestions, or would like to contribute!

A platform-agnostic MCP (Model Context Protocol) server for LLM observability, supporting platforms like LangSmith and Langfuse. It runs **both** transport protocols simultaneously: `streamable-http` (for Cursor) and `SSE` (for Windsurf) using FastMCP 2.0.

## Features

- 🔄 Support for multiple tracing platforms through a unified interface
- 🛠️ MCP tools for retrieving and analyzing traces
- 📊 Trace comparison across different platforms
- 🚀 **Dual transport support**: Runs both `streamable-http` and `SSE` simultaneously
- 📡 **Cursor compatibility**: `streamable-http` transport on port 52734
- 🌊 **Windsurf compatibility**: `SSE` transport on port 52735
- 🤖 **Claude Code compatibility**: Full MCP integration support
- 🧩 Easy integration with LangSmith and LangFuse
- 🔧 Use multiple clients at the same time with one server

## Quick Start (for End Users)

This guide provides the quickest way to get the TraceNexus server up and running.

### 1. Prerequisites

- Python 3.9+ (developed with 3.11)

### 2. Installation

1.  **(Optional but Recommended)** Create a dedicated directory and set up a virtual environment:
    ```bash
    mkdir ~/my_tracenexus_server
    cd ~/my_tracenexus_server
    python -m venv .venv
    source .venv/bin/activate
    ```

2.  Install TraceNexus from PyPI:
    ```bash
    pip install --upgrade tracenexus
    ```

### 3. Configuration (API Keys & Settings)

TraceNexus requires API keys for the tracing platforms it supports (e.g., LangSmith, Langfuse).

- Create a `.env` file in your project directory (e.g., `~/my_tracenexus_server/.env` if you followed the optional step above, or in the directory where you run `tracenexus`).
- Add your API keys and desired default platform to this file. The server automatically loads these settings on startup.

**Example `.env` file:**

```env
# Platform API Keys
LANGSMITH_API_KEY="YOUR_LANGSMITH_API_KEY_HERE"
# LANGFUSE_PUBLIC_KEY="YOUR_LANGFUSE_PUBLIC_KEY_HERE"
# LANGFUSE_SECRET_KEY="YOUR_LANGFUSE_SECRET_KEY_HERE"
```

Refer to `tracenexus/cli.py` (if installed from source) or use `tracenexus --help` for details on how provider-specific API keys are checked at startup.

### 4. Running the Server

Once installed and configured, run the server using:
```bash
tracenexus
```

This will start **both transport protocols simultaneously**:
- **📡 Streamable-HTTP** (Cursor): `http://localhost:52734/mcp`
- **🌊 SSE** (Windsurf): `http://localhost:52735/sse`

To see all available command-line options, including changing ports:
```bash
tracenexus --help
```

**Custom ports example:**
```bash
tracenexus --http-port 8000 --sse-port 8001
```

### 5. Using with MCP Client Applications

TraceNexus runs both transport protocols simultaneously, so you can use **Claude Code, Cursor, and Windsurf at the same time**!

#### For Claude Code

1. **Follow steps 1-3 from the Quick Start section above** to install TraceNexus and set up your `.env` file with API keys.

2. **Start the TraceNexus server:**
   ```bash
   tracenexus
   ```

3. **Add TraceNexus to Claude Code using the CLI:**
   ```bash
   claude mcp add --transport sse tracenexus http://localhost:52735/sse
   ```

That's it! Claude Code can now use the `langsmith_get_trace` and `langfuse_get_trace` tools.

To verify it's working, you can ask Claude: "What MCP tools do you have available?"

#### For Cursor (Streamable-HTTP)

1.  Ensure the TraceNexus server is running (e.g., via `tracenexus`).
2.  In Cursor's MCP server settings, add:

```json
{
  "mcpServers": {
    "tracenexus": {
      "transport": "streamable-http",
      "url": "http://localhost:52734/mcp" 
    }
  }
}
```

#### For Windsurf (SSE)

1.  Ensure the TraceNexus server is running (e.g., via `tracenexus`).
2.  In Windsurf's MCP server settings, add:

```json
{
  "mcpServers": {
    "tracenexus": {
      "serverUrl": "http://localhost:52735/sse"
    }
  }
}
```

**Note**: Both configurations can be used simultaneously with the same server instance!

## Available Tools

Once running, the server exposes the following MCP tools:

-   **`langsmith_get_trace`**: Retrieve a single trace by ID from LangSmith.
-   **`langfuse_get_trace`**: Retrieve a single trace by ID from Langfuse.

An example Python client showing how to connect and use these tools can be found in `examples/client.py`.

## Development Setup

If you want to contribute to TraceNexus, modify the source code, or run it directly from a cloned repository, follow these steps.

### 1. Prerequisites

- Python 3.9+ (developed with 3.11)
- Poetry (for dependency management)

### 2. Installation & Setup (from Source)

```bash
# Clone the repository
git clone https://github.com/sharrajesh/tracenexus.git
cd tracenexus

# Install dependencies (including development dependencies)
make install-dev
# or poetry install --with dev
```

### 3. Configuration
Follow the same `.env` file configuration steps outlined in "Quick Start (for End Users) -> 3. Configuration". Place the `.env` file in the root of the cloned `tracenexus` directory.

### 4. Running the Server (from Source)

```bash
# Run the TraceNexus server (runs both transports: HTTP on 52734, SSE on 52735)
make run
```
This uses `poetry run tracenexus`. You can also run `poetry run tracenexus --help` for options.

## Development

- **Formatting, Linting & Type Checking**: `make format` (uses `isort` and `black` to reformat code, `ruff` to check and auto-fix linting issues, and `mypy` for type checking).
- **Tests**: `make test`

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
