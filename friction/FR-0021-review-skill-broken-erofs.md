---
type: friction
id: FR-0021
slug: review-skill-broken-erofs
date: 2026-04-17
severity: critical
status: open
---

# FR-0021: `/review` skill fails system-wide with EROFS (read-only filesystem)

## What happened

The atlas PM tick completion report (2026-04-17T01:47Z) reported:

```
/review skill failed: EROFS: read-only file system, open '/root/.claude.json'
```

This error occurs when the `/review` skill attempts to write to `/root/.claude.json` in a sandboxed execution context where `/root/` is mounted read-only.

The same failure has now affected:
- **atlas tick** (2026-04-17T01:47Z) — adversarial review of ingest.py 5076ba0 blocked
- Every tick session that attempts `/review` — all return the same EROFS error

## Why it matters

Cross-agent adversarial review is a mandatory gate in the supervisor charter:
> "Use `/review` after completing any significant feature, refactor, or architectural change."

Three ADRs (0015, 0016, 0017) have been accepted without a review artifact because this skill is broken. The atlas deduplication + telemetry changes (5076ba0, c1395bb) have been shipped without adversarial review for 4+ cycles.

The `/review` breakage is not a project-specific issue — it is a workspace-wide infrastructure failure that has been silently defeating the adversarial review gate for every session.

## Workaround (until fixed)

CLAUDE.md §Cross-agent review documents:
> `codex exec --skip-git-repo-check --sandbox read-only "<review prompt>"`

This path may work if `/root/.claude.json` is not required. The attended session should test this immediately.

## Rule signal

A systemic tooling failure that defeats a mandatory governance gate must produce an URGENT handoff immediately — not a "review owed" note in a completion report. If the `/review` skill fails, the session must write `runtime/.handoff/URGENT-review-blocked-<project>-<ts>.md` before marking the task complete.

**Status**: Open — attended session must (a) diagnose the EROFS cause, (b) test the `codex exec` fallback, (c) clear the 3-ADR review debt once a working path is confirmed.
