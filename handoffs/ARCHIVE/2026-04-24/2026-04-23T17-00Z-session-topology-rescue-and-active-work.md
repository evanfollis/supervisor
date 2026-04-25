---
title: Session-topology rescue + active executive work in flight
from: ephemeral executive session (PID 359247, JSONL 2b3d89d0-86f1-4975-84f5-8c4cb3170242)
to: supervised general tmux session OR next executive session
date: 2026-04-23T17:00Z
priority: high
reason: the ephemeral /remote-control session carrying this work is NOT in tmux; principal needs to converge on the supervised general session for always-on continuity
---

# Pickup handoff — active executive work + session topology rescue

## Why this handoff exists

Principal (2026-04-23 ~16:50Z) observed that the command.synaplex.ai agent
"did not at all seem capable" when he tried to continue his conversation
there. Root cause: **he was talking to the wrong process.** There are
multiple Claude Code instances on this server:

- **PID 1414** — `claude --remote-control general` inside tmux session `general`, supervised by `workspace-session@general.service`, running since 2026-04-20. Its JSONL is in `/root/.claude/projects/-opt-workspace/` under a session_id distinct from `2b3d89d0`. Its live /remote-control URL (captured from tmux pane) is `https://claude.ai/code/session_019f4nAiJX9C9QHixN3CiXXM`. **This is the canonical always-on executive surface.**
- **PID 359247** — a second `claude` process started 2026-04-23T14:18Z from the principal's WSL via /remote-control. JSONL `2b3d89d0-86f1-4975-84f5-8c4cb3170242.jsonl` (~1.1MB, active). This session is carrying the current workspace-executive conversation with the principal but is NOT in tmux — when the WSL connection drops, this process dies.

When the principal tried command.synaplex.ai, its web UI likely showed a terminal view pointed at one of the other supervised tmux sessions (command project, atlas, etc.), each with their own CLAUDE.md and no context of this conversation. Hence "not at all capable" — the agent there was technically fine, just the wrong agent.

## What the principal needs structurally

One canonical always-on executive session. The supervised general tmux session should be that. The ephemeral /remote-control spawn pattern from WSL should either (a) attach to the supervised session instead of creating a new one, or (b) be replaced by the principal connecting directly to the supervised session's /remote-control URL.

**Recommended principal path forward:**
1. Close the WSL-spawned ephemeral /remote-control (this session).
2. Open `https://claude.ai/code/session_019f4nAiJX9C9QHixN3CiXXM` directly (the supervised general session's URL). That session is idle and will receive input when the principal types.
3. When attached to the supervised general session, read this handoff first — it contains the full state of work in flight.

**Alternatively** (operator path): access the supervised general session via `tmux attach -t general` over SSH to the server, or through command.synaplex.ai's terminal view *if* that view connects to the `general` tmux session (verify before relying — that's a command project fix; see structural tasks below).

## Durable state already landed this session (safe to rely on — in git, pushed)

Six supervisor commits on `main`, pushed to origin:

```
a3a174c Route URGENT-* handoffs to target sessions + register synaplex
f2c9de5 Propose ADR-0029: the synaplex loop — five-layer operational pipeline
79fae2f Dedupe S3-P2 tick URGENTs + scan project-level URGENT handoffs at session start
589bae1 Archive 29 tick-escalation URGENTs (80h bulk closure)
cee8af6 Exclude untracked files from tick dirty-tree guard (FR-0039)
fb5901e Add positioning-test playbook from forward-look research
```

And:
- Three new memories in `/root/.claude/projects/-opt-workspace/memory/` (persistent on disk): `project_synaplex_loop_architecture.md`, `feedback_executive_cadence_concurrent.md`, `feedback_no_unauthorized_brand_names.md`. MEMORY.md index updated.
- `/opt/workspace/CLAUDE.md` has in-place (unversioned) amendments: INBOX saturation exception + 24h dispatch obligation. **Governance gap flagged**: /opt/workspace is not a git repo; these edits need to be moved under `supervisor/` or the workspace root needs to become a governed repo. Named in the task list below.
- Task 12 (skillfoundry-valuation deadlines) was picked up and executed by the skillfoundry tmux session via the dispatch path within ~90 minutes of my handoff write — Preflight close note landed at skillfoundry-valuation-context commit `251adf4`, stale_close_dates already present from prior commit `8a5f1ff`. The synaplex loop's minimum-viable dispatch cycle is demonstrated working.

