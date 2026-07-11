---
from: synthesis-translator
to: general
date: 2026-07-02T03:30:46Z
priority: high
task_id: synthesis-reflection-cadence-gating
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-07-02T03-26-11Z.md
source_proposal: P2 — Reflection cadence gating for automated-only windows
---

# P2: Reflection cadence gating for automated-only windows

**Type:** `reflect.sh` change.

**Purpose:** When no attended session has occurred since the last reflection and the prior reflection's observations are materially identical, skip with a one-line carry-forward note instead of re-running the reflection.

**Rationale:** Pattern 2 (C119 synthesis) identifies a consumption-rate problem: reflections accumulate faster than attended sessions can read them. When the state hasn't changed (no attended session since last reflection + observations identical), running the reflection again produces zero new information but consumes tokens and disk. Activity-gated reflection already skips 12 of 16 cycles successfully. This proposal extends that logic: when a reflection would be identical to the prior one and no attended work has happened, output a one-line carry-forward instead of full re-run.

**Blast radius:** All reflected projects (opt-in via `projects.conf`).
**Status:** 6th cycle open (since C114).

## Verification before action (required)

- Check `/opt/workspace/supervisor/scripts/lib/reflect.sh` for existing activity gating (lines ~30–40, look for `no_activity` or similar).
- Search for any `carry-forward` pattern or skipped-reflection logic already in place.
- If partial gating exists, read the full function to understand the current skip logic before modifying.
- If the feature has already landed (synthesis C114 → now C119, so 6 cycles is a long carry), confirm via `git log --oneline -20 supervisor/scripts/lib/reflect.sh`.

## Acceptance criteria

- Modification to `reflect.sh` that:
  - Compares prior reflection output (same project, prior cycle) to current detection logic.
  - If observations are materially identical (same URGENTs, same counts, same patterns) AND no attended session since prior cycle, output: `"CARRY: [prior cycle ID] — observations unchanged, awaiting attended session."`
  - Otherwise, run full reflection as normal.
- Single commit with message: "Gate reflection cadence on material state change (synthesis C119 P2)"
- Completion report documenting the logic change and confirming at least one test run skipped a redundant reflection.

## Escalation

URGENT if:
- Determining "materially identical" observations requires complex diffing. If so, propose a simpler heuristic (e.g., "same counters + same URGENT count") and escalate design choice for confirmation.
- The prior reflection is not available in the same directory structure (e.g., reflections are rotated/deleted older than N days). Document the retention policy required for this feature to work.
