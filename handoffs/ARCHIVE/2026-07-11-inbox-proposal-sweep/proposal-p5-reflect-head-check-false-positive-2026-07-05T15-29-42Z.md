---
from: synthesis-translator
to: executive
date: 2026-07-05T15:29:42Z
priority: high
task_id: synthesis-p5-reflect-head-check-false-positive
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-05T15-26-01Z.md
source_proposal: "P5 (CARRY — C120, 8th cycle): Patch reflect.sh HEAD-check false positive"
---

# P5: Patch reflect.sh HEAD-check false positive

**Type:** `reflect.sh` whitelist amendment — suppress false URGENT on autocommit SHAs.
**Blast radius:** Supervisor. ~15 min implementation.

## Current state

`reflect.sh` at lines 154–168 performs a safety check: if the reflection session changes HEAD (advances the commit), it emits an URGENT:

```bash
if [[ "$BEFORE_HEAD" != "$AFTER_HEAD" ]]; then
  echo "reflect[$PROJECT]: CRITICAL — HEAD changed ($BEFORE_HEAD → $AFTER_HEAD)..." >&2
  cat > "$WORKSPACE_HANDOFF_DIR/URGENT-${PROJECT}-reflection-mutated-head.md" <<EOF
Reflection session for ${PROJECT} at ${ISO_NOW} advanced HEAD...
EOF
  exit 3
fi
```

This is correct. However, for the supervisor project, the **post-reflection CURRENT_STATE.md auto-commit** (lines 186–203) advances HEAD by 1 commit. The next reflection cycle then sees a different BEFORE_HEAD and falsely triggers the "HEAD changed" URGENT, even though the change was intentional and expected.

## Problem manifestation

Supervisor reflections cycle every ~12h:
1. Reflection writes CURRENT_STATE.md
2. reflect.sh auto-commits it (line 193-198)
3. Next cycle: BEFORE_HEAD from prior cycle ≠ current HEAD
4. Safety net incorrectly fires: "HEAD changed"
5. URGENT file written to `runtime/.handoff/URGENT-supervisor-reflection-mutated-head.md`
6. Each cycle adds another false URGENT

**This creates 8 cycles of false alarms** (since C120, carried 8 cycles). The URGENT counter in synthesis now oscillates between 9–10 rather than incrementing monotonically, producing cosmetic misleading reports.

## Proposed fix

Whitelist autocommit SHAs in the HEAD comparison. When checking if HEAD changed:

1. After reading `AFTER_HEAD`, check if the commit message mentions "reflect: auto-update CURRENT_STATE.md"
2. If yes, log a note "HEAD advanced by expected autocommit" and do **not** emit the URGENT
3. If no (unexpected HEAD change), emit the URGENT as before

**Implementation approach:**

```bash
AFTER_HEAD=$(git -C "$PROJECT_DIR" rev-parse HEAD 2>/dev/null || echo none)
if [[ "$BEFORE_HEAD" != "$AFTER_HEAD" ]]; then
  # Check if the new commit is an expected autocommit
  COMMIT_MSG=$(git -C "$PROJECT_DIR" log -1 --format=%s HEAD 2>/dev/null || echo "")
  if [[ "$COMMIT_MSG" == "reflect: auto-update CURRENT_STATE.md"* ]]; then
    echo "reflect[$PROJECT]: HEAD advanced by expected autocommit ($BEFORE_HEAD → $AFTER_HEAD)"
  else
    # Unexpected HEAD change — emit URGENT as before
    echo "reflect[$PROJECT]: CRITICAL — HEAD changed..." >&2
    ...
  fi
fi
```

## Verification before action (required)

- Read `/opt/workspace/supervisor/scripts/lib/reflect.sh` lines 154–168
- Check for an existing whitelist or autocommit detection logic — if it exists, write completion report "already implemented"
- Scan `/opt/workspace/runtime/.handoff/` for files like `URGENT-supervisor-reflection-mutated-head.md` — note how many exist and their age
- Run `git -C /opt/workspace/supervisor log --oneline -5 | grep reflect:` — confirm that recent commits are CURRENT_STATE.md auto-commits

## Acceptance criteria

- HEAD-change detection updated to whitelist autocommit SHAs
- When the new commit's message starts with "reflect: auto-update CURRENT_STATE.md", log a note instead of emitting URGENT
- Unexpected HEAD changes still emit URGENT as before (safety net intact)
- Change committed with message: `reflect: whitelist autocommit SHAs in HEAD-check per synthesis proposal P5`
- Completion report at `runtime/.handoff/general-p5-head-check-complete-<iso>.md`

## Escalation

Low risk. This is a false-positive filter that preserves the safety net for genuine unexpected HEAD changes.

---

**Background from synthesis (C126 / C125 Pattern 2, C120 → 8th cycle):** The reflect.sh safety net is correct. The auto-commit feature is also correct. The problem is that the safety net doesn't know about auto-commit and keeps firing false alarms. This is a 15-min whitelisting patch that has been carried 8 synthesis cycles. P5 fix = suppress the cosmetic noise without changing any real logic. Carries 26th consecutive rebase request.
