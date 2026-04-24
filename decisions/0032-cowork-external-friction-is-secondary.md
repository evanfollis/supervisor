# ADR-0032: Cowork is an external friction surface and secondary to the system backlog

Date: 2026-04-24
Status: accepted

## Context

On 2026-04-23 the workspace gained a bidirectional path with the principal's
Claude Cowork environment:

- Cowork can read selected substrate artifacts on a lagged cadence.
- Cowork can emit files into `runtime/friction/cowork/`.
- Cowork does not have shell, git, deploy, or project-code authority on this
  host.

The geometry is useful, but it creates an easy failure mode: an external
observer channel starts generating novel commentary, UI follow-ons, or
"helpful" protocol work that competes with the actual backlog the substrate
already has to execute. If that happens, cowork becomes a distraction tax on
the control plane instead of a net-subtractive source of friction.

The principal's direction on 2026-04-24 is explicit: if cowork work is
creating distraction or preventing smooth execution, it must be made a
secondary priority relative to the system backlog.

## Decision

Cowork is adopted as an **external friction surface**, not as a control-plane
dependency.

1. **Secondary priority by default.**
   Cowork-originated work yields to:
   - executive INBOX triage
   - synthesis/reflection follow-through
   - active project backlog and dispatch handoffs
   - live structural blockers affecting execution quality

2. **Non-load-bearing contract.**
   Cowork may sharpen judgment, but it may not become:
   - a validation gate
   - a required reviewer before dispatch or closure
   - a prerequisite input for synthesis, reflection, or PM execution

3. **UI and protocol follow-ons stay downstream.**
   Command-side cowork UI/panel work is not part of the critical path while
   command Phase C and broader backlog pressure remain open. The cowork path
   may exist; making it nicer is optional until the core system is running
   smoothly.

4. **Absence is not degradation.**
   If cowork emits nothing for a cycle, the substrate should make the same
   decisions it would have made without it. Silence from cowork is acceptable
   and must not block execution.

5. **Escalation threshold.**
   If cowork creates more than one new supervisory queue item without
   collapsing an existing one, treat that as a signal-quality problem and
   tighten scope rather than expanding integration.

## Consequences

- The workspace may read cowork emissions for structural seams, but it should
  do so after core backlog triage, not before.
- Cowork panels and similar niceties remain parked behind core command work.
- External commentary is preserved as useful friction without being promoted
  into hidden authority.

## Follow-ups

- `supervisor/AGENT.md` should name cowork as an external, secondary friction
  surface so executive reentry uses the same rule.
- If the substrate later wants synthesis/reflection to consume cowork
  emissions, that integration must ship with explicit non-substitution guards
  and separate conversion-rate accounting.
