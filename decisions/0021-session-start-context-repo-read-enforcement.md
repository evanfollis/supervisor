# ADR-0021: Session-start context-repo read enforcement

Date: 2026-04-18
Status: accepted
Accepted: 2026-04-18 (principal directive: "build the whole thing")
Supersedes-proposal: original proposed version (same file, this commit)
Amended-in-acceptance: adds 7-day freshness gate (KL2 mitigation) and pairs with ADR-0022 (M5 phase-1 detect-and-report) shipped in the same attended session.

## Acceptance amendments

Accepted with two amendments to the originally-proposed text:

**A1. 7-day freshness gate in the M4 hook.** Partially mitigates KL2
("stale-context amplification"): any file in `context-always-load` whose
YAML frontmatter `updated:` value is older than 7 days is still injected —
but wrapped in a loud "STALE — do not trust" banner with the calculated
age in days, instead of being laundered into trusted context. The banner
tells the agent to re-read from disk and verify before acting. This does
not eliminate KL2 but converts silent trust into a visible warning class.

**A2. Paired with ADR-0022 (M5 phase-1 detect-and-report).** M5 ships in
the same session as a SessionEnd hook that detects when a session with
substantial activity ended without touching `CURRENT_STATE.md` and routes
a low-priority handoff to `general`. This is not a full writer/retriever
implementation — it's a detection surface that makes drift visible rather
than silent. Full M5 enforcement still couples to the writer/retriever
separation proposal and remains future work.

Together, A1 + A2 close the worst-case path warned against in KL2:
(a) a stale file auto-injected with appearance of ground truth (A1 catches
this), and (b) a session that should have updated CURRENT_STATE leaving
silently without a signal (A2 catches this).

## Implementation (shipped)

- `/root/.claude/hooks/session-start-context-load.sh` — the M4 hook.
- `/root/.claude/hooks/session-end-current-state-check.sh` — the M5 phase-1 hook.
- `/root/.claude/settings.json` — `SessionStart` and `SessionEnd` registered.
- `context-always-load:` declarations added to:
  - `/opt/workspace/CLAUDE.md` (workspace root executive cwd)
  - `/opt/workspace/supervisor/AGENT.md` (via the CLAUDE.md symlink)
  - `/opt/workspace/projects/atlas/CLAUDE.md`
  - `/opt/workspace/projects/command/CLAUDE.md`
  - (already present before this session: context-repository, skillfoundry root)

Deferred (not blocking acceptance):
- Retrofit of `context-always-load:` to mentor and recruiter CLAUDE.md —
  blocked on those projects getting a CURRENT_STATE.md front door first
  (tracked in `system/active-issues.md` as the pass-2 retrofit).
- A dedicated `supervisor/playbooks/context-repo-session-enforcement.md` —
  low priority given the hook is self-describing in its banner.

## Original decision (unmodified below)



## Context

The `context-repository` pattern spec (`projects/context-repository/docs/agent-context-repo-pattern.md`)
now codifies **Required Mechanics** including M4 (session-start reads enforced,
not discretionary) and M5 (session-end updates enforced). The spec intentionally
defers the enforcement mechanism to this ADR.

The motivating incident: on 2026-04-18 the executive session failed to read
`skillfoundry-harness/CURRENT_STATE.md` before advising the principal on a paid
third-party service setup. The spec already said to read it. The memory system
already had an entry saying to read it. Neither survived contact with a busy
session. The failure class is discipline-only — no structural gate exists to
catch it.

Three candidate mechanisms have emerged:

- **Option A — SessionStart hook** in `~/.claude/settings.json` (or `hooks/`)
  that reads the cwd's `CLAUDE.md` for a `context-always-load:` block and
  injects the listed files' contents into the starting session.
- **Option B — CLAUDE.md directive** at project root stating "if asked about
  this project, read `CURRENT_STATE.md` first." Codifies discipline without
  mechanical enforcement.
- **Option C — `workspace.sh context` wrapper** that hard-fails a session if
  the cwd's always-load files haven't been read in the current session. Less
  universal than a hook (only fires when explicitly invoked).

## Decision

**Proposed**: Option A (SessionStart hook) as the primary enforcement mechanism,
with Option B (CLAUDE.md directive) retained as a fallback for sessions where
the hook cannot fire (Codex sessions, headless agent subagents, container
execution). Option C is rejected in favor of A.

