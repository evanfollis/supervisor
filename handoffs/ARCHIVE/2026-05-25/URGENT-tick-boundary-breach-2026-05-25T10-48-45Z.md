# URGENT — supervisor tick touched a Tier-C path

Tick at 2026-05-25T10-48-45Z violated its boundary. Investigate before the next tick.

Tier-C writes in supervisor repo:
  scripts/lib/.erofs-test-meta-reflection (matched scripts/lib/*, status=??)
  scripts/lib/TEST_WRITE_2951547 (matched scripts/lib/*, status=??)


Project HEAD changes:
  (none)

Pre-run supervisor HEAD: d403bea780a533d9aa8d87f15d90e1338a1a4c24
Post-run supervisor dirty tree:
```
     M system/verified-state.md
    ?? handoffs/ARCHIVE/2026-05-25/session-summary-supervisor-2026-05-25T10-50-31Z.md
    ?? handoffs/ARCHIVE/2026-05/URGENT-tick-boundary-breach-2026-05-25T08-48-53Z.md
    ?? scripts/lib/.erofs-test-meta-reflection
    ?? scripts/lib/TEST_WRITE_2951547
```

Investigate: --disallowedTools may need tightening, OS-level sandbox may
have a gap, or a path was missed in the Tier-C glob list.
