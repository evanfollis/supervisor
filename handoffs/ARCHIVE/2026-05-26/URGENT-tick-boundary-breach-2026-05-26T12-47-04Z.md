# URGENT — supervisor tick touched a Tier-C path

Tick at 2026-05-26T12-47-04Z violated its boundary. Investigate before the next tick.

Tier-C writes in supervisor repo:
  scripts/lib/.erofs-test-meta-reflection (matched scripts/lib/*, status=??)
  scripts/lib/TEST_WRITE_2951547 (matched scripts/lib/*, status=??)


Project HEAD changes:
  (none)

Pre-run supervisor HEAD: 0b2f40b5a274969932bfe8fa6b061a3d3d98e41c
Post-run supervisor dirty tree:
```
    ?? handoffs/ARCHIVE/2026-05-26/session-summary-supervisor-2026-05-26T12-50-22Z.md
    ?? scripts/lib/.erofs-test-meta-reflection
    ?? scripts/lib/TEST_WRITE_2951547
```

Investigate: --disallowedTools may need tightening, OS-level sandbox may
have a gap, or a path was missed in the Tier-C glob list.
