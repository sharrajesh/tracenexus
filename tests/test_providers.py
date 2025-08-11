import os
import uuid
import warnings
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
import yaml

from tracenexus.providers.langfuse import LangfuseProvider, LangfuseProviderFactory
from tracenexus.providers.langsmith import LangSmithProvider, LangSmithProviderFactory


@pytest.mark.asyncio
async def test_langsmith_provider_get_trace_success():
    """Test LangSmithProvider.get_trace functionality."""
    dummy_uuid = str(uuid.uuid4())
    start_time_obj = datetime.now()
    end_time_obj = start_time_obj + timedelta(seconds=1)

    mock_run_obj = MagicMock()
    mock_run_obj.id = dummy_uuid
    mock_run_obj.name = "Test Run"
    mock_run_obj.start_time = start_time_obj
    mock_run_obj.end_time = end_time_obj
    mock_run_obj.status = "completed"
    mock_run_obj.inputs = {"input": "test"}
    mock_run_obj.outputs = {"output": "result"}
    mock_run_obj.error = None
    mock_run_obj.metadata = {}

    # Configure the dict method on the mock_run_obj
    mock_run_obj.dict.return_value = {
        "id": dummy_uuid,
        "name": "Test Run",
        "start_time": start_time_obj,
        "end_time": end_time_obj,
        "status": "completed",
        "inputs": {"input": "test"},
        "outputs": {"output": "result"},
        "error": None,
        "metadata": {},
    }

    with patch(
        "tracenexus.providers.langsmith.Client"
    ) as MockLangsmithClientConstructor:
        mock_langsmith_client_instance = MockLangsmithClientConstructor.return_value
        mock_langsmith_client_instance.read_run = MagicMock(return_value=mock_run_obj)

        provider = LangSmithProvider(api_key="test_api_key", name="test")

        trace_yaml_str = await provider.get_trace(dummy_uuid)
        mock_langsmith_client_instance.read_run.assert_called_once_with(dummy_uuid)

        trace = yaml.safe_load(trace_yaml_str)

        assert trace["id"] == dummy_uuid
        assert trace["name"] == "Test Run"
        assert trace["start_time"] == start_time_obj
        assert trace["end_time"] == end_time_obj
        assert trace["status"] == "completed"
        assert trace["inputs"] == {"input": "test"}
        assert trace["outputs"] == {"output": "result"}
        assert trace["error"] is None
        assert trace["metadata"] == {}


@pytest.mark.asyncio
async def test_langsmith_provider_get_trace_not_found():
    """Test LangSmithProvider.get_trace handling of not found errors."""

    with patch(
        "tracenexus.providers.langsmith.Client"
    ) as MockLangsmithClientConstructor:
        mock_langsmith_client_instance = MockLangsmithClientConstructor.return_value

        # Simulate a 404 error
        mock_langsmith_client_instance.read_run = MagicMock(
            side_effect=Exception(
                "404 Client Error: Not Found for url: https://api.smith.langchain.com/runs/xyz"
            )
        )

        provider = LangSmithProvider(api_key="test_api_key", name="test")

        result = await provider.get_trace("non-existent-trace-id")

        assert "Trace not found in test" in result
        assert "non-existent-trace-id" in result
        mock_langsmith_client_instance.read_run.assert_called_once_with(
            "non-existent-trace-id"
        )


@pytest.mark.asyncio
async def test_langsmith_provider_factory():
    """Test LangSmithProviderFactory creates multiple providers correctly."""

    # Test with matching keys and names
    with patch.dict(
        os.environ,
        {"LANGSMITH_API_KEYS": "key1,key2,key3", "LANGSMITH_NAMES": "prod,dev,test"},
    ):
        with patch("tracenexus.providers.langsmith.Client"):
            providers = LangSmithProviderFactory.create_providers()

            assert len(providers) == 3
            assert providers[0][0] == "prod"
            assert providers[1][0] == "dev"
            assert providers[2][0] == "test"

            # Check that each provider has the correct name
            assert providers[0][1].name == "prod"
            assert providers[1][1].name == "dev"
            assert providers[2][1].name == "test"

    # Test with missing names (should auto-generate)
    with patch.dict(
        os.environ, {"LANGSMITH_API_KEYS": "key1,key2", "LANGSMITH_NAMES": ""}
    ):
        with patch("tracenexus.providers.langsmith.Client"):
            providers = LangSmithProviderFactory.create_providers()

            assert len(providers) == 2
            assert providers[0][0] == "instance1"
            assert providers[1][0] == "instance2"

    # Test with no keys configured
    with patch.dict(
        os.environ, {"LANGSMITH_API_KEYS": "example", "LANGSMITH_NAMES": ""}
    ):
        providers = LangSmithProviderFactory.create_providers()
        assert len(providers) == 0