Specifics of the hook (verified 2026-04-18 against Claude Code docs at
https://code.claude.com/docs/en/hooks.md via the claude-code-guide agent):

1. Lives at `~/.claude/hooks/session-start-context-load.sh` (host-level) and
   is registered in `~/.claude/settings.json` under the `SessionStart` hook
   key (verified exact name).
2. The hook receives JSON on stdin with a `cwd` field (plus `session_id` and
   `source` — one of `startup | resume | clear | compact`). No CLI args needed.
3. On fire, the hook reads `$CWD/CLAUDE.md` looking for a YAML block:
   ```yaml
   context-always-load:
     - CURRENT_STATE.md
     - index.md
     - docs/<repo-specific-spec>.md
   ```
4. Injection mechanism: hook emits JSON on stdout with a
   `hookSpecificOutput.additionalContext` field containing the concatenated
   file contents (with path-prefix headers so the agent sees which file each
   block came from). Multiple hooks' `additionalContext` values concatenate —
   this hook coexists with any others the user has installed.
5. Files that don't exist are emitted as a visible inline warning inside
   `additionalContext` — fail loud, don't silently skip.
6. Max injection size: configurable cap (default ~30 KB aggregate) to prevent
   runaway always-load lists from blowing out context budgets. If the list
   exceeds the cap, truncate with a visible marker and emit a `friction/`
   record that the always-load is too large.
7. **Subagent scope**: verified SessionStart does NOT fire when subagents are
   spawned via the Agent tool. The hook runs exactly once per session (on
   startup/resume/clear/compact). Long-running sessions with many subagents
   pay the cost once, not N times.
8. **Graceful no-op** on sessions without `context-always-load:` in CLAUDE.md
   (or without a CLAUDE.md at all): exit 0 with empty stdout. No performance
   cost, no behavior change for sessions that haven't opted in.

Session-end update enforcement (M5) is **deferred to a follow-on ADR**. The
read-side is higher-leverage and easier to enforce; write-side enforcement
is a harder design and benefits from the writer/retriever separation proposal
(`projects/context-repository/docs/writer-retriever-separation-proposal.md`).
A single ADR covering both read and write enforcement risks coupling two
decisions that should move independently.

## Consequences

**Positive:**

- Session-start read becomes structural, not discipline-dependent. The
  2026-04-18 Render incident failure class closes at the entry point.
- Context repos with a declared always-load list become self-activating
  domains — a fresh agent in the cwd has the right context in its prompt
  by the time it starts reasoning.
- Projects that haven't yet adopted the mechanics are unaffected (opt-in
  via the CLAUDE.md declaration).

**Negative:**

- Context budget consumption on every session start. A 5-file always-load
  averaging 3 KB each = 15 KB floor on every session. Acceptable per the
  injection cap, but measurable.
- Hook failures become a new failure class. The hook must fail-loud so that
  a silently-broken hook doesn't produce silently-uncontexted sessions.
- Host-level hook = host-level dependency. Transfer to a new host requires
  re-installation of `~/.claude/hooks/`. Manageable; document in
  `supervisor/playbooks/install-skills.md` or a sibling playbook.

**Risks:**

- Codex sessions don't share Claude Code's hook surface. The fallback
  (CLAUDE.md directive + written policy in `supervisor/CLAUDE.md`) is
  discipline-only for Codex. Accept this for now; revisit when Codex hook
  surfaces become available.
- Subagent execution (Agent tool): confirmed 2026-04-18 to NOT re-fire the
  hook. Any always-load content the main session received is already in its
  context when it spawns a subagent; subagents operate on their own prompts
  and don't inherit the injected content automatically. This is load-bearing
  only for subagents that need repo orientation — those should receive it
  via their Agent-tool prompt.

## Known limitations (surfaced by adversarial review, 2026-04-18)

Codex review of this ADR (`supervisor/.reviews/adr-0021-2026-04-18T13-20Z.md`)
flagged three failure modes this ADR does not fully address. Documenting them
here so an accepting session has honest input.

### KL1. Injection ≠ enforced reading

The hook puts content in the session's context. It does not force the agent
to *attend to* that content. An agent under pressure can still skim past
injected CURRENT_STATE content and fail the same way it did on 2026-04-18.
The hook changes the prior probability of reading, not the posterior. Declaring
"structural enforcement" on this basis risks replacing a silent failure mode
(no injection) with a louder one (injection believed to guarantee reading).

