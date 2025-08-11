from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tracenexus.server.mcp_server import TraceNexusServer

# Providers are used by the server, so their mocks are relevant


@pytest.fixture
def server_setup():
    """Set up a server instance with mocked providers and captured tools."""
    captured_tools = {}

    def tool_decorator_side_effect(*args, **kwargs):
        tool_name = kwargs.get("name")

        def decorator(func):
            if tool_name:
                captured_tools[tool_name] = func
            else:
                captured_tools[func.__name__] = func
            return func

        return decorator

    with patch(
        "tracenexus.server.mcp_server.LangSmithProviderFactory"
    ) as MockLangSmithProviderFactory, patch(
        "tracenexus.server.mcp_server.LangfuseProviderFactory"
    ) as MockLangfuseProviderFactory:

        # Create mock LangSmith providers
        mock_ls_provider_instance = MagicMock()
        MockLangSmithProviderFactory.create_providers.return_value = [
            ("test", mock_ls_provider_instance)
        ]

        # Create mock Langfuse providers
        mock_lf_provider_instance = MagicMock()
        MockLangfuseProviderFactory.create_providers.return_value = [
            ("test", mock_lf_provider_instance)
        ]

        # Instantiate the server
        server_instance = TraceNexusServer()

        # Now, mock the FastMCP instances on the server instance directly
        mock_mcp_http_instance = MagicMock()
        mock_mcp_sse_instance = MagicMock()
        server_instance.mcp_http = mock_mcp_http_instance
        server_instance.mcp_sse = mock_mcp_sse_instance

        # Set up the tool decorator mock on both instances
        mock_mcp_http_instance.tool = MagicMock(side_effect=tool_decorator_side_effect)
        mock_mcp_sse_instance.tool = MagicMock(side_effect=tool_decorator_side_effect)

        # Reregister tools on the mocked instances
        server_instance.register_tools()

        # We'll check the http instance for calls, assuming they are symmetrical
        yield server_instance, mock_mcp_http_instance, mock_ls_provider_instance, mock_lf_provider_instance, captured_tools


def test_server_initialization(server_setup):
    """Test that the server is properly initialized and tools are registered."""
    server_instance, mock_mcp_instance, _, _, captured_tools = server_setup

    assert mock_mcp_instance is not None
    # Check if the .tool() method on the mock_mcp_instance was called twice
    assert mock_mcp_instance.tool.call_count == 2

    # Verify names were passed to the tool decorator
    call_args_list = mock_mcp_instance.tool.call_args_list
    assert any(
        call.kwargs.get("name") == "langsmith_test_get_trace" for call in call_args_list
    )
    assert any(
        call.kwargs.get("name") == "langfuse_test_get_trace" for call in call_args_list
    )

    # Verify that the tools were captured
    assert "langsmith_test_get_trace" in captured_tools
    assert "langfuse_test_get_trace" in captured_tools

    # Since we replaced the run logic, we can't test it this way anymore.
    # To test run, we'd need a more complex setup with processes.
    # For now, we focus on tool registration.
    # server_instance.run()
    # mock_mcp_instance.run.assert_called_once_with(
    #     transport="streamable-http", port=8000, path="/mcp"
    # )


@pytest.mark.asyncio
async def test_langsmith_get_trace_tool(server_setup):
    """Test the langsmith_get_trace tool specifically."""
    _, _, mock_ls_provider_instance, _, captured_tools = server_setup

    mock_ls_provider_instance.get_trace = AsyncMock(return_value="yaml_trace_output_ls")

    langsmith_tool_func = captured_tools.get("langsmith_test_get_trace")
    assert (
        langsmith_tool_func is not None
    ), "Langsmith test get_trace tool was not captured"

    # Call the captured tool function
    # The first argument to the tool function will be `self` (the server_instance)
    result = await langsmith_tool_func(trace_id="ls_trace_123")

    mock_ls_provider_instance.get_trace.assert_called_once_with("ls_trace_123")
    assert result == "yaml_trace_output_ls"


@pytest.mark.asyncio
async def test_langfuse_get_trace_tool(server_setup):
    """Test the langfuse_get_trace tool specifically."""
    _, _, _, mock_lf_provider_instance, captured_tools = server_setup

    mock_lf_provider_instance.get_trace = AsyncMock(return_value="yaml_trace_output_lf")

    langfuse_tool_func = captured_tools.get("langfuse_test_get_trace")
    assert (
        langfuse_tool_func is not None
    ), "Langfuse test get_trace tool was not captured"

    # Call the captured tool function
    result = await langfuse_tool_func(trace_id="lf_trace_456")

    mock_lf_provider_instance.get_trace.assert_called_once_with("lf_trace_456")
    assert result == "yaml_trace_output_lf"
