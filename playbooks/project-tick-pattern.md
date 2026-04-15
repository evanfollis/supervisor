# Playbook: Project-manager tick pattern (discipline, not infrastructure)

**Status**: discipline-only in this release. Per-project timer
infrastructure is deferred per ADR-0014 §Project-manager tick
pattern. This playbook describes what a project session (the PM) is
expected to do to match the supervisor's self-improvement cadence.

**Trigger**: at the end of every attended project session. Also on
any session reentry if the most recent reflection artifact is stale
(older than 48h while the project has recent git activity).

**Owner**: the PM agent attached to the project session.

## Why this exists

The supervisor tick (ADR-0014) institutionalizes between-session
self-improvement for the meta layer. For that pattern to scale to
the project layer, each PM must treat reflection + friction capture
+ handoff routing as first-class responsibilities, not end-of-session
polish. Without this, the meta layer will drag the project layer
along one principal nudge at a time — which defeats the goal of
everyone moving up the stack.

The 12h `workspace-reflect.timer` already produces *passive* reflections
(read-only, propose-only). That is insufficient for driving project
improvement because nothing acts on the findings. This playbook is
the PM's active half.

## Session-end discipline (do this every session)

1. **Reflect before writing the handoff.** Use the friction signals
   from `playbooks/self-reflection.md` — they apply to project
   sessions too. Ask: what did the user have to correct twice? What
   did I almost get wrong? What did I wait on when I could have
   acted? What surface was missing that I had to reinvent?

2. **Write any friction records immediately.** If the project has a
   `friction/` surface, write `FR-NNNN-*.md` there. If it doesn't,
   write the friction as a handoff to supervisor INBOX at
   `/opt/workspace/supervisor/handoffs/INBOX/<iso>-project-friction-<slug>.md`
   so the supervisor can route or promote.

3. **Emit a reflection artifact** at
   `/opt/workspace/runtime/.meta/<project>-reflection-<iso>.md`. Use
   the same structure as the automated reflection output — even a
   3-line version is better than none. The supervisor tick will grade
   you on this artifact's freshness.

4. **Route open items to the right place**:
   - Cross-project concerns → supervisor INBOX
   - Project-internal TODOs → the project's own issue tracker or
     local planning file (not memory)
   - Items waiting on the principal → escalate in the session
     handoff, do not leave silent

5. **Emit a session-end event** if the project has a telemetry
   surface. At minimum, append to the workspace telemetry stream at
   `/opt/workspace/runtime/.telemetry/events.jsonl`:
   ```
   {"ts":"<iso>","agent":"<you>","project":"<name>","type":"session_reflected","ref":"<reflection-file>","note":"<n frictions, m handoffs>"}
   ```

## What the supervisor grades

The supervisor tick reads, for each project in
`scripts/lib/projects.conf`:

1. The most recent `<project>-reflection-*.md` artifact.
2. Whether the project has committed in the last 48h.

Combinations:
- Recent commits + recent reflection → fine, no action.
- Recent commits + stale reflection → supervisor sends a
  `<project>-reflection-stale.md` handoff asking the PM to reflect.
- No commits + stale reflection → no action (quiet project).
- No commits + fresh reflection → fine (PM reflected even on an idle
  session, which is good discipline).

## Anti-patterns

- **"I'll write the reflection when I have something to say."** The
  session-end pass is mandatory. Zero-extraction is a signal to
  look harder, not a sign of a clean session. See
  `playbooks/self-reflection.md` §Anti-patterns.
- **"The issue tracker is my reflection."** An issue is what needs
  to get done. A reflection is what the session revealed about the
  *system* — the substrate, the conventions, the friction. They are
  different artifacts.
- **"The supervisor will catch it."** The supervisor will catch
  patterns across the cohort, not the individual case. The individual
  case dies with the session.
- **"I already reflected last session."** Reflection compounds — a
  skipped session is a lost signal even if the prior one was rich.

## When a project is ready for its own tick

If a PM is consistently following this discipline, has its own
`friction/` surface, and has a declared set of write-scoped paths
distinct from read-only areas (analogous to ADR-0014's Tier A/B/C),
propose a follow-up ADR for that project's per-project tick. The
design will mirror the supervisor tick, tailored to the project's
substrate. Do not roll per-project ticks out broadly until at least
one has proven the model.