**Partial mitigation**: the injected content is prefixed with explicit headers
("this is your project's CURRENT_STATE — read it before answering about
this project"). A session that ignores this is visibly failing the pattern,
not silently. Full mitigation requires a downstream gate (e.g., a pre-tool-use
hook that checks whether CURRENT_STATE was referenced in the response before
allowing substantive tool calls) — out of scope for this ADR.

### KL2. Stale-context amplification (M4 without M5)

Read enforcement (this ADR) ships before write enforcement (deferred ADR).
A CURRENT_STATE that hasn't been updated in two weeks will be auto-injected
into every session for that cwd, where it will be *trusted more* than an
un-injected file would be. The net effect of read-without-write enforcement
may be worse than no enforcement at all in the interval between them.

**Partial mitigation**: the injected content shows the `updated:` frontmatter
field visibly. Agents can see "this file is 14 days old" and weight it
accordingly. This is not enforcement. It's a hint.

**Not fully mitigated**: this is a known reason to not let this ADR's hook
implementation run in production for long without M5 also shipping. Accepting
this ADR should be paired with a commitment to the M5 ADR within N sessions,
not "eventually."

### KL3. Repo-local declaration vs host-local enforcement

The `context-always-load:` block lives in repo CLAUDE.md. The hook that reads
it lives in `~/.claude/hooks/` on this one host. Portability to a new host,
a new workstation, a container, or a Codex session all silently break the
guarantee. Agents reading a project's CLAUDE.md will see the declaration and
may assume it's universally honored.

**Partial mitigation**: `supervisor/playbooks/context-repo-session-enforcement.md`
(to be written as part of implementation) documents the host-local dependency.
The install step is part of workspace setup, not per-project onboarding.

**Not fully mitigated**: this is an inherent property of hook-based enforcement.
A repo-level enforcement mechanism (e.g., a git hook, a build-time check)
would be universal but has its own costs. Considered not worth the complexity
for now; revisit if multi-host operation becomes common.

## Alternatives considered

**Option B alone (CLAUDE.md directive + textual policy):** rejected. This is
what the workspace already has via `supervisor/CLAUDE.md` §Context-repo
discipline. It's discipline-dependent by construction. The 2026-04-18 incident
is primary evidence that this doesn't hold under pressure.

**Option C (workspace.sh wrapper):** rejected. Requires explicit invocation
every session. Sessions that forget the wrapper enter the same uncontexted
state as today. Doesn't close the failure class.

**Hybrid A+C:** considered. The wrapper becomes a foreground helper that any
agent can invoke to refresh context mid-session. That's useful but orthogonal
to session-start enforcement — tracked as a separate follow-on, not part of
this ADR.

**Session-end write enforcement in the same ADR:** rejected. Separate decision;
see §Decision above.

## Implementation path (for the accepting session)

1. Write `~/.claude/hooks/session-start-context-load.sh`. Bash, no deps.
   Parses YAML block via awk (same pattern as `build-index.sh` in
   `context-repository`).
2. Register in `~/.claude/settings.json` under the correct hook key.
   Consult the Claude Code harness docs (or `claude-code-guide` agent) for
   the exact hook name — `SessionStart` is the working assumption but may
   need adjustment.
3. Add an always-load declaration to each governed project's CLAUDE.md,
   starting with `supervisor`, `context-repository`, and `skillfoundry-harness`.
   Rollout is per-project and idempotent.
4. Test: open a fresh Claude Code session in each governed cwd, verify the
   always-load files appear in the initial context. Test with a deliberately
   missing file to verify fail-loud behavior.
5. Document in `supervisor/playbooks/context-repo-session-enforcement.md`.
6. After 1 week of operation, review friction logs for hook-related issues
   before considering this ADR closed/accepted.

## References

- `projects/context-repository/docs/agent-context-repo-pattern.md` §Required mechanics (M4, M5)
- `projects/context-repository/docs/writer-retriever-separation-proposal.md`
- `supervisor/decisions/0014-supervisor-tick-and-pm-pattern.md` (tick already demonstrates hook-style enforcement for a related surface)
- Inspiration: Letta `system/` pinning (https://www.letta.com/blog/context-repositories), DiffMem `[ALWAYS_LOAD]` tags (https://github.com/Growth-Kinetics/DiffMem)
- Incident that motivated this: 2026-04-18 Render-walkthrough failure (discussed in session transcript; memory entries `feedback_verify_deploy_state_first.md`, `feedback_state_cost_before_signup.md`, `feedback_current_state_canonical.md`)
