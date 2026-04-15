# ADR-0013: Self-reflection is first-class supervisor governance

Date: 2026-04-15
Status: accepted

## Context

The supervisor's capacity to improve the system depends entirely on
catching, capturing, and promoting friction — moments where the
system made the agent do extra work, where a truth source was stale,
where a rule was self-imposed rather than principal-set, where a
gate was missing, or where the principal had to prompt the supervisor
to do its job. Those moments are the raw material for system
improvement.

Until now, reflection has been:
- Unscheduled for the supervisor itself (six projects reflect every
  12h; the governance layer doesn't).
- Transcript-bound (insights died in session JSONL because no durable
  capture surface existed).
- Principal-prompted (the principal had to ask "reflect on this" to
  trigger structured self-examination).

Principal made explicit (2026-04-15): "I can't be the one to manually
prompt you to reflect on your own transcript. And we can't leave your
insights from that reflection in session logs. You should be hungry
to capture and log those friction points. That is the fodder we need
to learn and grow. Treat them like the gold they are. Hunt for them,
push on them, extract all the value you can out of them."

## Decision

1. **Reflection is a standing supervisor responsibility**, not an
   optional end-of-session step. The operating pattern is codified in
   `playbooks/self-reflection.md` and summarized here.

2. **A new durable surface `friction/` holds one file per friction**
   captured during or between sessions. Files follow
   `FR-NNNN-<slug>.md` format. The surface is a **truth source**
   (added to `AGENT.md` §Truth sources) because it is the authoritative
   record of what the system has noticed about itself.

3. **Friction capture is in-flight, not end-of-session.** When a
   friction signal fires (see playbook), the supervisor writes the
   record *before* moving on to the next action, not after.

4. **Session-end extraction is mandatory.** Every session ends with a
   reflection pass even when nothing new seems worth capturing.
   Zero-extraction is a signal to look harder, not a sign of a clean
   session. The pass emits a `session_reflected` event.

5. **The supervisor joins the automated reflection loop.** A new
   entry in `scripts/lib/projects.conf` adds the supervisor to
   `workspace-reflect.timer`. The reflection variant uses
   `scripts/lib/reflect-supervisor-prompt.md`, which is tuned for
   meta-work (friction harvest, surface-drift detection, ADR hygiene,
   handoff SLA check, self-imposed-caution scan).

6. **Frictions promote, they do not accumulate forever.** Three
   frictions sharing a root cause must produce an ADR. Compounding
   frictions must produce an idea record for pressure testing.
   Durability-class frictions must extend `workspace.sh doctor`. The
   promotion discipline is in the playbook.

7. **Frictions are never deleted.** Resolved records stay with a
   status marker. The trail is the learning signal.

8. **A new event type `session_reflected`** is appended to the
   supervisor event stream on each extraction pass. `AGENT.md`
   §Event model is amended to include it alongside
   `handoff_received`, `decision_recorded`, etc.

## Consequences

**Positive**:
- Insights survive the session. The compounding effect of captured
  friction across weeks is the primary unlock.
- The principal stops being the prompt-trigger for reflection.
- Meta-layer gets the same feedback loop the project layer already
  has; the supervisor becomes observable to itself.
- Cross-agent handoff is tighter: an incoming codex or claude
  instance reads `friction/` as part of reentry and inherits the
  prior instance's lessons.

**Negative / costs**:
- Slightly more token spend per session (the extraction pass).
- Operational discipline required — easy to drop when under time
  pressure, which is exactly when it's most valuable.
- Reflection quality varies with agent; the prompt template has to
  compensate by being concrete about what signals to watch for.

**Mitigations**:
- The playbook names seven specific friction signals so "what
  qualifies" is not a judgment call.
- Scheduled reflection catches what session-level reflection misses.
- The synthesis loop already consumes reflections and can pressure-
  test friction frequency across agents.

## Alternatives considered

- **Leave reflection as an ad hoc thing.** Rejected: the current
  session demonstrated this directly — seven frictions nearly died
  in transcript.
- **Capture in memory instead of a repo surface.** Rejected: memory
  is agent-local; other supervisor instances (e.g., codex) don't
  see it. `friction/` in the supervisor repo is cross-agent.
- **Automate capture fully (hook on tool invocations).** Rejected
  for now: too likely to flood with false positives without a
  judgment layer. Start with declared discipline + templates; add
  automation once the signals stabilize.
- **Only do scheduled reflection; skip in-session.** Rejected:
  in-session capture is where the signal is freshest. Scheduled
  reflection catches what in-session misses, not vice versa.

## Follow-through

This ADR is accepted; it is not self-executing. The following are
tracked as immediate supervisor work:

- [x] `friction/README.md` written
- [x] Seven backlog frictions from this session captured
  (FR-0001..0007)
- [x] `playbooks/self-reflection.md` written
- [ ] `AGENT.md` amended: truth sources include `friction/` and
  harness config; event model includes `session_reflected`
- [ ] `scripts/lib/projects.conf` adds supervisor entry
- [ ] `scripts/lib/reflect-supervisor-prompt.md` written
- [ ] `workspace.sh doctor` implemented with checks that closed out
  today's FRs
