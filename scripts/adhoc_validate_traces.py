#!/usr/bin/env python3
"""Internal ad-hoc validation for known Langfuse trace IDs."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Dict

from dotenv import find_dotenv, load_dotenv

# Ensure local package imports work when running from repository root.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tracenexus.providers.langfuse import LangfuseProviderFactory

DEFAULT_TRACE_FILE = "validation/langfuse_trace_ids.json"


def _normalize(name: str) -> str:
    return name.strip().lower().replace("_", "-")


def _resolve_provider_name(alias: str, providers: Dict[str, object]) -> str | None:
    normalized_alias = _normalize(alias)
    normalized_map = {_normalize(name): name for name in providers}

    # First try exact normalized name.
    if normalized_alias in normalized_map:
        return normalized_map[normalized_alias]

    # Then support suffix matching (e.g., "team-dev").
    for normalized_name, original_name in normalized_map.items():
        if normalized_name.endswith(f"-{normalized_alias}"):
            return original_name

    return None


def _is_error(result: str) -> bool:
    return result.startswith("Trace not found") or result.startswith(
        "Error fetching trace"
    )


async def _run_validation(trace_file: Path) -> int:
    if not trace_file.exists():
        print(f"ERROR: Trace ID file not found: {trace_file}")
        return 1

    trace_map = json.loads(trace_file.read_text(encoding="utf-8"))
    if not isinstance(trace_map, dict) or not trace_map:
        print(f"ERROR: Trace ID file is empty or invalid: {trace_file}")
        return 1

    providers = dict(LangfuseProviderFactory.create_providers())
    if not providers:
        print("ERROR: No Langfuse providers are configured.")
        return 1

    print("Configured providers:", ", ".join(sorted(providers)))
    failures = 0

    for alias, trace_id in trace_map.items():
        provider_name = _resolve_provider_name(alias, providers)
        if not provider_name:
            failures += 1
            print(f"FAIL {alias}: provider not configured")
            continue

        provider = providers[provider_name]
        result = await provider.get_trace(trace_id)
        if _is_error(result):
            failures += 1
            print(f"FAIL {alias} ({provider_name}): {result}")
        else:
            print(f"PASS {alias} ({provider_name})")

    if failures:
        print(f"Validation failed: {failures} project(s) failed.")
        return 1

    print("Validation passed: all configured ad-hoc trace checks succeeded.")
    return 0


def main() -> int:
    load_dotenv(find_dotenv())

    parser = argparse.ArgumentParser(description="Run ad-hoc Langfuse trace checks.")
    parser.add_argument(
        "--trace-file",
        default=DEFAULT_TRACE_FILE,
        help=(
            "Path to JSON file mapping alias -> trace ID "
            f"(default: {DEFAULT_TRACE_FILE})"
        ),
    )
    args = parser.parse_args()
    return asyncio.run(_run_validation(Path(args.trace_file)))


if __name__ == "__main__":
    raise SystemExit(main())
