# TraceNexus

> **⚠️ WORK IN PROGRESS ⚠️**
>
> This project is currently under active development and should be considered experimental. 
> Features may change, and stability is not guaranteed.
>
> Please DM the author if you have any comments, suggestions, or would like to contribute!

A platform-agnostic MCP (Model Context Protocol) server for LLM observability, supporting platforms like LangSmith and Langfuse. It uses FastMCP 2.0 and the `streamable-http` transport.

## Features

- 🔄 Support for multiple tracing platforms through a unified interface
- 🛠️ MCP tools for retrieving and analyzing traces
- 📊 Trace comparison across different platforms
- 🔌 HTTP-based transport protocol (`streamable-http` using FastMCP 2.0)
- 🧩 Easy integration with LangSmith and LangFuse

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

This will start the server, typically listening on `http://localhost:8000/mcp`.
To see all available command-line options, including changing the port, or mount path:
```bash
tracenexus --help
```

### 5. Using with MCP Client Applications (e.g., Cursor, Codium)

To configure TraceNexus as an MCP server in client applications that support Model Context Protocol (like Cursor or Codium):

1.  Ensure the TraceNexus server is running (e.g., via `tracenexus`).
2.  In your client application's MCP server settings, add a configuration similar to the following:

```json
{
  "mcpServers": {
    "tracenexus": {
      "transport": "streamable-http",
      "url": "http://localhost:8000/mcp" 
    }
  }
}
```

This tells the client to connect to your local TraceNexus server. The `url` should match the host, port, and mount path your TraceNexus server is using (default is `http://localhost:8000/mcp`).

## Available Tools

Once running, the server exposes the following MCP tools:

-   **`langsmith.get_trace`**: Retrieve a single trace by ID from LangSmith.
-   **`langfuse.get_trace`**: Retrieve a single trace by ID from Langfuse.

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
# Run the TraceNexus server (defaults to streamable-http on port 8000 at /mcp)
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
