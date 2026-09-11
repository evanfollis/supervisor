#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "$0")/.." && pwd)
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT

cat > "$tmp/codex" <<'SH'
#!/usr/bin/env bash
printf '%s\n' "$*" >> "${CODEX_TEST_ARGS:?}"
if [[ "${1:-}" == --version ]]; then
  echo 'codex-cli test'
  exit 0
fi
if [[ "${1:-}" == login && "${2:-}" == status ]]; then
  echo 'Logged in using ChatGPT'
  exit 0
fi
if [[ "${1:-}" == sandbox && "${2:-}" == /bin/sh ]]; then
  echo sandbox-ok
  exit 0
fi
echo "unexpected codex invocation: $*" >&2
exit 1
SH
chmod +x "$tmp/codex"
for bin in bwrap git tmux node python3; do
  ln -s /bin/true "$tmp/$bin"
done
touch "$tmp/config.toml"

export CODEX_TEST_ARGS="$tmp/args"
export CODEX_CONFIG_PATH="$tmp/config.toml"
export CODEX_THREAD_ID=test-managed-session
output=$(PATH="$tmp:$PATH" "$ROOT/scripts/lib/check-codex-host.sh")
grep -q '^Codex dependency preflight ' <<<"$output"
grep -q 'not capability or host-control attestation' <<<"$output"
grep -q 'PASS  codex subscription login is active' <<<"$output"
grep -q 'PASS  codex sandbox smoke test passed' <<<"$output"
grep -q '^login status$' "$CODEX_TEST_ARGS"
grep -q '^sandbox /bin/sh -lc printf sandbox-ok$' "$CODEX_TEST_ARGS"
if grep -q '^sandbox linux ' "$CODEX_TEST_ARGS"; then
  echo 'obsolete codex sandbox linux syntax was used' >&2
  exit 1
fi

echo 'check-codex-host current CLI syntax: PASS'
