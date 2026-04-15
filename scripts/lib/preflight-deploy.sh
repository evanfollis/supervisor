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
