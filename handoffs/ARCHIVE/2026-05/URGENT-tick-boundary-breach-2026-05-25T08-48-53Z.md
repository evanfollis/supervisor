# URGENT — supervisor tick touched a Tier-C path

Tick at 2026-05-25T08-48-53Z violated its boundary. Investigate before the next tick.

Tier-C writes in supervisor repo:
  scripts/lib/.erofs-test-meta-reflection (matched scripts/lib/*, status=??)
  scripts/lib/TEST_WRITE_2951547 (matched scripts/lib/*, status=??)


Project HEAD changes:
  (none)

Pre-run supervisor HEAD: 1fc569097e3512daa5abadee50b555f22e385dde
Post-run supervisor dirty tree:
```
     M system/verified-state.md
    ?? handoffs/ARCHIVE/2026-05-25/session-summary-supervisor-2026-05-25T08-51-07Z.md
    ?? scripts/lib/.erofs-test-meta-reflection
    ?? scripts/lib/TEST_WRITE_2951547
```

Investigate: --disallowedTools may need tightening, OS-level sandbox may
have a gap, or a path was missed in the Tier-C glob list.
