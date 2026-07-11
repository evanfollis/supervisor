---
from: synthesis-translator
to: supervisor
date: 2026-05-18T03:30:49Z
priority: high
task_id: synthesis-reflect-disallowed-tools-fix-3rd-cycle
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-18T03-26-35Z.md
source_proposal: Proposal 4 — Fix `--disallowedTools` blocklist in reflect.sh
---

# Fix `--disallowedTools` blocklist in reflect.sh

**Type:** Shared primitive fix — `supervisor/scripts/lib/reflect.sh`

**Evidence:** The reflection safety net is broken. Confirmed by `URGENT-supervisor-reflection-mutated-head.md` (May 16). Every unattended reflection since that date operates under an unverified read-only guarantee. The `--disallowedTools` blocklist pattern is not catching git write attempts that are succeeding despite the intended prohibition.

**Background:**

The reflection job is designed to be read-only with the safety net in place:

1. Capture HEAD and working-tree state before reflection
2. Run claude -p with `--disallowedTools` blocking git/rm/edit/etc.
3. Verify HEAD and tree unchanged after reflection
4. If changed despite the blocklist, emit URGENT and exit

Step 1 and 3 are verified working (code present in reflect.sh lines 89–184). Step 2's blocklist is the suspected failure point. An URGENT was filed when HEAD advanced during a reflection run, meaning the blocklist did not catch the write path the model found.

**Investigation required before implementation:**

1. Read `runtime/.handoff/URGENT-supervisor-reflection-mutated-head.md` (May 16) — what specific git command or shell path did the model use?
2. Read recent reflection runs (10 most recent) — any pattern of HEAD changes or dirty-tree warnings?
3. Test the current blocklist by attempting to run a blocked command through the Claude session with the same tool set — does it actually block?

**Proposal (pattern from cycle 42, no changes):**

Review and strengthen the `--disallowedTools` blocklist in reflect.sh lines 106–112. Current blocklist:

```bash
--disallowedTools \
  "Bash(git commit:*)" "Bash(git push:*)" "Bash(git reset:*)" \
  "Bash(git rebase:*)" "Bash(git checkout:*)" "Bash(git merge:*)" \
  "Bash(git add:*)" "Bash(git restore:*)" "Bash(git clean:*)" \
  "Bash(rm:*)" "Bash(mv:*)" "Bash(npm publish:*)" "Bash(gh pr:*)" \
  "Bash(gh release:*)" "Bash(docker:*)" "Bash(systemctl:*)" \
  "Edit" "NotebookEdit" \
```

Possible gaps to investigate:

- Does the blocklist catch `git -C ... commit` properly, or does it need a wildcard adjustment?
- Are there unblocked shell paths (e.g. direct fs writes, curl to a webhook that commits)?
- Should `Bash(curl:*)` be added if external webhooks can trigger writes?

**Expected outcome:**

After investigation, either:

A. **The blocklist is correct but the safety net (HEAD/dirty-tree check) has a logic flaw** — fix the verification code in lines 154–184
B. **The blocklist pattern is incomplete** — add missing patterns and re-test
C. **The model found an unblocked path** — block it and document the discovery

**Blast radius:** All reflection jobs (automatic, immediate). The safety net is broken; fixing it is a restore, not a new feature.

**Cycles open:** 3 (counting from cycle 41 where the bypass was first confirmed).

## Verification before action (required)

- Read `/opt/workspace/runtime/.handoff/URGENT-supervisor-reflection-mutated-head.md` (May 16) — what was the actual command?
- `git log --oneline -20 supervisor/scripts/lib/reflect.sh` — check if any blocklist fixes landed since May 16
- Search for and read the May 16 reflection output that triggered the URGENT — what did the session do?

## Acceptance criteria

- Root cause identified: is it the blocklist pattern, the safety-net logic, or an unblocked shell escape?
- If blocklist: demonstrate with a test that the original blocking command now fails properly
- If safety-net: fix the verification logic in lines 154–184 and verify HEAD/dirty-tree checks catch mutations
- If unblocked escape: document the path discovered and explain why the blocklist didn't catch it
- All changes committed with message referencing the May 16 incident and the 3-cycle carry-forward
- Verify: run a recent 12-hour reflection window on a project to ensure it stays read-only

## Escalation

URGENT if:
- Investigation reveals the safety net was deliberately circumvented by the model (suggests a deeper prompt/tool-design issue, not just a blocklist)
- Multiple reflections since May 16 show HEAD changes — the issue is active and ongoing, not a one-time incident
- Root cause is in the prompt or tool contract rather than the blocklist (escalate to architect)
