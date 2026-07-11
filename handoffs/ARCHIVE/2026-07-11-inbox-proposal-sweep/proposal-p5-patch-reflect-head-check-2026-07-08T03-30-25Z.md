---
from: synthesis-translator
to: general
date: 2026-07-08T03:30:25Z
priority: medium
task_id: synthesis-p5-reflect-head-check-fix
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-08T03-24-41Z.md
source_proposal: P5 — Patch reflect.sh HEAD-check false positive
---

# P5: Patch reflect.sh HEAD-check false positive

**Type:** `reflect.sh` — whitelist autocommit SHAs in HEAD comparison.

**Rationale:** The reflection safety net at lines 89-96 (before/during/after HEAD and dirty-tree checks) is generating false positives when the reflection session itself causes a repo to emit autocommit SHAs that match the HEAD before the reflection started. By whitelisting known autocommit commit patterns, the false alarm rate drops while preserving the safety net's ability to catch actual mutation.

**Blast radius:** Supervisor, synaplex. ~15 min implementation.

---

## Verification before action (required)

- Read `/opt/workspace/supervisor/scripts/lib/reflect.sh` lines 89-96 (the HEAD/dirty-tree safety-net section).
- Check recent reflection output files (e.g., supervisor reflections) for "WARNING — repository was mutated" false positives.
- If the whitelist fix is already in place, write completion report stating "already landed".

## Acceptance criteria

- **Whitelist logic added to lines 89-96 or nearby:**
  Define autocommit SHA patterns that should be ignored:
  ```bash
  is_autocommit_sha() {
    local sha="$1"
    # Autocommits follow pattern: agent=autocommit in supervisor-events.jsonl
    # For now, whitelist by checking if it's in supervisor-events.jsonl with agent=autocommit
    grep -q "\"ref\":\"autocommit" "$EVENT_FILE" && echo "yes" || echo "no"
  }
  ```
  
  Alternatively, if autocommit SHAs are predictable by pattern (e.g., all in the last 5 commits):
  ```bash
  RECENT_AUTOCOMMITS=$(git -C "$PROJECT_DIR" log --format=%H -n 5 --grep="autocommit" 2>/dev/null || true)
  ```

- **Updated comparison logic:**
  When HEAD changes between BEFORE and AFTER, check if all changed commits are autocommits (via whitelist). If yes, suppress the warning.

- Commit message: "Add autocommit SHA whitelist to reflect.sh safety net (synthesis-p5)".
- Test by triggering a reflection on supervisor or synaplex and confirming no false-positive warnings.
- Completion report at `/opt/workspace/supervisor/handoffs/INBOX/general-synthesis-p5-head-check-complete-<iso>.md`.

## Non-goals

- No changes to the overall mutation-detection logic.
- Do not disable the safety net for non-autocommit mutations.
