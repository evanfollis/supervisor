---
priority: urgent
created: 2026-04-25T16:47Z
source: supervisor-tick-2026-04-25T16-47-24Z
doctor_check: tick-branch-age
---

# URGENT — tick branch `ticks/2026-04-20-22` aged 113h (merge overdue)

`workspace.sh doctor` reports FAIL:

> tick branch 'ticks/2026-04-20-22' aged 113h (>72h — attended merge overdue)

## Action required

Merge or delete the aged tick branch. If the branch contains work worth keeping, merge it to main and push. If it's stale/superseded, delete it:

```bash
git branch -d ticks/2026-04-20-22   # or -D if not fully merged
```

Doctor also reports 31 commits ahead of origin/main. If a push is warranted, coordinate with the git-push workflow.

## Evidence

`workspace.sh doctor` run at 2026-04-25T16:47Z; full output at supervisor-tick-2026-04-25T16-47-24Z.md.
