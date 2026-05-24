# URGENT — supervisor tick touched a Tier-C path

Tick at 2026-05-24T08-49-19Z violated its boundary. Investigate before the next tick.

Tier-C writes in supervisor repo:
  scripts/lib/.erofs-test-meta-reflection (matched scripts/lib/*, status=??)
  scripts/lib/TEST_WRITE_2951547 (matched scripts/lib/*, status=??)


Project HEAD changes:
  (none)

Pre-run supervisor HEAD: 059adc7ea1e528342cf19b333cfbfe7ee2490a5f
Post-run supervisor dirty tree:
```
     M system/active-issues.md
     M system/verified-state.md
    ?? handoffs/ARCHIVE/2026-05-24/session-summary-supervisor-2026-05-24T08-52-31Z.md
    ?? handoffs/ARCHIVE/2026-05/URGENT-tick-boundary-breach-2026-05-24T06-47-33Z.md
    ?? scripts/lib/.erofs-test-meta-reflection
    ?? scripts/lib/TEST_WRITE_2951547
```

Investigate: --disallowedTools may need tightening, OS-level sandbox may
have a gap, or a path was missed in the Tier-C glob list.