## Task list — 15 items, 4 done, 11 pending

Full list with status:

| # | Subject | Status |
|---|---------|--------|
| 1 | Unblock supervisor tick + patch dirty-tree guard | **done** (fb5901e + cee8af6) |
| 2 | Purge INBOX noise + codify saturation + URGENT handoff scan | **done** (589bae1 + 79fae2f + workspace CLAUDE.md edit) |
| 3 | Rename agentstack → synaplex across workspace | pending — next critical path |
| 4 | Write ADR for 5-layer synaplex loop + friction layer | **done** (f2c9de5 — ADR-0029 proposed) |
| 5 | Build Layer 1 — Intake subsystem | pending — depends on 3 |
| 6 | Build Layer 2 — Reasoning subsystem | pending — depends on 3 |
| 7 | Build Layer 3 — Validation subsystem | pending — depends on 3 |
| 8 | Build Layer 4 — Presentation subsystem | pending — depends on 3 |
| 9 | Build Layer 5 — Friction log + synthesis integration | pending — depends on 3 |
| 10 | Deploy synaplex.ai site to CF Pages | pending — depends on 3 |
| 11 | Deploy skillfoundry agentic inbound | pending — dispatch via handoff |
| 12 | Close skillfoundry-valuation deadlines | **done** (via dispatched skillfoundry session) |
| 13 | Close atlas canon gaps | pending — dispatch via handoff |
| 14 | Land command deploy + ADR-0028 promotion | pending — ADR promotion is supervisor work; deploy is dispatch |
| 15 | Resolve context-repo pass-2 scope | pending — draft proposal for principal |

## Active pressure (new from this session)

**NEW-1 — Session topology convergence (load-bearing for always-on executive)**
The /remote-control pattern allows multiple concurrent Claude Code processes to operate against /opt/workspace, each with its own JSONL and task state, invisible to each other. The supervised general session (PID 1414) is the only durable one. All executive work should converge there. Either (a) /remote-control launched outside tmux should be prevented or (b) the WSL client should always connect to the supervised session's URL. Command.synaplex.ai's terminal view should reliably surface the supervised general session, not other tmux sessions.

Action: write a handoff to command asking for: terminal view default to `general` tmux session, session-select UI surfaces which agent has which CLAUDE.md and role, deep-link to specific session by name. Treat this as pressure-queue item "Command must be a real executive control-plane product, not better-looking terminal utilities."

**NEW-2 — ADR-0029 policy inversion (advisor-flagged)**
ADR-0029 is `proposed`; the workspace CLAUDE.md amendments it authorizes already applied in-session. Options: (a) annotate ADR-0029 as "retroactive authorization pending adversarial review" and run Codex review via `supervisor/scripts/lib/adversarial-review.sh` — accept on passing review, (b) revert the workspace CLAUDE.md edits until review closes. Lean (a); edits reflect what 3 syntheses already proposed and the review is formal pressure-test, not permission.

**NEW-3 — /opt/workspace/CLAUDE.md unversioned**
Workspace-root CLAUDE.md is not in any git repo. Edits survive filesystem but not reset. Either promote /opt/workspace to a governed repo, or move the CLAUDE.md content to supervisor/ and symlink. Name the decision in an ADR.

## Rename operation (task 3) — surface audit before execution

Per advisor, these surfaces contain `agentstack` references that will need updating or fixing:

