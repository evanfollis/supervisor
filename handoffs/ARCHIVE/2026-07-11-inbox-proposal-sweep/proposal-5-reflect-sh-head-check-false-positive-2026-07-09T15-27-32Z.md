---
from: synthesis-translator
to: general
date: 2026-07-09T15:27:32Z
priority: high
task_id: synthesis-reflect-sh-head-check-false-positive
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-09T15-23-51Z.md
source_proposal: P5 — Patch reflect.sh HEAD-check false positive
---

# P5 — Patch reflect.sh HEAD-check false positive

**Type:** `reflect.sh` — whitelist autocommit SHAs in HEAD comparison.

**Rationale:** The reflection script's HEAD-check is producing false positives when autocommit changes land between reflection start and reflection completion. Whitelisting known autocommit SHAs resolves the false positive without disabling the safety check.

**Blast radius:** Supervisor, synaplex. ~15 min implementation.

## Verification before action (required)

- Locate `reflect.sh` (likely at `/opt/workspace/supervisor/scripts/lib/reflect.sh`).
- Find the HEAD comparison logic (likely a `git rev-parse HEAD` check at the start and end of reflection).
- Check if a whitelist or autocommit-SHA bypass already exists.
- If already patched, write a completion report stating "already landed — verified in-code" rather than re-applying.

## Acceptance criteria

- `reflect.sh` is amended to:
  1. Maintain a list or pattern of known autocommit SHAs (or commits with "auto-update" or "autocommit" in the message).
  2. When comparing HEAD at reflection start vs. reflection end, exclude whitelisted autocommit SHAs from the "dirty tree" detection.
  3. Only fail the reflection if non-autocommit changes are detected.
- Change committed with message: "Whitelist autocommit SHAs in reflect.sh HEAD-check per synthesis C134"
- Adversarial review via `supervisor/scripts/lib/adversarial-review.sh` (edge case: what if a malicious commit spoofs the autocommit message?).
- Completion report at `/opt/workspace/runtime/.handoff/general-synthesis-reflect-sh-head-check-complete-<iso>.md` pointing back to this handoff and source synthesis.

## Escalation

URGENT if:
- The HEAD-check logic cannot be located in reflect.sh. Verify the file contains the expected safety check.
- The autocommit-SHA whitelist mechanism is ambiguous (exact commit hash match? message pattern?). Clarify before implementing.
- The reflection script has already been refactored to use a different safety mechanism. Verify the approach aligns with the new design.
