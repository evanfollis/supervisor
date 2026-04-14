# Playbooks

Step-by-step runbooks for recurring supervisor tasks. Written so any instance
of the supervisor (Claude or Codex, current or future) can execute them
without re-deriving the procedure.

## When to add a playbook

You've done the same multi-step procedure twice, or you anticipate it
recurring. Examples:

- Onboarding a new project to the reflection loop
- Responding to a failing host health check
- Promoting a proposed gate from a synthesis file into `scripts/lib/preflight-deploy.sh`
- Closing a feature session and merging / discarding its branch
- Adding a new MCP connector to the relevant agent's config

## Format

One file per playbook: `<slug>.md`. Contents:

```
# Playbook: <title>

**Trigger**: when does this run
**Owner**: supervisor
**Preconditions**: what must be true before starting
**Steps**: numbered, each step one action + one verification
**Rollback**: how to undo if a step fails mid-way
**Outputs**: what artifacts or state changes to expect
```

## Rules

- **One trigger, one playbook.** If the same procedure handles two different triggers, split it.
- **Verification on every step.** A step that can't be verified is a step that will silently regress.
- **Named outputs.** If the playbook writes files, name them in the spec so the next run can detect partial execution.
- **Don't embed rationale.** The reasoning goes in an ADR. A playbook is the *how*, not the *why*.
