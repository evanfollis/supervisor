---
from: synthesis-translator
to: general
date: 2026-07-05T03:33:26Z
priority: high
task_id: synthesis-reflect-head-check-fp
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-05T03-28-11Z.md
source_proposal: P5 (CARRY — C120, 7th cycle): Patch reflect.sh HEAD-check false positive
---

# P5: Patch reflect.sh HEAD-check false positive

**Type:** `reflect.sh` — whitelist autocommit SHAs in HEAD comparison.

**Blast radius:** Supervisor. ~15 min. **7th cycle open — recurring across 7 synthesis cycles.**

## Current behavior (lines 159–167)

The script captures HEAD state before launching the reflection session and compares it after:

```bash
if [[ -d "$PROJECT_DIR/.git" ]]; then
  AFTER_HEAD=$(git -C "$PROJECT_DIR" rev-parse HEAD 2>/dev/null || echo none)
  ...
  if [[ "$BEFORE_HEAD" != "$AFTER_HEAD" ]]; then
    echo "reflect[$PROJECT]: CRITICAL — HEAD changed ($BEFORE_HEAD → $AFTER_HEAD)..." >&2
    cat > "$WORKSPACE_HANDOFF_DIR/URGENT-${PROJECT}-reflection-mutated-head.md" <<EOF
    ...
EOF
```

This safety net is designed to catch cases where the reflection session (which should be read-only) mutates the repo. However, in the supervisor repo, HEAD advances every cycle via `supervisor-autocommit.sh`, which lands commits like:

```
e9f07bf autocommit 2026-07-05T02-24-52Z: Tier-A governance artifacts
b395260 autocommit 2026-07-05T00-24-01Z: Tier-A governance artifacts
```

The reflect.sh safety net sees HEAD moving from `e9f07bf` to `b395260` and interprets this as a violation, even though:
1. The reflect session did NOT do this — the autocommit did
2. The reflect session ran in isolation and produced read-only output
3. The false URGENT is regenerated every cycle, degrading signal quality

## Proposed behavior

Whitelist autocommit SHAs by checking whether the HEAD change is attributable to a supervisor-level commit (not the reflect session itself).

Add this helper function before the HEAD-check block (around line 90):

```bash
is_autocommit_sha() {
  local sha="$1"
  # Autocommit SHAs have a predictable pattern in supervisor-autocommit.sh output.
  # Check if the commit message matches "autocommit <ISO>:" pattern.
  if git -C "$PROJECT_DIR" log -1 --format=%B "$sha" 2>/dev/null | grep -q "^autocommit [0-9T:-]*Z:"; then
    return 0  # it's an autocommit, whitelist it
  fi
  return 1  # not an autocommit, flag it
}
```

Replace the HEAD-change detection (line 159) with:

```bash
  if [[ "$BEFORE_HEAD" != "$AFTER_HEAD" ]]; then
    # Head changed. Check if it's an autocommit (supervisor layer) or a repo mutation.
    if is_autocommit_sha "$AFTER_HEAD"; then
      echo "reflect[$PROJECT]: HEAD advanced via autocommit ($BEFORE_HEAD → $AFTER_HEAD) — benign" >&2
    else
      # Actual repo mutation during reflection — this is a real problem.
      echo "reflect[$PROJECT]: CRITICAL — HEAD changed ($BEFORE_HEAD → $AFTER_HEAD). Reflection is supposed to be read-only." >&2
      cat > "$WORKSPACE_HANDOFF_DIR/URGENT-${PROJECT}-reflection-mutated-head.md" <<EOF
```

**Rationale (from synthesis C125):**
- **Pattern:** The reflect.sh HEAD-check fires every supervisor reflection cycle, generating a false URGENT file `URGENT-supervisor-reflection-mutated-head.md` that is immediately outdated.
- **Root cause:** Supervisor autocommit advances HEAD between the pre-reflection snapshot and post-reflection check. The reflect session itself is still read-only, but the check can't distinguish supervisor-layer commits from session-level mutations.
- **Impact:** 7 cycles of carry-forward. Each false URGENT degrades the signal quality of the URGENT surface in `runtime/.handoff/`. The supervisor INBOX keeps regenerating stale URGENTs instead of processing live issues.
- **Narrowest fix:** Whitelist autocommit SHAs by checking the commit message pattern. If the HEAD change is attributable to an autocommit, log it as benign; if not, flag it as before.

## Verification before action (required)

- Read `/opt/workspace/supervisor/scripts/lib/reflect.sh` lines 159–167. Confirm the HEAD-check is present and does NOT whitelist autocommit SHAs.
- Confirm supervisor autocommit commits have the pattern `autocommit <ISO>:` in their message: `git -C /opt/workspace/supervisor log -1 --format=%B HEAD | head -1`.
- Check `/opt/workspace/supervisor/handoffs/INBOX/` for any recent URGENT files mentioning "reflection-mutated-head". Confirm they are stale (regenerated every cycle).

## Acceptance criteria

- Helper function `is_autocommit_sha()` is added to `reflect.sh`
- Lines 159–167 of `reflect.sh` are amended to whitelist autocommit SHAs as shown above
- Change committed with message: "Whitelist autocommit SHAs in reflect.sh HEAD-check per synthesis C125 (C120, 7th carry-forward)"
- No adversarial review needed (targeted bug fix, well-scoped)
- Verify: run `supervisor-reflect.sh supervisor /opt/workspace/supervisor` and confirm no `URGENT-supervisor-reflection-mutated-head.md` file is created

## Escalation

None anticipated. This is a straightforward false-positive elimination that makes the safety net more precise without reducing its real protective value.