- `projects/agentstack/` — directory rename to `projects/synaplex/`
- `projects/agentstack/lab/.canon/` — canon envelopes reference this path in `sources` or metadata; verify
- `projects/agentstack/site/src/content/` — MDX frontmatter + copy
- `/root/.claude/plans/calm-squishing-peacock.md` — plan doc referencing agentstack
- `/opt/projects/` compatibility symlinks (check `ls -la /opt/projects/`)
- `supervisor/system/active-issues.md` — references agentstack (some retained to document the rename, some need update)
- `supervisor/scripts/lib/sessions.conf` — add `synaplex` entry after rename
- `supervisor/scripts/lib/projects.conf` — add `synaplex` entry after rename
- `supervisor/scripts/lib/dispatch-handoffs.sh` — `synaplex` already added to KNOWN_SESSIONS (a3a174c)
- GitHub remote — `gh repo rename agentstack synaplex` OR configure local to push to existing remote name
- Cloudflare Pages deploy target — point at `synaplex.ai` not `agentstack.pages.dev`

Execution order (proposed):
1. Survey all above paths with grep; list of edits in a branch
2. `mv projects/agentstack projects/synaplex`
3. Fix supervisor references (active-issues.md, sessions.conf, projects.conf)
4. Write handoff to the new synaplex session for in-project rebrand (CLAUDE.md, site MDX, CURRENT_STATE.md)
5. Add `workspace-session@synaplex.service` via systemctl (operator posture) after sessions.conf lands
6. GitHub remote rename (ask principal before executing — `gh repo rename` is visible externally)

## Dispatches next turn (once rename lands)

- `runtime/.handoff/atlas-canon-gap-fixes-2026-04-23T<iso>.md` — emit_decision() loop in migrate.py, non-transactional migration fix, `sources=[]` parameterization, SOL guard
- `runtime/.handoff/skillfoundry-agentic-inbound-deploy-2026-04-23T<iso>.md` — deploy the scaffolded personas + landing pages + blog queue + telemetry
- `runtime/.handoff/command-deploy-and-session-topology-fix-2026-04-23T<iso>.md` — deploy HEAD (2 commits behind), promote ADR-0028, address terminal-view session routing
- `runtime/.handoff/context-repo-pass-2-scope-draft-2026-04-23T<iso>.md` — draft new pass-2 targets (mentor/recruiter gone)
- `runtime/.handoff/synaplex-rebrand-and-layer-1-intake-2026-04-23T<iso>.md` — after rename: full in-project rebrand + stand up Layer 1 intake adapters (RSS/arxiv/HN/Reddit/GitHub/Substack first; podcasts week 2)

Each handoff should be written with the spec from `supervisor/AGENT.md` §Cross-agent handoff (task_id, target session, objective, constraints, non-goals, required deliverable, acceptance criteria, escalation conditions, artifacts).

## Recommendation to the receiving executive session

1. Read this handoff top-to-bottom.
2. Confirm current git state on supervisor matches the commit list above (pull if needed).
3. Verify the principal's current session context — if they return via the supervised general session's /remote-control URL, they'll see an idle prompt and will need onboarding to current state. Ideally the principal lands here via a handoff read at session resume.
4. Proceed with task 3 (rename) as the critical path unblocking tasks 5–10. Take care with the cross-cutting reference audit.
5. Write the NEW-1 command session-topology handoff before more work flows through the dispatch path — the principal's trust in the operator surface depends on it.

## Artifacts

- Supervisor main: see `git log -10` for the 6 commits listed above
- ADR-0029: `supervisor/decisions/0029-synaplex-loop-five-layer-pipeline.md`
- Memory index: `/root/.claude/projects/-opt-workspace/memory/MEMORY.md`
- Current ephemeral session JSONL (for transcript reference): `/root/.claude/projects/-opt-workspace/2b3d89d0-86f1-4975-84f5-8c4cb3170242.jsonl`
- Supervised general session: `tmux attach -t general` or `https://claude.ai/code/session_019f4nAiJX9C9QHixN3CiXXM`

## Honest labeling

This handoff is written by the ephemeral session itself, not by the principal. If the principal redirects the strategic direction before the receiving session reads this, follow the principal's current word over this handoff's task list.