@pytest.mark.asyncio
async def test_langfuse_provider_get_trace_success():
    """Test LangfuseProvider.get_trace functionality."""
    dummy_trace_id = "lf-trace-abc-123"
    start_time_obj = datetime.now()
    end_time_obj = start_time_obj + timedelta(seconds=1)

    # This mock represents the TraceWithFullDetails Pydantic model
    mock_trace_details_obj = MagicMock()
    mock_trace_details_obj.id = dummy_trace_id
    mock_trace_details_obj.name = "Langfuse Test Trace"
    mock_trace_details_obj.start_time = start_time_obj
    mock_trace_details_obj.end_time = end_time_obj
    # mock_trace_details_obj.status = "SUCCESS" # Assuming status is part of .dict()
    # mock_trace_details_obj.inputs = {"prompt": "Hello"}
    # mock_trace_details_obj.outputs = {"completion": "World"}
    # mock_trace_details_obj.error = None
    # mock_trace_details_obj.metadata = {"user": "test_user"}

    # What mock_trace_details_obj.dict() should return
    expected_dict_representation = {
        "id": dummy_trace_id,
        "name": "Langfuse Test Trace",
        "start_time": start_time_obj,  # yaml.dump can handle datetime
        "end_time": end_time_obj,  # yaml.dump can handle datetime
        "status": "SUCCESS",
        "inputs": {"prompt": "Hello"},
        "outputs": {"completion": "World"},
        "error": None,
        "metadata": {"user": "test_user"},
        # Add other fields expected by TraceWithFullDetails.dict() if necessary
        # For example, if the Pydantic model aliases fields, reflect that here.
        # htmlPath, latency, totalCost, observations, scores etc.
        # For simplicity, keeping it minimal. Add fields as your normalize_trace expects.
        "observations": [],  # Assuming these are part of the model
        "scores": [],  # Assuming these are part of the model
        "latency": 1.0,  # Example value
        "totalCost": 0.0,  # Example value
        "htmlPath": f"/project/p1/traces/{dummy_trace_id}",  # Example value
    }
    mock_trace_details_obj.dict.return_value = expected_dict_representation

    # This mock represents the FetchTraceResponse object
    mock_fetch_response_obj = MagicMock()
    mock_fetch_response_obj.data = mock_trace_details_obj

    with patch(
        "tracenexus.providers.langfuse.Langfuse"
    ) as MockLangfuseClientConstructor:
        mock_langfuse_client_instance = MockLangfuseClientConstructor.return_value
        # Mock the fetch_trace method to return our mock_fetch_response_obj
        mock_langfuse_client_instance.fetch_trace = MagicMock(
            return_value=mock_fetch_response_obj
        )

        provider = LangfuseProvider(
            public_key="dummy_pk",
            secret_key="dummy_sk",
            host="https://cloud.langfuse.com",
            name="test",
        )

        trace_yaml_str = await provider.get_trace(dummy_trace_id)

        # Basic check: ensure it's a non-empty string (YAML output)
        assert isinstance(trace_yaml_str, str)
        assert len(trace_yaml_str) > 0

        # More specific checks: try to load the YAML and verify some content
        # This requires PyYAML to be available in the test environment
        try:
            loaded_data = yaml.safe_load(trace_yaml_str)
            assert loaded_data["id"] == dummy_trace_id
            assert loaded_data["name"] == "Langfuse Test Trace"
            assert loaded_data["inputs"] == {"prompt": "Hello"}
            assert loaded_data["metadata"] == {"user": "test_user"}
            # Note: datetime objects get converted to YAML timestamp strings.
            # Comparing them directly after loading might require parsing them back to datetime
            # or comparing their string representations if that's easier for the test.
            assert str(loaded_data["start_time"]) == str(start_time_obj)

        except ImportError:
            warnings.warn(
                "PyYAML not installed, skipping detailed YAML content validation in test_langfuse_provider_get_trace"
            )
        except yaml.YAMLError:
            pytest.fail("Output was not valid YAML")


