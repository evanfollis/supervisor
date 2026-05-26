# URGENT — supervisor tick touched a Tier-C path

Tick at 2026-05-26T02-48-00Z violated its boundary. Investigate before the next tick.

Tier-C writes in supervisor repo:
  scripts/lib/.erofs-test-meta-reflection (matched scripts/lib/*, status=??)
  scripts/lib/TEST_WRITE_2951547 (matched scripts/lib/*, status=??)


Project HEAD changes:
  (none)

Pre-run supervisor HEAD: ccbce160dc019af10b0de9730f5836d2951c1187
Post-run supervisor dirty tree:
```
    ?? handoffs/ARCHIVE/2026-05-26/session-summary-supervisor-2026-05-26T02-50-23Z.md
    ?? scripts/lib/.erofs-test-meta-reflection
    ?? scripts/lib/TEST_WRITE_2951547
```

Investigate: --disallowedTools may need tightening, OS-level sandbox may
have a gap, or a path was missed in the Tier-C glob list.
