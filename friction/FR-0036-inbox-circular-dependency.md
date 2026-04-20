---
id: FR-0036
title: INBOX circular dependency — tick generates INBOX entries when blocked, INBOX processing requires healthy tick or attended session
status: open
filed: 2026-04-20
---

# FR-0036 — INBOX circular dependency

## What happened

When the tick is blocked (dirty tree, lock file, or other skip condition), it emits
escalation entries to `supervisor/handoffs/INBOX/`. But INBOX processing depends on
either a healthy tick run or an attended session. If the tick is the one that's
broken, its own INBOX entries cannot be processed until an attended session fires.

This means an unhealthy tick produces an escalation, but the escalation can only be
seen by the thing that's unhealthy (or a human). There is no external escalation path
— the `tmux display-message` notification and INBOX entry are both silent to anything
outside the local server.

## Observed impact

When the tick self-blocked via FR-0035, it generated INBOX escalations that sat
unprocessed for 9+ cycles (>18h) until a human happened to attach to the general
session. No external alert fired.

## Structural gap

The current escalation chain terminates at `supervisor/handoffs/INBOX/` — visible
only to an attended session at `/opt/workspace/supervisor`. There is no outbound
notification (email, push, Slack) to reach the principal when the workspace is unattended.

## Proposed fix

An outbound notification path (e.g. push notification via workspace-notify, or email
via config/slack.env) triggered by INBOX URGENT file creation. Currently `workspace-notify.timer`
is not installed per `doctor` output.

## Status: Open
