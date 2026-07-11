---
from: synthesis-translator
to: general
date: 2026-05-17T15:33:32Z
priority: high
task_id: synthesis-dispatch-obligation-gate
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-17T15-27-50Z.md
source_proposal: Proposal 4 — Mechanize dispatch obligation with auto-deferral
---

# Mechanize dispatch obligation with auto-deferral

## Proposal

Auto-deferral record when synthesis detects an expired dispatch obligation with no corresponding dispatch or deferral file. Prevents silent obligation breaches.

**Type:** Shared primitive change — `synthesize.sh`.
**Blast radius:** Synthesis job only (automatic).
**Cycles carried forward:** 3.

## Rationale

Per the CLAUDE.md executive charter:

> **Dispatch obligation.** When a synthesis proposal lands in `runtime/.meta/cross-cutting-*.md`, the executive must dispatch a delegated project session within 24h — via `runtime/.handoff/<project>-*.md` handoff — or record an explicit deferral reason in `supervisor/decisions/` or `runtime/.meta/`. Synthesis proposals sitting >24h without dispatched action or recorded deferral escalate as FR-class structural issues.

This gate is currently honor-system. Synthesis detects when an obligation is expired (proposal >24h without dispatch or deferral) but does not automatically create a deferral record or escalate.

**Current impact:** "Context-repo Option B dispatch" item 12 in the standing recommendations has expired ~82h with no dispatch, deferral, or escalation. The synthesis can detect this but has no mechanism to act.

## Verification before action (required)

- Read `supervisor/scripts/lib/synthesize.sh` and identify where it emits synthesis proposals to `/opt/workspace/runtime/.meta/`.
- Check `runtime/.handoff/` for all active proposals and note how long each has been sitting without corresponding dispatch or deferral.
- Verify that no auto-deferral or escalation mechanism exists yet (check synthesize.sh for deferral-record emission or expiry-check logic).
- Review the standing recommendations table in the latest synthesis — item 12 (Context-repo Option B dispatch, ~82h expired) is the canonical example.

## Acceptance criteria

- `synthesize.sh` is updated to read recent synthesis files and check for proposals without corresponding dispatch or deferral after 24h.
- For each expired proposal, an auto-deferral record is created at `runtime/.meta/auto-deferral-<proposal-id>-<iso>.md` stating the reason (elapsed time, no dispatch, no explicit deferral).
- An escalation event is emitted (if synthesis job emits events) or an URGENT handoff created noting the expired obligation.
- The synthesis report itself notes which obligations were auto-deferred and why.
- Changes committed with message explaining the dispatch-obligation gate.
- Completion report at `runtime/.handoff/general-supervisor-proposal-dispatch-gate-complete-<iso>.md` pointing to this handoff and the synthesis source.

## Escalation

URGENT if:
- The dispatch obligation itself (the 24h requirement) is under review or contested by recent ADR changes.
- Auto-deferral records would conflict with explicit user deferrals already recorded manually.
- Synthesis job does not have read access to `runtime/.handoff/` or `decisions/` to verify dispatch/deferral state.
