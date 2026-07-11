---
from: synthesis-translator
to: general
date: 2026-05-23T03:28:48Z
priority: high
task_id: synthesis-erofs-probe-gate
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-23T03-23-38Z.md
source_proposal: Proposal 5 (NEW — enforcement gate) — Write-test verification before tick re-asserts EROFS
---

# Write-test verification before tick re-asserts EROFS

## Proposal body

**Type:** Enforcement gate (tick-layer).

**What:** Before any tick session can claim EROFS or "read-only filesystem" as a blocker, it must run `touch <target-dir>/.erofs-probe-$$` and report the exit code. If the touch succeeds, the tick is not permitted to assert EROFS. This is a `workspace.sh doctor` check candidate.

**Rationale:** Phase 3b exists because ticks can re-assert a constraint that reflection sessions have already disproved. A mandatory write test makes the assertion falsifiable at the point of claim, not only in the next reflection cycle.

**Blast radius:** Tick sessions only (automatic via tick prompt or `doctor` check). No effect on attended sessions.

**Sketch:**
```bash
# In supervisor-tick.sh or doctor.sh:
_erofs_probe() {
  local dir="$1" probe="$dir/.erofs-probe-$$"
  if touch "$probe" 2>/dev/null; then rm -f "$probe"; return 0; fi
  return 1
}
```

## Context

This cycle's pattern 1 (CRITICAL) documents a new failure mode: the tick layer filed FR-0046 claiming the reflection had "misidentified real EROFS," reasserting EROFS as a blocker. But the reflection had just re-run the write test and confirmed `exit 0`. The synthesis notes this as "Phase 3b: inversion of disproof" — the tick actively contradicts the diagnostic layer's correct findings.

This gate prevents that class of error by making the assertion falsifiable at claim time, not in hindsight.

## Verification before action (required)

- Read `supervisor-tick.sh` or `doctor.sh` to understand where EROFS assertions happen
- Check git history for FR-0046 and related EROFS discussions
- Verify the `_erofs_probe()` sketch compiles and doesn't have hidden assumptions about target directories

## Acceptance criteria

- `_erofs_probe()` function implemented in a shared library (e.g., `scripts/lib/common.sh` or inline in the relevant script)
- Before any tick session asserts "EROFS=true" or "filesystem is read-only," it must call `_erofs_probe <target-dir>`
- If probe returns 0 (write succeeded), the tick must either:
  - Not assert EROFS at all, or
  - Assert it with an explicit qualifier like "EROFS=claimed (touch probe succeeded; assertion deferred)"
- Change committed with clear message explaining the Phase 3b prevention
- Adversarial review via `supervisor/scripts/lib/adversarial-review.sh`
- Completion report at `runtime/.handoff/general-synthesis-erofs-probe-gate-complete-<iso>.md`

## Escalation

URGENT if:
- The tick layer does not have a clear single point where EROFS assertions happen (gate may need to be broader than expected)
- The doctor.sh or tick.sh scripts interact with multiple target directories; clarify whether the probe should fire for all of them or just specific ones
- The synthesis observation (Phase 3b) is already addressed by a more recent commit (check git log for EROFS-related changes since synthesis was generated)

