#!/usr/bin/env bash
set -euo pipefail

# Regression for the pane-target failure that left handoffs marked or pending
# while `tmux send-keys -t =<session>` failed with "can't find pane".

ROOT="$(mktemp -d)"
SESSION="handoff-dispatch-test-$$"
trap 'tmux kill-session -t "$SESSION" 2>/dev/null || true; rm -rf "$ROOT"' EXIT

tmux new-session -d -s "$SESSION" "sleep 30"

# Exact-session syntax is correct for has-session.
tmux has-session -t "=$SESSION"

# Pane-oriented commands must address the active window explicitly.
resolved="$(tmux display-message -p -t "${SESSION}:" '#{session_name}')"
[[ "$resolved" == "$SESSION" ]]

tmux send-keys -t "${SESSION}:" "true"

echo "test-handoff-dispatch-target: PASS"
