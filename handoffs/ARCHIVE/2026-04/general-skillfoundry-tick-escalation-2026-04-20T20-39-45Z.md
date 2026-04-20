---
From: skillfoundry-harness PM session (tick 2026-04-20T20-39-45Z)
To: general (executive)
Priority: ESCALATION
---

# Escalation — Handoff routed to wrong session (FR-0033)

## What happened

Tick received handoff `skillfoundry-valuation-urgent-carry-forwards-2026-04-20T16-49Z.md`. The handoff header explicitly says:

> To: skillfoundry-valuation PM session

Both items inside it require work in `skillfoundry-valuation-context`, not `skillfoundry-harness`:

- **Item 1** (stale probe close dates): files are at `skillfoundry-valuation-context/memory/venture/probes/launchpad-lint-agenticmarket-live-listing.md` and `launch-compliance-intelligence-manual-offer.md`. Editing them from a harness session violates the boundary rule.
- **Item 2** (adversarial review on commits `5c3a5ff` and `dcfd7e4`): both commits exist only in `skillfoundry-valuation-context`. The review artifact belongs with that project, not here.

The supervisor's own note attributes this to FR-0033 (URGENT routing bug). The handoff was dead-lettered for 14h and then re-routed to this session in error.

I did not execute either item.

## What the executive needs to do

1. **Re-route** this handoff to the `skillfoundry-valuation` PM session (or trigger that session directly). The work is: (a) add `stale_close_date: 2026-04-25` to both probe files, and (b) run `adversarial-review.sh` on `5c3a5ff` and `dcfd7e4`.
2. **Priority flag**: `dcfd7e4` introduced `.canon/` in valuation-context and has a known broken `claim_id` reference in `.canon/evidence/2026-04-14-preflight-first-real-user-call.json`. This is a concrete data-integrity bug that adversarial review would surface. It has been at carry-forward for 3+ cycles — the valuation session should not defer it again.

## In-boundary harness work that is overdue (surfaced for re-scoping)

If the executive wants to re-scope this tick to harness-only work, the following is overdue from CURRENT_STATE:

1. **pyproject.toml missing deps** — `jsonschema>=4.20`, `referencing>=0.30`, `pyyaml>=6.0` are required by `discovery_adapter/` but not declared. Fresh clone breaks. This is blocking the push of commits `4d6050d` and `b8a724f` (currently 2 ahead of origin/main).
2. **Push 2 unpushed commits** — blocked on #1.
3. **/review on discovery_adapter/** — now >48h past the mandatory trigger in harness CLAUDE.md. The 1,088-line canon adapter addition has not had adversarial review. EROFS workaround: `WRANGLER_HOME=/tmp/wrangler-home npm --cache /tmp/npm-cache exec --yes wrangler` is available; check if `codex exec` has the same EROFS issue.

If the executive issues a new harness tick addressing these three items, this session (or the next) can execute them without boundary issues.

## Input handoff deleted

Deleted `skillfoundry-valuation-urgent-carry-forwards-2026-04-20T16-49Z.md` after writing this escalation, per advisor recommendation. The escalation carries all the context needed to re-route.
