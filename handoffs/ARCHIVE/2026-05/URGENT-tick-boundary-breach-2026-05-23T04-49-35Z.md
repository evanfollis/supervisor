# URGENT — supervisor tick touched a Tier-C path

Tick at 2026-05-23T04-49-35Z violated its boundary. Investigate before the next tick.

Tier-C writes in supervisor repo:
  scripts/lib/.erofs-test-meta-reflection (matched scripts/lib/*, status=??)
  scripts/lib/TEST_WRITE_2951547 (matched scripts/lib/*, status=??)


Project HEAD changes:
  (none)

Pre-run supervisor HEAD: 9b0366dd837fa6a6b904aef17f3aeb4899cec8e2
Post-run supervisor dirty tree:
```
     M friction/FR-0038-false-ghost-write-resolution-claims.md
     M friction/FR-0039-automated-adr-commit-on-handoff-trigger.md
     M friction/FR-0040-ghost-write-governance-tier-escalation.md
     M friction/FR-0041-synthesis-carryforward-duplicate-inbox-deposits.md
     M system/active-issues.md
     M system/verified-state.md
    ?? .reviews/atlas-escalation-gate-2026-04-27T17-00Z.md
    ?? handoffs/ARCHIVE/2026-05-23/session-summary-supervisor-2026-05-23T04-55-41Z.md
    ?? scripts/lib/.erofs-test-meta-reflection
    ?? scripts/lib/TEST_WRITE_2951547
```

Investigate: --disallowedTools may need tightening, OS-level sandbox may
have a gap, or a path was missed in the Tier-C glob list.
