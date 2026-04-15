#!/bin/bash
# rate-limit-watcher.sh — Auto-dismiss Claude Code rate limit menus in tmux sessions
# Cron: */5 * * * * /opt/workspace/supervisor/rate-limit-watcher.sh >> /var/log/rate-limit-watcher.log 2>&1

SESSIONS=(general mentor skillfoundry recruiter context-repo)

for session in "${SESSIONS[@]}"; do
    if ! tmux has-session -t "$session" 2>/dev/null; then
        continue
    fi

    pane_content=$(tmux capture-pane -t "$session" -p -S -30 2>/dev/null)

    if echo "$pane_content" | grep -q "rate-limit-options"; then
        tmux send-keys -t "$session" "1" Enter
        echo "[$(date -u '+%Y-%m-%dT%H:%M:%SZ')] Rate limit detected in '$session' — selected 'Stop and wait'"
    fi
done
