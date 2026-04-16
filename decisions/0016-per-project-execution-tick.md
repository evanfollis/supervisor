# ADR-0016: Per-project execution tick
Date: 2026-04-16
Status: accepted

## Context

ADR-0014 established the supervisor tick as a between-session governance driver
for the supervisor repo itself. It deliberately deferred per-project execution:
the tick could *route* work (via handoffs to project sessions) but couldn't
*execute* it autonomously. That left a manual gap: handoffs piled up in
`runtime/.handoff/` and only drained when a human attended a project session.

After four synthesis cycles, the pattern of "work delegated but not done"
emerged as the primary autonomy bottleneck. The executive stack runs reliably;
the execution layer has no driver. The principal has explicitly delegated
approval authority and authorized the system to make large judgment calls
without asking permission, requesting only Slack notification for significant
actions.

## Decision

Add a per-project systemd timer (`workspace-project-tick@<name>.timer`) that
fires every 4 hours and drives project PM sessions headlessly.

**Mechanism** (`supervisor-project-tick.sh`):

1. Read `sessions.conf` to find the project cwd for the named instance.
2. Check tmux session activity — skip if the attended session was active in the
   last 15 minutes (same interlock as the supervisor tick).
3. Find the oldest pending handoff: `runtime/.handoff/<project>-*.md`.
4. If none, exit cleanly — the timer is a no-op when there's no work.
5. Render the prompt template (`supervisor-project-tick-prompt.md`) using Python
   so that multiline content (CLAUDE.md, handoff body) is safely substituted.
6. Run `claude -p <prompt>` rooted in the project cwd. The model executes the
   handoff, commits, pushes, and writes a completion or escalation report back
   to `runtime/.handoff/general-<project>-tick-{complete,escalation}-<ts>.md`.
7. Emit `project_tick_{succeeded,failed,escalated}` to `supervisor-events.jsonl`.
   The Slack notifier picks these up on its next cycle.

**Safety sandbox** (systemd unit):

- `ProtectSystem=strict` — filesystem is read-only except explicit write paths.
- `ReadWritePaths=/opt/workspace/projects` — covers all project repos including
  `career-os/` subdirs.
- `ReadWritePaths=/opt/workspace/runtime` — for handoff writes and lock files.
- `ReadWritePaths=/opt/workspace/supervisor/events` — for event emission.
- `ReadWritePaths=/root/.claude` — Claude writes transcripts here.
- `NoNewPrivileges=true`, `PrivateTmp=true`.

**Disallowed tools** (claude --disallowedTools):

- `Bash(git push --force:*)`, `Bash(git reset --hard:*)`, `Bash(git rebase:*)`
- `Bash(rm -rf:*)`, `Bash(docker:*)`, `Bash(systemctl:*)`
- `Bash(npm publish:*)`, `Bash(gh release:*)`, `NotebookEdit`

The model may push to origin (non-force) — this is intentional; the principal
has delegated approval authority.

**Timer schedule**: `OnCalendar=*-*-* 00/4:30:00` (at :30 past each 4h window:
00:30, 04:30, 08:30, 12:30, 16:30, 20:30 UTC). `RandomizedDelaySec=90min`
spreads instances so they don't all fire simultaneously. This gives at least
2.5h of human review time between tick firings before the next one picks up.

**One handoff per tick**: Each invocation processes only the oldest pending
handoff. If multiple handoffs are queued, subsequent ticks drain them. This
limits blast radius — a bad execution doesn't compound by running multiple
handoffs in one session.

## Consequences

- Project backlogs drain autonomously without human attendance.
- Completion and escalation reports land in `runtime/.handoff/` for the
  executive to review on next attended session start.
- Slack notifications go to `#workspace-ops` for completions/failures and
  `#supervisor-loop` for escalations that need principal attention.
- Handoffs that require human input generate escalation files — the notifier
  pings the principal in Slack rather than letting the tick spin silently.
- The tick is a no-op when there are no handoffs — zero cost for idle projects.

## Alternatives considered

**Expanding the supervisor tick scope**: Rejected. The supervisor tick's safety
model (ADR-0014) is built around governance-only writes. Adding project execution
would conflate governance and code mutation in a single sandboxed session,
defeating the tier model.

**Single omnibus project tick**: Considered processing all projects in one
invocation. Rejected because template-unit-per-project is simpler to enable/
disable selectively, the lock-per-project prevents races, and failures in one
project don't affect others.

**Continuous monitoring instead of timer**: Would require a persistent process
watching the handoff directory. The timer approach is simpler, more auditable,
and aligns with the existing systemd-based driver pattern.
