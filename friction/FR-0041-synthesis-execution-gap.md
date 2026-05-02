---
name: FR-0041-synthesis-execution-gap
description: 11+ consecutive synthesis cycles with 0/40 proposals implemented — handoff consumption marks .done without executing the work
type: friction
status: Open
created: 2026-05-02
---

# FR-0041 — Synthesis execution gap (11 cycles, 0 proposals landed)

## What happened

The workspace synthesis loop has produced 40+ unique proposals across 11 consecutive 12h synthesis windows (2026-04-26 through 2026-05-02). Zero have been implemented. INBOX grew from ~15 items to 45+.

The confirmed mechanism (cross-cutting synthesis 2026-05-02T15:27Z, Pattern 1): handoffs are being marked `.done` by tick sessions that cannot actually execute the requested changes. The tick reads the handoff, acknowledges it, marks it `.done` — but the changes are Tier B/C and require either operator access (`scripts/lib/`) or principal judgment (charter amendments). The `.done` mark has lost its semantic meaning.

## Failure class

Three dispatch paths exist:
- (a) Attended principal sessions — not active in the last 11 synthesis windows
- (b) Autonomous tick sessions — limited to Tier-A/B, cannot edit shared infrastructure
- (c) Handoff-to-general-session pipeline — marks `.done` without implementing (confirmed)

The workspace has no working path from "synthesis proposal" to "implemented change" when the principal is absent. The synthesis loop is accumulating high-fidelity diagnosis at ~$2–4/cycle with zero execution output.

## Status: Open

Requires one of:
1. Principal-attended triage session (bulk disposition or implement top proposals)
2. Expanded tick authority for Tier-B-auto changes (Proposal 5 from synthesis)
3. A dedicated "infrastructure executor" session that can edit `scripts/lib/` under controlled conditions

## Systemic fix needed

Synthesis Proposal 5 (Tier-B-auto classification): changes to workspace infrastructure that have been proposed in 2+ cycles, are additive, and require no principal decision should be implementable by the general session's tick without attended confirmation.
