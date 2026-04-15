# FR-0004: Near-miss executing live migration without impact check

Captured: 2026-04-15
Source: session (ADR-0012 drafting)
Status: averted this time, structural gap remains

## What happened

While drafting ADR-0012 (relocate `supervisor-events.jsonl` from repo
to runtime), I started to execute the file move in the same breath as
writing the decision. Mid-step I remembered that
`scripts/slack/notifier.py` is running on a 60-second timer and reads
from the old path. A path swap without a coordinated script update
would have broken the live notifier and lost events inside its dedupe
window.

I caught it, retreated to "accepted decision, migration queued," and
left ADR-0012 with the execution explicitly deferred.

## Why it matters

This is the shape of mistake that does real damage:
- The action feels small (one `mv`).
- The decision context is still fresh (I just wrote the reasoning).
- The automation touching the file is invisible from the ADR file.

If the principal had handed me the same ADR and said "ship it," I
might have shipped it and broken the notifier mid-cycle. The failure
mode is "supervisor silently breaks a live service it was supposed to
be governing."

## Root cause / failure class

**No pre-execution impact check for paths touched by live automation.**
The workspace has systemd timers and scripts reading/writing specific
files on schedules; nothing cross-references proposed edits against
that inventory. The human has to remember which paths are live.

## Proposed fix

1. **Live-path registry.** A machine-readable file listing paths that
   live services touch (`scripts/lib/live-paths.json` or similar).
   Entries record the path, the service that reads/writes it, the
   cadence, and a short "impact of outage" note.
2. **Pre-execution check.** Before moving or deleting a path, grep
   the live-path registry. If matched, require the plan to name the
   coordinated update and the timer stop/start sequence.
3. **Workspace.sh doctor**: include a "live-paths consistency" audit
   that flags registry entries pointing at nonexistent files.

## References

- `decisions/0012-runtime-vs-repo-state-location.md` — the ADR whose
  execution is deferred because of this
- `scripts/slack/notifier.py` — reads `events/supervisor-events.jsonl`
- `systemd/workspace-slack-notifier.timer` — 60s cadence
