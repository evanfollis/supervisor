# Playbook: Slack integration setup

**Trigger**: first-time Slack integration, or re-provisioning after a token
rotation / workspace change.

**Owner**: principal (manual Slack-side work) + supervisor (workspace-side).

**Preconditions**:
- ADR-0010 (`notes/TRIAGE/`) and ADR-0011 (Slack mobile I/O) accepted.
- Notifier scaffold present at `scripts/slack/notifier.py`.
- Systemd units present at `systemd/workspace-slack-notifier.{service,timer}`.

**Outputs**:
- A live Slack app with bot token stored in `config/slack.env`.
- Two channels the bot is a member of: `#supervisor-loop`, `#workspace-ops`.
- `workspace-slack-notifier.timer` enabled and running.
- First real card visible in Slack within 2 minutes of enabling the timer.

## Steps

### Slack-side (manual, principal)

1. **Create the Slack app.**
   - Go to <https://api.slack.com/apps> → *Create New App* → *From scratch*.
   - Name: `workspace-supervisor`. Pick the target workspace.
   - Under *OAuth & Permissions*, add these Bot Token Scopes:
     - `chat:write` — post status cards
     - `chat:write.public` — post to channels the bot isn't a member of (optional but useful)
     - `reactions:write` — Stage 2 (confirm normalizer routing)
     - `users:read` — Stage 2 (presence)
     - `channels:history` — Stage 2 (inbound)
     - `channels:join` — auto-join on channel add (optional)
     - `files:read` — Stage 2 (attachments)
   - Click *Install to Workspace*. Approve the scopes.
   - Copy the **Bot User OAuth Token** (starts with `xoxb-`).

2. **Create the channels.**
   - `#supervisor-loop` — governance activity.
   - `#workspace-ops` — operational activity.
   - `#principal-notes` — Stage 2 inbound (create now or defer).
   - Invite the `workspace-supervisor` bot into each: `/invite @workspace-supervisor`.

3. **(Stage 2 only — defer until Stage 1 is tuned.)**
   - Under *Event Subscriptions*, enable events. Subscribe to `message.channels`,
     `message_changed`, `message_deleted` for the principal-notes channel.
   - Set the Request URL to the normalizer's public endpoint (not provisioned
     yet; Stage 2 work).

### Workspace-side (supervisor)

4. **Install the token.**
   ```
   cp /opt/workspace/supervisor/config/slack.env.example \
      /opt/workspace/supervisor/config/slack.env
   chmod 600 /opt/workspace/supervisor/config/slack.env
   # Edit config/slack.env and paste the xoxb- token.
   ```

   **Verify**: `config/slack.env` exists with mode 600 and a non-empty
   `SLACK_BOT_TOKEN`. This file is gitignored.

5. **Dry-run test.**
   ```
   python3 /opt/workspace/supervisor/scripts/slack/notifier.py --once --dry-run
   tail -5 /opt/workspace/runtime/.telemetry/slack-outbound.jsonl
   ```

   **Verify**: the command exits 0 and new entries appear in
   `slack-outbound.jsonl` with `mode: dry_run`, `posted: false`.

6. **Live smoke test (single card).**
   - Ensure the bot is in `#supervisor-loop`.
   - Wipe the dedupe state so one pending event reposts live:
     ```
     jq 'del(.dedupe_keys)' /opt/workspace/runtime/.slack-state.json > /tmp/s.json && \
       mv /tmp/s.json /opt/workspace/runtime/.slack-state.json
     ```
     (Only wipe if you want to verify a live post; otherwise enable the timer and wait for the next event.)
   - Run `sudo -E env $(cat /opt/workspace/supervisor/config/slack.env | xargs) \
      python3 /opt/workspace/supervisor/scripts/slack/notifier.py --once`

   **Verify**: at least one card appears in the channel, and the
   corresponding outbound entry has `posted: true` and a `message_ts`.

7. **Enable the timer.**
   ```
   sudo ln -sf /opt/workspace/supervisor/systemd/workspace-slack-notifier.service \
     /etc/systemd/system/workspace-slack-notifier.service
   sudo ln -sf /opt/workspace/supervisor/systemd/workspace-slack-notifier.timer \
     /etc/systemd/system/workspace-slack-notifier.timer
   sudo systemctl daemon-reload
   sudo systemctl enable --now workspace-slack-notifier.timer
   systemctl list-timers workspace-slack-notifier.timer
   ```

   **Verify**: the timer shows an `ACTIVATES` time within 60 seconds.

8. **Observe Stage 1 SLOs (2-week window).**
   - latency p95 < 120s for real-time events
   - daily digest reliability ≥ 95% (Stage 1 SLO — note: digest is
     scaffolded out in current notifier, needs addition before Stage 1 exits)
   - real-time card rate ≤ 20/day/channel under normal load

   Track these in `system/active-issues.md` if SLOs slip.

## Rollback

- Disable the timer: `sudo systemctl disable --now workspace-slack-notifier.timer`.
- Revoke the bot token in the Slack admin UI if it's suspected compromised.
- Remove `config/slack.env` and rotate the token before re-enabling.

## Known gaps (Stage 1 → Stage 2 carry-forward)

- Daily digest post is not yet implemented in the notifier (Stage 1 exit
  requires it).
- Heartbeat-staleness health integration (90-min stale → incident) is
  planned but not wired up.
- Throttling (60s burst collapse, routine-event-in-digest-only) is planned
  but not wired up.
- Stage 2 normalizer (inbound) is not built; requires a public HTTP endpoint
  for Slack Events API and an `--idempotency-source`-capable ledger CLI
  (which is already in place — see `scripts/lib/idea-ledger.py`).

Track these as issues before closing Stage 1.
