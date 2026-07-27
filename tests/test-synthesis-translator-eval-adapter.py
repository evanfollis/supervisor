#!/usr/bin/env python3
"""Fail-closed retry contract for the stateful synthesis eval adapter."""

from __future__ import annotations

import importlib.util
import io
import json
import re
import sys
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "lib"))

# Load the worktree's package before the adapter inserts the canonical deployed
# path. This keeps the test hermetic while exercising the adapter module itself.
from prompteval.llm import AllProvidersThrottled  # noqa: E402

ADAPTER_PATH = (
    ROOT
    / "scripts"
    / "lib"
    / "prompteval-adapters"
    / "synthesis-translator-eval-adapter.py"
)
SPEC_PATH = ROOT / ".prompteval" / "synthesis-translator" / "spec.json"

module_spec = importlib.util.spec_from_file_location(
    "synthesis_translator_eval_adapter",
    ADAPTER_PATH,
)
assert module_spec and module_spec.loader
adapter = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(adapter)

configured = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
executor = configured["executor"]
assert executor["same_provider_max_attempts"] == 1
assert executor["allow_fallback"] is True

calls = []


def fail_after_partial_write(provider_calls, **kwargs):
    calls.append((provider_calls, kwargs))
    if provider_calls[0].provider == "claude":
        prompt = provider_calls[0].input_text
        match = re.search(r"HANDOFF_DIR=(/[^\n]+)", prompt)
        assert match, prompt
        partial = Path(match.group(1)) / "partial-from-failed-attempt.md"
        partial.write_text("must never be promoted", encoding="utf-8")
    raise AllProvidersThrottled([])


payload = {
    "prompt_text": (
        "SYNTHESIS={{SYNTHESIS_FILE}}\n"
        "HANDOFF_DIR={{HANDOFF_DIR}}\n"
        "INBOX_DIR={{INBOX_DIR}}\n"
        "NOW={{ISO_NOW}}\n"
        "FILENAME={{ISO_FILENAME}}\n"
    ),
    "model": configured["model"],
    "params": {},
    "transport_policy": {
        "same_provider_max_attempts": executor["same_provider_max_attempts"],
        "allow_fallback": executor["allow_fallback"],
    },
    "input": {
        "synthesis": "# Fixture\n",
        "iso_now": "2026-07-27T00:00:00Z",
        "iso_filename": "2026-07-27T00-00-00Z",
    },
}
stdout = io.StringIO()
stderr = io.StringIO()
with mock.patch.object(adapter, "run_with_fallback", side_effect=fail_after_partial_write), \
     mock.patch.object(sys, "stdin", io.StringIO(json.dumps(payload))), \
     mock.patch.object(sys, "stdout", stdout), \
     mock.patch.object(sys, "stderr", stderr):
    result = adapter.main()

assert result == 75
assert stdout.getvalue() == "", "failed partial output must never be promoted"
assert len(calls) == 2, "one Claude attempt plus one allowed sibling attempt"
assert [entry[0][0].provider for entry in calls] == ["claude", "codex"]
assert all(entry[1]["max_attempts"] == 1 for entry in calls)
assert all(entry[1]["allow_fallback"] is False for entry in calls)
assert "all providers blocked" in stderr.getvalue()

print("synthesis translator partial-write exhaustion is fail-closed")
