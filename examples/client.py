import asyncio
import logging

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    mcp_server_url = "http://localhost:8000/mcp"  # Default server URL
    server_key = "tracenexus_server"
    mcp_config = {
        server_key: {
            "transport": "streamable_http",  # Specify the transport
            "url": mcp_server_url,
        }
    }
    print(f"Attempting to connect to MCP server at {mcp_server_url}")

    client = MultiServerMCPClient(mcp_config)
    async with client.session(server_key) as session:
        tools = await load_mcp_tools(session)
        print("\nAvailable TraceNexus tools:")
        if not tools:
            print("No tools found.")
        for tool in tools:
            print(f"- {tool.name}: {tool.description}")
        if not tools:
            print("Skipping tool invocation as no tools were found.")
            return
        langsmith_trace_id = "96e32516-590a-47c5-9510-72194ee02937"
        langsmith_get_tool_name = "langsmith_get_trace"
        langsmith_get_tool = next(
            (t for t in tools if t.name == langsmith_get_tool_name), None
        )
        if langsmith_get_tool:
            print(
                f"\nAttempting to get details for trace '{langsmith_trace_id}' using '{langsmith_get_tool_name}':"
            )
            try:
                trace = await langsmith_get_tool.ainvoke(
                    {"trace_id": langsmith_trace_id}
                )
                print(f"Trace details (from LangSmith): {trace}")
            except Exception as e:
                print(f"Error during LangSmith tool invocation: {e}")
        else:
            print(
                f"\nTool '{langsmith_get_tool_name}' not found. Skipping LangSmith get_trace example."
            )

        langfuse_trace_id = "fe8c36d8-ef31-41ea-8899-f735fb4872fa"
        langfuse_get_tool_name = "langfuse_get_trace"
        langfuse_get_tool = next(
            (t for t in tools if t.name == langfuse_get_tool_name), None
        )
        if langfuse_get_tool:
            print(
                f"\nAttempting to get details for trace '{langfuse_trace_id}' using '{langfuse_get_tool_name}':"
            )
            try:
                trace = await langfuse_get_tool.ainvoke({"trace_id": langfuse_trace_id})
                print(f"Trace details (from Langfuse): {trace}")
            except Exception as e:
                print(f"Error during Langfuse tool invocation: {e}")
        else:
            print(
                f"\nTool '{langfuse_get_tool_name}' not found. Skipping Langfuse get_trace example."
            )


if __name__ == "__main__":
    print("Starting TraceNexus client example...")
    print("Ensure the TraceNexus server is running, e.g.: poetry run tracenexus")
    asyncio.run(main())
