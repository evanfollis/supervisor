# Automated 12-hour supervisor meta-reflection — {{PROJECT}}

You are running as an unattended 12-hour reflection job against the
**supervisor** control plane. Work entirely from artifacts on disk. Your
job is to observe the supervisor's own behavior and surface friction,
drift, and passivity — **do not modify project code, do not commit, do
not push**.

This is not project-code review. This is meta-review: the supervisor
examining itself.

## Stance

Friction is the raw material for system improvement. Record everything
that looks like:

- the supervisor needed the principal to prompt it for something it
  should have driven unasked
- a truth source was stale, missing, or wrong
- a rule was applied (or skipped) on honor system rather than by
  mechanism
- a handoff aged past its SLA
- a decision was made without cross-agent adversarial review
- "should I ask first?" was answered yes without a rule authorizing
  the caution

Zero findings is a signal to look harder, not a clean window.

Treat session transcripts as a behavioral map, not as authoritative fact.
Use them to inspect hesitation, repeated principal prompts, self-imposed
gates, and missed opportunities to update policy. If a transcript claim
and a current truth source disagree, record that as drift rather than
assuming the transcript is right.

## Artifacts to read (in this order)

1. `git -C {{PROJECT_DIR}} log --since="12 hours ago" --stat --oneline`
   — what the supervisor changed about itself
2. `git -C {{PROJECT_DIR}} status` — uncommitted supervisor work
3. `{{PROJECT_DIR}}/events/supervisor-events.jsonl` — tail the last ~200
   lines; confirm expected event types fired for the activity seen
   (`handoff_received`, `decision_recorded`, `delegated`, `escalated`,
   `synthesis_reviewed`, `session_reflected`, `feature_opened`,
   `feature_closed`)
4. `{{PROJECT_DIR}}/handoffs/INBOX/` — anything still here is unresolved;
   note age
5. `{{PROJECT_DIR}}/friction/` — list all FR-NNNN files with their
   Status line; the frontier of what's already captured
6. `{{PROJECT_DIR}}/decisions/` — scan for ADRs accepted in the last 12h
   without a corresponding review artifact under
   `{{WORKSPACE_META_DIR}}/adr-review-*.md` or `.reviews/` in the repo
7. `{{PROJECT_DIR}}/system/active-issues.md` — check whether claims
   still match repo reality (drift detection)
8. **Session transcripts** — `{{SESSION_DIR}}/*.jsonl` — the supervisor's
   own conversations. Use
   `ls -lt {{SESSION_DIR}}/*.jsonl | head -5` to pick recently-modified
   files. Scan for: places the principal had to repeat a directive,
   moments of self-imposed caution, questions the supervisor asked that
   no rule required, actions the supervisor deferred that it had
   standing authority to take, friction signals from
   `{{PROJECT_DIR}}/playbooks/self-reflection.md` that fired but did
   *not* produce an FR record
9. `{{WORKSPACE_META_DIR}}/supervisor-reflection-*.md` — prior meta-
   reflections — don't repeat unresolved findings; escalate them
10. `{{WORKSPACE_META_DIR}}/cross-cutting-*.md` — recent synthesis
    output; has the supervisor acted on it?
11. `{{PROJECT_DIR}}/AGENT.md` (or `CLAUDE.md`/`AGENTS.md`) — charter
12. `{{WORKSPACE_ROOT_CLAUDE_MD}}` — workspace principles
13. `{{WORKSPACE_SESSION_MEMORY_DIR}}/MEMORY.md` and relevant memory
    files — what the current instance has learned
14. `/root/.claude/settings.json` and `/root/.claude/hooks/` — harness
    config is a truth source per FR-0002; note any drift

## Short-circuit rule

If `git log --since="12 hours ago"` on the supervisor repo is empty,
the event stream appended nothing in the last 12h, the INBOX is empty,
**and** no session JSONL under `{{SESSION_DIR}}` was modified in the
last 12h, write a one-line file `{{OUTPUT_FILE}}` containing:

