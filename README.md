# TraceNexus

> **WORK IN PROGRESS**
>
> This project is under active development and should be considered experimental.

TraceNexus is an MCP (Model Context Protocol) server for LLM observability traces.
It currently supports LangSmith and Langfuse and runs both MCP transports:

- `streamable-http` for clients like Cursor
- `sse`

## Quick Start

### 1. Prerequisites

- Python 3.11+

### 2. Install

```bash
pip install --upgrade tracenexus
```

### 3. Configure

Create a `.env` file where you run `tracenexus`.

If you are running from a cloned repo, start with:

```bash
cp .env.example .env
```

Example `.env`:

```env
# LangSmith configuration (comma-separated)
LANGSMITH_API_KEYS="prod-api-key,dev-api-key"
LANGSMITH_NAMES="prod,dev"

# Langfuse configuration (comma-separated)
LANGFUSE_NAMES="dev,prod,staging,nightly,services"
LANGFUSE_PUBLIC_KEYS="pk_dev,pk_prod,pk_staging,pk_nightly,pk_services"
LANGFUSE_SECRET_KEYS="sk_dev,sk_prod,sk_staging,sk_nightly,sk_services"
LANGFUSE_HOSTS="https://cloud.langfuse.com,https://cloud.langfuse.com,https://cloud.langfuse.com,https://cloud.langfuse.com,https://cloud.langfuse.com"
```

Rules:

- Values are positional. Item `N` in each list must describe the same project.
- If multiple projects share one host, repeat that host value.
- Restart `tracenexus` after `.env` changes.

### 4. Run

```bash
tracenexus
```

Default endpoints:

- HTTP: `http://localhost:52734/mcp`
- SSE: `http://localhost:52735/sse`

### 5. Connect Your MCP Client

For Claude Code:

```bash
claude mcp add tracenexus --transport streamable-http --url http://localhost:52734/mcp
```

For Cursor:

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

## Tool Naming

TraceNexus exposes tools in this format:

- `langsmith_<name>_get_trace`
- `langfuse_<name>_get_trace`

If a configured name contains dashes, they become underscores in tool names.

## Troubleshooting

- `404 ... not found within authorized project`: Key is valid, but mapped to the wrong project for that trace ID.
- `401 ... invalid credentials`: Key and host do not belong together.
- Tool names not updated after changing `.env`: Restart `tracenexus`.

## Contributing

Contributor/developer workflow is documented in `CONTRIBUTING.md`.

## License

This project is licensed under MIT. See `LICENSE.md`.
