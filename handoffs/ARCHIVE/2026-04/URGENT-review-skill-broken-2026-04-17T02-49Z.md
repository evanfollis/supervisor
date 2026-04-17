# URGENT: `/review` skill broken system-wide — 3 ADR review debt + atlas code unreviewed

**Written**: 2026-04-17T02:49Z (supervisor tick)
**Priority**: Critical — mandatory governance gate defeated

## What's broken

The `/review` skill fails on every session with:
```
EROFS: read-only file system, open '/root/.claude.json'
```

First confirmed: atlas tick 2026-04-17T01:47Z (§What I'd push back on).
Structural cause: sandboxed sessions mount `/root/` read-only; the skill writes to `/root/.claude.json`.

## Accumulated review debt

| Item | Age | Notes |
|------|-----|-------|
| ADR-0015 (exec/supervisor/operator split) | 4 cycles | Most semantically broad — workspace-wide |
| ADR-0016 (autonomous project tick) | 2 cycles | Highest blast radius — 6 projects with push authority |
| ADR-0017 (radical truth principle) | 1 cycle | Accepted same session that produced it |
| atlas ingest.py 5076ba0 | 4 cycles | Two concurrent write paths, no locking |
| atlas dedup + telemetry c1395bb | 1 cycle | New ingest-path logic, concurrent-writers concern noted |

## What to do

1. **Test the codex fallback**:
   ```bash
   codex exec --skip-git-repo-check --sandbox read-only "Adversarial review of ADR-0015 at /opt/workspace/supervisor/decisions/0015-executive-supervisor-operator-split.md. Challenge the design decisions, blast radius, and missing invariants. Be a skeptic."
   ```
2. If that works, batch the 3 ADR reviews in one attended session.
3. If that also fails, open an ADR for the review-path gap (this is itself a structural problem worth documenting).
4. Fix the EROFS root cause — either by having the skill write to a temp location, or by patching the harness to not write to `/root/.claude.json` in sandboxed contexts.

## Reference

- FR-0021: `/opt/workspace/supervisor/friction/FR-0021-review-skill-broken-erofs.md`
- Completion report: `/opt/workspace/runtime/.handoff/general-atlas-tick-complete-2026-04-17T01-47-37Z.md`
- ADR-0015: `/opt/workspace/supervisor/decisions/0015-executive-supervisor-operator-split.md`
