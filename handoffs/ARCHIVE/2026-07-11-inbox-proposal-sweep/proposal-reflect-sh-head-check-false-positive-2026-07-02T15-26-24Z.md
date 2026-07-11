---
from: synthesis-translator
to: general
date: 2026-07-02T15:26:24Z
priority: high
task_id: synthesis-reflect-head-check-false-positive
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-02T15-23-04Z.md
source_proposal: P5 (NEW)
---

# P5: Patch reflect.sh HEAD-check false positive

**Type:** `reflect.sh` — whitelist autocommit SHAs in HEAD comparison.

**Context:** C120 identified a new governance-tooling failure class: the reflect.sh safety net at lines 159-167 snapshots HEAD at session start and compares at session end. It cannot distinguish "reflection session wrote to repo" (a real violation) from "autocommit fired concurrently during session" (expected behavior). On reflections that straddle a 2h autocommit boundary, this produces false URGENT files that pollute the governance queue.

**Cited incident:** Supervisor C60: "URGENT-supervisor-reflection-mutated-head.md filed by reflect.sh at 02:25Z [...] Investigation shows this is a false positive. The HEAD advance was the autocommit at 02:23Z firing concurrently during the 02:22Z-02:25Z reflection session."

**Failure class:** Same as stale-URGENT accumulation — governance infrastructure produces noise that degrades its own signal channel. Unlike Pattern 3 (which requires principal cleanup), this one is fixable by patching reflect.sh.

## Implementation sketch (from synthesis)

After the HEAD comparison at line 159 detects an advance, before filing URGENT at line 161:

```bash
# After HEAD comparison detects advance, before filing URGENT:
ADVANCE_MSG=$(git -C "$REPO" log --format=%s "${SNAPSHOT_HEAD}..HEAD" 2>/dev/null)
if echo "$ADVANCE_MSG" | grep -qE '^autocommit [0-9T:-]+Z: Tier-A governance artifacts$'; then
  echo "HEAD advance is concurrent autocommit, not reflection mutation" >&2
  # Skip URGENT filing
fi
```

The autocommit commit message pattern is stable (`autocommit <iso>: Tier-A governance artifacts`), making a whitelist check straightforward.

## Current implementation reference

Lines 159-167 of `/opt/workspace/supervisor/scripts/lib/reflect.sh`:
```bash
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
```

The patch inserts the whitelist check inside the `if` block, before the file write.

## Acceptance criteria

- The whitelist check detects concurrent autocommit by commit message pattern.
- When a concurrent autocommit is detected, skip URGENT filing and log "HEAD advance is concurrent autocommit" to stderr.
- The reflect session exits cleanly (exit 0, not exit 3) when autocommit is detected and whitelisted.
- One commit with message: "fix reflect.sh HEAD-check false positive per C120 P5"
- Completion report pointing back to this handoff.
- Adversarial review recommended (governance tooling safety change) via `supervisor/scripts/lib/adversarial-review.sh`.

## Escalation

URGENT if:
- The false-positive URGENT (`URGENT-supervisor-reflection-mutated-head.md`) has already been manually deleted from `runtime/.handoff/` (verify with `git log --all -- runtime/.handoff/URGENT-*`).
- The HEAD-check logic has been removed or restructured since this proposal was written (check reflect.sh lines 159-167).
- A reflection session has filed multiple false URGENTs after this proposal was identified (gather evidence before applying).

## Blast radius

- All reflected projects with concurrent autocommit (currently: supervisor only).
- Opt-in — only fires on HEAD-advance detection.
- Effort: ~15 min.
