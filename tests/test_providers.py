import os
import uuid
import warnings
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
import yaml

from tracenexus.providers.langfuse import LangfuseProvider
from tracenexus.providers.langsmith import LangSmithProvider


@pytest.mark.asyncio
async def test_langsmith_provider_get_trace():
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

        provider = LangSmithProvider()

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
        # assert trace["platform"] == "langsmith" # Removed as platform is no longer added


@pytest.mark.asyncio
async def test_langfuse_provider_get_trace():
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

        with patch.dict(
            os.environ,
            {"LANGFUSE_PUBLIC_KEY": "dummy_pk", "LANGFUSE_SECRET_KEY": "dummy_sk"},
        ):
            provider = LangfuseProvider()

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
