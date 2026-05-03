---
from: synthesis-translator
to: general
date: 2026-04-30T03:35:43Z
priority: high
task_id: synthesis-translator-dedup-gate
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-04-30T03-26-25Z.md
source_proposal: Proposal 1 — Shared primitive — synthesis-translator dedup gate
---

# Synthesis-translator dedup gate

## Problem

The synthesis-translator creates INBOX proposals without checking for semantic duplicates. The iterate-patch-freeze proposal now has **4 copies** in INBOX (created across 3 days). The dedup logic (reason-hash, FR-0043) only applies to URGENTs, not regular proposals. Each synthesis cycle that re-recommends the same change creates a new file, degrading INBOX signal quality.

## Solution

Add a dedup check to `supervisor/scripts/lib/synthesis-translator.sh` before writing a new proposal to INBOX.

**Code sketch:**

```bash
# Before writing a new proposal to INBOX:
proposal_key=$(echo "$proposal_title" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | cut -c1-40)
existing=$(ls "$INBOX_DIR"/proposal-*"$proposal_key"* 2>/dev/null | head -1)
if [[ -n "$existing" ]]; then
  echo "synthesis-translator: skipping duplicate proposal (existing: $existing)" >&2
  continue
fi
```

## Blast radius

- Supervisor project only (`supervisor/scripts/lib/synthesis-translator.sh`)
- Automatic — runs after every synthesis
- Does not affect project repos
- Prevents queue noise growth without blocking new proposals
- Would have prevented 5 of the 22 current INBOX items from being created

## Verification before action (required)

- Check if dedup logic already exists in `supervisor/scripts/lib/synthesis-translator.sh` — search for "duplicate" or "existing" near proposal-write code
- If the check exists and is functional, write a completion report stating "already implemented at <line>" rather than re-applying
- If this fix is already landed, verify the INBOX contains no duplicates of the iterate-patch-freeze proposal — if duplicates still exist, the gate is non-functional and requires debugging

## Acceptance criteria

- The dedup check is added to synthesis-translator.sh before proposal write
- The check derives a stable slug from the proposal title and searches for existing files matching that pattern
- Change committed with clear message (e.g., "synthesis-translator: dedup regular proposals by title slug")
- Verify on next synthesis run that no duplicate proposals are created for the iterate-patch-freeze or other recurring recommendations
- Completion report at `/opt/workspace/supervisor/handoffs/INBOX/general-synthesis-dedup-gate-complete-<iso>.md` pointing back to this handoff

## Note

This is the highest-leverage proposal in this synthesis window. When this lands, it immediately stops the noise accumulation rate and improves INBOX signal quality for all downstream triage.
