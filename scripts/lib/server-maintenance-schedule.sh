#!/usr/bin/env bash
# Weekly Codex synthesis over daily maintenance reports to propose a stable
# server maintenance cadence and next operator window.

set -euo pipefail

LIB_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$LIB_DIR/workspace-paths.sh"
META_DIR="$WORKSPACE_META_DIR"
HANDOFF_DIR="$WORKSPACE_HANDOFF_DIR"
mkdir -p "$META_DIR" "$HANDOFF_DIR"

ISO_NOW="$(date -u +%Y-%m-%dT%H-%M-%SZ)"
RAW_JSON="$META_DIR/server-maintenance-schedule-${ISO_NOW}.json"
REPORT_FILE="$META_DIR/server-maintenance-schedule-${ISO_NOW}.md"
LATEST_PTR="$WORKSPACE_LATEST_SERVER_MAINTENANCE_SCHEDULE_PTR"
PROMPT_FILE="/tmp/server-maintenance-schedule-prompt-${ISO_NOW}.md"

sed \
  -e "s|{{WORKSPACE_META_DIR}}|$WORKSPACE_META_DIR|g" \
  -e "s|{{WORKSPACE_REMOTE_SETUP_MD}}|$WORKSPACE_REMOTE_SETUP_MD|g" \
  "$LIB_DIR/server-maintenance-schedule-prompt.md" > "$PROMPT_FILE"

codex exec \
  --skip-git-repo-check \
  -C "$WORKSPACE_ROOT" \
  -s read-only \
  --output-schema "$LIB_DIR/server-maintenance-schedule-schema.json" \
  -o "$RAW_JSON" \
  - < "$PROMPT_FILE"

python3 - "$RAW_JSON" "$REPORT_FILE" "$HANDOFF_DIR" "$ISO_NOW" <<'PY'
import json
import pathlib
import sys

raw_json = pathlib.Path(sys.argv[1])
report_path = pathlib.Path(sys.argv[2])
handoff_dir = pathlib.Path(sys.argv[3])
iso_now = sys.argv[4]
data = json.loads(raw_json.read_text())

lines = [
    "# Weekly Server Maintenance Schedule",
    "",
    f"- Generated: {iso_now}",
    f"- Overall status: `{data['overall_status']}`",
    f"- Next maintenance window: {data['next_maintenance_window']}",
    "",
    "## Summary",
    "",
    data["summary"],
    "",
    "## Scheduled Tasks",
    "",
]

if data["scheduled_tasks"]:
    for task in data["scheduled_tasks"]:
        lines.append(f"- `{task['priority']}` `{task['cadence']}` {task['title']} — {task['reason']}")
        lines.append(f"  Window: {task['recommended_window']}")
        if task["commands"]:
            lines.append("  Commands:")
            for command in task["commands"]:
                lines.append(f"  - `{command}`")
else:
    lines.append("- No scheduled maintenance tasks proposed.")

lines.extend(["", "## Automation Improvements", ""])
if data["automation_improvements"]:
    for item in data["automation_improvements"]:
        lines.append(f"- {item}")
else:
    lines.append("- No automation changes proposed this week.")

report_path.write_text("\n".join(lines) + "\n")

if data["handoff_required"]:
    handoff_path = handoff_dir / f"general-server-maintenance-schedule-{iso_now}.md"
    handoff_lines = [
        f"Weekly server maintenance schedule generated at {iso_now}.",
        "",
        data["handoff_note"],
        "",
        f"Report: {report_path}",
    ]
    if data["scheduled_tasks"]:
        handoff_lines.append("")
        handoff_lines.append("Scheduled tasks:")
        for task in data["scheduled_tasks"]:
            handoff_lines.append(f"- {task['priority']}: {task['title']} [{task['cadence']}]")
    handoff_path.write_text("\n".join(handoff_lines) + "\n")
PY

echo "$REPORT_FILE" > "$LATEST_PTR"

if command -v tmux >/dev/null 2>&1 && tmux has-session -t general 2>/dev/null; then
  tmux display-message -t general "weekly maintenance schedule ready: $REPORT_FILE"
fi

rm -f "$PROMPT_FILE"
echo "$REPORT_FILE"
