#!/usr/bin/env bash
# Generic pre-deploy checklist. Source or invoke with a project directory.
# Extracted from skillfoundry-harness/scripts/preflight-deploy.sh + command/scripts/check-patterns.ts
# so every project can gate on the same baseline.
#
# Usage: preflight-deploy.sh [dir]
# Exit 0 on pass, 1 on fail.

set -euo pipefail
DIR="${1:-.}"
cd "$DIR"
FAIL=0

say()   { printf "%-44s %s\n" "$1" "$2"; }
check() { if eval "$2" >/dev/null 2>&1; then say "$1" "✓"; else say "$1" "✗"; FAIL=1; fi; }

echo "=== Workspace preflight: $(pwd) ==="

# --- Secrets hygiene (universal) ---
check ".gitignore present"                "test -f .gitignore"
check ".gitignore excludes env/key/token" "grep -qE '(\\*token\\*|\\*\\.key|\\.env)' .gitignore"
check "No secret-looking files tracked"   "! git ls-files 2>/dev/null | grep -iE '(token|secret|\\.env$|\\.key$|credentials)'"

# --- Bloat (universal) ---
check ".gitignore excludes node_modules"  "! test -d node_modules || grep -q '^node_modules' .gitignore"
check "No node_modules tracked"           "! git ls-files 2>/dev/null | grep -q '^node_modules/'"
check ".gitignore excludes __pycache__"   "! find . -name __pycache__ -not -path './.git/*' -print -quit 2>/dev/null | grep -q . || grep -q '__pycache__' .gitignore"

# --- Anti-patterns caught by Command's check-patterns.ts (apply anywhere with req.url) ---
# These scan tracked files only — skips node_modules, dist, etc.
check "No NextResponse.redirect(new URL..req.url)" \
  "! git ls-files 2>/dev/null | xargs -r grep -lE 'NextResponse\\.redirect\\(new URL\\(.+req\\.url' 2>/dev/null | grep -q ."
check "No new URL(path, req.url) in handlers"  \
  "! git ls-files 2>/dev/null | xargs -r grep -lE 'new URL\\([^,]+,\\s*req\\.url' 2>/dev/null | grep -q ."

# --- /review compliance (projects with git history) ---
# Synthesis 2026-04-14 Proposal 1: fail if commits touching code since the last
# deploy tag have no review artifact. Review evidence is a file at
# .reviews/<full-sha>.md. Projects without a deploy tag scan HEAD..HEAD~20.
# Code paths are any tracked file outside README*, *.md docs, *.json/yaml/toml
# config, and .gitignore-adjacent metadata.
if git rev-parse --git-dir >/dev/null 2>&1; then
  LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
  if [[ -n "$LAST_TAG" ]]; then
    RANGE_ARG=("$LAST_TAG..HEAD")
  else
    # No tag — scan up to the last 20 commits, or fewer if shallower history.
    DEPTH=$(git rev-list --count HEAD 2>/dev/null || echo 0)
    if (( DEPTH > 20 )); then
      RANGE_ARG=("HEAD~20..HEAD")
    else
      RANGE_ARG=("HEAD")
    fi
  fi
  UNREVIEWED=$(git log --format='%H' "${RANGE_ARG[@]}" -- \
      '*.py' '*.ts' '*.tsx' '*.js' '*.jsx' '*.go' '*.rs' '*.sh' '*.sql' \
      2>/dev/null \
    | while read -r sha; do
        [[ -z "$sha" ]] && continue
        test -f ".reviews/$sha.md" && continue
        git notes --ref=review show "$sha" >/dev/null 2>&1 && continue
        echo "$sha"
      done)
  if [[ -z "$UNREVIEWED" ]]; then
    say "Review artifacts for code commits" "✓"
  else
    say "Review artifacts for code commits" "✗"
    echo "    unreviewed SHAs (need .reviews/<sha>.md or git note): "
    echo "$UNREVIEWED" | sed 's/^/      /'
    FAIL=1
  fi
fi

# --- README / metadata (soft; warn-only could be added later) ---
check "README present"                    "test -f README.md -o -f README.rst -o -f README"

echo
if [[ $FAIL -eq 0 ]]; then
  echo "PASS — baseline preflight checks green."
  exit 0
else
  echo "FAIL — resolve checks above before deploying."
  exit 1
fi
