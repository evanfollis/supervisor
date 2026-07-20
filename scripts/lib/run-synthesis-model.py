#!/usr/bin/env python3
"""Run workspace synthesis through subscription CLIs with bounded failover.

The primary and fallback models receive the same synthesis contract. Full
inputs, outputs, and diagnostics are retained by prompteval.llm in the
owner-only run transcript; aggregate telemetry remains compact.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

LIB = Path(__file__).resolve().parent
sys.path.insert(0, str(LIB))

from prompteval.llm import (  # noqa: E402
    AllProvidersThrottled,
    CliCall,
    LLMCallError,
    run_with_fallback,
)


CLAUDE_DENY = [
    "Bash(git commit:*)",
    "Bash(git push:*)",
    "Bash(git reset:*)",
    "Bash(git rebase:*)",
    "Bash(git checkout:*)",
    "Bash(git merge:*)",
    "Bash(git add:*)",
    "Bash(git restore:*)",
    "Bash(git clean:*)",
    "Bash(rm:*)",
    "Bash(mv:*)",
    "Bash(systemctl:*)",
    "Bash(docker:*)",
    "Edit",
    "NotebookEdit",
]


def build_calls(prompt: str, cwd: str, claude_model: str) -> list[CliCall]:
    claude_cmd = [
        "claude",
        "-p",
        prompt,
        "--model",
        claude_model,
        "--effort",
        "high",
        "--disallowedTools",
        *CLAUDE_DENY,
    ]
    fallback_prompt = (
        prompt
        + "\n\n## Provider fallback context\n"
        + "Claude subscription capacity is unavailable. Complete the same synthesis "
        + "contract using the Codex subscription. You may write only the output and "
        + "runtime evidence explicitly authorized by the prompt. Do not change git "
        + "history, commit, push, deploy, or alter project source.\n"
    )
    codex_cmd = [
        "codex",
        "exec",
        "--skip-git-repo-check",
        "-c",
        'approval_policy="never"',
        "--sandbox",
        "workspace-write",
        "-C",
        cwd,
        "-",
    ]
    return [
        CliCall(
            provider="claude",
            model=claude_model,
            cmd=claude_cmd,
            input_text=prompt,
            cwd=cwd,
        ),
        CliCall(
            provider="codex",
            model="default",
            cmd=codex_cmd,
            stdin_text=fallback_prompt,
            input_text=fallback_prompt,
            cwd=cwd,
            fallback_from="claude",
        ),
    ]


def execute(prompt: str, cwd: str, run_id: str, timeout: int, claude_model: str) -> str:
    return run_with_fallback(
        build_calls(prompt, cwd, claude_model),
        timeout=timeout,
        retries=0,
        role="workspace-synthesis",
        project="supervisor",
        prompt_id="workspace-synthesis",
        run_id=run_id,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt-file", required=True)
    parser.add_argument("--cwd", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--timeout", type=int, default=1100)
    parser.add_argument("--claude-model", default="claude-opus-4-6")
    args = parser.parse_args()

    prompt = Path(args.prompt_file).read_text(encoding="utf-8")
    try:
        output = execute(
            prompt=prompt,
            cwd=args.cwd,
            run_id=args.run_id,
            timeout=args.timeout,
            claude_model=args.claude_model,
        )
    except AllProvidersThrottled as exc:
        print(f"synthesis providers unavailable: {exc}", file=sys.stderr)
        return 75
    except LLMCallError as exc:
        print(f"synthesis model call failed closed: {exc}", file=sys.stderr)
        return 1
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

