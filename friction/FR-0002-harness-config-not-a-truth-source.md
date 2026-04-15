# FR-0002: Global Claude-harness config isn't declared as a truth source

Captured: 2026-04-15
Source: session (Slack notification investigation)
Status: open

## What happened

Principal asked why "AI Mentor" was sending catch-all Slack DMs from
every session. I searched the supervisor repo, then the mentor backend,
before finally looking at `/root/.claude/hooks/notify-slack.sh` and
`/root/.claude/settings.json`. The Notification/Stop hooks registered
there were the actual cause. Investigation took longer than it needed
to because the supervisor's truth-source list never mentions
`/root/.claude/`.

## Why it matters

The Claude-Code harness is the substrate supervisor *runs on*. Its
hooks, permissions, and memory shape every action the agent takes.
Treating that directory as out-of-scope for orientation means:

- Behavior-shaping config can sit for months without being noticed.
- Investigations that should take three greps take ten.
- Global hooks attributed to a project (like today's "AI Mentor" DMs)
  mislead both principal and supervisor about what's actually active.

## Root cause / failure class

**Truth-source list is incomplete.** `AGENT.md` enumerates code, git,
telemetry, decisions, ideas, manifests, server snapshots, syntheses,
reflections, user messages — but not the harness substrate. The rule
"do not treat prior supervisor conversation transcripts as truth
sources" implies the transcripts *under* `/root/.claude/` but never
disambiguates that the config files in that tree *are* authoritative.

## Proposed fix

1. Extend `AGENT.md` §Truth sources and `CLAUDE.md` to explicitly list
   `/root/.claude/settings.json`, `/root/.claude/hooks/`, and
   `/root/.claude/projects/<cwd>/memory/` as read-authoritative surfaces
   for "what this agent is configured to do."
2. Add a `workspace.sh doctor` check that scans `/root/.claude/hooks/`
   and `~/.codex/hooks/` for active hooks and lists them on session
   start. A one-line "active hooks: …" in reentry would have solved
   today's investigation instantly.
3. Reference-memory entry noting this (done 2026-04-15).

## References

- `/root/.claude/settings.json` — the hook registration
- `/root/.claude/hooks/notify-slack.sh.disabled` — today's renamed
  offender
