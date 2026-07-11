---
from: synthesis-translator
to: general
date: 2026-07-10T03:27:28Z
priority: medium
task_id: synthesis-p5-reflect-head-check
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-10T03-23-34Z.md
source_proposal: P5 (CARRY — C120, 17th cycle) — Patch reflect.sh HEAD-check false positive
---

# P5: Patch reflect.sh HEAD-check false positive

**Type:** `reflect.sh` — whitelist autocommit SHAs in HEAD comparison.

**Blast radius:** Supervisor, synaplex. ~15 min.

## Rationale

The HEAD-check in reflect.sh compares current HEAD against prior reflection to detect dirty-tree or unexpected commits. Autocommit operations generate mechanically identical commits that should not trigger a false-positive dirty-tree detection.

## Verification before action (required)

- Read `/opt/workspace/supervisor/scripts/lib/reflect.sh` lines around the HEAD comparison logic
- Check if autocommit SHA whitelist already exists (pattern like `autocommit.*` or similar)
- If already patched, write a completion report stating "already landed"

## Acceptance criteria

- `reflect.sh` amended to whitelist autocommit SHAs when comparing HEAD to prior reflection state
- Whitelist can be a simple pattern match (e.g., commits matching `^autocommit`) or a maintained list
- Affected projects: supervisor, synaplex (carry-forward notes OK for others)
- Single commit with message: "Whitelist autocommit SHAs in HEAD check — prevent false-positive dirty-tree detection (synthesis C135)"
- Completion report filed to `runtime/.handoff/general-supervisor-synthesis-p5-complete-<iso>.md`
