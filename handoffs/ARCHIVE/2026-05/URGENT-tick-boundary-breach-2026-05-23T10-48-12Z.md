# URGENT — supervisor tick touched a Tier-C path

Tick at 2026-05-23T10-48-12Z violated its boundary. Investigate before the next tick.

Tier-C writes in supervisor repo:
  scripts/lib/.erofs-test-meta-reflection (matched scripts/lib/*, status=??)
  scripts/lib/TEST_WRITE_2951547 (matched scripts/lib/*, status=??)


Project HEAD changes:
  (none)

Pre-run supervisor HEAD: 4304a2b67c0a4d96fd5f80308064c7a0d4dd1f3d
Post-run supervisor dirty tree:
```
     M system/verified-state.md
    ?? .reviews/atlas-escalation-gate-2026-04-27T17-00Z.md
    ?? handoffs/ARCHIVE/2026-05-23/session-summary-supervisor-2026-05-23T10-50-44Z.md
    ?? scripts/lib/.erofs-test-meta-reflection
    ?? scripts/lib/TEST_WRITE_2951547
```

Investigate: --disallowedTools may need tightening, OS-level sandbox may
have a gap, or a path was missed in the Tier-C glob list.
