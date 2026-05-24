# URGENT — supervisor tick touched a Tier-C path

Tick at 2026-05-24T02-50-05Z violated its boundary. Investigate before the next tick.

Tier-C writes in supervisor repo:
  scripts/lib/.erofs-test-meta-reflection (matched scripts/lib/*, status=??)
  scripts/lib/TEST_WRITE_2951547 (matched scripts/lib/*, status=??)


Project HEAD changes:
  (none)

Pre-run supervisor HEAD: c060d7e713fb096ac698d82961f9ff73ed8fe65d
Post-run supervisor dirty tree:
```
    ?? handoffs/ARCHIVE/2026-05-24/session-summary-supervisor-2026-05-24T02-52-57Z.md
    ?? scripts/lib/.erofs-test-meta-reflection
    ?? scripts/lib/TEST_WRITE_2951547
```

Investigate: --disallowedTools may need tightening, OS-level sandbox may
have a gap, or a path was missed in the Tier-C glob list.
