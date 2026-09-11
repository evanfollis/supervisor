#!/usr/bin/env bash
# verify-state.sh — produce supervisor/system/verified-state.md from PRIMARY sources only.
#
# Output format is stable so sessions, ticks, and the principal can diff it across runs.
# Never reads tick-generated narrative; only queries the host and the repos.
#
# Usage:
#   scripts/lib/verify-state.sh            # writes to system/verified-state.md
#   scripts/lib/verify-state.sh --stdout   # prints to stdout only
#
# This script MUST remain fast (<10s) so sessions actually run it.
set -euo pipefail

WORKSPACE=/opt/workspace
SUPERVISOR=$WORKSPACE/supervisor
RUNTIME=$WORKSPACE/runtime
OUT=$SUPERVISOR/system/verified-state.md

STDOUT=0
if [[ "${1:-}" == "--stdout" ]]; then STDOUT=1; fi

TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
NOW_EPOCH=$(date -u +%s)
STALE_THRESHOLD_SECONDS=900

warn_if_existing_verified_state_stale() {
  [[ -f "$OUT" ]] || return 0
  local generated_ts generated_epoch age
  generated_ts=$(grep '^generated:' "$OUT" 2>/dev/null | head -1 | awk '{print $2}')
  [[ -n "$generated_ts" ]] || return 0
  generated_epoch=$(date -u -d "$generated_ts" +%s 2>/dev/null || echo 0)
  [[ "$generated_epoch" =~ ^[0-9]+$ ]] || generated_epoch=0
  (( generated_epoch > 0 )) || return 0
  age=$(( NOW_EPOCH - generated_epoch ))
  if (( age > STALE_THRESHOLD_SECONDS )); then
    printf 'WARN: verified-state.md content is %dm stale (generated: %s)\n' \
      $(( age / 60 )) "$generated_ts" >&2
  fi
}

warn_if_existing_verified_state_stale

q() { # quiet-fail command substitution
  "$@" 2>/dev/null || echo "(unavailable)"
}

inbox_actionable_count() {
  find "$SUPERVISOR/handoffs/INBOX" -maxdepth 1 -type f \
    ! -name '.gitkeep' \
    ! -name 'session-summary-*.md' 2>/dev/null | wc -l
}

inbox_actionable_items() {
  local items
  items=$(find "$SUPERVISOR/handoffs/INBOX" -maxdepth 1 -type f \
    ! -name '.gitkeep' \
    ! -name 'session-summary-*.md' -printf '%f\n' 2>/dev/null | sort | head -10 | sed 's/^/  - /')
  [[ -n "$items" ]] && printf '%s' "$items" || printf '(none)'
}

general_actionable_count() {
  find "$RUNTIME/.handoff" -maxdepth 1 -type f -name 'general-*.md' \
    ! -name 'general-*-complete-*.md' \
    ! -name 'general-*-tick-complete-*.md' \
    ! -name 'general-cowork-loop-closed-confirmation-*.md' 2>/dev/null | wc -l
}

supervisor_dirty_state() {
  local dirty
  dirty=$(cd "$SUPERVISOR" && git status --short -- . ':!system/verified-state.md' 2>/dev/null || true)
  [[ -z "$dirty" ]] && echo "clean" || echo "DIRTY — run git status"
}

http_probe() {
  local url=$1 marker=$2 body code marker_state
  body=$(mktemp)
  code=$(curl -L -s -o "$body" -w "%{http_code}" --max-time 5 "$url" 2>/dev/null || true)
  if [[ -z "$code" || "$code" == "000" ]]; then
    code="unobservable"
    marker_state="unobservable"
  elif grep -Fqi -- "$marker" "$body"; then
    marker_state="expected-marker-present"
  else
    marker_state="EXPECTED-MARKER-MISSING"
  fi
  rm -f "$body"
  printf '%s; marker=%s' "$code" "$marker_state"
}

kernel_pending() {
  local running newest
  running=$(uname -r)
  newest=$(ls /boot/vmlinuz-* 2>/dev/null | sed 's|/boot/vmlinuz-||' | sort -V | tail -1 || true)
  if [[ -z "$newest" ]]; then
    echo "unobservable — installed kernel inventory unavailable"
    return
  fi
  if [[ "$running" == "$newest" ]]; then
    echo "no"
  else
    echo "YES — running $running, newest installed $newest"
  fi
}

installed_kernels() {
  local kernels
  kernels=$(ls /boot/vmlinuz-* 2>/dev/null | sed 's|/boot/vmlinuz-||' | paste -sd ', ' || true)
  [[ -n "$kernels" ]] && printf '%s' "$kernels" || printf '(unobservable)'
}

svc() {
  local unit=$1
  local state load
  load=$(systemctl show "$unit" -p LoadState --value 2>/dev/null || true)
  if [[ -z "$load" ]]; then
    printf "%-40s %-10s since %s\n" "$unit" "unobservable" "(n/a)"
    return
  fi
  if [[ "$load" == "not-found" ]]; then
    printf "%-40s %-10s since %s\n" "$unit" "missing" "(n/a)"
    return
  fi
  state=$(systemctl is-active "$unit" 2>/dev/null || true)
  local since
  since=$(systemctl show "$unit" -p ActiveEnterTimestamp --value 2>/dev/null || true)
  printf "%-40s %-10s since %s\n" "$unit" "$state" "${since:-(n/a)}"
}

