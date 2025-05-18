import logging
from typing import cast

from fastmcp import FastMCP

from ..providers import LangfuseProvider, LangSmithProvider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TraceNexusServer:
    def __init__(self):
        self.mcp = FastMCP("TraceNexus")
        # Instantiate providers
        self.langsmith_provider = LangSmithProvider()
        self.langfuse_provider = LangfuseProvider()
        self.register_tools()

    def register_tools(self):
        @self.mcp.tool(name="langsmith.get_trace")  # Explicit tool name
        async def langsmith_get_trace(
            trace_id: str,
        ) -> str:  # Return type is str (YAML)
            result = await self.langsmith_provider.get_trace(trace_id)
            return cast(str, result)

        @self.mcp.tool(name="langfuse.get_trace")  # Explicit tool name
        async def langfuse_get_trace(trace_id: str) -> str:  # Return type is str (YAML)
            result = await self.langfuse_provider.get_trace(trace_id)
            return cast(str, result)

        # Add other provider tools here as they are developed  # e.g., datadog_get_trace, newrelic_get_trace

    def run(
        self,
        transport: str = "streamable-http",
        port: int = 8000,
        mount_path: str = "/mcp",
    ):
        if transport != "streamable-http":
            raise ValueError(
                f"Unsupported transport: {transport}. Only 'streamable-http' is supported."
            )

        run_args = {
            "transport": "streamable-http",
            "port": port,
            "path": mount_path,
        }
        log_message_parts = [
            f"transport={run_args['transport']}",
            f"port={port}",
            f"path={mount_path}",
        ]

        logger.info(f"Running MCP server with {', '.join(log_message_parts)}")
        self.mcp.run(**run_args)
