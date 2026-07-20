#!/usr/bin/env python3
"""Parser tests for provider-neutral reflection invocation envelopes."""

import importlib.util
import json
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "reflection-invoke.py"
SPEC = importlib.util.spec_from_file_location("reflection_invoke", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def test_claude_envelope_preserves_provider_state():
    raw = json.dumps({
        "session_id": "provider-session",
        "is_error": False,
        "result": "# Reflection",
        "usage": {"input_tokens": 12},
        "duration_ms": 44,
    })
    value = MODULE.normalize_claude(raw, "invocation", "claude-sonnet-4-6", "medium")
    assert value["session_id"] == "invocation"
    assert value["provider_session_id"] == "provider-session"
    assert value["provider"] == "anthropic"
    assert value["result"] == "# Reflection"


def test_claude_stream_extracts_result_and_usage():
    raw = "\n".join([
        json.dumps({"type": "system", "session_id": "provider-session"}),
        json.dumps({"type": "assistant", "message": {"content": []}}),
        json.dumps({
            "type": "result", "session_id": "provider-session",
            "is_error": False, "result": "# Stream reflection",
            "usage": {"output_tokens": 20},
        }),
    ])
    value = MODULE.normalize_claude(raw, "invocation", "claude-sonnet-4-6", "medium")
    assert value["provider_session_id"] == "provider-session"
    assert value["result"] == "# Stream reflection"
    assert value["usage"]["output_tokens"] == 20


def test_codex_stream_extracts_last_agent_message_and_usage():
    raw = "\n".join([
        json.dumps({"type": "thread.started", "thread_id": "thread-1"}),
        json.dumps({"type": "item.completed", "item": {
            "type": "agent_message", "text": "intermediate",
        }}),
        json.dumps({"type": "item.completed", "item": {
            "type": "agent_message", "text": "# Final reflection",
        }}),
        json.dumps({"type": "turn.completed", "usage": {"output_tokens": 25}}),
    ])
    value = MODULE.normalize_codex(raw, "invocation", "medium")
    assert value["provider"] == "openai"
    assert value["provider_session_id"] == "thread-1"
    assert value["result"] == "# Final reflection"
    assert value["usage"]["output_tokens"] == 25


def test_empty_codex_stream_fails_closed():
    try:
        MODULE.normalize_codex(
            json.dumps({"type": "turn.completed", "usage": {}}),
            "invocation", "medium",
        )
    except ValueError as error:
        assert "no final agent message" in str(error)
    else:
        raise AssertionError("empty event stream was accepted")


TESTS = [
    test_claude_envelope_preserves_provider_state,
    test_claude_stream_extracts_result_and_usage,
    test_codex_stream_extracts_last_agent_message_and_usage,
    test_empty_codex_stream_fails_closed,
]


if __name__ == "__main__":
    failures = 0
    for test in TESTS:
        try:
            test()
            print(f"ok: {test.__name__}")
        except Exception as error:
            failures += 1
            print(f"FAIL: {test.__name__}: {error}")
    print(f"\n{len(TESTS) - failures}/{len(TESTS)} passed")
    raise SystemExit(1 if failures else 0)