file_readiness() {
  local path=$1
  if [[ -r "$path" ]]; then
    echo "present and readable"
  elif [[ -e "$path" ]]; then
    echo "present but unreadable"
  else
    echo "absent"
  fi
}

claude_readiness() {
  local status
  command -v claude >/dev/null 2>&1 || { echo "unobservable — CLI unavailable"; return; }
  status=$(claude auth status --json 2>/dev/null || true)
  if jq -e '.loggedIn == true' >/dev/null 2>&1 <<<"$status"; then
    echo "logged in"
  else
    echo "not logged in or unobservable"
  fi
}

codex_readiness() {
  local status
  command -v codex >/dev/null 2>&1 || { echo "unobservable — CLI unavailable"; return; }
  status=$(codex login status 2>&1 || true)
  if [[ "$status" == *"Logged in"* ]]; then
    echo "logged in"
  else
    echo "not logged in or unobservable"
  fi
}

BUF=$(mktemp)
exec 3>"$BUF"

cat >&3 <<HEADER
---
name: Verified system state
description: Locally observed primary-source snapshot of workspace state. Generated by scripts/lib/verify-state.sh. Never hand-edit — re-run the script. This is primary evidence for the observations captured at the generated time; active-issues.md is curated pressure, not state.
updated: $(date -u +%Y-%m-%d)
generated: $TS
---

# Verified system state

This file is generated. Do not edit by hand. Principal-facing claims about the
locally observable kernel, services, public URLs, or CLI access readiness must
be consistent with this timestamped evidence (not inferred from
\`active-issues.md\`, which is curated pressure). \`unobservable\` means the
generator lacked evidence; it never means absent or inactive.

## Host

- **Kernel running**: $(q uname -r)
- **Kernels installed**: $(installed_kernels)
- **Reboot pending**: $(kernel_pending)
- **Uptime**: $(uptime -p 2>/dev/null || echo "(unavailable)")
- **Disk /**: $(df -h / | awk 'NR==2 {print $3" used / "$2" total ("$5" full)"}')
- **Memory**: $(free -h | awk 'NR==2 {print $3" used / "$2" total"}')

## Services (workspace scope)

\`\`\`
$(svc cloudflared.service)
$(svc command.service)
$(svc launchpad-lint.service)
$(svc preflight.service)
$(svc preflight-watcher.service)
$(svc workspace-session@atlas.service)
$(svc workspace-session@command.service)
$(svc workspace-session@context-repo.service)
$(svc workspace-session@general.service)
$(svc workspace-session@skillfoundry.service)
\`\`\`

## Public URLs (live HTTP and expected-marker check)

These are fast availability/surface probes, not release-identity receipts.
Project deployments still require their declared immutable-origin and body
digest or exact behavior checks.

HEADER

while IFS='|' read -r url marker; do
  result=$(http_probe "$url" "$marker")
  echo "- \`$result\` $url" >&3
done <<'URLS'
https://synaplex.ai/|A discovery system in public
https://synaplex.ai/research|Registered research
https://command.synaplex.ai/|Owner Observatory
https://command.synaplex.ai/login|Owner Observatory
https://skillfoundry.synaplex.ai/products/launchpad-lint/|MCP Marketplace Launch Auditor
https://skillfoundry.synaplex.ai/|Tools for agent builders
https://preflight.skillfoundry.workers.dev/health|"service":"preflight","status":"ok"
URLS

cat >&3 <<ACCESS

## Locally observable access readiness

| Surface | Observation | Primary source |
|---|---|---|
| Cloudflare tunnel | $(svc cloudflared.service | awk '{print $2}') | systemd unit state |
| Cloudflare automation credential file | $(file_readiness "$RUNTIME/.secrets/cloudflare_api_token") | local filesystem metadata; contents not read |
| Claude subscription CLI | $(claude_readiness) | \`claude auth status --json\`; non-secret fields only |
| Codex subscription CLI | $(codex_readiness) | \`codex login status\` |

Account ownership, billing, registrar, and marketplace history are intentionally
excluded because this host cannot live-verify them. Administrative register:
\`supervisor/system/paid-services.md\`.

## Control-plane sensors (not decision authority)

- **Supervisor HEAD**: $(cd $SUPERVISOR && git rev-parse --short HEAD) — $(cd $SUPERVISOR && git log -1 --pretty=%s)
- **Dirty tree**: $(supervisor_dirty_state)
- **INBOX count**: $(inbox_actionable_count) item(s)
- **INBOX items**: $(inbox_actionable_items)
- **general handoffs pending**: $(general_actionable_count)
- **Aged tick branches (>24h)**: $(aged_ticks=$(cd "$SUPERVISOR" && git for-each-ref --format='%(refname:short)|%(committerdate:unix)' 'refs/heads/ticks/*' 2>/dev/null | awk -F'|' -v now="$NOW_EPOCH" 'NF == 2 && $2 ~ /^[0-9]+$/ && now - $2 > 86400 {print "  - "$1" age_seconds="now-$2}' | head -5); [[ -n "$aged_ticks" ]] && printf '%s' "$aged_ticks" || printf '(none)')

---
_Regenerated: \`$SUPERVISOR/scripts/lib/verify-state.sh\`. If this file is older than 1h and you're about to make a principal-facing claim, re-run first._
ACCESS

exec 3>&-

if [[ $STDOUT -eq 1 ]]; then
  cat "$BUF"
else
  mv "$BUF" "$OUT"
  echo "wrote: $OUT"
fi
