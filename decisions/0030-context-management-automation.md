# ADR-0030: Automate context management so sessions rotate without external reset

Date: 2026-04-23
Status: accepted

## Context

The principal has been manually `/clear`-ing executive sessions when they
accumulate ~6+ hours of tool-heavy activity. This is an external reset — a
rescue move the principal has to initiate because the stack isn't
self-managing its own context pressure. The failure mode:

- Sessions stretch long enough that context rot (per Chroma 2026 research:
  output quality degrades well before hard ceilings) starts silently
  degrading output.
- When the principal notices degraded responses or drift, they
  `/clear`, which discards in-context work and forces the next session
  to be rescued by hand.
- The workspace already has substantial scaffolding (SessionStart
  always-load, CURRENT_STATE.md front doors, M5 drift detector) but
  nothing that makes the *rotation itself* automatic.

Four things sit on the rotation path:

1. **Auto-compact** (Claude Code built-in, on by default). The real
   rotation mechanism. Documentation does not publish a threshold —
   treat it as opaque but functional. This ADR does not try to tune it;
   it trusts the default.
2. **Prompt cache** (Anthropic API, on by default since early 2026).
   Auto-caches the longest stable prefix. Performance depends on
   always-load files being ordered stable → volatile so dynamic files at
   the tail don't invalidate the cache for stable files at the head.
3. **SessionEnd handoff discipline**. Before this ADR, only CURRENT_STATE
   drift was detected. A generic session-summary handoff did not exist;
   next-session reentry depended on the executive having hand-written a
   rescue note *before* the session ended.
4. **Native memory tool** (Anthropic, free tier since March 2026) handles
   cross-session state natively. The workspace currently hand-rolls this
   via `/root/.claude/projects/-opt-workspace/memory/`. A migration is
   tractable but meaty — deferred from this ADR.

## Decision

Ship three automation surfaces now; defer one to a follow-up ADR.

### 1. Reorder `context-always-load:` for cache-prefix stability (SHIPPED)

Both `/opt/workspace/CLAUDE.md` and `/opt/workspace/supervisor/CLAUDE.md`
now list always-load files stable → volatile:

```
ESSENCE.md                    # ~immutable
agent-platforms-latest.md     # weekly (only in workspace CLAUDE.md)
paid-services.md              # monthly
pressure-queue.md             # curated, weekly-ish
status.md                     # daily
active-issues.md              # daily, highest churn
verified-state.md             # regenerated every tick
```

`verified-state.md` is the most volatile (re-run by `verify-state.sh` on
every tick and on workspace.sh context). Putting it at position 3
(previous order) invalidated the cache for every file after it. Moving
it to the tail preserves the stable prefix.

The injection hook (`session-start-context-load.sh`) concatenates in
declaration order, so ordering in CLAUDE.md is the control surface.

### 2. SessionEnd auto-summary hook (SHIPPED)

New file: `/root/.claude/hooks/session-end-auto-summary.sh`. Writes a
session-summary handoff to `supervisor/handoffs/INBOX/` (fallback
`runtime/.handoff/`) containing structural data only — no LLM
summarization inside the hook. Contents:

- session_id, cwd, transcript path, start/end time
- transcript line count, user/assistant turn counts, tool-use count
- last user message (truncated, 500 char)
- git log since session start (if cwd is a repo)
- git status --short (if cwd is a repo)

Gated on the cwd's CLAUDE.md declaring `context-always-load:` — only
governed executive/project cwds get summaries. Short sessions (< 10
transcript lines) skipped. Kept separate from the existing
`session-end-current-state-check.sh` so disabling one doesn't break the
other.

Registered in `/root/.claude/settings.json` as a second SessionEnd hook
alongside the existing M5 CURRENT_STATE drift detector.

Smoke-tested against this session's transcript — fires, emits valid
markdown, handoff file lands in INBOX.

### 3. Context-freshness UI surface (DELEGATED)

Surfacing live token count / turn count / context % in the `command` UI
is a project-session concern. Handoff written to
`runtime/.handoff/command-context-usage-ui-<iso>.md` against the
already-scoped Phase D right-panel context inspector.

### 4. Native memory tool adoption (DEFERRED to follow-up ADR)

Migrating `/root/.claude/projects/-opt-workspace/memory/` to Anthropic's
native memory tool is tractable but touches every executive-session
convention. Not in scope here. Follow-up ADR when we have bandwidth —
low urgency since the file-based system is working.

## Consequences

- Next cold session picks up via INBOX session-summary handoff without
  the principal narrating what was done.
- Prompt-cache hit rate on the always-load prefix improves (undocumented
  thresholds but structurally better).
- Auto-compact remains the real rotation mechanism; these changes
  complement it, not replace it. If auto-compact produces noticeably
  bad summaries in practice, that's a separate issue to escalate
  (and cannot be fixed here — it's internal to Claude Code).
- SessionEnd INBOX will accumulate auto-summaries. They are
  low-priority, delete-on-consume. If this becomes noisy the next-session
  executive should trim aggressively; if they prove unused for 30+ days
  we remove the hook.

## Alternatives considered

- **Tune auto-compact threshold** — not possible; undocumented and no
  config key exposed. Default is the only option.
- **LLM-summarize inside the SessionEnd hook** — rejected. Adds latency
  and cost on every session end; C1 review risk (over-trust of
  agent-written summary) already flagged by M5 phase 1. Structural data
  only is the safer contract.
- **Migrate memory to native tool now** — scope-creep. Not rotation work.
- **Don't reorder always-load** — rejected. `verified-state` re-generation
  per tick demonstrably invalidates the cached prefix; reordering is a
  one-line change per file with no downside.

## Follow-ups

- Monitor whether SessionEnd summaries are actually being read by next
  sessions. If they pile up unread, either promote to a more visible
  surface or remove the hook.
- Memory-tool adoption ADR (separate).
- Cap-collision on 30KB always-load aggregate is tracked in the existing
  URGENT handoff `synaplex-always-load-cap-collision`; this ADR does not
  address it.
