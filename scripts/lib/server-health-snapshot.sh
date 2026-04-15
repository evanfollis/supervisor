#!/usr/bin/env bash
# Capture a rich server-health snapshot for human and agent review.
# Also updates /opt/workspace/runtime/.health-status.txt for the dashboard.

set -euo pipefail

LIB_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$LIB_DIR/workspace-paths.sh"

META_DIR="$WORKSPACE_META_DIR"
mkdir -p "$META_DIR"

ISO_NOW="$(date -u +%Y-%m-%dT%H-%M-%SZ)"
TIMESTAMP="$(date -u '+%Y-%m-%d %H:%M UTC')"
OUTPUT_FILE="$META_DIR/server-health-${ISO_NOW}.md"
LATEST_PTR="$WORKSPACE_LATEST_SERVER_HEALTH_PTR"

ROOT_DISK_PCT="$(df -P / | awk 'NR==2 {gsub("%","",$5); print $5}')"
OPT_DISK_PCT="$(df -P /opt | awk 'NR==2 {gsub("%","",$5); print $5}')"
MEM_PCT="$(free | awk '/Mem:/ {printf "%.0f", $3/$2*100}')"
SWAP_PCT="$(free | awk '/Swap:/ {if ($2 == 0) {print 0} else {printf "%.0f", $3/$2*100}}')"
LOAD_AVG="$(awk '{print $1" "$2" "$3}' /proc/loadavg)"
UPTIME_HUMAN="$(uptime -p | sed 's/^up //')"
FAILED_UNITS="$(systemctl --failed --no-legend --plain --no-pager 2>/dev/null || true)"
FAILED_COUNT="$(printf '%s\n' "$FAILED_UNITS" | sed '/^\s*$/d' | wc -l)"

TOTAL_CONTAINERS=0
RUNNING_CONTAINERS=0
UNHEALTHY_CONTAINERS=0
EXITED_CONTAINERS=0
CONTAINER_TABLE=""
if command -v docker >/dev/null 2>&1 && docker ps >/dev/null 2>&1; then
  TOTAL_CONTAINERS="$(docker ps -aq 2>/dev/null | wc -l)"
  RUNNING_CONTAINERS="$(docker ps -q 2>/dev/null | wc -l)"
  UNHEALTHY_CONTAINERS="$(docker ps --filter 'health=unhealthy' -q 2>/dev/null | wc -l)"
  EXITED_CONTAINERS="$(docker ps -a --filter 'status=exited' -q 2>/dev/null | wc -l)"
  CONTAINER_TABLE="$(docker ps -a --format '{{.Names}}|{{.Status}}|{{.State}}' 2>/dev/null || true)"
fi

UPGRADABLE_PACKAGES_RAW="$(apt list --upgradable 2>/dev/null | sed '1d' || true)"
UPGRADABLE_COUNT="$(printf '%s\n' "$UPGRADABLE_PACKAGES_RAW" | sed '/^\s*$/d' | wc -l)"
UPGRADABLE_SAMPLE="$(printf '%s\n' "$UPGRADABLE_PACKAGES_RAW" | sed '/^\s*$/d' | head -n 20 || true)"

REBOOT_REQUIRED=false
REBOOT_PACKAGES=""
if [[ -f /run/reboot-required || -f /var/run/reboot-required ]]; then
  REBOOT_REQUIRED=true
  if [[ -f /run/reboot-required.pkgs ]]; then
    REBOOT_PACKAGES="$(cat /run/reboot-required.pkgs)"
  elif [[ -f /var/run/reboot-required.pkgs ]]; then
    REBOOT_PACKAGES="$(cat /var/run/reboot-required.pkgs)"
  fi
fi

status_of() {
  local unit="$1"
  systemctl is-active "$unit" 2>/dev/null || echo unknown
}

TUNNEL_STATUS="$(status_of cloudflared)"
DOCKER_STATUS="$(status_of docker)"
AUTODEPLOY_STATUS="$(status_of autodeploy)"
COMMAND_STATUS="$(status_of command)"

FLAGS=()
(( ROOT_DISK_PCT > 80 )) && FLAGS+=("[DISK HIGH]")
(( MEM_PCT > 90 )) && FLAGS+=("[MEM HIGH]")
(( UNHEALTHY_CONTAINERS > 0 )) && FLAGS+=("[${UNHEALTHY_CONTAINERS} UNHEALTHY]")
(( EXITED_CONTAINERS > 0 )) && FLAGS+=("[${EXITED_CONTAINERS} EXITED]")
(( FAILED_COUNT > 0 )) && FLAGS+=("[${FAILED_COUNT} FAILED UNITS]")
[[ "$TUNNEL_STATUS" != "active" ]] && FLAGS+=("[TUNNEL ${TUNNEL_STATUS^^}]")
[[ "$REBOOT_REQUIRED" == true ]] && FLAGS+=("[REBOOT REQUIRED]")
  (( UPGRADABLE_COUNT > 0 )) && FLAGS+=("[${UPGRADABLE_COUNT} UPGRADABLE]")

