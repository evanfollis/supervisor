#!/usr/bin/env python3
import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "lib" / "session-trace-scan.py"
SPEC = importlib.util.spec_from_file_location("session_trace_scan", MODULE_PATH)
scanner = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(scanner)


REGISTRY = [
    {
        "session_name": "general",
        "cwd": "/opt/workspace",
        "agent": "mixed",
        "role": "executive",
        "kind": "persistent",
    }
]


class ModelProvenanceTest(unittest.TestCase):
    def test_claude_assistant_carries_model_and_usage(self):
        obj = {
            "type": "assistant",
            "timestamp": "2026-01-01T00:00:00Z",
            "cwd": "/opt/workspace",
            "sessionId": "claude-session",
            "message": {
                "content": [{"type": "text", "text": "result"}],
                "model": "claude-opus-4-8",
                "usage": {
                    "input_tokens": 2,
                    "cache_creation_input_tokens": 100,
                    "cache_read_input_tokens": 300,
                    "output_tokens": 12,
                    "service_tier": "standard",
                },
            },
        }
        event = scanner.event_for_claude(obj, 7, Path("/tmp/claude.jsonl"), REGISTRY)
        self.assertEqual(event["model"], "claude-opus-4-8")
        self.assertEqual(event["model_provider"], "anthropic")
        self.assertEqual(event["context_tokens"], 402)
        self.assertEqual(event["output_tokens"], 12)
        self.assertEqual(event["service_tier"], "standard")

    def test_codex_turn_context_applies_to_following_messages(self):
        meta = {}
        scanner.event_for_codex(
            {
                "type": "session_meta",
                "payload": {
                    "id": "codex-thread",
                    "cwd": "/opt/workspace",
                    "model_provider": "openai",
                },
            },
            1,
            Path("/tmp/codex.jsonl"),
            REGISTRY,
            meta,
        )
        scanner.event_for_codex(
            {
                "type": "turn_context",
                "payload": {"model": "gpt-5.6-sol", "effort": "high"},
            },
            2,
            Path("/tmp/codex.jsonl"),
            REGISTRY,
            meta,
        )
        event = scanner.event_for_codex(
            {
                "type": "response_item",
                "timestamp": "2026-01-01T00:00:00Z",
                "payload": {
                    "type": "message",
                    "role": "assistant",
                    "content": [{"type": "output_text", "text": "result"}],
                },
            },
            3,
            Path("/tmp/codex.jsonl"),
            REGISTRY,
            meta,
        )
        self.assertEqual(event["model"], "gpt-5.6-sol")
        self.assertEqual(event["model_provider"], "openai")
        self.assertEqual(event["reasoning_effort"], "high")


if __name__ == "__main__":
    unittest.main()
