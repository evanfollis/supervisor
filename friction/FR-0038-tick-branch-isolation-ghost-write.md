# FR-0038: Tick-branch isolation — friction files never reach main

Captured: 2026-05-03T06:50Z
Source: attended-tick-2026-05-03T06-50-00Z
Status: open

## What happened

Multiple tick sessions (2026-05-01T08, 2026-05-02T06, 2026-05-02T22, 2026-05-03T04)
each claimed to write FR-0038 through FR-0041 to disk. As of 2026-05-03T06:50Z,
none of those files exist on main.

Root cause: the supervisor tick wrapper checks out a `ticks/YYYY-MM-DD-HH` branch
before launching the Claude session. All writes and commits go to that branch.
The branch is pushed to origin but never merged to main. Verification steps inside
the tick session confirm file presence on the tick branch — they pass — but the
files never appear on main.

This is the same class as FR-0029 (ghost FR claimed in events). FR-0029 was written
Apr 18; as of May 3 the mechanism is now confirmed across 4+ tick sessions and all
claims about friction files, active-issues updates, and other Tier-A writes from tick
sessions should be treated as "written to tick branch only" until a merge playbook
or wrapper merge step lands.

## Evidence

- `ls /opt/workspace/supervisor/friction/FR-00{38,39,40,41,42}* → none found` (2026-05-03T06:50Z)
- git log --oneline shows only autocommit entries; no tick-session commits on main
- Tick sessions ticks/2026-05-03-00, ticks/2026-05-03-02, ticks/2026-05-03-04 all claimed
  to write these files; all failed to land on main.

## Fix needed

Merge playbook: `proposal-merge-tick-branches-playbook-2026-04-26T03-37-07Z.md` (INBOX Apr 26).
Or: modify tick wrapper to `git merge --no-ff` the tick branch to main after the session exits.
Tier-C: requires attended session or Tier-B-auto authority approval.

## Impact

- Governance surfaces (friction/, active-issues.md, verified-state.md) updated by ticks
  are on orphaned branches; main diverges from reality by every unmerged tick.
- Attended sessions must re-write what ticks claimed to write.
- Doctor WARN "friction surface: no records in last 7 days" is a false positive —
  the records exist on tick branches.