STATUS_LINE="disk:${ROOT_DISK_PCT}% mem:${MEM_PCT}% swap:${SWAP_PCT}% up:${UPTIME_HUMAN} containers:${RUNNING_CONTAINERS}/${TOTAL_CONTAINERS} tunnel:${TUNNEL_STATUS}"
if [[ ${#FLAGS[@]} -gt 0 ]]; then
  printf '%s — %s — %s\n' "$TIMESTAMP" "$STATUS_LINE" "${FLAGS[*]}" > "$WORKSPACE_HEALTH_STATUS_FILE"
else
  printf '%s — %s — all healthy\n' "$TIMESTAMP" "$STATUS_LINE" > "$WORKSPACE_HEALTH_STATUS_FILE"
fi

{
  echo "# Server Health Snapshot"
  echo
  echo "- Captured: $TIMESTAMP"
  echo "- Host: $(hostname -f 2>/dev/null || hostname)"
  echo "- Kernel: $(uname -r)"
  echo "- Uptime: $UPTIME_HUMAN"
  echo "- Load average: $LOAD_AVG"
  echo "- Dashboard status line: $(cat "$WORKSPACE_HEALTH_STATUS_FILE")"
  echo
  echo "## Core Metrics"
  echo
  echo "| Metric | Value |"
  echo "|---|---|"
  echo "| Root disk usage | ${ROOT_DISK_PCT}% |"
  echo "| /opt disk usage | ${OPT_DISK_PCT}% |"
  echo "| Memory usage | ${MEM_PCT}% |"
  echo "| Swap usage | ${SWAP_PCT}% |"
  echo "| Failed systemd units | ${FAILED_COUNT} |"
  echo "| Running containers | ${RUNNING_CONTAINERS}/${TOTAL_CONTAINERS} |"
  echo "| Unhealthy containers | ${UNHEALTHY_CONTAINERS} |"
  echo "| Exited containers | ${EXITED_CONTAINERS} |"
  echo "| Upgradable packages | ${UPGRADABLE_COUNT} |"
  echo "| Reboot required | ${REBOOT_REQUIRED} |"
  echo
  echo "## Service Status"
  echo
  echo "| Unit | State |"
  echo "|---|---|"
  echo "| cloudflared | ${TUNNEL_STATUS} |"
  echo "| docker | ${DOCKER_STATUS} |"
  echo "| autodeploy | ${AUTODEPLOY_STATUS} |"
  echo "| command | ${COMMAND_STATUS} |"
  for timer in workspace-reflect.timer workspace-synthesize.timer workspace-meta-prune.timer command-meta-scan.timer server-health-capture.timer server-maintenance.timer server-maintenance-schedule.timer; do
    if systemctl list-unit-files --type=timer --no-legend 2>/dev/null | awk '{print $1}' | grep -Fxq "$timer"; then
      echo "| ${timer} | $(status_of "$timer") |"
    fi
  done
  echo
  echo "## Failed Units"
  echo
  if [[ "$FAILED_COUNT" -gt 0 ]]; then
    printf '```\n%s\n```\n' "$FAILED_UNITS"
  else
    echo "No failed systemd units."
  fi
  echo
  echo "## Docker Containers"
  echo
  if [[ -n "$CONTAINER_TABLE" ]]; then
    echo "| Name | Status | State |"
    echo "|---|---|---|"
    while IFS='|' read -r name status state; do
      [[ -n "$name" ]] || continue
      echo "| $name | $status | $state |"
    done <<< "$CONTAINER_TABLE"
  else
    echo "No container data available."
  fi
  echo
  echo "## Package and Reboot State"
  echo
  echo "- Upgradable package count: ${UPGRADABLE_COUNT}"
  echo "- Reboot required: ${REBOOT_REQUIRED}"
  if [[ -n "$REBOOT_PACKAGES" ]]; then
    echo "- Reboot-required packages:"
    printf '```\n%s\n```\n' "$REBOOT_PACKAGES"
  fi
  if [[ -n "$UPGRADABLE_SAMPLE" ]]; then
    echo
    echo "Top upgradable packages:"
    printf '```\n%s\n```\n' "$UPGRADABLE_SAMPLE"
  fi
  echo
  echo "## Disk Detail"
  echo
  printf '```\n'
  df -hP / /opt
  printf '```\n'
  echo
  echo "## Codex Host Preflight"
  echo
  printf '```\n'
  "$WORKSPACE_SCRIPTS_ROOT/check-codex-host.sh" || true
  printf '```\n'
} > "$OUTPUT_FILE"

echo "$OUTPUT_FILE" > "$LATEST_PTR"
echo "$OUTPUT_FILE"
