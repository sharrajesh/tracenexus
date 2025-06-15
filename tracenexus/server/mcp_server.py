import logging
import multiprocessing
from typing import cast

from fastmcp import FastMCP

from ..providers import LangfuseProvider, LangSmithProvider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TraceNexusServer:
    def __init__(self):
        # Create two FastMCP instances - one for each transport
        self.mcp_http = FastMCP("TraceNexus-HTTP")
        self.mcp_sse = FastMCP("TraceNexus-SSE")
        # Instantiate providers
        self.langsmith_provider = LangSmithProvider()
        self.langfuse_provider = LangfuseProvider()
        self.register_tools()

    def register_tools(self):
        # Register tools on both FastMCP instances
        for mcp_instance in [self.mcp_http, self.mcp_sse]:

            @mcp_instance.tool(name="langsmith_get_trace")  # Explicit tool name
            async def langsmith_get_trace(
                trace_id: str,
            ) -> str:  # Return type is str (YAML)
                result = await self.langsmith_provider.get_trace(trace_id)
                return cast(str, result)

            @mcp_instance.tool(name="langfuse_get_trace")  # Explicit tool name
            async def langfuse_get_trace(
                trace_id: str,
            ) -> str:  # Return type is str (YAML)
                result = await self.langfuse_provider.get_trace(trace_id)
                return cast(str, result)

        # Add other provider tools here as they are developed  # e.g., datadog_get_trace, newrelic_get_trace

    def run(
        self,
        http_port: int = 52734,
        sse_port: int = 52735,
        mount_path: str = "/mcp",
        host: str = "127.0.0.1",
    ):
        logger.info("Starting TraceNexus with DUAL transport support:")
        logger.info(
            f"  📡 Streamable-HTTP (Cursor): http://{host}:{http_port}{mount_path}"
        )
        logger.info(f"  🌊 SSE (Windsurf): http://{host}:{sse_port}/sse")

        # Start both transports in separate processes
        def run_http_server():
            logger.info(f"Starting HTTP transport on port {http_port}")
            self.mcp_http.run(
                transport="streamable-http",
                port=http_port,
                path=mount_path,
            )

        def run_sse_server():
            logger.info(f"Starting SSE transport on port {sse_port}")
            self.mcp_sse.run(
                transport="sse",
                host=host,
                port=sse_port,
                path="/sse",
            )

        # Start HTTP server in a separate process
        http_process = multiprocessing.Process(target=run_http_server, daemon=True)
        http_process.start()

        # Start SSE server in main thread (so Ctrl+C works properly)
        try:
            run_sse_server()
        except KeyboardInterrupt:
            logger.info("Shutting down TraceNexus server...")
        except Exception as e:
            logger.error(f"Error running server: {e}")
            raise
