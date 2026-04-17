#!/usr/bin/env bash
# Dispatch new handoffs in /opt/workspace/runtime/.handoff/ to their target
# PM tmux sessions. Triggered by systemd .path unit on filesystem changes
# and safe to run from cron or manually.
#
# Handoff filename convention: <session-name>-<slug>-<timestamp>.md
#
# Per-run the dispatcher:
# 1. scans the handoff dir
# 2. filters out already-dispatched files via .dispatched tracker
# 3. groups remaining handoffs by target session
# 4. sends ONE consolidated tmux nudge per session (listing all new handoffs)
# 5. marks every dispatched file in .dispatched
#
# Batching prevents three send-keys in rapid succession from interrupting a
# PM mid-response. PMs read their own inbox on activation anyway; the nudge
# just tightens the write→read latency from hours to seconds.

set -euo pipefail

HANDOFF_DIR="/opt/workspace/runtime/.handoff"
DISPATCHED_FILE="${HANDOFF_DIR}/.dispatched"
TELEMETRY_LOG="/opt/workspace/runtime/.telemetry/events.jsonl"

mkdir -p "$HANDOFF_DIR" "$(dirname "$TELEMETRY_LOG")"
touch "$DISPATCHED_FILE"

# Known PM sessions. Handoffs addressed to "general" are completion reports
# flowing UP to the executive; the executive reads its own INBOX on reentry,
# so no tmux nudge is needed.
KNOWN_SESSIONS=(mentor skillfoundry recruiter context-repo command atlas)

emit_event() {
  local event_type="$1"
  local target="$2"
  local count="$3"
  local note="$4"
  local ts_ms
  ts_ms=$(($(date +%s%N) / 1000000))
  printf '{"project":"supervisor","source":"handoff-dispatcher","eventType":"%s","level":"info","sourceType":"system","timestamp":%d,"details":{"target":"%s","count":%d,"note":"%s"}}\n' \
    "$event_type" "$ts_ms" "$target" "$count" "$note" >> "$TELEMETRY_LOG"
}

already_dispatched() {
  grep -Fxq "$1" "$DISPATCHED_FILE"
}

mark_dispatched() {
  echo "$1" >> "$DISPATCHED_FILE"
}

target_session_for() {
  local filename="$1"
  local stem="${filename%.md}"
  local best=""
  for sess in "${KNOWN_SESSIONS[@]}"; do
    if [[ "$stem" == "${sess}-"* ]]; then
      if (( ${#sess} > ${#best} )); then
        best="$sess"
      fi
    fi
  done
  echo "$best"
}

# Build per-target pending lists as newline-delimited strings in tmpfiles.
TMPDIR_PENDING="$(mktemp -d)"
trap 'rm -rf "$TMPDIR_PENDING"' EXIT

shopt -s nullglob
for f in "$HANDOFF_DIR"/*.md; do
  base="$(basename "$f")"
  case "$base" in
    README.md|.*) continue ;;
  esac
  if already_dispatched "$f"; then
    continue
  fi
  target="$(target_session_for "$base")"
  if [[ -z "$target" ]]; then
    # Not a project handoff; mark seen and skip
    mark_dispatched "$f"
    continue
  fi
  echo "$f" >> "$TMPDIR_PENDING/$target"
done

# Dispatch one batch per target session.
for list_file in "$TMPDIR_PENDING"/*; do
  [[ -f "$list_file" ]] || continue
  target="$(basename "$list_file")"

  if ! tmux has-session -t "$target" 2>/dev/null; then
    count=$(wc -l < "$list_file")
    emit_event "handoff.dispatch_skipped" "$target" "$count" "session not running"
    # Don't mark dispatched — try again next run.
    continue
  fi

  # Build the nudge message (single line to avoid premature submit on
  # embedded newlines in Claude/Codex REPLs).
  count=$(wc -l < "$list_file")
  newest="$(sort "$list_file" | tail -1)"

  nudge="[handoff-dispatcher] ${count} new handoff(s) for ${target} in /opt/workspace/runtime/.handoff/ (newest: ${newest}). Read per ADR-0020 — reversible work ships with commits + CURRENT_STATE.md update; reserve asks for principal-only decisions. Use 'ls /opt/workspace/runtime/.handoff/${target}-*' to see all addressed to you."

  # The Claude Code REPL wraps long input across display lines and the first
  # Enter can land inside the wrapped buffer instead of submitting. Send the
  # text, wait, then send Enter twice to guarantee submit.
  tmux send-keys -t "$target" "$nudge"
  sleep 0.3
  tmux send-keys -t "$target" Enter
  sleep 0.3
  tmux send-keys -t "$target" Enter

  emit_event "handoff.dispatched" "$target" "$count" "tmux batch nudge"

  # Mark all files in this batch as dispatched.
  while IFS= read -r path; do
    mark_dispatched "$path"
  done < "$list_file"
done
