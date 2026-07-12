#!/usr/bin/env bash
# Shared bounded tick-branch lifecycle helpers.

tick_branch_refs() {
  git -C "$1" for-each-ref --format='%(refname)' refs/heads/ticks 2>/dev/null
}

tick_branch_count() {
  tick_branch_refs "$1" | awk 'NF {count++} END {print count+0}'
}

tick_branch_class() {
  local repo="$1" count ref
  count=$(tick_branch_count "$repo")
  if (( count == 0 )); then
    printf 'empty\n'
    return 0
  fi
  if (( count > 1 )); then
    printf 'multiple\n'
    return 0
  fi
  ref=$(tick_branch_refs "$repo")
  if [[ "$ref" == refs/heads/ticks/pending ]]; then
    printf 'pending\n'
  else
    printf 'unexpected\n'
  fi
}

tick_branch_blocking_summary() {
  local repo="$1"
  tick_branch_refs "$repo" | while IFS= read -r ref; do
    [[ -z "$ref" ]] && continue
    printf '%s %s\n' "$ref" "$(git -C "$repo" rev-parse "$ref" 2>/dev/null || printf unknown)"
  done
}

tick_branch_create_pending() {
  local repo="$1" base="$2"
  # `git branch` refuses an existing ref; this must never become a force update.
  git -C "$repo" branch --no-track ticks/pending "$base"
}

tick_branch_delete_empty_pending() {
  local repo="$1" base="$2" current
  current=$(git -C "$repo" rev-parse refs/heads/ticks/pending 2>/dev/null || return 1)
  [[ "$current" == "$base" ]] || return 1
  git -C "$repo" update-ref -d refs/heads/ticks/pending "$base"
}
