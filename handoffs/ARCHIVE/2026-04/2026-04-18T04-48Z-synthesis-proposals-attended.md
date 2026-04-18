---
From: supervisor tick 2026-04-18T04-48-24Z
Source: cross-cutting synthesis 2026-04-18T03-26-01Z, Proposals 1–3
Priority: high
Requires: attended session
---

# Synthesis proposals requiring attended session — 2026-04-18

Three proposals from the 03:26Z synthesis are ready to implement. All touch Tier B or C surfaces.

## P1 — Add conditional git push to supervisor tick commit path

**Surface**: `scripts/lib/supervisor-autocommit.sh` (Tier C — scripts/lib)
**Why urgent**: supervisor is now 12 commits ahead of origin/main (up from 4 in prior synthesis). Every subsequent tick widens the gap. All cross-session tooling, reflection scripts, and adversarial-review paths read `origin/main` and are 12 commits stale.

Proposed addition after `git commit` in the autocommit script:
```bash
if git rev-parse --verify origin/main >/dev/null 2>&1 && [ "$(git rev-parse --abbrev-ref HEAD)" = "main" ]; then
  AHEAD=$(git rev-list origin/main..HEAD --count)
  if [ "$AHEAD" -gt 0 ]; then
    git push origin main 2>&1 || echo "WARN: push failed" >&2
  fi
fi
```
Guard: main branch + remote exists. Fail-open (warn, don't abort tick).

**Immediate action also needed**: run `git push` from `/opt/workspace/supervisor` now to clear the 12-commit backlog.

## P2 — Add governance-sync requirement to tick prompt

**Surface**: `playbooks/supervisor-project-tick-prompt.md` (Tier B)
**Why**: Tick sessions update CURRENT_STATE but don't cross-reference active-issues.md when closing tracked items. Result: governance surfaces lag execution by 12h+, next session misallocates attention to already-resolved items.

Proposed addition after the adversarial-review gate section:

> **Governance sync**: If your work in this tick resolves or materially advances an item listed in `supervisor/system/active-issues.md`, update that entry (move to Resolved or update status). If you consumed an INBOX handoff, move it to `handoffs/ARCHIVE/YYYY-MM/`. Do not leave governance surfaces stale.

## P3 — Add credential-blocker escalation rule to CLAUDE.md

**Surface**: `/opt/workspace/CLAUDE.md` §Quality: Radical Truth (Tier C — charter)
**Why**: Skillfoundry has 5 separate credential-blocked deploys that accumulated silently across 3 ticks. The "pushed is not deployed" rule catches individual instances but doesn't force early escalation when a blocker is first discovered.

Proposed addition after the "Pushed is not deployed" bullet:
> **Credential-blocked work must escalate on first occurrence, not accumulate.** If a tick produces code that requires external credentials, API tokens, or manual deployment steps to become live, the completion report must include a `Credential blocker` section naming the specific credential and the command needed once it's available. If the same credential blocks work in 2+ consecutive ticks, the second tick must write an URGENT escalation — the blocker is structural, not transient.

## One-time cleanup also needed (from P4)

- `FR-0025`: open the file, add `Status: resolved` (ADR reviews completed 2026-04-17).
- Merge `ticks/2026-04-16-12` and `ticks/2026-04-17-02` branches to main.

## Acceptance criteria

- [ ] `git push` runs from supervisor, clearing 12-commit backlog
- [ ] P1 push guard added to autocommit script
- [ ] P2 governance-sync text added to tick prompt playbook
- [ ] P3 credential-blocker rule in CLAUDE.md
- [ ] FR-0025 marked resolved
- [ ] Both aged tick branches merged
