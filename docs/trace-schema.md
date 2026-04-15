# Trace Schema

Legibility is infrastructure, not a nice-to-have. This document defines the
minimum durable traces that make recursive governance possible.

## Canonical rule

Source artifacts remain the truth. Normalized traces are indexes that make the
truth governable.

In this workspace:

- source transcripts live in agent-specific durable storage
- normalized session trace lives in `runtime/.telemetry/session-trace.jsonl`
- operational workspace events continue to live in `runtime/.telemetry/events.jsonl`

## Session manifest

Persistent sessions should have a runtime manifest in
`supervisor/sessions/<name>.json`.

Minimum shape:

```json
{
  "session_name": "general",
  "cwd": "/opt/workspace/supervisor",
  "agent": "claude",
  "role": "supervisor",
  "kind": "persistent",
  "source": "sessions.conf",
  "desired_state": "running",
  "updated_at": "2026-04-14T17:30:00Z"
}
```

Purpose:

- identify intended role without replaying launch logic
- allow trace scanners to map transcript activity to governance layers
- expose the intended steady state of the control plane

## Normalized session trace

The transcript scanner emits one JSON object per observed interaction event.

Minimum shape:

```json
{
  "ts": "2026-04-14T17:12:46.790Z",
  "source": "codex",
  "session_name": "workspace-root",
  "session_role": "supervisor",
  "cwd": "/opt/workspace",
  "actor": "user",
  "kind": "message",
  "preview": "Regarding the evaluation/feedback loop...",
  "char_count": 412,
  "trace_ref": "/root/.codex/sessions/2026/04/14/rollout-...jsonl:4",
  "thread_id": "019d8cf9-050e-7120-be03-41a58a67f06d",
  "direct_human_intervention": false
}
```

### Required fields

- `ts`
- `source`
- `session_role`
- `cwd`
- `actor`
- `kind`
- `preview`
- `trace_ref`

### Recommended fields

- `session_name`
- `thread_id`
- `char_count`
- `direct_human_intervention`

## Direct human intervention

`direct_human_intervention` should be `true` when:

- `actor` is `user`, and
- the session role is `project` or `feature`

This is not an error flag. It is a governance signal. The system must remain
coherent when the principal interacts directly with lower layers.

## Promotion trace

When repeated behavior becomes policy, the promotion should leave durable
artifacts in one of:

- `supervisor/decisions/`
- `supervisor/playbooks/`
- workspace or project `CLAUDE.md` / `AGENTS.md`

The trace should make it possible to answer:

- what repeated pattern was observed
- what resolution became policy
- where that policy now lives

## Design constraint

Do not make the normalized trace the only place where meaning exists. It is an
index to source truth, not a second transcript system.
