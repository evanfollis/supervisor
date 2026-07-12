#!/usr/bin/env python3
"""prompteval `command` executor adapter for synthesis-translator-prompt.md.

Mirrors the REAL runtime path (scripts/lib/synthesis-translator.sh) as
closely as eval isolation allows: same template substitution, same model,
same --permission-mode acceptEdits, same --disallowedTools set — but
HANDOFF_DIR / INBOX_DIR / the synthesis file live in a throwaway sandbox,
so eval runs can never write into the live queues.

stdin:  {"prompt_text": <template>, "model": "...", "params": {...},
         "input": {"synthesis": "<file content>",
                   "iso_now": "...", "iso_filename": "..."}}
stdout: the translator's report, then a machine-gradable footer:
          ===EMITTED:<count>===
          ===FILE:<relative path>===
          <file content>
        (one FILE block per handoff the translator wrote)
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

DISALLOWED = [
    "Bash(git commit:*)", "Bash(git push:*)", "Bash(git reset:*)",
    "Bash(git rebase:*)", "Bash(git checkout:*)", "Bash(git merge:*)",
    "Bash(git add:*)", "Bash(git restore:*)", "Bash(git clean:*)",
    "Bash(rm:*)", "Bash(mv:*)", "Bash(cp:*)", "Bash(systemctl:*)",
    "Bash(docker:*)", "Bash(tmux send-keys:*)",
    "Edit", "NotebookEdit",
]


def main() -> int:
    payload = json.load(sys.stdin)
    template = payload["prompt_text"]
    model = payload.get("model") or "claude-haiku-4-5-20251001"
    case_input = payload["input"]

    with tempfile.TemporaryDirectory(prefix="translator-eval-") as tmp:
        sandbox = Path(tmp)
        synthesis_file = sandbox / "synthesis.md"
        handoff_dir = sandbox / "handoff"
        inbox_dir = sandbox / "inbox"
        handoff_dir.mkdir()
        inbox_dir.mkdir()
        synthesis_file.write_text(case_input["synthesis"], encoding="utf-8")

        prompt = (
            template
            .replace("{{SYNTHESIS_FILE}}", str(synthesis_file))
            .replace("{{ISO_NOW}}", case_input.get("iso_now", "2026-07-12T00:00:00Z"))
            .replace("{{ISO_FILENAME}}", case_input.get("iso_filename", "2026-07-12T00-00-00Z"))
            .replace("{{HANDOFF_DIR}}", str(handoff_dir))
            .replace("{{INBOX_DIR}}", str(inbox_dir))
        )

        cmd = ["claude", "-p", prompt, "--model", model,
               "--permission-mode", "acceptEdits", "--disallowedTools"] + DISALLOWED
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600,
                              cwd=sandbox, check=False)
        if proc.returncode != 0:
            sys.stderr.write(proc.stderr[-500:])
            return proc.returncode

        emitted = sorted(p for p in list(handoff_dir.rglob("*")) + list(inbox_dir.rglob("*"))
                         if p.is_file())
        out = [proc.stdout.strip(), f"===EMITTED:{len(emitted)}==="]
        for path in emitted:
            out.append(f"===FILE:{path.relative_to(sandbox)}===")
            out.append(path.read_text(encoding="utf-8"))
        print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
