# URGENT — supervisor tick touched a Tier-C path

Tick at 2026-05-25T20-47-40Z violated its boundary. Investigate before the next tick.

Tier-C writes in supervisor repo:
  scripts/lib/.erofs-test-meta-reflection (matched scripts/lib/*, status=??)
  scripts/lib/TEST_WRITE_2951547 (matched scripts/lib/*, status=??)


Project HEAD changes:
  (none)

Pre-run supervisor HEAD: 0d854eb61a35d8c0036aa3a541829a974c35d26e
Post-run supervisor dirty tree:
```
     M system/active-issues.md
     M system/verified-state.md
    ?? handoffs/ARCHIVE/2026-05-25/session-summary-supervisor-2026-05-25T20-49-16Z.md
    ?? handoffs/ARCHIVE/2026-05/URGENT-tick-boundary-breach-2026-05-25T18-47-53Z.md
    ?? scripts/lib/.erofs-test-meta-reflection
    ?? scripts/lib/TEST_WRITE_2951547
```

Investigate: --disallowedTools may need tightening, OS-level sandbox may
have a gap, or a path was missed in the Tier-C glob list.
