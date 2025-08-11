import asyncio
import logging

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    mcp_server_url = "http://localhost:52734/mcp"  # Updated to use correct port
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

        # Example: Using LangSmith tools (now with instance names)
        # Tool names follow pattern: langsmith_<instance_name>_get_trace
        langsmith_trace_id = "96e32516-590a-47c5-9510-72194ee02937"

        # Try to find any LangSmith tool (e.g., langsmith_prod_get_trace)
        langsmith_tools = [
            t
            for t in tools
            if t.name.startswith("langsmith_") and t.name.endswith("_get_trace")
        ]
        if langsmith_tools:
            # Use the first available LangSmith tool
            langsmith_tool = langsmith_tools[0]
            print(
                f"\nAttempting to get details for trace '{langsmith_trace_id}' using '{langsmith_tool.name}':"
            )
            try:
                trace = await langsmith_tool.ainvoke({"trace_id": langsmith_trace_id})
                print(f"Trace details (from LangSmith): {trace}")
            except Exception as e:
                print(f"Error during LangSmith tool invocation: {e}")
        else:
            print(
                "\nNo LangSmith tools found. Make sure LANGSMITH_API_KEYS is configured."
            )

        # Example: Using Langfuse tools (now with instance names)
        # Tool names follow pattern: langfuse_<instance_name>_get_trace
        langfuse_trace_id = "fe8c36d8-ef31-41ea-8899-f735fb4872fa"

        # Try to find any Langfuse tool (e.g., langfuse_prod_get_trace)
        langfuse_tools = [
            t
            for t in tools
            if t.name.startswith("langfuse_") and t.name.endswith("_get_trace")
        ]
        if langfuse_tools:
            # Use the first available Langfuse tool
            langfuse_tool = langfuse_tools[0]
            print(
                f"\nAttempting to get details for trace '{langfuse_trace_id}' using '{langfuse_tool.name}':"
            )
            try:
                trace = await langfuse_tool.ainvoke({"trace_id": langfuse_trace_id})
                print(f"Trace details (from Langfuse): {trace}")
            except Exception as e:
                print(f"Error during Langfuse tool invocation: {e}")
        else:
            print(
                "\nNo Langfuse tools found. Make sure LANGFUSE_PUBLIC_KEYS, LANGFUSE_SECRET_KEYS, and LANGFUSE_HOSTS are configured."
            )


if __name__ == "__main__":
    print("Starting TraceNexus client example...")
    print("Ensure the TraceNexus server is running, e.g.: poetry run tracenexus")
    asyncio.run(main())
