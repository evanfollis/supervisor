# URGENT — supervisor tick touched a Tier-C path

Tick at 2026-05-26T06-49-03Z violated its boundary. Investigate before the next tick.

Tier-C writes in supervisor repo:
  scripts/lib/.erofs-test-meta-reflection (matched scripts/lib/*, status=??)
  scripts/lib/TEST_WRITE_2951547 (matched scripts/lib/*, status=??)


Project HEAD changes:
  (none)

Pre-run supervisor HEAD: b87c92e6771ab5f63b64d6f0bc0433d90a0a74a2
Post-run supervisor dirty tree:
```
    ?? handoffs/ARCHIVE/2026-05-26/session-summary-supervisor-2026-05-26T06-52-09Z.md
    ?? scripts/lib/.erofs-test-meta-reflection
    ?? scripts/lib/TEST_WRITE_2951547
```

Investigate: --disallowedTools may need tightening, OS-level sandbox may
have a gap, or a path was missed in the Tier-C glob list.
