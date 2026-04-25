---
from: synthesis-translator
to: general
date: 2026-04-25T03:32:44Z
priority: high
task_id: synthesis-advisor-review-enforcement
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-04-25T03-27-27Z.md
source_proposal: Proposal 3 — Advisor-before-deploy enforcement gate
---

# Advisor-before-deploy enforcement gate

## Context

Pattern 2 in the synthesis: discretionary advisor/review rules are not being followed on large/complex sessions. Three consecutive reflection windows across command and atlas report zero advisor calls and zero `/review` invocations on significant work (115-turn sessions, WebSocket reconnect races, 3-file routing changes, infrastructure config). One of those sessions had adversarial review applied post-hoc by a separate session, which found and fixed a real reconnect close-race — proving the review had value.

The workspace rule exists but is discretionary. Three consecutive windows of non-compliance without consequence means it's advisory rather than structural. This proposal makes it structural.

## Proposed Change

**Amendment to `/opt/workspace/CLAUDE.md`** — Add the following rule under `### Code Philosophy`, after the "Minimal diffs" rule (around line 121):

```markdown
- **Advisor and /review before deploying sessions >50 turns or >2 files changed.** Sessions that exceed either threshold must call `advisor()` at least once and invoke `/review` before deploying. The review artifact must exist before `npm run deploy` / `git push` / any deploy action. No exceptions. Three consecutive windows of non-compliance (command Phase C2, routing fix, atlas service deploy) established that discretionary review doesn't happen — this makes it structural.
```

## Why

Three consecutive large sessions shipped without advisor calls or `/review` invocation. When `/review` was eventually run post-hoc on one (command Phase C2), it identified a real reconnect close-race. The rule is discretionary; compliance has reached zero on complex work. Making it structural (mandatory, with review artifact verification before deploy) converts it from a goal to a gate.

## Acceptance criteria

- The amendment is added to `/opt/workspace/CLAUDE.md` under Code Philosophy
- Text matches the proposal above (or a close paraphrase)
- Change committed with message explaining the synthesis source
- Completion report at `runtime/.handoff/general-supervisor-synthesis-advisor-review-enforcement-complete-<iso>.md` pointing back to this handoff and the source synthesis

## Escalation

URGENT if:
- The amendment conflicts with a more recent decision or active ADR. (Check `supervisor/decisions/` for advisor/review related ADRs.)
- A hard gate implementation (preflight-deploy.sh check for `.reviews/` artifacts) is deemed necessary — that requires a separate proposal/implementation.

## Notes

The synthesis mentions that a hard gate could be added to `preflight-deploy.sh` to verify a `.reviews/` artifact exists for the current HEAD, but that is a separate implementation step. This handoff focuses on the policy amendment. If a hard gate is needed, it can be a follow-up proposal.
