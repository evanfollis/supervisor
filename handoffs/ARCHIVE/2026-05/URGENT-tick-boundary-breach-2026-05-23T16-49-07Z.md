# URGENT — supervisor tick touched a Tier-C path

Tick at 2026-05-23T16-49-07Z violated its boundary. Investigate before the next tick.

Tier-C writes in supervisor repo:
  scripts/lib/.erofs-test-meta-reflection (matched scripts/lib/*, status=??)
  scripts/lib/TEST_WRITE_2951547 (matched scripts/lib/*, status=??)


Project HEAD changes:
  (none)

Pre-run supervisor HEAD: 94dd79c3b88e0ec7be0f76ef6ed65f88153a3991
Post-run supervisor dirty tree:
```
    ?? .reviews/atlas-escalation-gate-2026-04-27T17-00Z.md
    ?? handoffs/ARCHIVE/2026-05-23/session-summary-supervisor-2026-05-23T16-53-19Z.md
    ?? scripts/lib/.erofs-test-meta-reflection
    ?? scripts/lib/TEST_WRITE_2951547
```

Investigate: --disallowedTools may need tightening, OS-level sandbox may
have a gap, or a path was missed in the Tier-C glob list.
