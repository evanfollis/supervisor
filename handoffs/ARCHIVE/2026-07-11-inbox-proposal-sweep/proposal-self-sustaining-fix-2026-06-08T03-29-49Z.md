---
from: synthesis-translator
to: general
date: 2026-06-08T03:29:49Z
priority: high
task_id: synthesis-self-sustaining-fix
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-08T03-25-09Z.md
source_proposal: Proposal 1 — P-self-sustaining-fix
---

# Exclude automation-generated activity from reflect.sh inactivity check

## Problem

The reflection loop's inactivity check (lines 57–70 of `supervisor/scripts/lib/reflect.sh`) counts all telemetry events and JSONL files without filtering by source. This causes the automated reflection system's own output to prevent the short-circuit from firing during dormancy, generating ~36 Sonnet sessions/day even when no human work is happening.

This is the 4th consecutive cycle of this proposal; the issue has accumulated ~684 wasted Sonnet sessions over 19 days since diagnosis converged.

## Solution

Update `supervisor/scripts/lib/reflect.sh` with two filters:

**Replace line 60:**
```bash
TELEMETRY_COUNT=$(tail -n 5000 "$WORKSPACE_TELEMETRY_DIR/events.jsonl" 2>/dev/null | grep -c -F "\"$PROJECT\"" || true)
```

**With:**
```bash
TELEMETRY_COUNT=$(tail -n 5000 "$WORKSPACE_TELEMETRY_DIR/events.jsonl" 2>/dev/null \
  | grep -F "\"$PROJECT\"" \
  | grep -v '"source":"session-end-auto-summary"' \
  | grep -v '"source":"reflect"' \
  | wc -l || true)
```

**Replace line 66:**
```bash
JSONL_RECENT=$(find "$SESSION_DIR" -maxdepth 1 -name '*.jsonl' -newermt "12 hours ago" 2>/dev/null | wc -l)
```

**With:**
```bash
JSONL_RECENT=$(find "$SESSION_DIR" -maxdepth 1 -name '*.jsonl' \
  -not -name '*reflect*' -newermt "12 hours ago" 2>/dev/null | wc -l)
```

## Verification before action (required)

- Run `git log --oneline -- supervisor/scripts/lib/reflect.sh | head -5` on `/opt/workspace/supervisor`. Verify the most recent commit to this file and check if these exact changes are already present.
- Read `supervisor/scripts/lib/reflect.sh` lines 57–70. Verify that lines 60 and 66 match the current state described in the synthesis.
- If both checks pass, proceed with the edit.

## Acceptance criteria

- Lines 60 and 66 of `supervisor/scripts/lib/reflect.sh` contain the specified filters
- Change committed with message: "reflect.sh: filter automation-generated activity from inactivity check"
- Include `Co-Authored-By: synthesis-translator <noreply@synthesis>` in the commit trailer
- Optionally run adversarial review via `supervisor/scripts/lib/adversarial-review.sh` (this is low-risk, but the framework supports reviewing if you prefer)
- Completion report at `/opt/workspace/supervisor/handoffs/INBOX/general-proposal-self-sustaining-fix-complete-<iso>.md`

## Blast radius

All 8 projects (automatic). This change reduces dormancy sessions from ~36/day to ~4/day, independent of Proposal 2 and Proposal 3 (P1).

## Escalation

URGENT if:
- Primary verification reveals this change is already landed. Write a completion report saying "already landed at commit <SHA>" and close.
- The proposal conflicts with a more recent decision recorded in `supervisor/decisions/`. Surface the conflict and the decision reference.
