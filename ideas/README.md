# Ideas

Durable ledger of novel ideas, experiments, and structural proposals being
governed by the supervisor.

## Purpose

This directory exists so novelty becomes a governed control-plane object
instead of a conversational impulse.

Each idea record should be durable enough that a future supervisor instance can
understand:

- what the idea is
- what layer it affects
- what structure it would disturb
- what evidence exists for or against it
- what the current disposition is
- what should happen next

## Record shape

Each file is pretty-printed JSON named:

`IDEA-NNNN-<slug>.json`

Minimum fields:

- `id`
- `slug`
- `title`
- `status`
- `summary`
- `proposer`
- `scope`
- `target_layer`
- `created_at`
- `updated_at`
- `next_step`

Optional fields:

- `disturbs`
- `evidence`
- `artifacts`
- `disposition_rationale`
- `priority`
- `compoundability`
- `risk`
- `review_after`

## Lifecycle statuses

- `captured`
- `framed`
- `pressure_tested`
- `adopted`
- `sandboxed`
- `deferred`
- `rejected`

## CLI

Use the supervisor ledger helper through:

```bash
workspace.sh idea new --title "..." --summary "..."
workspace.sh idea update IDEA-0001 --status sandboxed --next-step "Run bounded trial"
workspace.sh idea list
workspace.sh idea show IDEA-0001
```

The ledger helper appends supervisor events when records are created or updated.
Those events, together with git history, are the durable change history for an
idea record. The idea file itself should reflect current state only.

The active working set is derived separately into the runtime idea-focus queue.
Use:

```bash
workspace.sh idea-focus
```

to regenerate it manually. The systemd timer should keep it fresh automatically.

## Rule

Do not let a novel idea reshape the workspace until it has at least been
captured and framed here.
