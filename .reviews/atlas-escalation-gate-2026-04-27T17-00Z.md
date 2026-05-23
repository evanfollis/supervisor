---
target: src/atlas/runner.py — frozen-loop escalation gate
reviewer: claude-sonnet (subagent; codex CLI not installed in this env)
date: 2026-04-27T17:00Z
commits_under_review: 90bd5fc, 34f4a83, ee9beaf
---

# Adversarial review — atlas escalation gate

The codex-based `adversarial-review.sh` was not available in this
environment (`codex: command not found`). Substituted a subagent in the
role of skeptical reviewer with explicit focus on the four areas the
URGENT named: walk-back edges, the 200-event truncation, concurrent
runner safety, and state-file seed inconsistency.

## 1. Most dangerous assumption

That the **read window is large enough to contain `last_emitted_ts` plus
the breaking event**. The gate truncated to the last 200 atlas.runner
events. The dedup at `_maybe_escalate_frozen_loop` requires the window
to contain a `cycle.completed` whose timestamp `> last_emitted_ts` AND
whose decisions break "all-continue." If activity since the last
emission has produced more than 200 atlas.runner events,
`last_emitted_ts` falls outside the window and dedup behavior becomes
silently wrong in either direction (spam or silence depending on
whether the visible window contains a kill).

**Action taken**: raised `READ_WINDOW_MAX_EVENTS` to 5000 (≈ 600h of
cycles at ~8 events/cycle) AND added a coverage check: if every visible
event is younger than `last_emitted_ts`, log a warning and fail-open
(emit). S3-P2 specifically forbids silent monitoring, so fail-open is
the correct choice when the window is uncovered.

## 2. Missing failure mode

**State-file shape and timestamp skew.** `_load_escalation_state` did no
schema validation — `null`, `[1,2,3]`, `{"last_emitted_ts": "x"}`, and
future-dated values all parsed as JSON. A non-int `last_emitted_ts`
raised `TypeError` inside the dedup generator, caught by the cycle's
outer exception handler, and the gate appeared to run while never
escalating. A *future* `last_emitted_ts` would silently kill the gate
because no visible event's timestamp could exceed it.

**Action taken**: `_load_escalation_state` now coerces both timestamps
to `int` and returns `{}` on any malformed value (logs at WARNING). Test
covers the null/string/list cases.

## 3. Boundary most likely to be collapsed in practice

**Concurrent `--once` debug + live service.** The read-check-write at
`_maybe_escalate_frozen_loop` is not atomic. Two parallel runners can
both see the same state, both emit `cycle.escalated`, both call
`_save_escalation_state` (atomic per-writer; second wins, harmless),
and both call `_write_frozen_loop_handoff` (glob-based dedup is racy
between two writers and the filename uses minute precision, so a
within-the-same-minute collision overwrites the URGENT body).

**Action NOT taken**: deferred. In production the systemd service is
the only normal writer; an operator running `atlas run --once` for
debugging while the service is live is the only collision path, and
the worst-case outcome is two telemetry events plus one URGENT file
(handoff dedup wins eventually). A flock around the
read-check-emit-save sequence would close it; tracked in CURRENT_STATE
as a known boundary, not URGENT-class.

## Verdict

Two of the three findings (window cap + state validation) had a real
chance of producing a third bug in a row in this gate — both fixed in
the same session as the review. Concurrency is a known soft edge that
will only bite under simultaneous `--once` + service operation; left
documented but not fixed.
