#!/usr/bin/env bash
# synthesis-translator.sh — translate synthesis proposals into executable handoffs.
#
# Closes the translation gap identified 2026-04-23: the synthesize.sh job
# writes diagnostic output to runtime/.meta/cross-cutting-*.md but nothing
# converts those concrete proposals into handoffs that sessions actually
# pick up and execute. Without this primitive, synthesis proposals sit
# unexecuted indefinitely, producing "perfect diagnosis, zero execution"
# (see cross-cutting-2026-04-23T15-24-05Z.md §Headline).
#
# Usage: synthesis-translator.sh <synthesis-file>
#
# Called from synthesize.sh immediately after the main synthesis run so
# every synthesis cycle auto-emits handoffs for its live proposals.
#
# Output:
#   - Handoffs to /opt/workspace/runtime/.handoff/ for project-scope work
#   - Handoffs to /opt/workspace/supervisor/handoffs/INBOX/ for supervisor-scope
#
# Policy: applies the "people-or-money" rubric — anything that isn't a named
# external human or a dollar amount is autonomous-bucket.

set -euo pipefail

SYNTHESIS_FILE="${1:-}"
if [[ -z "$SYNTHESIS_FILE" || ! -f "$SYNTHESIS_FILE" ]]; then
  echo "usage: $0 <synthesis-file>" >&2
  echo "       synthesis file not found: ${SYNTHESIS_FILE:-<missing>}" >&2
  exit 2
fi

# Short-circuit if the synthesis itself short-circuited.
if head -1 "$SYNTHESIS_FILE" | grep -q '^# Synthesis skipped'; then
  echo "synthesis-translator: source short-circuited; nothing to translate"
  exit 0
fi

LIB_DIR="$(cd "$(dirname "$0")" && pwd)"
PROMPT_TEMPLATE="$LIB_DIR/synthesis-translator-prompt.md"
ISO_FILENAME="$(date -u +%Y-%m-%dT%H-%M-%SZ)"
ISO_TS="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
HANDOFF_DIR="/opt/workspace/runtime/.handoff"
INBOX_DIR="/opt/workspace/supervisor/handoffs/INBOX"
LOG_FILE="/opt/workspace/runtime/.meta/synthesis-translator-${ISO_FILENAME}.log"

mkdir -p "$HANDOFF_DIR" "$INBOX_DIR" "$(dirname "$LOG_FILE")"

if [[ ! -f "$PROMPT_TEMPLATE" ]]; then
  echo "synthesis-translator: prompt template missing: $PROMPT_TEMPLATE" >&2
  exit 1
fi

PROMPT="$(sed \
  -e "s|{{SYNTHESIS_FILE}}|$SYNTHESIS_FILE|g" \
  -e "s|{{ISO_NOW}}|$ISO_TS|g" \
  -e "s|{{ISO_FILENAME}}|$ISO_FILENAME|g" \
  -e "s|{{HANDOFF_DIR}}|$HANDOFF_DIR|g" \
  -e "s|{{INBOX_DIR}}|$INBOX_DIR|g" \
  "$PROMPT_TEMPLATE")"

PROMPT_FILE="$(mktemp /tmp/workspace-synthesis-translator-prompt.XXXXXX)"
cleanup_prompt() { rm -f "$PROMPT_FILE"; }
trap cleanup_prompt EXIT
printf '%s' "$PROMPT" > "$PROMPT_FILE"

echo "synthesis-translator: translating $SYNTHESIS_FILE"

# Haiku remains primary; subscription capacity routes to Codex. The shared
# runner preserves the write boundary, full private transcript, and compact
# provider telemetry for the translation leg as well as synthesis itself.
"$LIB_DIR/run-synthesis-model.py" \
  --prompt-file "$PROMPT_FILE" \
  --cwd /opt/workspace \
  --run-id "synthesis-translation-$ISO_FILENAME" \
  --timeout 600 \
  --claude-model claude-haiku-4-5-20251001 \
  --claude-permission-mode acceptEdits \
  --role synthesis-translation \
  --project supervisor \
  --prompt-id synthesis-translator \
  2>&1 | tee "$LOG_FILE" | tail -n 40

EXIT_CODE="${PIPESTATUS[0]}"
if [[ "$EXIT_CODE" -ne 0 ]]; then
  echo "synthesis-translator: all configured model routes failed ($EXIT_CODE); see $LOG_FILE" >&2
  exit "$EXIT_CODE"
fi

# Emit a structured completion event so synthesis job + reflection can
# observe the translation rate (friction event shape per ADR-0029 §Layer 5).
EVENTS_FILE="/opt/workspace/runtime/friction/events.jsonl"
mkdir -p "$(dirname "$EVENTS_FILE")"
printf '{"ts":"%s","layer":"validation","source":"synthesis-translator","eventType":"success","reason":"translation complete","ref":"%s"}\n' \
  "$ISO_TS" "$SYNTHESIS_FILE" >> "$EVENTS_FILE"

# Prompt-eval flywheel (ADR-0039): every real synthesis this prompt
# processed becomes a golden-set candidate for the synthesis-translator
# eval loop. Dedup by input hash is handled inside append_candidate.
# Non-fatal: candidate capture must never break the translation path.
python3 - "$SYNTHESIS_FILE" "$ISO_TS" <<'PYEOF' || echo "synthesis-translator: candidate capture failed (non-fatal)" >&2
import sys
from pathlib import Path
sys.path.insert(0, "/opt/workspace/supervisor/scripts/lib")
from prompteval.goldens import append_candidate
from prompteval.telemetry import emit
synthesis_file, iso_ts = sys.argv[1], sys.argv[2]
spec_dir = Path("/opt/workspace/supervisor/.prompteval/synthesis-translator")
if spec_dir.exists():
    try:
        content = Path(synthesis_file).read_text(encoding="utf-8")
        entry = append_candidate(
            spec_dir,
            {"synthesis": content, "iso_now": iso_ts,
             "iso_filename": iso_ts.replace(":", "-")},
            source=f"live-run:{synthesis_file}",
        )
        print(f"synthesis-translator: golden candidate "
              f"{'captured' if entry else 'already present'}")
    except Exception as exc:  # capture failure must be visible, not silent
        emit("supervisor", "failure",
             f"synthesis-translator: candidate capture failed: {exc}",
             ref=synthesis_file, source_type="cron")
        raise
PYEOF

echo "synthesis-translator: complete at $ISO_TS (log: $LOG_FILE)"