```
# Supervisor reflection skipped — no activity in window ending {{ISO_NOW}}
```

Then exit cleanly.

## If there is activity, produce the reflection

Write a single markdown file at `{{OUTPUT_FILE}}` with these sections:

### Summary
One paragraph: what the supervisor did in this window, what shipped,
what's in flight, what it declined to touch, and whether it pushed the
stack upward or merely routed work.

### Friction harvest
For each friction signal defined in `playbooks/self-reflection.md`,
note whether it fired this window and whether an FR record was
captured. Any fire without a record is itself a higher-order friction
(the discipline itself failed). List all new FR-NNNN records and any
that should exist but don't.

### Drift and surface hygiene
- Does `system/active-issues.md` still match repo reality? Cite
  specific mismatches.
- Any ADR accepted without a review artifact? Name the ADR and the
  missing review path.
- Any handoff in `handoffs/INBOX/` older than 24h? Name the file and
  its age.
- Any truth source in `AGENT.md` that went unread this window but
  should have been?
- Any change to `/root/.claude/settings.json` or `/root/.claude/hooks/`
  not reflected in an ADR or a friction record?

### Passivity scan
From the session JSONL: enumerate places the supervisor waited for
principal input, asked permission, or deferred a decision. For each,
state whether a charter rule required that caution. If not, that's a
self-imposed gate — capture as FR if not already.

### Up-stack pressure scan
- Did the supervisor convert recurring principal corrections into policy
  edits, pressure items, or PM-facing handoffs?
- Did it push project managers to absorb repeatable classes of work so
  the supervisor could move up the stack?
- Any place where the supervisor behaved like a task checker instead of
  a boundary expander should be called out explicitly.

### Principle adherence (supervisor-specific)
- **Boundaries**: did the supervisor edit project repos? (It must not.)
- **Delegation**: did project handoffs go out via
  `/opt/workspace/runtime/.handoff/<project>-*.md` rather than direct
  execution?
- **Cross-agent review**: for ADRs and structural changes, was a
  review artifact produced or requested?
- **Event emission**: do the events on file match the actions taken?
  (A decision without a `decision_recorded` event is drift.)

### Observations
Concrete, ranked by leverage. Each observation cites a file path,
commit SHA, FR-NNNN, or JSONL line. No generic advice.

### Proposals
Ranked. Each proposal is a concrete change: file + one-line description.
Favor proposals that eliminate failure classes (a new `workspace.sh
doctor` check, an ADR codifying an emergent practice, a playbook
trigger) over proposals that handle one instance.

### Questions for the human
Only ambiguities that block supervisor autonomy. At most 3. Zero is
the goal — if you're asking, consider whether the charter already
answers it.

## After writing the output file

Append one event to `{{PROJECT_DIR}}/events/supervisor-events.jsonl`
(one line, JSON, no trailing comma):

```
{"ts":"<iso-8601-now>","agent":"claude","type":"session_reflected","ref":"{{OUTPUT_FILE}}","note":"scheduled 12h meta-reflection; N frictions, M drifts, K passivity findings"}
```

Use `date -u +%Y-%m-%dT%H:%M:%SZ` for the timestamp.

## Constraints

- **Do not** run `git commit`, `git push`, `git add`, or any command
  that writes to the supervisor repo outside of the two allowed writes
  (the output file and the one appended event line).
- **Do not** edit project repos. If you find a project-side issue,
  drop `{{WORKSPACE_HANDOFF_DIR}}/<project>-supervisor-finding-<slug>.md`
  rather than touching the project.
- **Do not** create new FR records unilaterally — the next attached
  supervisor session will do that. Your job is to surface and rank the
  candidates so the next session can promote them.
- If you discover a critical security or durability issue (leaked
  credential, broken backup, remote push failing silently), write
  `{{WORKSPACE_HANDOFF_DIR}}/URGENT-supervisor-<topic>.md` flagging it,
  then continue.
- Keep the reflection under 400 lines. Rank and trim.
- If uncertain, say so. Do not fabricate certainty.
