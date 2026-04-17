---
name: /review skill broken — EROFS in sandboxed sessions
description: The /review skill fails system-wide with EROFS on /root/.claude.json, defeating the mandatory adversarial review gate for all project sessions
type: feedback
status: resolved-workaround
resolved_ts: 2026-04-17T06:02Z
---

The `/review` skill fails with `EROFS: read-only file system, open '/root/.claude.json'` in every sandboxed project session context. This is a system-level filesystem constraint, not a project bug.

**First detected**: atlas reflection 2026-04-16T14:21Z.
**URGENT handoff written**: 2026-04-17T02:49Z (3 cycles after first detection — carry-forward escalation fired correctly).

**Accumulated review debt** (as of 2026-04-17T04:47Z):
- ADR-0015 (exec/supervisor/operator split) — 4 cycles
- ADR-0016 (autonomous project tick) — 2 cycles
- ADR-0017 (radical truth) — 1 cycle
- Atlas ingest.py second write path — 5 cycles, 3 additional layers on top
- Context-repository spec doc — 1 cycle

**Why this matters:** The adversarial review gate is mandatory per CLAUDE.md and the charter. Without it, ADRs are self-reviewed and high-blast-radius code ships without adversarial pressure. The carry-forward escalation mechanism eventually caught this, but only after 3+ cycles of accumulation.

**Root cause**: The `/review` skill writes to `/root/.claude.json`. Sandboxed sessions mount `/root/` read-only. The skill was designed for non-sandboxed contexts.

**Resolution paths** (for attended session):
1. Diagnose whether `/root/.claude.json` EROFS is a harness sandbox or container filesystem constraint.
2. Test `codex exec --skip-git-repo-check --sandbox read-only "<review prompt>"` as fallback.
3. If codex works: create `supervisor/scripts/lib/adversarial-review.sh` wrapping the codex call.
4. If both fail: document the gap in a disposition entry and stop carry-forward loops that cannot be actioned.

**How to apply:** Do not accept ADRs or mark "review complete" while this is unresolved. Use the URGENT INBOX handoff as the action item for the next attended session.

**Discovered**: 2026-04-16T14:21Z. Promoted to FR: 2026-04-17T04:47Z (supervisor tick).

**Resolved (workaround)**: 2026-04-17T06:02Z. `supervisor/scripts/lib/adversarial-review.sh` wraps `codex exec --sandbox read-only` with the standard 3-section review prompt. Batch-executed against ADR-0015, ADR-0016, ADR-0017, and atlas `research/ingest.py` 5076ba0 — outputs at `runtime/.reviews/`, accepted into `dispositions.jsonl`. Root-cause EROFS on `/root/.claude.json` is still open (native `/review` skill still fails) — this is a parallel review path, not a root-cause fix.
