#!/usr/bin/env python3
"""Isolated executor for the artifact-driven reflection prompt.

The adapter builds a disposable project and runs the same read-only model path
as production.  It then applies the deterministic primary-object attestor and
emits compact grading markers.  No eval case can write to a live project.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, "/opt/workspace/supervisor/scripts/lib")

from prompteval.llm import AllProvidersThrottled, CliCall, LLMCallError, run_with_fallback  # noqa: E402
from reflection_document import normalize_with_metadata  # noqa: E402

CHECKER = "/opt/workspace/supervisor/scripts/lib/reflection-evidence.py"
SNAPSHOT = "/opt/workspace/supervisor/scripts/lib/reflection-snapshot.py"


def git(directory: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(directory), *args], check=True,
        capture_output=True, text=True,
    ).stdout.strip()


def final_claude_result(raw: str) -> str:
    result = ""
    for line in raw.splitlines():
        if not line.strip():
            continue
        event = json.loads(line)
        if isinstance(event, dict) and event.get("type") == "result":
            candidate = event.get("result")
            if isinstance(candidate, str):
                result = candidate
    if not result.strip():
        raise ValueError("Claude event stream has no final result")
    return result


def final_codex_result(raw: str) -> str:
    result = ""
    for line in raw.splitlines():
        if not line.strip():
            continue
        event = json.loads(line)
        if isinstance(event, dict) and event.get("type") == "item.completed":
            item = event.get("item") or {}
            if item.get("type") == "agent_message" and isinstance(item.get("text"), str):
                result = item["text"]
    if not result.strip():
        raise ValueError("Codex event stream has no final agent message")
    return result


def main() -> int:
    payload = json.load(sys.stdin)
    template = payload["prompt_text"]
    case = payload["input"]
    model = payload.get("model") or "claude-sonnet-4-6"
    telemetry = payload.get("telemetry") or {}

    with tempfile.TemporaryDirectory(prefix="reflection-eval-") as tmp_value:
        root = Path(tmp_value)
        workspace = root / "workspace"
        project = workspace / "projects" / "fixture"
        session_dir = root / "sessions"
        meta = workspace / "runtime" / ".meta"
        telemetry_dir = workspace / "runtime" / ".telemetry"
        handoff = workspace / "runtime" / ".handoff"
        memory = root / "memory"
        for directory in (project, session_dir, meta, telemetry_dir, handoff, memory):
            directory.mkdir(parents=True, exist_ok=True)

        (workspace / "CLAUDE.md").write_text(
            "# Fixture principles\n\nRead primary evidence before theorizing. "
            "Do not manufacture certainty.\n",
            encoding="utf-8",
        )
        (project / "CLAUDE.md").write_text(
            "# Project principles\n\nPropose only from observed artifacts.\n",
            encoding="utf-8",
        )
        (project / "CURRENT_STATE.md").write_text(
            case.get("current_state", "# Current state\n\nNo known degradation.\n"),
            encoding="utf-8",
        )
        for relative, content in (case.get("files") or {}).items():
            destination = project / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(content, encoding="utf-8")
        (telemetry_dir / "events.jsonl").write_text(
            case.get("telemetry", ""), encoding="utf-8"
        )
        (session_dir / "fixture.jsonl").write_text(
            case.get("transcript", ""), encoding="utf-8"
        )
        (memory / "MEMORY.md").write_text("# Empty fixture memory\n", encoding="utf-8")

        git(project, "init", "-b", "main")
        git(project, "config", "user.email", "eval@example.com")
        git(project, "config", "user.name", "Reflection Eval")
        git(project, "add", ".")
        git(project, "commit", "-m", case.get("commit_message", "Record fixture evidence"))
        before = git(project, "status", "--porcelain=v1")

        output = meta / "fixture-reflection.md"
        snapshot = meta / "fixture-reflection-snapshot.json"
        subprocess.run([
            "python3", SNAPSHOT,
            "--project", "fixture",
            "--project-dir", str(project),
            "--output", str(snapshot),
            "--explicit-file", str(telemetry_dir / "events.jsonl"),
            "--explicit-file", str(project / "CURRENT_STATE.md"),
            "--explicit-file", str(project / "CLAUDE.md"),
            "--explicit-file", str(workspace / "CLAUDE.md"),
            "--session-dir", str(session_dir),
            "--prior-reflection-dir", str(meta),
        ], check=True, capture_output=True, text=True)
        prompt = (
            template
            .replace("{{PROJECT}}", "fixture")
            .replace("{{PROJECT_DIR}}", str(project))
            .replace("{{OUTPUT_FILE}}", str(output))
            .replace("{{ISO_NOW}}", "2026-07-20T12-00-00Z")
            .replace("{{SESSION_DIR}}", str(session_dir))
            .replace("{{WORKSPACE_TELEMETRY_FILE}}", str(telemetry_dir / "events.jsonl"))
            .replace("{{WORKSPACE_META_DIR}}", str(meta))
            .replace("{{WORKSPACE_ROOT_CLAUDE_MD}}", str(workspace / "CLAUDE.md"))
            .replace("{{WORKSPACE_HANDOFF_DIR}}", str(handoff))
            .replace("{{WORKSPACE_SESSION_MEMORY_DIR}}", str(memory))
            .replace("{{REFLECTION_SNAPSHOT}}", str(snapshot))
        )

        claude_cmd = [
            "claude", "-p", prompt, "--model", model, "--effort", "medium",
            "--tools", "Read,Glob,Grep", "--disable-slash-commands",
            "--output-format", "stream-json", "--verbose", "--include-hook-events",
        ]
        codex_prompt = prompt + (
            "\n\nYou are the subscription fallback. Inspect only the fixture paths above, "
            "remain read-only, and print the requested reflection markdown to stdout."
        )
        try:
            raw = run_with_fallback(
                [
                    CliCall("claude", model, claude_cmd, input_text=prompt, cwd=str(project)),
                    CliCall(
                        "codex", "",
                        ["codex", "exec", "--skip-git-repo-check", "--sandbox", "read-only", "--json", "-"],
                        stdin_text=codex_prompt, input_text=codex_prompt,
                        cwd=str(project), fallback_from="claude",
                    ),
                ],
                timeout=600,
                role="executor-adapter",
                project=telemetry.get("project", "supervisor"),
                prompt_id=telemetry.get("prompt_id", "artifact-reflection"),
                case_id=telemetry.get("case_id", ""),
                trial=telemetry.get("trial"),
                run_id=telemetry.get("run_id", ""),
            )
            try:
                reflection = final_claude_result(raw)
            except (json.JSONDecodeError, ValueError):
                reflection = final_codex_result(raw)
        except AllProvidersThrottled as error:
            sys.stderr.write(str(error))
            return 75
        except LLMCallError as error:
            sys.stderr.write(str(error))
            return 1

        normalized, normalization = normalize_with_metadata(reflection)
        output.write_text(normalized, encoding="utf-8")
        sidecar = meta / "fixture-reflection.evidence.json"
        check = subprocess.run(
            ["python3", CHECKER, str(output), "--sidecar", str(sidecar)],
            check=True, capture_output=True, text=True,
        )
        counts = json.loads(check.stdout)
        attested = output.read_text(encoding="utf-8").rstrip()
        after = git(project, "status", "--porcelain=v1")
        mutated = before != after
        print(attested)
        print(
            "\n===PRIMARY-OBJECT-MATCHED:"
            f"{counts['primary_object_matched_count']}==="
        )
        print(f"===UNVERIFIED:{counts['unverified_count']}===")
        print(f"===PROJECT-MUTATED:{str(mutated).lower()}===")
        print(
            "===SUPPRESSED-QUESTION-LINES:"
            f"{normalization['question_lines_suppressed']}==="
        )
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
