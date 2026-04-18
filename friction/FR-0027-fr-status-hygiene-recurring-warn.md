# FR-0027 — FR Status hygiene has been a recurring doctor WARN for 3+ cycles

Status: resolved
Detected: 2026-04-18T00:47Z
Source: workspace doctor WARN; also noted in tick 2026-04-17T22:48Z, tick 2026-04-17T18:48Z

## What happened

`workspace.sh doctor` reports 7 FR files missing a `Status:` line in every tick.
The friction/README.md requires every `FR-NNNN-*.md` to carry
`Status: open|mitigated|resolved|promoted-to-<ref>`. The 7 affected files:

- FR-0008-workspace-doctor-broken.md (RESOLVED in commit 6c91398)
- FR-0009-maintenance-window-missed.md (likely RESOLVED — patch applied 2026-04-15)
- FR-0010-aged-general-handoffs-unprocessed.md
- FR-0021-review-skill-broken-erofs.md (open — workaround in place, root cause not fixed)
- FR-0022-executive-event-claimed-file-not-written.md
- FR-0023-sourcetype-mandate-not-applied-to-pre-mandate-services.md
- FR-0024-urgent-archived-without-active-issues-entry.md

No tick has fixed this because ticks are instructed to write **new** friction records,
not edit existing ones (Tier A = new records only). Editing existing friction records
to add a missing Status line is arguably maintenance, but no attended session picked it up.

## Failure class

Operational hygiene debt that accumulates in unattended mode because:
- Ticks catch it via doctor but cannot fix it (Tier A = new only).
- Attended sessions see the WARN but treat it as low priority vs. higher-leverage items.
- No gate or escalation forces it into the attended queue until it becomes a recurring WARN.

## Proposed fix

Attended session: open the 7 files, add the correct `Status:` line to each,
and commit. This is a 5-minute maintenance pass. FR-0008 and FR-0009 are
likely RESOLVED; the others need a quick triage before setting status.

Alternatively: add a `make fr-hygiene` or `scripts/lib/fr-hygiene.sh` that
auto-detects missing Status lines and prints the right one based on context
(commits that reference the FR number, active-issues entries, etc.). That
converts this from a recurring human task into an automated gate.
