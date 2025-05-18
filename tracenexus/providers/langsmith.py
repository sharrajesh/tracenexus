import asyncio
import logging
import os
from typing import Any

import yaml
from langsmith import Client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LangSmithProvider:
    def __init__(self):
        LANGSMITH_API_KEY = os.environ.get("LANGSMITH_API_KEY", "example")
        logger.info(f"Initializing LANGSMITH_API_KEY : {LANGSMITH_API_KEY[:5]}xxxxx")
        self.client = Client(api_key=LANGSMITH_API_KEY)

    async def get_trace(self, trace_id: str) -> str:
        logger.info(f"Getting trace {trace_id} from LangSmith")
        run = await asyncio.to_thread(self.client.read_run, trace_id)
        return self.normalize_trace(run)

    def normalize_trace(self, run: Any) -> str:
        trace_as_dict = run.dict()
        return yaml.dump(
            trace_as_dict, sort_keys=False, indent=2, default_flow_style=False
        )
