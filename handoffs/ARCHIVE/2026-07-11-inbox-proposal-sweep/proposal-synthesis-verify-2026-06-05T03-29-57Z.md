---
from: synthesis-translator
to: general
date: 2026-06-05T03:29:57Z
priority: high
task_id: synthesis-verify-primary-check
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-05T03-26-55Z.md
source_proposal: P-synthesis-verify (NEW from cycle 19)
---

# P-synthesis-verify — Primary verification step in synthesis prompt

## Proposal body (from synthesis)

**Type:** Shared primitive update — `synthesize-prompt.md` or `synthesize.sh`.

**Sketch:** Add to synthesis prompt template:
```
Before asserting principal activity status, run:
  ls -lt /root/.claude/projects/-opt-workspace/*.jsonl | head -5
Cross-check any counter-derived claim against actual session artifacts.
Do not publish a principal-absence duration derived solely from arithmetic
on a prior synthesis counter.
```

**Blast radius:** Synthesis only (automatic). Prevents the counter-derived-claim failure class from recurring. Does not require principal authorization.

## Context

Cycle 78 published "Principal absence ~13.5 days" as a standing-recommendation table entry. This claim was derived from arithmetic on a stale counter, not from JSONL session inspection. Cycle 19 discovered the principal was present at 15:30Z Jun 4 — making the claim false by ~22 hours at time of publication.

The failure class: synthesis loop has no primary-verification step for factual claims it publishes. Counter-derived assertions flow into `LATEST_SYNTHESIS`, which is the escalation surface read by the principal and by future synthesis cycles. A false claim in `LATEST_SYNTHESIS` compounds: it becomes the baseline for the next counter increment.

## Verification before action (required)

- Check `supervisor/scripts/lib/synthesize-prompt.md` for any existing primary-verification gate. If present, verify it covers session JSONL inspection and counter-derived claim validation.
- Check recent synthesis files (`runtime/.meta/cross-cutting-*.md`) for any evidence this pattern has already been addressed.
- If either is true, write a completion report stating "already present in synthesize-prompt.md" rather than re-applying.

## Acceptance criteria

- The sketch text (or equivalent primary-verification logic) is added to `synthesize-prompt.md` before the "Questions for the human" section.
- The addition explicitly names the failure class it prevents (counter-derived false claims).
- Change committed with clear message explaining it prevents synthesis self-corruption.
- No adversarial review required (small prompt amendment, non-structural).
- Completion report at `runtime/.handoff/general-synthesis-verify-complete-<iso>.md` pointing back to this handoff and the source synthesis.

## Escalation

URGENT if:
- The proposal is based on stale state (the verification step already exists in a branch not visible in the current reading).
- The proposal conflicts with a more recent synthesis finding or ADR.

---

**Synthesis finding:** This is a new cross-cutting pattern from cycle 19, not an incremental counter. The failure class (derived-data treated as primary evidence) is the same structural class as the `sourceType` discrimination rule (ADR-0019) — a measurement system must not trust its own intermediate outputs as ground truth.
