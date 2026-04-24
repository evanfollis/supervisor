#!/usr/bin/env bash
# Keep runtime/.handoff focused on live executive work by archiving obvious
# completion artifacts and session summaries.

set -euo pipefail

HANDOFF_DIR="/opt/workspace/runtime/.handoff"
ARCHIVE_ROOT="${HANDOFF_DIR}/ARCHIVE"
ARCHIVE_DAY="$(date -u +%Y-%m-%d)"
ARCHIVE_DIR="${ARCHIVE_ROOT}/${ARCHIVE_DAY}"

[[ -d "$HANDOFF_DIR" ]] || exit 0

collect_breadcrumbs() {
  find "$HANDOFF_DIR" -maxdepth 1 -type f \
    \( -name 'session-summary-*.md' \
       -o -name 'general-*-complete-*.md' \
       -o -name 'general-*-tick-complete-*.md' \
       -o -name 'general-cowork-loop-closed-confirmation-*.md' \
       -o -name 'general-cowork-*-response-*.md' \) \
    -print

  while IFS= read -r candidate; do
    [[ -f "$candidate" ]] || continue
    if head -n 20 "$candidate" | grep -Eiq '^status:[[:space:]].*complete'; then
      printf '%s\n' "$candidate"
    fi
  done < <(find "$HANDOFF_DIR" -maxdepth 1 -type f -name 'general-*.md' -print)
}

mapfile -t breadcrumbs < <(collect_breadcrumbs | sort -u)

if [[ "${#breadcrumbs[@]}" -eq 0 ]]; then
  echo "archive-runtime-executive-breadcrumbs: nothing to archive"
  exit 0
fi

mkdir -p "$ARCHIVE_DIR"

for item in "${breadcrumbs[@]}"; do
  mv "$item" "$ARCHIVE_DIR/"
done

echo "archive-runtime-executive-breadcrumbs: archived ${#breadcrumbs[@]} file(s) to ${ARCHIVE_DIR}"
