#!/usr/bin/env bash
# ws feature/close/tree — feature session lifecycle.
# See /opt/workspace/supervisor/decisions/0002-feature-sessions.md
set -euo pipefail

LIB_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$LIB_DIR/workspace-paths.sh"

SESSIONS_DIR="$WORKSPACE_SUPERVISOR_SESSIONS_DIR"
FEATURES_ROOT="$WORKSPACE_FEATURES_ROOT"
PROJECTS_CONF="$WORKSPACE_SESSION_CONF"

mkdir -p "$SESSIONS_DIR" "$FEATURES_ROOT"

# Resolve the project for a feature session.
# If --project given, use it. Otherwise, walk up from $PWD and match against sessions.conf.
resolve_project() {
  local explicit="${1:-}"
  if [[ -n "$explicit" ]]; then echo "$explicit"; return; fi
  local pwd_abs="$PWD"
  while IFS='|' read -r name dir; do
    [[ "$name" =~ ^[[:space:]]*# ]] && continue
    [[ -z "$name" ]] && continue
    [[ "$name" == "general" ]] && continue
    if [[ "$pwd_abs" == "$dir" || "$pwd_abs" == "$dir"/* ]]; then
      echo "$name"; return
    fi
  done < "$PROJECTS_CONF"
  echo "ERROR: cannot infer project from cwd ($pwd_abs); pass --project <name>" >&2
  return 1
}

project_dir() {
  local name="$1"
  grep -E "^${name}\|" "$PROJECTS_CONF" | head -1 | cut -d'|' -f2
}

iso_now() { date -u +%Y-%m-%dT%H:%M:%SZ; }

default_branch() {
  # Resolve the project's default branch explicitly. Never fall back to
  # whatever HEAD happens to be — that silently inherits parent-repo drift.
  local dir="$1"
  local b
  b=$(git -C "$dir" symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's|^origin/||') && { echo "$b"; return; }
  for cand in main master; do
    git -C "$dir" show-ref --verify --quiet "refs/heads/$cand" && { echo "$cand"; return; }
  done
  echo "ERROR: cannot determine default branch for $dir (no origin/HEAD, no main, no master)" >&2
  return 1
}

cmd_feature() {
  local slug="" project="" agent="claude"
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --project) project="$2"; shift 2 ;;
      --agent)   agent="$2"; shift 2 ;;
      -h|--help) echo "Usage: ws feature <slug> [--project <name>] [--agent claude|codex]"; return 0 ;;
      --*) echo "unknown flag: $1" >&2; return 2 ;;
      *) if [[ -z "$slug" ]]; then slug="$1"; shift; else echo "unexpected arg: $1" >&2; return 2; fi ;;
    esac
  done
  [[ -z "$slug" ]] && { echo "Usage: ws feature <slug> [--project <name>] [--agent claude|codex]" >&2; return 2; }
  [[ "$slug" =~ ^[a-z0-9][a-z0-9-]*$ ]] || { echo "slug must be lowercase alphanumeric with hyphens" >&2; return 2; }
  [[ "$agent" == "claude" || "$agent" == "codex" ]] || { echo "--agent must be claude or codex" >&2; return 2; }

  project=$(resolve_project "$project")
  local pdir; pdir=$(project_dir "$project")
  [[ -d "$pdir/.git" || -f "$pdir/.git" ]] || { echo "ERROR: $pdir is not a git repo" >&2; return 1; }

  local tmux_name="${project}--${slug}"
  local worktree="${FEATURES_ROOT}/${project}/${slug}"
  local branch="feat/${slug}"
  local meta="${SESSIONS_DIR}/${tmux_name}.json"

  [[ -e "$meta" ]] && { echo "ERROR: feature '$tmux_name' already exists ($meta)" >&2; return 1; }
  [[ -e "$worktree" ]] && { echo "ERROR: worktree path already exists ($worktree)" >&2; return 1; }
  tmux has-session -t "$tmux_name" 2>/dev/null && { echo "ERROR: tmux session '$tmux_name' already exists" >&2; return 1; }

  local base; base=$(default_branch "$pdir") || return 1

  # Reopen path: if the branch already exists (e.g. from a prior `ws close --force`
  # that kept the branch), reuse it rather than creating a new one.
  local branch_exists=0
  if git -C "$pdir" show-ref --verify --quiet "refs/heads/$branch"; then
    branch_exists=1
  fi

  echo "ws feature: project=$project slug=$slug branch=$branch base=$base agent=$agent$([[ $branch_exists -eq 1 ]] && echo ' (reusing existing branch)')"

  if [[ $branch_exists -eq 1 ]]; then
    git -C "$pdir" worktree add "$worktree" "$branch" >&2
  else
    git -C "$pdir" worktree add -b "$branch" "$worktree" "$base" >&2
  fi

  local created; created=$(iso_now)
  cat > "$meta" <<EOF
{
  "project": "$project",
  "slug": "$slug",
  "tmux_name": "$tmux_name",
  "branch": "$branch",
  "base_branch": "$base",
  "worktree": "$worktree",
  "agent": "$agent",
  "created_at": "$created",
  "parent_session": "$project"
}
EOF

  local launch
  if [[ "$agent" == "claude" ]]; then
    launch="claude --remote-control \"$tmux_name\""
  else
    launch="codex"
  fi
  tmux new-session -d -s "$tmux_name" -c "$worktree" "$launch"

  # Event log
  local ev="$WORKSPACE_SUPERVISOR_EVENTS_FILE"
  mkdir -p "$(dirname "$ev")"
  printf '{"ts":"%s","agent":"%s","type":"feature_opened","ref":"%s","note":"opened %s on %s"}\n' \
    "$created" "$agent" "$meta" "$tmux_name" "$branch" >> "$ev"

  echo "opened: $tmux_name"
  echo "  worktree: $worktree"
  echo "  branch:   $branch"
  echo "  meta:     $meta"
  echo "attach: ws-attach $tmux_name"
}

cmd_close() {
  local name="${1:-}" force="${2:-}"
  [[ -z "$name" ]] && { echo "Usage: ws close <tmux_name> [--force]" >&2; return 2; }
  local meta="${SESSIONS_DIR}/${name}.json"
  [[ -f "$meta" ]] || { echo "ERROR: no metadata for '$name' at $meta" >&2; return 1; }

  local project slug worktree branch base
  project=$(jq -r .project "$meta")
  slug=$(jq -r .slug "$meta")
  worktree=$(jq -r .worktree "$meta")
  branch=$(jq -r .branch "$meta")
  base=$(jq -r .base_branch "$meta")
  local pdir; pdir=$(project_dir "$project")

  # Evaluate state BEFORE killing anything. If we refuse, the live session
  # stays up so the user can act on it.
  local dirty="" commits_ahead=0 merged=0 worktree_exists=0 branch_exists=0
  if [[ -d "$worktree" ]]; then
    worktree_exists=1
    dirty=$(git -C "$worktree" status --porcelain 2>/dev/null || true)
  fi
  if [[ -n "$pdir" && -d "$pdir/.git" ]] || [[ -n "$pdir" && -f "$pdir/.git" ]]; then
    if git -C "$pdir" show-ref --verify --quiet "refs/heads/$branch"; then
      branch_exists=1
      commits_ahead=$(git -C "$pdir" rev-list --count "${base}..${branch}" 2>/dev/null || echo 0)
      if git -C "$pdir" merge-base --is-ancestor "$branch" "$base" 2>/dev/null; then
        merged=1
      fi
    fi
  fi

  # Decide action before any destructive step.
  local action=""
  if [[ $worktree_exists -eq 0 && $branch_exists -eq 0 ]]; then
    action="stale_meta"
  elif [[ -z "$dirty" && "$commits_ahead" -eq 0 ]]; then
    action="empty"
  elif [[ -n "$dirty" && "$force" != "--force" ]]; then
    echo "close: uncommitted changes in $worktree:" >&2
    git -C "$worktree" status --short >&2
    echo "refusing to close (tmux session left running). Options:" >&2
    echo "  commit inside the worktree, then rerun ws close" >&2
    echo "  ws close $name --force  (discards uncommitted changes)" >&2
    return 3
  elif [[ "$commits_ahead" -gt 0 && "$merged" -eq 0 && "$force" != "--force" ]]; then
    echo "close: branch $branch has $commits_ahead commits ahead of $base, not merged" >&2
    echo "refusing to close (tmux session left running). Options:" >&2
    echo "  merge $branch into $base from the project session, then rerun ws close" >&2
    echo "  push $branch and open a PR, then rerun ws close --force (keeps the branch)" >&2
    echo "  ws close $name --force  (keeps the branch, removes worktree + meta)" >&2
    return 3
  elif [[ "$commits_ahead" -gt 0 && "$merged" -eq 0 ]]; then
    action="keep_branch"
  else
    action="merged"
  fi

  # Committed to closing. Kill tmux, then clean up.
  tmux kill-session -t "$name" 2>/dev/null && echo "killed tmux: $name" || true

  case "$action" in
    stale_meta)
      echo "close: worktree and branch already gone — removing stale metadata"
      ;;
    empty)
      echo "close: empty feature — silent cleanup"
      [[ $worktree_exists -eq 1 ]] && git -C "$pdir" worktree remove "$worktree" --force 2>/dev/null || true
      [[ $branch_exists -eq 1 ]]  && git -C "$pdir" branch -D "$branch" 2>/dev/null || true
      ;;
    keep_branch)
      echo "--force: keeping branch $branch, removing worktree + meta"
      [[ $worktree_exists -eq 1 ]] && git -C "$pdir" worktree remove "$worktree" --force 2>/dev/null || true
      ;;
    merged)
      echo "close: branch merged — cleaning up"
      [[ $worktree_exists -eq 1 ]] && git -C "$pdir" worktree remove "$worktree" --force 2>/dev/null || true
      if [[ $branch_exists -eq 1 ]]; then
        git -C "$pdir" branch -d "$branch" 2>/dev/null || git -C "$pdir" branch -D "$branch" 2>/dev/null || true
      fi
      ;;
  esac

  rm -f "$meta"

  local agent
  agent="$(jq -r '.agent // "unknown"' "$meta")"
  local ev="$WORKSPACE_SUPERVISOR_EVENTS_FILE"
  mkdir -p "$(dirname "$ev")"
  printf '{"ts":"%s","agent":"%s","type":"feature_closed","ref":"%s","note":"closed %s (%s)"}\n' \
    "$(iso_now)" "$agent" "$meta" "$name" "$action" >> "$ev"
}

cmd_tree() {
  printf 'general\n'
  local seen_features=0
  while IFS='|' read -r name dir; do
    [[ "$name" =~ ^[[:space:]]*# ]] && continue
    [[ -z "$name" ]] && continue
    [[ "$name" == "general" ]] && continue
    local tmx; tmx=$(tmux has-session -t "$name" 2>/dev/null && echo up || echo down)
    printf '├── %s (%s)\n' "$name" "$tmx"
    # Features for this project
    for meta in "$SESSIONS_DIR"/"${name}"--*.json; do
      [[ -e "$meta" ]] || continue
      seen_features=1
      local fname agent branch ftmx
      fname=$(jq -r .tmux_name "$meta")
      agent=$(jq -r .agent "$meta")
      branch=$(jq -r .branch "$meta")
      ftmx=$(tmux has-session -t "$fname" 2>/dev/null && echo up || echo down)
      printf '│   └── %s [%s] %s (%s)\n' "$fname" "$agent" "$branch" "$ftmx"
    done
  done < "$PROJECTS_CONF"
}

case "${1:-}" in
  feature) shift; cmd_feature "$@" ;;
  close)   shift; cmd_close "$@" ;;
  tree)    shift; cmd_tree "$@" ;;
  *) echo "Usage: ws-feature.sh {feature|close|tree} ..." >&2; exit 2 ;;
esac
