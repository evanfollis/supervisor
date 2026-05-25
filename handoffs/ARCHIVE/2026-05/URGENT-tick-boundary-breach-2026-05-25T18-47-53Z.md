# URGENT — supervisor tick touched a Tier-C path

Tick at 2026-05-25T18-47-53Z violated its boundary. Investigate before the next tick.

Tier-C writes in supervisor repo:
  scripts/lib/.erofs-test-meta-reflection (matched scripts/lib/*, status=??)
  scripts/lib/TEST_WRITE_2951547 (matched scripts/lib/*, status=??)


Project HEAD changes:
  (none)

Pre-run supervisor HEAD: 6b0596429380cc296585076f98412b7447492ca9
Post-run supervisor dirty tree:
```
     M system/verified-state.md
    ?? handoffs/ARCHIVE/2026-05-25/session-summary-supervisor-2026-05-25T18-49-33Z.md
    ?? scripts/lib/.erofs-test-meta-reflection
    ?? scripts/lib/TEST_WRITE_2951547
```

Investigate: --disallowedTools may need tightening, OS-level sandbox may
have a gap, or a path was missed in the Tier-C glob list.
