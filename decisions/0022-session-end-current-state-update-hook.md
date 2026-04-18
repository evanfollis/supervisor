# ADR-0022: Session-end CURRENT_STATE update detection (M5 phase 1)

Date: 2026-04-18
Status: accepted

## Context

ADR-0021 (session-start context-repo read enforcement, M4) ships an
auto-injection hook for `context-always-load:` files. Its own §Known
Limitations KL2 names "stale-context amplification" as the primary risk:
a `CURRENT_STATE.md` that doesn't get updated at session end becomes
*more* trusted in every subsequent session than it would without the
hook — the hook launders stale state into confident context.

The context-repository pattern spec's M5 (session-end update enforced)
is the counter-mechanism. The spec explicitly defers full M5 enforcement
to a follow-on ADR because write-side enforcement couples to the
writer/retriever-separation proposal, whose adversarial review
(context-repository/docs/writer-retriever-separation-proposal.md §C1-C3)
flagged three unresolved concerns:

- **C1**: transcript-as-ground-truth over-trusts a lossy evidence source
- **C2**: sessions end before state settles (mid-exploration closure)
- **C3**: exception boundaries erode the single mutation path

Shipping a naive auto-writer today would instantiate those failure
modes. Shipping nothing leaves KL2 from ADR-0021 open indefinitely.

## Decision

Ship M5 as **phase 1: detect-and-report**, not auto-write.

A `SessionEnd` hook at `/root/.claude/hooks/session-end-current-state-check.sh`
fires once per session close. Its logic:

1. Read stdin for `cwd`, `session_id`, `transcript_path`.
2. No-op unless cwd has a `CLAUDE.md` with a `context-always-load:`
   block (this is the opt-in gate — ADR-0021 already requires this).
3. No-op unless cwd has a `CURRENT_STATE.md`.
4. No-op if transcript line count < 20 (short/exploratory sessions
   don't need a front-door update).
5. No-op if `CURRENT_STATE.md` mtime is within the last 24 hours
   (≈ was touched during this session).
6. Otherwise: emit a telemetry event
   (`event_type: session_end_without_current_state_update`,
   `sourceType: system`) and route a low-priority handoff to
   `/opt/workspace/runtime/.handoff/general-m5-current-state-untouched-<project>-<iso>.md`
   noting the signal, with a checklist for the next attended session
   to act on or dismiss.

The hook **does not**:
- Commit anything
- Modify `CURRENT_STATE.md` or any other file inside the cwd
- Block the session from ending

This is the minimum shape that closes KL2 without inheriting C1/C2/C3.

## Consequences

**Enables:**

- Stale CURRENT_STATE files become visible. If M4 ever auto-injects a
  stale file (despite the 7-day freshness gate in ADR-0021), the next
  session end creates a handoff pointing at the exact file + project.
- The "did the session actually settle?" question (C2) becomes an
  attended judgment instead of an automated commit decision. A human
  reads the handoff and decides whether the session's work warranted a
  CURRENT_STATE update.
- Telemetry accumulates a measurable signal ("how often do sessions end
  with unsettled CURRENT_STATE?") that informs the phase-2 design.

**Makes harder:**

- Low-signal handoffs will accumulate during read-only investigation
  sessions. Mitigation: the 20-line threshold filters the noisiest
  cases; tune `ACTIVITY_THRESHOLD` or `STALE_HOURS` if the noise/signal
  ratio is wrong.
- The next attended session has a new class of handoffs to triage.
  Each is cheap to dismiss but they are not self-resolving.

**Foreclosed:**

- "We'll get around to M5 later." The hook is live; the only remaining
  question is whether phase 2 (auto-writer) is worth building on top.

## Phase 2 (not this ADR)

Phase 2 is: a writer pass runs on the handoff signal, generates a
proposed CURRENT_STATE diff from transcript + git log + telemetry,
commits the diff to a `writer/<session-id>` branch (never main),
and routes a review handoff. Phase 2 requires:

1. Resolution of C1 (triangulate transcript claims against git diff +
   tool results before writing).
2. Resolution of C2 (explicit "session settled?" gate — agent-declared,
   heuristic on transcript tail, or time delay).
3. Resolution of C3 (emergency write escape hatch is high-friction and
   audit-loud, not a convenience).

Those resolutions live in a future writer/retriever-separation ADR.
Phase 2 explicitly does not ship here.

## Consequences for ADR-0021 KL2

KL2 (stale-context amplification under M4-without-M5) is reduced from
"known latent failure class" to "observable via hook signal + visible
freshness banner":

- A1 (freshness banner from ADR-0021): agent sees the staleness
  inline, weighted accordingly.
- A2 (this ADR): when a session ends without updating a stale file,
  a handoff is routed for human review.

KL2 is not eliminated — an agent could still skim the STALE banner and
act as if the file were fresh, and the handoff queue could accumulate
without attention. These are residual risks, not structural ones.

## Implementation (shipped)

- `/root/.claude/hooks/session-end-current-state-check.sh`
- `/root/.claude/settings.json` — `SessionEnd` hook registered.
- Smoke-tested against a synthetic cwd with 3-day-old CURRENT_STATE:
  handoff landed correctly, telemetry event appended.

## Alternatives considered

**Auto-commit to CURRENT_STATE.md directly.** Rejected — instantiates
C1/C2/C3 without mitigation. A confident-wrong auto-write is worse than
a stale-but-true manual one.

**Writer commits to a `writer/<session-id>` branch (phase 2 done now).**
Rejected as premature — the C1/C2/C3 mitigations aren't designed yet.
Shipping the branching infrastructure without the triangulation, settling,
and emergency-escape design would lock us into a shape we'd regret.

**Stop hook (per-turn) instead of SessionEnd (once per session).**
Rejected — `Stop` fires every agent turn, producing handoff spam. Full
session close is the correct granularity for "did this work settle?"

**Hard-block session end if CURRENT_STATE is stale.** Rejected —
`SessionEnd` blocking semantics aren't well-documented; even if they
worked, blocking would punish legitimate read-only sessions and could
be bypassed by tool timeout. Detect-and-report is the honest intensity.

## References

- ADR-0021 (this ADR's companion; M4 session-start read enforcement)
- `projects/context-repository/docs/agent-context-repo-pattern.md` §M5
- `projects/context-repository/docs/writer-retriever-separation-proposal.md` §C1-C3
- `/root/.claude/hooks/session-end-current-state-check.sh` (implementation)
