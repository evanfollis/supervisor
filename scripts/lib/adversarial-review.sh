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
      if [[ $# -lt 2 || -z "${2:-}" ]]; then
        echo "--out requires a non-empty output path" >&2
        exit 2
      fi
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
if [[ ! -f "$TARGET" || ! -r "$TARGET" ]]; then
  echo "target must be a regular readable file: $TARGET" >&2
  exit 2
fi
TARGET_SIZE_BYTES="$(wc -c < "$TARGET")"
MAX_TARGET_BYTES="${ADVERSARIAL_REVIEW_MAX_BYTES:-1048576}"
if (( TARGET_SIZE_BYTES > MAX_TARGET_BYTES )); then
  echo "target too large for single-file review: ${TARGET_SIZE_BYTES} bytes > ${MAX_TARGET_BYTES}" >&2
  exit 2
fi
TARGET_REAL="$(realpath -- "$TARGET")"
if [[ "$TARGET_REAL" == *$'\n'* || "$TARGET_REAL" == *$'\r'* ]]; then
  echo "target path contains unsupported control characters" >&2
  exit 2
fi

if [[ -n "$OUT" ]]; then
  OUT_DIR="$(dirname -- "$OUT")"
  if [[ ! -d "$OUT_DIR" ]]; then
    echo "output directory not found: $OUT_DIR" >&2
    exit 2
  fi
  if [[ -e "$OUT" ]]; then
    echo "output file already exists: $OUT" >&2
    exit 2
  fi
fi

CODEX_BIN="$(command -v codex || true)"
if [[ -z "$CODEX_BIN" ]]; then
  # systemd and non-login shells often miss the nvm-managed Node bin directory.
  # Keep this explicit rather than sourcing shell profiles in automation.
  for candidate in \
    /root/.nvm/versions/node/v22.22.0/bin/codex \
    /root/.nvm/versions/node/v22.21.0/bin/codex \
    /usr/local/bin/codex \
    /usr/bin/codex; do
    if [[ -x "$candidate" ]]; then
      CODEX_BIN="$candidate"
      export PATH="$(dirname "$candidate"):$PATH"
      break
    fi
  done
fi

if [[ -z "$CODEX_BIN" ]]; then
  echo "codex CLI not found on PATH or known install locations" >&2
  exit 1
fi

PROMPT="Adversarial review of this exact file path:

${TARGET_REAL}

You are a skeptical reviewer. Read the target file carefully. Then produce a review with exactly these three sections:

1. **Most dangerous assumption** — the claim that if wrong, produces the largest blast radius.
2. **Missing failure mode** — what the design does not account for that is likely to happen in practice.
3. **Boundary most likely to be collapsed in practice** — where the nominal separation will erode under real use.

Cite specific line numbers. Be terse and concrete. End with a 1-2 sentence overall verdict. Under 500 words total. Do not edit any files."

TMPFILE="$(mktemp)"
trap 'rm -f "$TMPFILE"' EXIT

if ! "$CODEX_BIN" exec --skip-git-repo-check --sandbox read-only "$PROMPT" 2>&1 | tee "$TMPFILE" ; then
  echo "codex exec failed" >&2
  exit 1
fi

if [[ -n "$OUT" ]]; then
  cp "$TMPFILE" "$OUT"
  echo "review saved to: $OUT" >&2
fi
