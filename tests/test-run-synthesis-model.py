#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "scripts" / "lib" / "run-synthesis-model.py"
spec = importlib.util.spec_from_file_location("run_synthesis_model", path)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

calls = module.build_calls("PROMPT", "/opt/workspace", "claude-opus-4-6")
assert [call.provider for call in calls] == ["claude", "codex"]
assert calls[0].model == "claude-opus-4-6"
assert "--disallowedTools" in calls[0].cmd
assert "Bash(git commit:*)" in calls[0].cmd
assert calls[1].fallback_from == "claude"
assert calls[1].stdin_text and "same synthesis contract" in calls[1].stdin_text
assert calls[1].stdin_text and "Do not change git history" in calls[1].stdin_text
assert Path(calls[1].cmd[0]).name == "codex"
assert calls[1].cmd[-1] == "-"

translator_calls = module.build_calls(
    "TRANSLATE", "/opt/workspace", "claude-haiku-4-5-20251001", "acceptEdits"
)
assert translator_calls[0].cmd[1:3] == ["--permission-mode", "acceptEdits"]

captured = {}


def fake_run(configured, **kwargs):
    captured["calls"] = configured
    captured.update(kwargs)
    return "complete"


module.run_with_fallback = fake_run
result = module.execute("PROMPT", "/opt/workspace", "synthesis-test", 42, "claude-opus-4-6")
assert result == "complete"
assert captured["run_id"] == "synthesis-test"
assert captured["role"] == "workspace-synthesis"
assert captured["project"] == "supervisor"
assert captured["prompt_id"] == "workspace-synthesis"
assert captured["retries"] == 0
assert captured["timeout"] == 42

captured.clear()
module.execute(
    "TRANSLATE",
    "/opt/workspace",
    "translation-test",
    21,
    "claude-haiku-4-5-20251001",
    role="synthesis-translation",
    project="supervisor",
    prompt_id="synthesis-translator",
    claude_permission_mode="acceptEdits",
)
assert captured["role"] == "synthesis-translation"
assert captured["prompt_id"] == "synthesis-translator"
assert captured["calls"][0].cmd[1:3] == ["--permission-mode", "acceptEdits"]
print("workspace synthesis subscription fallback contract passed")
