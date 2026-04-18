# URGENT — supervisor tick touched a Tier-C path

Tick at 2026-04-18T16-49-48Z violated its boundary. Investigate before the next tick.

Tier-C writes in supervisor repo:
  (none)

Project HEAD changes:
  command: e1f230361dd7b2bd8c8885c2351cd06358adaa30 -> c3aac729b5f617c67c1d6db052a0809b745c62ed


Pre-run supervisor HEAD: b78795c368b93340a7ad40779993dfe7d59f5e8a
Post-run supervisor dirty tree:
```
     M system/active-issues.md
    ?? friction/FR-0029-tick-urgent-fires-on-attended-session-backoff.md
    ?? handoffs/ARCHIVE/2026-04/2026-04-18T14-20Z-workspace-alignment-sweep-findings.md
    ?? handoffs/ARCHIVE/2026-04/URGENT-tick-escalation-2026-04-18T14-47-59Z.md
```

Investigate: --disallowedTools may need tightening, OS-level sandbox may
have a gap, or a path was missed in the Tier-C glob list.
