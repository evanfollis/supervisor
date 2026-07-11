# URGENT — supervisor tick touched a Tier-C path

Tick at 2026-05-26T14-47-09Z violated its boundary. Investigate before the next tick.

Tier-C writes in supervisor repo:
  scripts/lib/.erofs-test-meta-reflection (matched scripts/lib/*, status=??)
  scripts/lib/TEST_WRITE_2951547 (matched scripts/lib/*, status=??)


Project HEAD changes:
  (none)

Pre-run supervisor HEAD: 4b5c6108c56e1260ee0d61d9ee02167519ea6f98
Post-run supervisor dirty tree:
```
    ?? handoffs/ARCHIVE/2026-05-26/session-summary-supervisor-2026-05-26T14-49-56Z.md
    ?? scripts/lib/.erofs-test-meta-reflection
    ?? scripts/lib/TEST_WRITE_2951547
```

Investigate: --disallowedTools may need tightening, OS-level sandbox may
have a gap, or a path was missed in the Tier-C glob list.
