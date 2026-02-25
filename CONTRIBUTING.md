# Contributing

Thanks for contributing to TraceNexus.

## Prerequisites

- Python 3.11+
- Poetry

## Setup (From Source)

```bash
git clone https://github.com/sharrajesh/tracenexus.git
cd tracenexus
make install-dev
cp .env.example .env
```

Populate `.env` with your LangSmith/Langfuse credentials.

Important:

- Do not commit real API keys.
- Keep comma-separated provider lists positional (`N`th key/name/host belongs together).

## Run Locally

```bash
make run
```

This starts:

- `http://127.0.0.1:52734/mcp` (streamable-http)
- `http://127.0.0.1:52735/sse` (sse)

To stop running servers:

```bash
make stop
```

## Quality Checks

```bash
make format
make test
```

## Internal Ad-hoc Validation (Optional)

This check is intended for internal operational verification.

```bash
make adhoc-validate-traces
```

Use a different file if needed:

```bash
make adhoc-validate-traces ADHOC_TRACE_FILE=path/to/trace_ids.json
```

## Build And Publish Helpers

```bash
make build
make version
make version-patch
make version-minor
make version-major
make publish
```

## Project Layout

- `tracenexus/cli.py`: CLI entrypoint and env loading.
- `tracenexus/server/mcp_server.py`: MCP tool registration and server startup.
- `tracenexus/providers/`: LangSmith/Langfuse provider integrations.
