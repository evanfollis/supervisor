---
from: synthesis-translator
to: general
date: 2026-07-03T15:29:41Z
priority: medium
task_id: synthesis-reflect-head-check-whitelist
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-03T15-24-18Z.md
source_proposal: P5 (CARRY — C120, 3rd cycle): Patch reflect.sh HEAD-check false positive
---

# P5: Patch reflect.sh HEAD-check false positive

**Type:** `reflect.sh` — whitelist autocommit SHAs in HEAD comparison.

**Target file:** `/opt/workspace/supervisor/scripts/lib/reflect.sh`

## Current behavior (lines 154–168)

```bash
# Safety net — verify the reflection session did not mutate the repo.
if [[ -d "$PROJECT_DIR/.git" ]]; then
  AFTER_HEAD=$(git -C "$PROJECT_DIR" rev-parse HEAD 2>/dev/null || echo none)
  AFTER_DIRTY=$(git -C "$PROJECT_DIR" status --porcelain 2>/dev/null || true)
  mkdir -p "$WORKSPACE_HANDOFF_DIR"
  if [[ "$BEFORE_HEAD" != "$AFTER_HEAD" ]]; then
    echo "reflect[$PROJECT]: CRITICAL — HEAD changed ($BEFORE_HEAD → $AFTER_HEAD). Reflection is supposed to be read-only." >&2
    cat > "$WORKSPACE_HANDOFF_DIR/URGENT-${PROJECT}-reflection-mutated-head.md" <<EOF
Reflection session for ${PROJECT} at ${ISO_NOW} advanced HEAD from
${BEFORE_HEAD} to ${AFTER_HEAD}. --disallowedTools did not catch it.
Investigate immediately — the blocklist pattern for git writes may be
incorrect, or the model found an unblocked path (gh, curl, direct fs).
EOF
    exit 3
  fi
  ...
```

When reflection runs on a project with concurrent autocommit (currently just supervisor), the autocommit may have committed `CURRENT_STATE.md` changes between `BEFORE_HEAD` capture and `AFTER_HEAD` capture. This causes a false URGENT to be generated.

## Proposed behavior

Whitelist known-safe autocommit SHAs so they are not treated as unexpected HEAD mutations:

1. Capture autocommit SHAs (look for commit messages matching `"reflect: auto-update CURRENT_STATE.md"` or similar pattern).
2. Before comparing HEAD, check if `AFTER_HEAD` is in the whitelist. If yes, allow the mutation.
3. Only generate URGENT if HEAD changed to a non-whitelisted commit.

**Sketch from C120:**
```bash
EXPECTED_SHAS=()
if [[ -d "$PROJECT_DIR/.git" ]]; then
  # Capture recent autocommit SHAs (reflect: auto-update pattern)
  mapfile -t EXPECTED_SHAS < <(git -C "$PROJECT_DIR" log --oneline --grep="reflect: auto-update" -n 5 2>/dev/null | awk '{print $1}' || true)
fi

if [[ "$BEFORE_HEAD" != "$AFTER_HEAD" ]]; then
  # Check if AFTER_HEAD is a known safe autocommit
  if [[ " ${EXPECTED_SHAS[*]} " =~ " $AFTER_HEAD " ]]; then
    echo "reflect[$PROJECT]: HEAD advanced to autocommit $AFTER_HEAD (safe)"
  else
    # Generate URGENT for unexpected HEAD change
    ...
  fi
fi
```

## Rationale (from C122 synthesis)

Currently, `URGENT-supervisor-reflection-mutated-head.md` is regenerated every 12h reflection cycle (now ~24h old) from this false positive. The file churns without providing signal. Effort: ~15 min.

This is the 3rd cycle this proposal has been open (since C120).

## Verification before action (required)

- Run `git log --oneline -20` on `/opt/workspace/supervisor/` to check if this change has already landed.
- Check for recent `URGENT-*-reflection-mutated-head.md` files in `runtime/.handoff/` — if present and all mention autocommit SHAs, the false positive is still occurring.
- If already landed, write a completion report stating "already landed at commit <SHA>".

## Acceptance criteria

- `reflect.sh` captures recent autocommit SHAs using the git grep pattern.
- HEAD mutations to whitelisted autocommit SHAs are allowed (logged as informational, not URGENT).
- Unexpected HEAD mutations (non-whitelisted) still generate URGENT.
- No more `URGENT-*-reflection-mutated-head.md` churn from autocommit mutations.
- Change committed with message: `Whitelist safe autocommit SHAs in reflect.sh HEAD-check to eliminate false URGENT churn`
- Completion report written to `runtime/.handoff/general-reflect-head-check-complete-<iso>.md`.

## Escalation

None anticipated. This is a safety-net refinement to eliminate false positives.
