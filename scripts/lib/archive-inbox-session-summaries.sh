#!/usr/bin/env bash
# Archive low-priority executive reentry breadcrumbs so INBOX stays focused on
# substantive handoffs.

set -euo pipefail

INBOX_DIR="/opt/workspace/supervisor/handoffs/INBOX"
ARCHIVE_ROOT="/opt/workspace/supervisor/handoffs/ARCHIVE"
AGE_MINUTES="${1:-720}"
ARCHIVE_DAY="$(date -u +%Y-%m-%d)"
ARCHIVE_DIR="${ARCHIVE_ROOT}/${ARCHIVE_DAY}"

[[ -d "$INBOX_DIR" ]] || exit 0

mapfile -t summaries < <(find "$INBOX_DIR" -maxdepth 1 -type f -name 'session-summary-*.md' -mmin +"$AGE_MINUTES" | sort)

if [[ "${#summaries[@]}" -eq 0 ]]; then
  echo "archive-inbox-session-summaries: nothing to archive"
  exit 0
fi

mkdir -p "$ARCHIVE_DIR"

for summary in "${summaries[@]}"; do
  mv "$summary" "$ARCHIVE_DIR/"
done

echo "archive-inbox-session-summaries: archived ${#summaries[@]} file(s) to ${ARCHIVE_DIR}"
