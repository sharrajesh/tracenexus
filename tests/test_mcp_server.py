from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tracenexus.server.mcp_server import TraceNexusServer

# Providers are used by the server, so their mocks are relevant


@pytest.fixture
def server_setup():
    """Set up a server instance with mocked providers and captured tools."""
    # Dictionary to store captured tool functions
    captured_tools = {}

    # Custom side effect for the mcp.tool decorator mock
    def tool_decorator_side_effect(*args, **kwargs):
        tool_name = kwargs.get("name")

        def decorator(func):
            if tool_name:
                captured_tools[tool_name] = func
            else:  # Fallback if name isn't used, though our server does use it.
                captured_tools[func.__name__] = func
            return func  # The decorator should return the original function

        return decorator

    with patch("tracenexus.server.mcp_server.FastMCP") as MockFastMCP, patch(
        "tracenexus.server.mcp_server.LangSmithProvider"
    ) as MockLangSmithProvider, patch(
        "tracenexus.server.mcp_server.LangfuseProvider"
    ) as MockLangfuseProvider:

        mock_mcp_instance = MockFastMCP.return_value
        # Configure the .tool attribute to use our capturing side effect
        mock_mcp_instance.tool = MagicMock(side_effect=tool_decorator_side_effect)

        mock_ls_provider_instance = MockLangSmithProvider.return_value
        mock_lf_provider_instance = MockLangfuseProvider.return_value

        # Server initialization will call register_tools, which will use the mocked .tool
        server_instance = TraceNexusServer()

        # Yield everything needed, including the captured_tools dictionary
        yield server_instance, mock_mcp_instance, mock_ls_provider_instance, mock_lf_provider_instance, captured_tools


def test_server_initialization(server_setup):
    """Test that the server is properly initialized and tools are registered."""
    server_instance, mock_mcp_instance, _, _, captured_tools = server_setup

    assert mock_mcp_instance is not None
    # Check if the .tool() method on the mock_mcp_instance was called twice
    assert mock_mcp_instance.tool.call_count == 2

    # Verify names were passed to the tool decorator
    call_args_list = mock_mcp_instance.tool.call_args_list
    assert any(
        call.kwargs.get("name") == "langsmith.get_trace" for call in call_args_list
    )
    assert any(
        call.kwargs.get("name") == "langfuse.get_trace" for call in call_args_list
    )

    # Verify that the tools were captured
    assert "langsmith.get_trace" in captured_tools
    assert "langfuse.get_trace" in captured_tools

    server_instance.run()
    mock_mcp_instance.run.assert_called_once_with(
        transport="streamable-http", port=8000, path="/mcp"
    )


@pytest.mark.asyncio
async def test_langsmith_get_trace_tool(server_setup):
    """Test the langsmith.get_trace tool specifically."""
    _, _, mock_ls_provider_instance, _, captured_tools = server_setup

    mock_ls_provider_instance.get_trace = AsyncMock(return_value="yaml_trace_output_ls")

    langsmith_tool_func = captured_tools.get("langsmith.get_trace")
    assert langsmith_tool_func is not None, "Langsmith get_trace tool was not captured"

    # Call the captured tool function
    # The first argument to the tool function will be `self` (the server_instance)
    # if it was defined as a method. Since they are nested functions, they don't take `self`.
    result = await langsmith_tool_func(trace_id="ls_trace_123")

    mock_ls_provider_instance.get_trace.assert_called_once_with("ls_trace_123")
    assert result == "yaml_trace_output_ls"


@pytest.mark.asyncio
async def test_langfuse_get_trace_tool(server_setup):
    """Test the langfuse.get_trace tool specifically."""
    _, _, _, mock_lf_provider_instance, captured_tools = server_setup

    mock_lf_provider_instance.get_trace = AsyncMock(return_value="yaml_trace_output_lf")

    langfuse_tool_func = captured_tools.get("langfuse.get_trace")
    assert langfuse_tool_func is not None, "Langfuse get_trace tool was not captured"

    # Call the captured tool function
    result = await langfuse_tool_func(trace_id="lf_trace_456")

    mock_lf_provider_instance.get_trace.assert_called_once_with("lf_trace_456")
    assert result == "yaml_trace_output_lf"
