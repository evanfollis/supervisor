#!/usr/bin/env python3
import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "lib" / "reflection-provenance.py"
SPEC = importlib.util.spec_from_file_location("reflection_provenance", MODULE_PATH)
module = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(module)


class ReflectionProvenanceTest(unittest.TestCase):
    def test_groups_source_models_and_records_reflector(self):
        now = datetime(2026, 1, 1, 12, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as td:
            trace = Path(td) / "trace.jsonl"
            rows = [
                {
                    "ts": "2026-01-01T08:00:00Z",
                    "cwd": "/opt/workspace/projects/demo",
                    "actor": "assistant",
                    "model": "claude-opus-4-8",
                    "model_provider": "anthropic",
                    "trace_ref": "claude.jsonl:2",
                },
                {
                    "ts": "2026-01-01T09:00:00Z",
                    "cwd": "/opt/projects/demo",
                    "actor": "assistant",
                    "model": "gpt-5.6-sol",
                    "model_provider": "openai",
                    "reasoning_effort": "high",
                    "trace_ref": "codex.jsonl:4",
                },
                {
                    "ts": "2025-12-30T09:00:00Z",
                    "cwd": "/opt/workspace/projects/demo",
                    "actor": "assistant",
                    "model": "old-model",
                },
            ]
            trace.write_text("".join(json.dumps(row) + "\n" for row in rows))
            manifest = module.build_manifest(
                trace,
                "/opt/workspace/projects/demo",
                12,
                "anthropic",
                "claude-sonnet-4-6",
                "medium",
                now=now,
            )

        self.assertEqual(manifest["source_assistant_message_count"], 2)
        self.assertEqual(manifest["reflector"]["model"], "claude-sonnet-4-6")
        self.assertEqual({item["model"] for item in manifest["source_models"]}, {"claude-opus-4-8", "gpt-5.6-sol"})


if __name__ == "__main__":
    unittest.main()
