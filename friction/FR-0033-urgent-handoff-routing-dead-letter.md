---
id: FR-0033
title: URGENT-prefixed handoffs silently dead-lettered by dispatch-handoffs.sh
Status: open
opened: 2026-04-20T16:49Z
source: synthesis cross-cutting-2026-04-20T15-28-05Z (Pattern #1)
---

# FR-0033 — URGENT-prefixed handoffs silently dead-lettered

## What happened

`dispatch-handoffs.sh:52–64` matches filenames against `KNOWN_SESSIONS` by checking if the stem starts with `"${sess}-"`. A file named `URGENT-atlas-carry-forward-*.md` starts with `URGENT-`, not `atlas-` — no session matches. Lines 80–84 then silently mark the file as "dispatched" and skip delivery:

```bash
if [[ -z "$target" ]]; then
  mark_dispatched "$f"
  continue
fi
```

No warning event emitted. The executive session's reentry procedure reads `supervisor/handoffs/INBOX/` (step 4) and `runtime/.handoff/general-*` (step 8) — neither path catches `runtime/.handoff/URGENT-*`.

## Impact

5 URGENT handoffs dead-lettered for 1–26h before tick re-routed them:
- `URGENT-context-repository-spec-honesty-block.md` — 26h
- `URGENT-skillfoundry-valuation-stale-close-carry-forward.md` — 14h
- `URGENT-skillfoundry-valuation-review-discipline-carry-forward.md` — 14h
- `URGENT-atlas-carry-forward-2026-04-20T14-21Z.md` — 2h
- `URGENT-command-metrics-producer-undocumented-2026-04-20T14-31Z.md` — 2h

The carry-forward escalation mechanism fires correctly; the delivery path is the broken link.

## Fix (requires attended session — scripts/lib/ is Tier C)

Two options (pick one):
1. `dispatch-handoffs.sh`: strip `URGENT-` prefix, extract the actual project token (e.g. `atlas` from `URGENT-atlas-*`), route to that session.
2. Alternatively: add `runtime/.handoff/URGENT-*` to the executive reentry step 8 glob so the attended session reads them directly.

Option 2 is simpler and avoids fragile prefix-stripping logic.

## Workaround applied this tick

Supervisor tick created properly-named copies in `runtime/.handoff/<project>-urgent-*.md` for all 5 dead-lettered files. Original URGENT files remain in place (already marked dispatched; harmless).
