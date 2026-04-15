# Project: mentor

## Current status

- **Parked, not retired.** The principal has more to build than time for
  targeted learning right now. Mentor stays in the reflection loop but
  is deprioritized.
- The global Claude-Code `Notification` / `Stop` Slack hook at
  `/root/.claude/hooks/notify-slack.sh` was sending traffic under the
  AI Mentor app across every session, which made mentor look active
  when it wasn't. That hook is now disabled (2026-04-15); AI Mentor
  traffic should drop to zero unless the bot's slash commands are used.
- Deployed instance still runs at mentor.synaplex.ai / api.synaplex.ai
  via Docker Compose at `/opt/mentor/`. Dev repo at
  `/opt/workspace/projects/career-os/mentor/` has local uncommitted WIP
  the project session owns.

## What needs to change (later, not now)

- Eventually: find a way to fold targeted-learning sessions *into*
  actual product work rather than requiring dedicated study time.
  Principal intent — don't engineer this proactively; surface it when
  an opportunity appears during other work.
- Near-term: nothing. Mentor does not need supervisor attention unless
  reflections start flagging issues.

## Retention

Keep this state file while the project is still nominally governed. If
mentor stays parked for multiple synthesis cycles without reflection
activity, reassess whether it should drop out of
`scripts/lib/projects.conf` (the reflection loop's inventory).

## Active artifact links

- Deployed path: `/opt/mentor/` (Docker Compose)
- Dev repo: `/opt/workspace/projects/career-os/mentor/`
- Slack bot: `backend/app/integrations/slack_bot.py` (slash commands)
  + `backend/app/scheduler/daily_agenda.py` (background briefings)
