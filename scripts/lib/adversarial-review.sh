#!/usr/bin/env bash
# adversarial-review.sh — codex-based adversarial review (fallback for /review EROFS)
#
# Usage:
#   adversarial-review.sh <target-path> [--out <output-file>]
#
# The /review Claude Code skill writes to /root/.claude.json which is mounted
# read-only in sandboxed sessions (EROFS). This wrapper uses codex exec as an
# alternative adversarial review path. See FR-0021.
#
# Output: review markdown to stdout, optionally duplicated to --out file.

set -euo pipefail

TARGET="${1:-}"
OUT=""

if [[ -z "$TARGET" ]]; then
  echo "usage: $0 <target-path> [--out <output-file>]" >&2
  exit 2
fi

shift || true
while [[ $# -gt 0 ]]; do
  case "$1" in
    --out)
      OUT="$2"
      shift 2
      ;;
    *)
      echo "unknown arg: $1" >&2
      exit 2
      ;;
  esac
done

if [[ ! -e "$TARGET" ]]; then
  echo "target not found: $TARGET" >&2
  exit 1
fi

if ! command -v codex >/dev/null 2>&1; then
  echo "codex not installed" >&2
  exit 1
fi

PROMPT="Adversarial review of ${TARGET}.

You are a skeptical reviewer. Read the target file carefully. Then produce a review with exactly these three sections:

1. **Most dangerous assumption** — the claim that if wrong, produces the largest blast radius.
2. **Missing failure mode** — what the design does not account for that is likely to happen in practice.
3. **Boundary most likely to be collapsed in practice** — where the nominal separation will erode under real use.

Cite specific line numbers. Be terse and concrete. End with a 1-2 sentence overall verdict. Under 500 words total. Do not edit any files."

TMPFILE="$(mktemp)"
trap 'rm -f "$TMPFILE"' EXIT

if ! codex exec --skip-git-repo-check --sandbox read-only "$PROMPT" 2>&1 | tee "$TMPFILE" ; then
  echo "codex exec failed" >&2
  exit 1
fi

if [[ -n "$OUT" ]]; then
  cp "$TMPFILE" "$OUT"
  echo "review saved to: $OUT" >&2
fi
