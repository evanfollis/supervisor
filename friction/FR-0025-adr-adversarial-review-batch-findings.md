# FR-0025: ADR adversarial-review batch surfaced real structural gaps in 0015/0016/0017

Captured: 2026-04-17
Source: supervisor/.reviews/adr-review-001{5,6,7}-2026-04-17T14-55Z.md
Status: open

## What happened

The executive session ran `adversarial-review.sh` against ADR-0015 (executive/supervisor/operator split), ADR-0016 (per-project execution tick), and ADR-0017 (radical truth) for the first time. All three reviews returned substantive critiques — not style notes, actual design holes. The full reviews live at `supervisor/.reviews/`; summary of the structural gaps surfaced:

**ADR-0015 — attestation ≠ enforcement.** The role split (executive / supervisor / operator) is enforced by honest self-classification at session start, but nothing prevents the top-level session from acting as though it has full authority after the check. The executive and supervisor postures share the same persistent session — under pressure, the distinction collapses back into one surface. No protocol for mid-session re-attestation if capabilities drift.

**ADR-0016 — no claim/ack/idempotency on handoff execution.** The tick grabs "the oldest pending handoff" and runs it, but the ADR does not specify when the handoff is atomically marked in-progress, retired, or recognized as already partially executed after a crash, push rejection, or model timeout. This failure mode produces duplicate execution, conflicting commits, or infinite-retry on a poisoned handoff. Additionally: commit-and-push happens before executive review, so "review later" is de facto approval and the executive stops being a gate.

**ADR-0017 — formatting is not verification.** The Evidence/Uncertainty/Pushback section requirements are presence-checks; they cannot distinguish real verification from schema-gaming. The likely equilibrium is low-grade laundering: Evidence that is real but non-dispositive, Uncertainty phrased generically, Pushback omitted by reframing ambiguity as handled. And `CURRENT_STATE.md` — injected into every tick prompt — is at risk of becoming an unofficial truth source that outranks primary evidence because it's the fastest thing to trust.

## Why it matters

These are not theoretical objections. Each one is a plausible operational failure class:
- Exec/supervisor boundary collapse → governance-vs-execution separation becomes semantic.
- Handoff non-atomicity → duplicate writes, lost state after crashes, poisoned handoffs cycling.
- Schema-gaming on radical truth → the whole self-assessment layer produces better-looking falsehoods.

All three ADRs are already in production use. The code and prompts built on them are accumulating a structural debt that each review cycle made more expensive to pay down.

## Root cause / failure class

Adversarial review was not run at acceptance time because `/review` was EROFS-blocked and the codex fallback (`adversarial-review.sh`) landed only this window. The ADRs accumulated in a state of "accepted without adversarial pressure" for 5 / 3 / 2 cycles respectively. The batch exercise proved the capability gap was the bottleneck — once the tool worked, the reviews produced real signal immediately.

## Proposed fix

Three follow-up work items, each tied to a specific review critique:

1. **ADR-0019 (or amendment to ADR-0016): handoff claim/ack/idempotency protocol.** Atomic `INBOX → IN_PROGRESS → DONE/FAILED` state transitions via rename; crash-recovery rule (any `IN_PROGRESS` at startup is inspected, not retried blind); idempotency key on the handoff itself so a re-run detects "already applied" without re-writing.
2. **ADR-0020 (or amendment to ADR-0015): mid-session capability re-attestation.** Periodic or event-triggered re-check when a host-control action is attempted; demotion of posture if capability is lost mid-session; explicit rule for partial-operator scenarios.
3. **ADR-0021 (or amendment to ADR-0017): verification layer on top of radical-truth format.** External pass that reads completion reports and checks them against git diffs / telemetry. The ADR already flagged this as "worth pursuing as follow-on, not blocking" — the batch review confirms it should be blocking. Alternatively: rejection-criteria for low-quality Evidence/Uncertainty/Pushback content (not just presence).

## References

- `/opt/workspace/supervisor/.reviews/adr-review-0015-2026-04-17T14-55Z.md`
- `/opt/workspace/supervisor/.reviews/adr-review-0016-2026-04-17T14-55Z.md`
- `/opt/workspace/supervisor/.reviews/adr-review-0017-2026-04-17T14-55Z.md`
- ADR-0018 (notify-after-action default) — authorized the executive to batch these without permission
- FR-0021 (review skill broken EROFS) — the blocker this resolved
