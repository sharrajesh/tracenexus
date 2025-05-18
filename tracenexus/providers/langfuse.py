import asyncio
import logging
import os
from typing import Any

import yaml
from langfuse import Langfuse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LangfuseProvider:
    def __init__(self):
        LANGFUSE_HOST = os.environ.get("LANGFUSE_HOST", "example")
        LANGFUSE_PUBLIC_KEY = os.environ.get("LANGFUSE_PUBLIC_KEY", "example")
        LANGFUSE_SECRET_KEY = os.environ.get("LANGFUSE_SECRET_KEY", "example")
        logger.info(f"Initializing LANGFUSE_HOST : {LANGFUSE_HOST} ")
        logger.info(
            f"LANGFUSE_PUBLIC_KEY : {LANGFUSE_PUBLIC_KEY[:5]}-xxxxx LANGFUSE_SECRET_KEY : {LANGFUSE_SECRET_KEY[:5]}-xxxxx"
        )
        self.client = Langfuse(
            public_key=LANGFUSE_PUBLIC_KEY,
            secret_key=LANGFUSE_SECRET_KEY,
            host=LANGFUSE_HOST,
        )

    async def get_trace(self, trace_id: str) -> str:
        fetch_response = await asyncio.to_thread(self.client.fetch_trace, trace_id)
        return self.normalize_trace(fetch_response.data)

    def normalize_trace(self, trace_data: Any) -> str:
        trace_as_dict = trace_data.dict()
        return yaml.dump(
            trace_as_dict,
            sort_keys=False,
            indent=2,
            default_flow_style=False,
            allow_unicode=True,
        )
