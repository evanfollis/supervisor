# URGENT — supervisor tick touched a Tier-C path

Tick at 2026-05-24T18-48-49Z violated its boundary. Investigate before the next tick.

Tier-C writes in supervisor repo:
  scripts/lib/.erofs-test-meta-reflection (matched scripts/lib/*, status=??)
  scripts/lib/TEST_WRITE_2951547 (matched scripts/lib/*, status=??)


Project HEAD changes:
  (none)

Pre-run supervisor HEAD: b2a2cd644ade085deb151e2946bc09b7af1598d8
Post-run supervisor dirty tree:
```
     M system/verified-state.md
    ?? handoffs/ARCHIVE/2026-05-24/session-summary-supervisor-2026-05-24T18-52-23Z.md
    ?? scripts/lib/.erofs-test-meta-reflection
    ?? scripts/lib/TEST_WRITE_2951547
```

Investigate: --disallowedTools may need tightening, OS-level sandbox may
have a gap, or a path was missed in the Tier-C glob list.
