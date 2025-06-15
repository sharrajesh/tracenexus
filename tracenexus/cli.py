import argparse
import logging
import os

from dotenv import find_dotenv, load_dotenv

from .server.mcp_server import TraceNexusServer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv(find_dotenv())


def main():
    parser = argparse.ArgumentParser(
        description="TraceNexus: MCP server for LLM tracing platforms (runs BOTH transports)"
    )
    parser.add_argument(
        "--http-port",
        type=int,
        default=52734,
        help="Port for streamable-http transport (Cursor)",
    )
    parser.add_argument(
        "--sse-port",
        type=int,
        default=52735,
        help="Port for SSE transport (Windsurf)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host address to bind to",
    )
    parser.add_argument(
        "--mount-path",
        type=str,
        default="/mcp",
        help="Path to mount the MCP endpoints (streamable-http)",
    )
    args = parser.parse_args()
    for key in [
        "LANGSMITH_API_KEY",
        "LANGFUSE_HOST",
        "LANGFUSE_PUBLIC_KEY",
        "LANGFUSE_SECRET_KEY",
    ]:
        value = os.environ.get(key, "example").lower()
        if value == "example":
            logger.warning(
                f"WARNING: {key} is set to 'example'. This is a placeholder. Please set a valid value."
            )
    server = TraceNexusServer()
    server.run(
        http_port=args.http_port,
        sse_port=args.sse_port,
        mount_path=args.mount_path,
        host=args.host,
    )


if __name__ == "__main__":
    main()
