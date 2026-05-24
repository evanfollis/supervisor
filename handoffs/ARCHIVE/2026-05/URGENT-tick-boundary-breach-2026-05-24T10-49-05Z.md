# URGENT — supervisor tick touched a Tier-C path

Tick at 2026-05-24T10-49-05Z violated its boundary. Investigate before the next tick.

Tier-C writes in supervisor repo:
  scripts/lib/.erofs-test-meta-reflection (matched scripts/lib/*, status=??)
  scripts/lib/TEST_WRITE_2951547 (matched scripts/lib/*, status=??)


Project HEAD changes:
  (none)

Pre-run supervisor HEAD: 189ad6b0e30bc593547225e59e6d1d927169578f
Post-run supervisor dirty tree:
```
     M system/verified-state.md
    ?? handoffs/ARCHIVE/2026-05-24/session-summary-supervisor-2026-05-24T10-52-15Z.md
    ?? scripts/lib/.erofs-test-meta-reflection
    ?? scripts/lib/TEST_WRITE_2951547
```

Investigate: --disallowedTools may need tightening, OS-level sandbox may
have a gap, or a path was missed in the Tier-C glob list.
