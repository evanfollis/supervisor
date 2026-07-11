---
from: synthesis-translator
to: general
date: 2026-06-28T03:27:59Z
priority: critical
task_id: synthesis-p7-reflect-failure-self-reporting
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-06-28T03-24-11Z.md
source_proposal: P7 (CRITICAL, carry from C110) — Reflection/synthesis failure self-reporting
---

# P7 (CRITICAL): Reflection/synthesis failure self-reporting

**Type:** Shared primitive — guard in `reflect.sh`.

**Status (at synthesis time):** Not implemented. `reflect.sh:115-119` still exits with code 2 and stderr warning only. No handoff written, no telemetry event emitted.

## Proposal body (from synthesis)

When a reflection job produces no output, the current code exits silently to stderr. This creates a blind spot: if an API key fails, a session crashes, or a network timeout occurs, the diagnostic loop reports nothing and produces no self-documenting escalation.

**Patch to apply** (lines 115–160 of `supervisor/scripts/lib/reflect.sh`):

Replace the current failure handler:
```bash
if [[ -f "$OUTPUT_FILE" ]]; then
  echo "reflect[$PROJECT]: wrote $OUTPUT_FILE"
else
  echo "reflect[$PROJECT]: WARNING — no output file produced" >&2
  exit 2
fi
```

With the new handler that writes a self-reporting handoff:
```bash
if [[ -f "$OUTPUT_FILE" ]]; then
  echo "reflect[$PROJECT]: wrote $OUTPUT_FILE"
else
  echo "reflect[$PROJECT]: WARNING — no output file produced" >&2
  FAIL_FILE="$WORKSPACE_HANDOFF_DIR/URGENT-reflect-failure-${PROJECT}-${ISO_NOW}.md"
  cat > "$FAIL_FILE" <<EOFAIL
# URGENT: Reflection job failed for $PROJECT

Session exited with no substantive output at $ISO_NOW.
Check API key, credential path, and session launch mechanism.
EOFAIL
  exit 2
fi
```

**Blast radius:** All reflected projects (automatic — fires on failure).

**Effort:** <5 min. Independent of all other proposals.

## Verification before action (required)

- Check `reflect.sh:115–120` in `/opt/workspace/supervisor/scripts/lib/reflect.sh`. Confirm the current code still shows `exit 2` with no FAIL_FILE write.
- If already patched, write a completion report stating "already landed at commit <SHA>" rather than re-applying.

## Acceptance criteria

- The patch is applied to lines 115–160 of `supervisor/scripts/lib/reflect.sh`.
- `reflect.sh` emits a handoff at `$WORKSPACE_HANDOFF_DIR/URGENT-reflect-failure-${PROJECT}-${ISO_NOW}.md` when a reflection session exits with no output file.
- Change committed with message explaining the synthesis source and the self-reporting purpose.
- Tested by triggering a reflection failure (e.g., simulate a missing API key in a test project or accept the next natural failure).

## Escalation

- If the API failure that triggered Pattern 6 (the 7-day auth dark period) recurs, this patch ensures it self-reports immediately rather than silently accumulating across cycles.
- No external dependencies or credential provisioning required.