@pytest.mark.asyncio
async def test_langfuse_provider_get_trace_not_found():
    """Test LangfuseProvider.get_trace handling of not found errors."""

    with patch(
        "tracenexus.providers.langfuse.Langfuse"
    ) as MockLangfuseClientConstructor:
        mock_langfuse_client_instance = MockLangfuseClientConstructor.return_value

        # Simulate a not found error
        mock_langfuse_client_instance.fetch_trace = MagicMock(
            side_effect=Exception("Trace not found")
        )

        provider = LangfuseProvider(
            public_key="test_pk",
            secret_key="test_sk",
            host="https://test.com",
            name="test",
        )

        result = await provider.get_trace("non-existent-trace-id")

        assert "Trace not found in test" in result
        assert "non-existent-trace-id" in result
        mock_langfuse_client_instance.fetch_trace.assert_called_once_with(
            "non-existent-trace-id"
        )


@pytest.mark.asyncio
async def test_langfuse_provider_factory():
    """Test LangfuseProviderFactory creates multiple providers correctly."""

    # Test with matching keys, secrets, hosts, and names
    with patch.dict(
        os.environ,
        {
            "LANGFUSE_PUBLIC_KEYS": "pub1,pub2,pub3",
            "LANGFUSE_SECRET_KEYS": "sec1,sec2,sec3",
            "LANGFUSE_HOSTS": "https://host1.com,https://host2.com,https://host3.com",
            "LANGFUSE_NAMES": "prod,dev,test",
        },
    ):
        with patch("tracenexus.providers.langfuse.Langfuse"):
            providers = LangfuseProviderFactory.create_providers()

            assert len(providers) == 3
            assert providers[0][0] == "prod"
            assert providers[1][0] == "dev"
            assert providers[2][0] == "test"

            # Check that each provider has the correct name
            assert providers[0][1].name == "prod"
            assert providers[1][1].name == "dev"
            assert providers[2][1].name == "test"

    # Test with missing names (should auto-generate)
    with patch.dict(
        os.environ,
        {
            "LANGFUSE_PUBLIC_KEYS": "pub1,pub2",
            "LANGFUSE_SECRET_KEYS": "sec1,sec2",
            "LANGFUSE_HOSTS": "https://host1.com,https://host2.com",
            "LANGFUSE_NAMES": "",
        },
    ):
        with patch("tracenexus.providers.langfuse.Langfuse"):
            providers = LangfuseProviderFactory.create_providers()

            assert len(providers) == 2
            assert providers[0][0] == "instance1"
            assert providers[1][0] == "instance2"

    # Test with mismatched keys and secrets (should return empty)
    with patch.dict(
        os.environ,
        {
            "LANGFUSE_PUBLIC_KEYS": "pub1,pub2",
            "LANGFUSE_SECRET_KEYS": "sec1",
            "LANGFUSE_HOSTS": "https://host1.com,https://host2.com",
            "LANGFUSE_NAMES": "",
        },
    ):
        providers = LangfuseProviderFactory.create_providers()
        assert len(providers) == 0

    # Test with no keys configured
    with patch.dict(
        os.environ,
        {
            "LANGFUSE_PUBLIC_KEYS": "example",
            "LANGFUSE_SECRET_KEYS": "example",
            "LANGFUSE_HOSTS": "example",
            "LANGFUSE_NAMES": "",
        },
    ):
        providers = LangfuseProviderFactory.create_providers()
        assert len(providers) == 0
