# URGENT — supervisor tick touched a Tier-C path

Tick at 2026-05-25T02-49-29Z violated its boundary. Investigate before the next tick.

Tier-C writes in supervisor repo:
  scripts/lib/.erofs-test-meta-reflection (matched scripts/lib/*, status=??)
  scripts/lib/TEST_WRITE_2951547 (matched scripts/lib/*, status=??)


Project HEAD changes:
  (none)

Pre-run supervisor HEAD: f30f665d66e8ae7f0053fe498beb2af7e77a2928
Post-run supervisor dirty tree:
```
    ?? handoffs/ARCHIVE/2026-05-25/session-summary-supervisor-2026-05-25T02-52-21Z.md
    ?? scripts/lib/.erofs-test-meta-reflection
    ?? scripts/lib/TEST_WRITE_2951547
```

Investigate: --disallowedTools may need tightening, OS-level sandbox may
have a gap, or a path was missed in the Tier-C glob list.
