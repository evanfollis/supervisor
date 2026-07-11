---
from: synthesis-translator
to: general
date: 2026-05-26T15:33:02Z
priority: high
task_id: synthesis-proposal-1-auth-gate-banner
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-05-26T15-27-05Z.md
source_proposal: Proposal 1 — Authorization-gate banner requirement for conditional documents
---

# Authorization-gate banner requirement for conditional documents

## Proposal body (from synthesis)

**Type:** CLAUDE.md amendment — new rule under "Active Decisions > Code Philosophy" or a skillfoundry project-level convention with workspace endorsement.

**What:** Any document that describes work contingent on authorization (probe plans, outreach campaigns, external commitments) must have an authorization-state banner as the first content block, before any milestone table or schedule. Format: `> **AUTHORIZATION:** [Not authorized | Authorized YYYY-MM-DD | Closed]`. Reflection agents must check this banner before treating schedule content as describing in-flight work.

```markdown
### Authorization-state banners on conditional documents
Documents describing work contingent on principal authorization (probes,
outreach campaigns, external commitments) must have an authorization-state
banner as the first content block, before any milestone table or schedule.
Reflection agents must check this banner before treating schedule content
as describing in-flight work.
```

**Why:** The recommerce false alarm consumed 4 reflection cycles and a synthesis question slot. Commit `0d4b237` fixes the specific instance; this rule prevents the class. Any skillfoundry candidate doc, atlas strategy doc, or workspace proposal with a schedule but no authorization state has the same structural risk.

**Blast radius:** All projects with conditional documents (opt-in convention; automatic for reflection interpretation). Skillfoundry is the primary consumer.

## Verification before action (required)

- Check `/opt/workspace/CLAUDE.md` for existing authorization-state banner rule.
- Search for "AUTHORIZATION:" in the file; if found and matches the proposal content, the change is already landed.
- If not found, proceed with the amendment.

## Acceptance criteria

- Add the new subsection under "Active Decisions > Code Philosophy" in `/opt/workspace/CLAUDE.md`.
- The rule clearly names the format (`> **AUTHORIZATION:** ...`) and the placement requirement (first content block, before schedules).
- Commit with message: "Add authorization-state banner requirement for conditional documents (Pattern 2, Cycle 60)"
- Reference the synthesis source in the commit message.
- No adversarial review required (policy addition, established pattern from `0d4b237`).
- Completion report to `/opt/workspace/runtime/.handoff/general-proposal-1-synthesis-auth-gate-complete-2026-05-26T15-33-02Z.md`.

## Escalation

URGENT if:
- The synthesis was based on stale state (commit `0d4b237` was a different fix than described).
- A conflicting authorization-gate rule already exists elsewhere in the workspace charter.
