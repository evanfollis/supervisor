# Playbook update proposal: tick handoff consumption gate

**Written**: 2026-04-17T04:47Z (supervisor tick)
**Source**: cross-cutting-2026-04-17T03-23-27Z.md Proposal 1
**Requires**: attended session — editing `scripts/lib/supervisor-project-tick-prompt.md` (Tier C for ticks)

## What to add

After the "read CURRENT_STATE.md" instruction in `supervisor-project-tick-prompt.md`, insert:

> **Before starting prescribed work, check for pending handoffs:**
> ```
> ls /opt/workspace/runtime/.handoff/<project-name>-* 2>/dev/null
> ```
> If handoffs exist, read and execute them before running the normal tick agenda. After completing a handoff, delete the file. If a handoff is blocked (requires permissions you don't have, depends on external action), note the blocker in your completion report but do not delete the file.

## Why

The preflight evidence handoff (`skillfoundry-preflight-evidence-2026-04-16T23-15Z.md`) sat for 2 cycles unread because the skillfoundry-harness tick session never checked `runtime/.handoff/skillfoundry-*`. The command homepage redesign handoff (`command-homepage-redesign-2026-04-16T12-30Z.md`) sat >38h for the same reason. Tick sessions run their prescribed loop without checking if incoming work has been routed to them.

## Blast radius

All project tick sessions. The change is automatic once the prompt is updated. No impact on attended sessions or supervisor ticks (which already check INBOX/).

## Reference

- Synthesis: `/opt/workspace/runtime/.meta/cross-cutting-2026-04-17T03-23-27Z.md` §Proposal 1
- Affected prompt: `/opt/workspace/supervisor/scripts/lib/supervisor-project-tick-prompt.md`
