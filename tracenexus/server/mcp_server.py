import logging
import multiprocessing
from typing import Annotated, Dict

from fastmcp import FastMCP
from pydantic import Field

from ..providers import (
    LangfuseProvider,
    LangfuseProviderFactory,
    LangSmithProvider,
    LangSmithProviderFactory,
)

logger = logging.getLogger(__name__)


class TraceNexusServer:
    def __init__(self) -> None:
        # Create two FastMCP instances - one for each transport
        self.mcp_http: FastMCP = FastMCP("TraceNexus-HTTP")
        self.mcp_sse: FastMCP = FastMCP("TraceNexus-SSE")

        # Instantiate LangSmith providers (multiple instances)
        self.langsmith_providers: Dict[str, LangSmithProvider] = {}
        for name, provider in LangSmithProviderFactory.create_providers():  # type: ignore[assignment]
            self.langsmith_providers[name] = provider  # type: ignore[assignment]

        # Instantiate Langfuse providers (multiple instances)
        self.langfuse_providers: Dict[str, LangfuseProvider] = {}
        for name, provider in LangfuseProviderFactory.create_providers():  # type: ignore[assignment]
            self.langfuse_providers[name] = provider  # type: ignore[assignment]

        self.register_tools()

    def create_langsmith_tool(self, provider: LangSmithProvider, name: str):
        """Create a tool function for a specific LangSmith provider instance."""

        async def tool_func(
            trace_id: Annotated[
                str, Field(description="The ID of the trace to retrieve")
            ],
        ) -> str:
            """Get a trace from LangSmith by its ID."""
            logger.info(f"langsmith_{name}_get_trace called with trace_id: {trace_id}")
            try:
                result = await provider.get_trace(trace_id)
                return result
            except Exception as e:
                logger.error(f"Error in langsmith_{name}_get_trace: {e}")
                raise

        return tool_func

    def create_langfuse_tool(self, provider: LangfuseProvider, name: str):
        """Create a tool function for a specific Langfuse provider instance."""

        async def tool_func(
            trace_id: Annotated[
                str, Field(description="The ID of the trace to retrieve")
            ],
        ) -> str:
            """Get a trace from Langfuse by its ID."""
            logger.info(f"langfuse_{name}_get_trace called with trace_id: {trace_id}")
            try:
                result = await provider.get_trace(trace_id)
                return result
            except Exception as e:
                logger.error(f"Error in langfuse_{name}_get_trace: {e}")
                raise

        return tool_func

    def register_tools(self) -> None:
        # Register tools on both FastMCP instances
        for mcp_instance in [self.mcp_http, self.mcp_sse]:
            logger.info(f"Registering tools for {mcp_instance.name}")

            # Register a tool for each LangSmith instance
            for name, provider in self.langsmith_providers.items():
                tool_name = f"langsmith_{name}_get_trace"
                logger.info(f"Registering tool: {tool_name}")

                # Create and register the tool
                tool_func = self.create_langsmith_tool(provider, name)
                mcp_instance.tool(
                    name=tool_name,
                    description=f"Get a trace from LangSmith instance '{name}' by trace ID",
                )(tool_func)

            # Register a tool for each Langfuse instance
            for name, provider in self.langfuse_providers.items():  # type: ignore[assignment]
                tool_name = f"langfuse_{name}_get_trace"
                logger.info(f"Registering tool: {tool_name}")

                # Create and register the tool
                tool_func = self.create_langfuse_tool(provider, name)  # type: ignore[arg-type]
                mcp_instance.tool(
                    name=tool_name,
                    description=f"Get a trace from Langfuse instance '{name}' by trace ID",
                )(tool_func)

        logger.info("Tool registration complete")

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
            # Create a new server instance in this process for HTTP
            server = TraceNexusServer()
            logger.info(f"Starting HTTP transport on port {http_port}")
            server.mcp_http.run(
                transport="streamable-http",
                port=http_port,
                path=mount_path,
            )

        # Start HTTP server in a separate process
        http_process = multiprocessing.Process(target=run_http_server, daemon=True)
        http_process.start()

        # Start SSE server in main thread (so Ctrl+C works properly)
        # This uses the existing server instance created by CLI
        try:
            logger.info(f"Starting SSE transport on port {sse_port}")
            self.mcp_sse.run(
                transport="sse",
                host=host,
                port=sse_port,
                path="/sse",
            )
        except KeyboardInterrupt:
            logger.info("Shutting down TraceNexus server...")
            http_process.terminate()
        except Exception as e:
            logger.error(f"Error running server: {e}")
            raise
