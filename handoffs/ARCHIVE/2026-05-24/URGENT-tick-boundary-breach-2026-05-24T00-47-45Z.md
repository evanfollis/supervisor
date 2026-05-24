# URGENT — supervisor tick touched a Tier-C path

Tick at 2026-05-24T00-47-45Z violated its boundary. Investigate before the next tick.

Tier-C writes in supervisor repo:
  scripts/lib/.erofs-test-meta-reflection (matched scripts/lib/*, status=??)
  scripts/lib/TEST_WRITE_2951547 (matched scripts/lib/*, status=??)


Project HEAD changes:
  (none)

Pre-run supervisor HEAD: a95062410d7d6716aff50cc5ffccd0ace7ac10e2
Post-run supervisor dirty tree:
```
     M system/active-issues.md
     M system/verified-state.md
    ?? handoffs/ARCHIVE/2026-05-23/URGENT-tick-boundary-breach-2026-05-23T22-50-05Z.md
    ?? handoffs/ARCHIVE/2026-05-24/
    ?? scripts/lib/.erofs-test-meta-reflection
    ?? scripts/lib/TEST_WRITE_2951547
```

Investigate: --disallowedTools may need tightening, OS-level sandbox may
have a gap, or a path was missed in the Tier-C glob list.
