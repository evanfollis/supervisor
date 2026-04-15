#!/usr/bin/env bash
# Run nightly Codex analysis over the latest server-health snapshot and turn it
# into a durable maintenance report plus operator handoff if needed.

set -euo pipefail

LIB_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$LIB_DIR/workspace-paths.sh"
META_DIR="$WORKSPACE_META_DIR"
HANDOFF_DIR="$WORKSPACE_HANDOFF_DIR"
mkdir -p "$META_DIR" "$HANDOFF_DIR"

ISO_NOW="$(date -u +%Y-%m-%dT%H-%M-%SZ)"
RAW_JSON="$META_DIR/server-maintenance-${ISO_NOW}.json"
REPORT_FILE="$META_DIR/server-maintenance-${ISO_NOW}.md"
LATEST_PTR="$WORKSPACE_LATEST_SERVER_MAINTENANCE_PTR"
PROMPT_FILE="/tmp/server-maintenance-prompt-${ISO_NOW}.md"

SNAPSHOT_FILE="$("$LIB_DIR/server-health-snapshot.sh" | tail -n 1)"

sed "s|{{SNAPSHOT_FILE}}|$SNAPSHOT_FILE|g" \
  "$LIB_DIR/server-maintenance-prompt.md" \
  | sed \
      -e "s|{{WORKSPACE_HEALTH_STATUS_FILE}}|$WORKSPACE_HEALTH_STATUS_FILE|g" \
      -e "s|{{WORKSPACE_REMOTE_SETUP_MD}}|$WORKSPACE_REMOTE_SETUP_MD|g" \
      -e "s|{{WORKSPACE_META_DIR}}|$WORKSPACE_META_DIR|g" \
      > "$PROMPT_FILE"

codex exec \
  --skip-git-repo-check \
  -C "$WORKSPACE_ROOT" \
  -s read-only \
  --output-schema "$LIB_DIR/server-maintenance-schema.json" \
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
    "# Nightly Server Maintenance Report",
    "",
    f"- Generated: {iso_now}",
    f"- Overall status: `{data['overall_status']}`",
    "",
    "## Summary",
    "",
    data["summary"],
    "",
    "## Key Findings",
    "",
]

if data["key_findings"]:
    for item in data["key_findings"]:
        lines.append(f"- `{item['severity']}` {item['area']}: {item['evidence']} Implication: {item['implication']}")
else:
    lines.append("- No significant findings.")

lines.extend(["", "## Assigned Maintenance Tasks", ""])
if data["maintenance_tasks"]:
    for task in data["maintenance_tasks"]:
        lines.append(f"- `{task['priority']}` {task['title']} — {task['reason']}")
        lines.append(f"  Window: {task['proposed_window']}")
        lines.append(f"  Automation candidate: {'yes' if task['automation_candidate'] else 'no'}")
        if task["commands"]:
            lines.append("  Commands:")
            for command in task["commands"]:
                lines.append(f"  - `{command}`")
else:
    lines.append("- No maintenance tasks assigned.")

report_path.write_text("\n".join(lines) + "\n")

if data["handoff_required"]:
    handoff_path = handoff_dir / f"general-server-maintenance-{iso_now}.md"
    handoff_lines = [
        f"Nightly server maintenance run at {iso_now} produced actionable work.",
        "",
        data["handoff_note"],
        "",
        f"Report: {report_path}",
    ]
    if data["maintenance_tasks"]:
        handoff_lines.append("")
        handoff_lines.append("Tasks:")
        for task in data["maintenance_tasks"]:
            handoff_lines.append(f"- {task['priority']}: {task['title']} ({task['proposed_window']})")
    handoff_path.write_text("\n".join(handoff_lines) + "\n")
PY

echo "$REPORT_FILE" > "$LATEST_PTR"

if command -v tmux >/dev/null 2>&1 && tmux has-session -t general 2>/dev/null; then
  tmux display-message -t general "nightly maintenance ready: $REPORT_FILE"
fi

rm -f "$PROMPT_FILE"
echo "$REPORT_FILE"
