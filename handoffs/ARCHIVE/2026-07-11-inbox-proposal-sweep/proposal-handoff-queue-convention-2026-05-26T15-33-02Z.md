---
from: synthesis-translator
to: general
date: 2026-05-26T15:33:02Z
priority: high
task_id: synthesis-proposal-2-handoff-queue
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-26T15-27-05Z.md
source_proposal: Proposal 2 — Unify handoff scanning with a single queue convention
---

# Unify handoff scanning with a single queue convention

## Proposal body (from synthesis)

**Type:** Shared primitive sketch — clarification in CLAUDE.md or a helper script.

**What:** Establish that `supervisor/handoffs/INBOX/` is the single authoritative queue for all URGENT escalations, including those from meta-reflections. `runtime/.handoff/` remains the surface for project-to-executive completion reports and delegations, but URGENTs always go to INBOX. The handoff-dispatcher should check for file deletion durability before re-firing.

```markdown
### Handoff queue convention
- `supervisor/handoffs/INBOX/` — authoritative queue for URGENTs and
  proposals. Scanned by tick and executive reentry.
- `runtime/.handoff/` — project-to-executive completion reports and
  delegations. Scanned by executive reentry only.
- URGENTs always go to INBOX, regardless of origin (tick, reflection,
  project session). A meta-reflection URGENT placed in `runtime/.handoff/`
  bypasses the tick's archival loop.
```

**Why:** Supervisor 14:25Z identified that the 02:24Z URGENT for test-artifact deletion was written to `runtime/.handoff/` rather than `INBOX/`, making it invisible to the tick's scan. The handoff-dispatcher re-fire (4+ invocations for one handoff, harness 14:21Z) suggests deletion timing issues. Both produce wasted cycles.

**Blast radius:** Reflection jobs and handoff-dispatcher (automatic). No project code impact.

## Verification before action (required)

- Check `/opt/workspace/CLAUDE.md` for existing "Handoff queue convention" or similar section.
- Search for the phrase "supervisor/handoffs/INBOX/" and "authoritative queue" together; if found in a subsection with clear guidance, may already be landed.
- Check `/opt/workspace/supervisor/scripts/lib/synthesize.sh` and `supervisor-tick.sh` for hardcoded queue paths; verify they match the convention below.

## Acceptance criteria

- Add a new subsection "Handoff queue convention" under "Session Awareness" or "Active Decisions > Architecture Governance" in `/opt/workspace/CLAUDE.md`.
- The rule clearly separates INBOX (URGENTs and proposals) from `runtime/.handoff/` (completion reports and delegations).
- Explicitly state that URGENTs always route to INBOX regardless of origin.
- Identify the handoff-dispatcher re-fire issue (`/opt/workspace/supervisor/scripts/lib/handoff-dispatcher.sh` or equivalent) and note that deletion-durability concerns should be reviewed (but final fix may be deferred to dispatcher maintainer).
- Commit with message: "Establish single-queue convention for URGENT escalations (Pattern 4, Cycle 60)"
- Reference the synthesis source and the queue-routing defects.
- No adversarial review required (policy clarification).
- Completion report to `/opt/workspace/runtime/.handoff/general-proposal-2-synthesis-handoff-queue-complete-2026-05-26T15-33-02Z.md`.

## Escalation

URGENT if:
- The queue paths are already segregated in the codebase differently than the proposal assumes.
- The tick and synthesis jobs are scanning queues in a way that contradicts the proposed convention.
