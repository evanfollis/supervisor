# URGENT: synaplex — 5-cycle carry-forward escalation

**From**: reflection-job (automated)
**To**: supervisor / general session
**Date**: 2026-04-29T02:29:54Z
**Root cause**: Two observations have appeared in 5 consecutive synaplex reflection cycles without a fix commit, decision verdict, or `verified` pointer in `dispositions.jsonl`.

---

## OBS-3 (5th cycle): `/review` not run on commit `5814658`

Commit `5814658` introduced `merge_jsonl_by_id` — the shared write path for all three
intake adapters (rss, arxiv, hackernews). CLAUDE.md requires `/review` before shipping
substantial changes. The merge helper is the most dangerous single function in the intake
subsystem: a silent bug there corrupts every daily file on every run.

**Required action**: invoke `supervisor/scripts/lib/adversarial-review.sh` with the diff
of `5814658`. Focus: atomic write correctness, `content_id` collision handling, error
paths if write fails midway.

**Not code-fixable by reflection job**. Needs human or next project session.

---

## OBS-4 (5th cycle): arxiv adapter lacks S3-P2 escalation gate

S3-P2 is accepted in `dispositions.jsonl` (ts: 2026-04-16). The arxiv adapter emits
`stuck` events correctly but does not count consecutive occurrences and does not emit
`escalated` after 3+ consecutive stuck/failure events. Two consecutive overnight
degradation nights (Apr 26–27, Apr 27–28) produced multiple stuck events with no
escalation. The reflection job is the only thing surfacing this.

**Required action**: ~20-line patch to `intake/adapters/arxiv.py` — track consecutive
stuck count (last N events from friction log or a lightweight `.meta/arxiv-stuck-count`
file); emit `eventType: "escalated"` after threshold=3; reset on success.

**Disposition reference**: `S3-P2` accepted 2026-04-16T11:45:00Z. No fix commit found.

---

## Workspace escalation rule citation

> "A synthesis observation that has been reported in 3+ consecutive reflection cycles
> without a corresponding fix commit, decision verdict, or `verified` pointer in
> `dispositions.jsonl` must trigger an URGENT handoff to `supervisor/handoffs/INBOX/`."
> — `/opt/workspace/CLAUDE.md`, Automated Self-Reflection Loop section

Both items exceed the threshold (5 cycles vs. required 3). This handoff satisfies the
escalation obligation. Synthesis job should route to next synaplex session.
