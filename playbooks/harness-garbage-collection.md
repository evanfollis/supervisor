# Playbook: Harness Garbage Collection

**Trigger**: weekly, and after any repeated failure appears in two or more
reflection windows.

**Owner**: supervisor first; project PM owns repo-local follow-through.

## Purpose

Turn recurring agent friction into durable harness improvements. A harness
improvement is one of:

- a check
- a test
- a role-specific review prompt
- a QA journey
- a front-door/context update
- a smaller task/orchestration boundary

## Procedure

1. Read the latest cross-cutting synthesis and the last seven days of project
   reflections.
2. Read recent adversarial review artifacts and accepted-tradeoff sections.
3. List repeated failure modes. Ignore one-off bugs unless they expose a missing
   invariant.
4. For each repeated mode, choose the smallest durable encoding:
   - ambiguous routing -> policy or task-state rule
   - stale state -> harness check or front-door freshness gate
   - browser uncertainty -> browser QA journey
   - repeated review comment -> lint/test/reviewer profile
   - recurring manual command -> script or workspace wrapper
5. Dispatch one small handoff per owner. Do not bundle unrelated improvements.
6. If no owner exists, create or activate a maintenance-agent manifest before
   filing more work.
7. Record what was encoded and what was deliberately left as human judgment.

## Output

Write a dated artifact under `runtime/.meta/harness-gc-<iso>.md` containing:

- input files read
- repeated patterns found
- encoding chosen for each pattern
- handoffs dispatched
- checks promoted or deferred

## Quality Bar

The pass is successful only if at least one repeated pattern becomes a concrete
artifact or an explicit deferral. A list of observations without routing is not
garbage collection.

