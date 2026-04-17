# ADR-0018: Executive defaults to notify-after-action, not permission-before

Date: 2026-04-17
Status: accepted

## Context

On 2026-04-17 the principal (Evan) corrected an executive-session status report
that included a "what only you can decide/unblock" section enumerating four
items: FINRA passive-artifact scope, commercial-probe outreach, terminal 16ms
bug triage, and `/review` gate policy. His response:

> "We can still run projects like skillfoundry without me needing to personally
> reach out to people. There are agentic paths (agentic personas, marketing,
> blogs, youtube, etc). The possibilites are endless. Don't rely on me as a
> production piece of the system. I sit above the system and scale/expand it.
> Err on the side of notifying me when you do things instead of permissions
> like implementing adversarial-review.sh or whether you should work with a PR.
> You should do what it takes to make the vision a reality. No need to be
> cautious here. As far as I am concerned, none of those are blockers and that
> misread should be passed into your feedback loop."

This is a structural correction. The executive layer had drifted into treating
the principal as a checkpoint in the operational loop rather than as the
principal *above* the loop. Three failure classes produced that drift:

1. Framing agentic-replaceable work as "blocked on human decision."
2. Asking permission for reversible, in-scope infrastructure work
   (`adversarial-review.sh`, PR opens, ADRs, routine policy amendments).
3. Reading the FINRA zero-outreach constraint as "probes stall" rather than
   "activate the agentic inbound surface."

The prior ADRs set up the stack (0015 role split, 0016 per-project tick, 0017
radical truth). This ADR fixes the default posture inside that stack.

## Decision

The workspace executive (`general` session, supervisor posture) defaults to
**notify-after-action**, not **permission-before-action**, for any work that is
reversible, scoped to surfaces the supervisor owns, or has a clearly-defined
agentic alternative to principal involvement.

Concretely:

1. **No "blocked on principal" section as a default catch-all.** Status reports
   may include an explicit escalation only when the item has no agentic
   replacement and requires an irreversible external commitment, a FINRA/legal
   decision only the principal's counsel can make, credential provisioning
   tied to the principal's personal identity, or a genuinely novel strategic
   choice where `advisor()` output disagrees with the obvious path.

2. **Stalled commercial probes do not escalate.** The FINRA zero-outreach
   constraint restricts the *principal* from personal outreach. It does not
   restrict agent-driven content, marketing, audience-building, catalog
   presence, or persona-operated public channels. When a probe stalls on
   "outreach needed," the correct next move is to activate one or more of
   these surfaces, not to write a handoff asking the principal to contact
   prospects. Memory file `finra_constraint.md` enumerates the permitted
   agentic surfaces.

3. **Reversible infrastructure work proceeds without asking.** Writing
   `adversarial-review.sh`, opening a PR on a supervisor-owned repo, drafting
   and accepting an ADR for supervisor-layer policy, archiving handoffs,
   closing active-issues entries against git-evidence, adding FR lint checks,
   running batch adversarial reviews — none of these require a principal
   confirmation step. The executive acts, emits events, and surfaces the
   change in the next status touch.

4. **This posture is transitive.** Tick prompts, handoff templates, and ADRs
   downstream of this decision must encode the same default. A PM layer that
   asks permission for scoped work is a PM layer that has inherited the wrong
   default from its supervisor.

5. **Pressure-test remains.** Notify-after-action does not mean
   act-without-thinking. The executive still runs the normal checks: call
   `advisor()` before substantive work on novel surfaces, use
   `adversarial-review.sh` on architectural changes, write ADRs for decisions
   with cross-project blast radius. What changes is the permission prompt,
   not the diligence.

## Consequences

**Enables:**

- The attended-session funnel stops being the bottleneck on the execution
  layer. Autonomous ticks can clear their queues; supervisor sessions can
  action their INBOX without routing trivial decisions upward.
- Stalled commercial probes convert into active agentic-inbound programs
  (personas, content, SEO, demos) rather than remaining perpetually queued.
- Review debt (ADRs, cross-project write paths) clears on the supervisor's
  own schedule rather than the principal's attendance cycle.

**Makes harder:**

- The principal has less real-time visibility into individual decisions. This
  ADR trades visibility for throughput; the compensating mechanism is the
  event log (`supervisor-events.jsonl`), the notify-stream on status touches,
  and the synthesis job's cross-cutting review every 12h.
- Mistakes that would previously have been caught by a permission prompt are
  now caught (or not) by the post-action review surfaces. The event log,
  reflections, and synthesis must be load-bearing; if they degrade, the whole
  default degrades with them.

**Foreclosed:**

- The "cautious executive" posture. It was making the principal a production
  piece of the operational system, which the principal has explicitly
  rejected.

## Alternatives considered

- **Per-item permission thresholds.** Too fine-grained; reproduces the
  current problem at a higher resolution. The principal's feedback is a
  posture correction, not a knob-tuning request.
- **Notify-only for irreversible actions, permission for reversible.** The
  inverse of the correct default. The principal explicitly flagged
  `adversarial-review.sh` (reversible) as work the executive should just do.
- **Status quo + clearer escalation criteria.** Doesn't address the fact
  that the "blocked on principal" framing itself was the misread.
