#!/usr/bin/env bash
set -euo pipefail

failures=0

pass() {
  printf 'PASS  %s\n' "$1"
}

warn() {
  printf 'WARN  %s\n' "$1"
}

fail() {
  printf 'FAIL  %s\n' "$1"
  failures=1
}

check_bin() {
  local bin="$1"
  if command -v "$bin" >/dev/null 2>&1; then
    pass "$bin on PATH: $(command -v "$bin")"
  else
    fail "$bin is missing from PATH"
  fi
}

check_file() {
  local path="$1"
  if [[ -f "$path" ]]; then
    pass "present: $path"
  else
    fail "missing required file: $path"
  fi
}

echo "Codex host preflight for $(hostname)"

check_bin codex
check_bin bwrap
check_bin git
check_bin tmux
check_bin node
check_bin python3

check_file /root/.codex/config.toml

if [[ -f /root/.codex/auth.json ]]; then
  pass "present: /root/.codex/auth.json"
else
  warn "missing /root/.codex/auth.json (interactive login may be required)"
fi

codex_version_output="$(codex --version 2>&1 || true)"
if [[ "$codex_version_output" == *"codex-cli"* ]]; then
  pass "codex version: $(printf '%s\n' "$codex_version_output" | tail -n1)"
else
  fail "unable to read Codex version"
fi

if [[ "$codex_version_output" == *"could not update PATH"* ]]; then
  warn "Codex reported a PATH update warning; this is usually harmless in locked-down environments"
fi

if [[ -n "${CODEX_THREAD_ID:-}" ]]; then
  warn "codex sandbox smoke test skipped because the check is running inside a Codex-managed session"
else
  sandbox_output="$(codex sandbox linux /bin/sh -lc 'printf sandbox-ok' 2>&1 || true)"
  if [[ "$sandbox_output" == *"sandbox-ok"* ]]; then
    pass "codex sandbox smoke test passed"
  else
    fail "codex sandbox smoke test failed"
  fi

  if [[ "$sandbox_output" == *"could not find bubblewrap on PATH"* ]]; then
    fail "Codex is still falling back to vendored bubblewrap"
  fi
fi

userns_setting="$(cat /proc/sys/user/max_user_namespaces 2>/dev/null || true)"
if [[ -n "$userns_setting" ]]; then
  if [[ "$userns_setting" -gt 0 ]]; then
    pass "user namespaces enabled: /proc/sys/user/max_user_namespaces=$userns_setting"
  else
    warn "user namespaces disabled: /proc/sys/user/max_user_namespaces=$userns_setting"
  fi
fi

exit "$failures"
