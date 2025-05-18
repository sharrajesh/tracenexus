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
        description="TraceNexus: MCP server for LLM tracing platforms"
    )
    parser.add_argument(
        "--transport",
        choices=["streamable-http"],
        default="streamable-http",
        help="Transport protocol (only streamable-http is supported)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for the HTTP server (used with streamable-http transport)",
    )
    parser.add_argument(
        "--mount-path",
        type=str,
        default="/mcp",
        help="Path to mount the MCP endpoints (used with streamable-http transport)",
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
    server.run(transport=args.transport, port=args.port, mount_path=args.mount_path)


if __name__ == "__main__":
    main()
