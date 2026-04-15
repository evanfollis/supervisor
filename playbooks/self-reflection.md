# Playbook: Self-reflection is first-class

**Trigger**: every supervisor session, always. Not optional, not
end-of-session-only, not dependent on principal prompting.

**Owner**: whichever supervisor instance is attached (claude or codex).

**Preconditions**: none.

**Outputs**:
- Zero or more `friction/FR-NNNN-*.md` records for frictions surfaced.
- Zero or more `ideas/IDEA-NNNN-*.json` records for compounding
  patterns.
- A session-end extraction line in `events/supervisor-events.jsonl`.
- Any promotion-worthy friction routed into an ADR, handoff, or issue.

## Stance

Friction is the raw material for system improvement. Each friction
point caught, captured, and acted on compounds into a system that
can hold more state, drive more loops, and escalate less. Frictions
that die in session transcripts are stolen learning.

Treat friction like gold. Hunt for it. Don't wait for it to find you.

## During work — continuous capture

Watch for these signals *as they happen*, and write a
`friction/FR-NNNN-*.md` record **before** moving on to the next
action:

1. **"I had to search harder than I should have for X."** — a
   truth-source gap.
2. **"Wait, that thing I read earlier turned out to be wrong."** — a
   surface-drift event.
3. **"Should I ask permission for this?"** — a self-imposed gate.
   Capture even if you decide to go ahead without asking.
4. **"That almost caused a live-service break."** — an impact-blindness
   moment.
5. **"No check would have caught this."** — a missing-gate event.
6. **"Principal had to tell me to do X."** — a passivity event. These
   are the highest-value frictions because they reveal what the
   supervisor should be doing unasked.
7. **"We shipped X without running the rule that applies to X."** —
   an honor-system rule being skipped (often by the supervisor
   itself).

If you catch one, **write the record immediately**, not at session
end. Session-end is for ones you missed in flight.

## Session end — extraction discipline

Before writing a handoff or detaching from the session, run this
pass. Zero extracted is a signal to look harder, not a clean session.

1. **Review the transcript-level events.** What surprised you? What
   did you re-do? What did you almost get wrong?
2. **Check what the principal had to say twice.** Repetition of a
   directive is a strong friction signal.
3. **Check for self-imposed caution.** Anywhere you paused to ask
   permission, question whether the rule requiring it exists in the
   charter or was invented.
4. **Check for unused tools/surfaces.** If a truth source in
   `AGENT.md` §Truth sources went unread this session and should have
   been, that's a reentry-discipline friction.
5. **Write any frictions caught now as FR records.** Late is
   infinitely better than never.
6. **Emit a session-end event**:

   ```
   {"ts":"<iso>","agent":"<claude|codex>","type":"session_reflected",
    "ref":"<handoff-or-session-id>",
    "note":"N frictions captured (FR-NNNN, FR-NNNN); M promotions"}
   ```

## Promotion paths

Frictions are source material, not the end state. Promote them:

- **Three frictions sharing a root cause** → open an ADR naming the
  failure class and the fix.
- **Friction that points at a missing skill or maintenance-agent** →
  open an `IDEA-NNNN` for pressure testing, or extend an existing
  skill.
- **Friction that points at a live-service or durability gap** →
  `workspace.sh doctor` gains a check for it.
- **Friction that points at a principal-facing drag** → escalate
  proactively. Do not wait for the principal to re-raise.

Mark promoted frictions `promoted-to-<ref>` in their header. Do not
delete them — the trail is the learning.

## Scheduled meta-reflection

The supervisor is part of the reflection loop, not outside it. Every
12h, `workspace-reflect.timer` fires a supervisor-specific reflection
against:

- session transcripts at
  `/root/.claude/projects/-opt-workspace-supervisor/*.jsonl`
- the friction surface
- open handoffs and their age
- ADRs without cross-agent review
- drift between narrative surfaces and their authoritative sources

The prompt is `scripts/lib/reflect-supervisor-prompt.md`. The output
lands in `/opt/workspace/runtime/.meta/supervisor-reflection-<iso>.md`
and is picked up by the next synthesis pass.

## Anti-patterns

- **"I had a clean session so there's nothing to extract."** — wrong.
  Clean sessions are where complacency drift accumulates.
- **"The friction was minor."** — minor frictions compound. Record
  them; the pattern emerges over the cohort, not the individual.
- **"I'll remember to fix it next time."** — memory is not durable.
  Write the record.
- **"It's already captured in the transcript."** — transcripts are
  not truth sources (charter §Truth sources). If it matters, it
  belongs in the repo.
