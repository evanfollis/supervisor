#!/usr/bin/env python3
"""Invoke a reflector through subscription CLIs with cross-provider fallback."""

from __future__ import annotations

import argparse
import json
import sys
import uuid
from pathlib import Path

sys.path.insert(0, "/opt/workspace/supervisor/scripts/lib")

from prompteval.llm import (  # noqa: E402
    AllProvidersThrottled,
    CliCall,
    LLMCallError,
    run_with_fallback,
)

def normalize_claude(raw: str, invocation_id: str, model: str, effort: str) -> dict:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        value = {}
        for line in raw.splitlines():
            if not line.strip():
                continue
            event = json.loads(line)
            if isinstance(event, dict) and event.get("type") == "result":
                value = event
    if not isinstance(value, dict):
        raise ValueError("Claude response is not an object")
    result = value.get("result")
    if not isinstance(result, str) or not result.strip():
        raise ValueError("Claude response has no final result")
    return {
        "session_id": invocation_id,
        "provider_session_id": value.get("session_id", ""),
        "provider": "anthropic",
        "model": model,
        "effort": effort,
        "is_error": bool(value.get("is_error")),
        "result": result,
        "usage": value.get("usage", {}),
        "total_cost_usd": value.get("total_cost_usd"),
        "duration_ms": value.get("duration_ms"),
        "num_turns": value.get("num_turns"),
    }


def normalize_codex(raw: str, invocation_id: str, effort: str) -> dict:
    thread_id = ""
    result = ""
    usage: dict = {}
    for line in raw.splitlines():
        if not line.strip():
            continue
        event = json.loads(line)
        if event.get("type") == "thread.started":
            thread_id = event.get("thread_id", "")
        if event.get("type") == "item.completed":
            item = event.get("item") or {}
            if item.get("type") == "agent_message" and isinstance(item.get("text"), str):
                result = item["text"]
        if event.get("type") == "turn.completed":
            usage = event.get("usage") or {}
    if not result.strip():
        raise ValueError("Codex event stream has no final agent message")
    return {
        "session_id": invocation_id,
        "provider_session_id": thread_id,
        "provider": "openai",
        "model": "codex-subscription-default",
        "effort": effort,
        "is_error": False,
        "result": result,
        "usage": usage,
        "total_cost_usd": None,
        "duration_ms": None,
        "num_turns": None,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt-file", required=True, type=Path)
    parser.add_argument("--project", required=True)
    parser.add_argument("--project-dir", required=True, type=Path)
    parser.add_argument("--model", default="claude-sonnet-4-6")
    parser.add_argument("--effort", default="medium")
    parser.add_argument("--invocation-id", default="")
    parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args()

    invocation_id = args.invocation_id or str(uuid.uuid4())
    prompt = args.prompt_file.read_text(encoding="utf-8")
    claude_session_id = str(uuid.uuid4())
    claude = [
        "claude", "-p", prompt,
        "--model", args.model,
        "--effort", args.effort,
        "--output-format", "stream-json",
        "--verbose",
        "--include-hook-events",
        "--session-id", claude_session_id,
        "--tools", "Read,Glob,Grep",
        "--disable-slash-commands",
    ]
    codex_prompt = prompt + (
        "\n\nYou are the Codex subscription fallback for the reflector. Remain "
        "read-only and return only the requested reflection markdown."
    )
    codex = [
        "codex", "exec", "--skip-git-repo-check", "--sandbox", "read-only",
        "--json", "-",
    ]
    try:
        raw = run_with_fallback(
            [
                CliCall(
                    "claude", args.model, claude,
                    input_text=prompt, cwd=str(args.project_dir),
                ),
                CliCall(
                    "codex", "default", codex,
                    stdin_text=codex_prompt, input_text=codex_prompt,
                    cwd=str(args.project_dir), fallback_from="claude",
                ),
            ],
            timeout=args.timeout,
            retries=0,
            role="reflector",
            project=args.project,
            prompt_id="artifact-reflection",
            run_id=invocation_id,
        )
        try:
            normalized = normalize_claude(raw, invocation_id, args.model, args.effort)
        except (json.JSONDecodeError, ValueError, AttributeError):
            normalized = normalize_codex(raw, invocation_id, args.effort)
        print(json.dumps(normalized, ensure_ascii=False))
        return 0
    except AllProvidersThrottled as error:
        sys.stderr.write(str(error) + "\n")
        return 75
    except (LLMCallError, OSError, ValueError, json.JSONDecodeError) as error:
        sys.stderr.write(str(error) + "\n")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
