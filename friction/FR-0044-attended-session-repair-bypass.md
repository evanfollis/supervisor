---
id: FR-0044
title: Attended sessions skip charter-authorized P1 repairs to pursue strategy work
class: behavioral
first-observed: 2026-05-24
recurrences: 2
status: open
---

# FR-0044 — Attended session repair bypass

## Observation

Two consecutive attended sessions opened new strategy threads while skipping named P1 repairs that are explicitly marked in `active-issues.md` as "first action of next attended session":

- **2026-05-24T04:49Z prior window**: strategy work done, P1 repairs skipped
- **2026-05-24T01:40Z this window**: `ea3751d` ("Frame recommerce underwriting income sleeve") committed; `scripts/lib/.erofs-test-meta-reflection` + `TEST_WRITE_2951547` still untracked; `reflect.sh:193` arg ordering still broken

The skipped items are:
1. `git clean -f scripts/lib/.erofs-test-meta-reflection scripts/lib/TEST_WRITE_2951547` — zero-judgment, direct action
2. Fix `scripts/lib/reflect.sh:193` arg ordering — Tier-B access confirmed, no principal gate

## Why this is friction

The charter (`CLAUDE.md`) names these items "ATTENDED SESSION ACTIONABLE" and "Direct action — no judgment required." The attended session had Tier-B access (it committed `ea3751d`). The charter provides no authorization to defer P1 items in favor of unrelated strategy work. The pattern has recurred without any policy change permitting it.

## Impact

- Test-artifact false-positive cascade continues (11 cycles)
- `reflect.sh:193` fix undelivered for 10+ cycles
- Carry-forward loops accumulate without close

## Proposed fix

The executive should add a charter rule or playbook step: at session start, if `active-issues.md` lists items marked `ATTENDED SESSION ACTIONABLE` or `Direct action`, clear those before opening new threads. The rule already exists implicitly in the reentry procedure; it needs to be enforced more explicitly and checked at session start.

**Status: open**
