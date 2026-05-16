---
target: commit 6bba7dd in projects/synaplex (skip_next_run primitive in intake/escalation.py + arxiv wiring + test)
reviewer: Claude (general-purpose subagent fallback; codex not installed on this host)
mechanism: /review skill, fallback path
date: 2026-05-16T03:00Z
handoff: runtime/.handoff/URGENT-synaplex-adversarial-review-6bba7dd.md (4-cycle escalation)
status: review complete; BLOCK-level finding fixed in follow-up commit; non-blocking findings carried forward
---

# Adversarial Review — synaplex 6bba7dd

## Challenges (from reviewer)

1. **`set_skip_next_run` OSError swallow is mis-framed as telemetry.**
   The function catches `OSError` on `write_text("")` and silently
   returns. This is labeled `"best-effort, like record_stuck —
   telemetry not load-bearing"` but the framing is wrong. `record_stuck`
   is genuinely decorative (the load-bearing signal is the separate
   `escalated` event); `set_skip_next_run`'s **marker file IS the
   backoff mechanism**. If `write_text` fails (ENOSPC, perms drift,
   tmpfs full, RO remount), the 429 handler thinks the next run will
   skip but it won't, and the next 4h cron hammers the degraded
   upstream with zero telemetry that the backoff itself failed. This
   is a "silent failure inside the failure handler" pattern.
   **BLOCK** — must surface the write failure or remove the silent swallow.

2. **`STATE_DIR.mkdir(...)` on every call.** Cheap on a warm inode
   cache but adds a syscall to every fetch and every 429. Worth
   folding into `paths.ensure_dirs()` at startup. Cleanup, not bug.

3. **`consume_skip_next_run`'s `exists()` → `unlink()` window** IS a
   TOCTOU race, but the existing `except OSError: return False` catch
   closes it correctly under a real two-consumer race. The `exists()`
   check is redundant and obscures the reasoning; cleaner pattern:
   `try: p.unlink(); return True; except FileNotFoundError: return False`.
   Cleanup, not blocker.

4. **Exception-after-consume**: if `emit_throttled` or
   `read_existing_items` raises after `consume_skip_next_run` returned
   True, the flag is already gone. The skip semantic was honored by
   the raise (no fetch happened) but the *next* run goes ahead and
   fetches a possibly-still-degraded upstream — one extra hammer
   before the next 429 re-arms. Minor in practice given how trivial
   those calls are; worth noting because the documented "one-shot"
   contract is stronger than the code guarantees.

5. **TimeoutError symmetric to 429 — yes on Py3.12.** `socket.timeout`
   aliases `TimeoutError` since Python 3.10, and the venv is 3.12.3.
   If the venv ever regresses to 3.9, `isinstance(exc, TimeoutError)`
   silently stops catching `urlopen` timeouts. Pin or assert
   somewhere.

6. **Test gaps:** no concurrent set/consume test; no write-failure
   path test (the BLOCK in #1 makes this currently un-testable); no
   integration test that arxiv wiring actually emits `throttled` when
   consume returns True (test exercises the primitive only).

## Systemd `Type=oneshot` answer (from reviewer, verbatim)

> Concurrent firing of `synaplex-intake.service` via the timer is
> structurally prevented — but not by `Type=oneshot`. The mechanism
> is systemd's job engine: while the unit is in `activating` (ExecStart
> running) or `active`, a new start job from the timer is merged/dropped
> (default job mode `replace`, which on a unit already starting becomes
> a no-op for the duplicate start). The same would be true under
> `Type=simple`. `Type=oneshot` is incidental — it controls when the
> unit transitions to `active` vs `inactive`, not concurrency.
>
> However, §4 from the prior review does NOT close. Two real
> concurrency vectors remain:
> - Manual invocation of `.venv/bin/python -m intake ingest ...` from
>   a shell or another tmux session bypasses systemd entirely.
> - `systemctl start synaplex-intake.service` overlapping a
>   timer-triggered run is blocked by systemd, but the python module
>   is directly executable and is the path Evan/Claude sessions
>   actually take for smoke runs.

## Verdict (from reviewer, verbatim)

> Block on the OSError-swallow framing fix in `set_skip_next_run`
> (either emit on write failure, or stop labeling the backoff write
> as "telemetry not load-bearing"). §4 from the prior review remains
> open for manual-invocation interleave and must not be marked
> closed for this codepath. TOCTOU and TimeoutError handling are
> correct as-is; test coverage gaps are real but ship-blocking only
> if you want to harden before Episode 6. Otherwise the design is
> sound.

## Disposition (this session)

**Fixed in follow-up commit (BLOCK + cleanups):**
- #1: `set_skip_next_run` now emits a `failure` friction event when
  the marker write fails, and the function comment is corrected to
  reflect that the marker IS the backoff mechanism.
- #3: `consume_skip_next_run` rewritten using
  `try: p.unlink(); except FileNotFoundError: return False` —
  removes the exists() redundancy and makes the TOCTOU handling
  legible.
- #5: docstring on the new helpers calls out the
  `socket.timeout == TimeoutError` Py3.10+ assumption that arxiv.py
  relies on.

**Carried forward (non-blocking):**
- #2 mkdir-on-every-call — fold into `paths.ensure_dirs()` next time
  paths.py is touched. Pure performance, no correctness implication.
- #4 exception-after-consume — micro-edge case; documented in code
  comment so future readers don't trip.
- #6 test gaps — `intake/test_skip_next_run.py` covers the primitive
  in isolation; integration test (arxiv wiring under mocked failure
  modes) and concurrent test are deferred.
- §4 (file-lock race for manual-invocation interleave) — explicitly
  remains open per the reviewer's verdict; do NOT close in
  CURRENT_STATE.

The reviewer's BLOCK is satisfied this turn; the carry-forward
items are documented in CURRENT_STATE Known broken with explicit
trigger conditions.

## Procedural note

Codex unavailable on host (`adversarial-review.sh` exits with
"codex not installed"). The /review skill's documented fallback was
used: a separate Claude session via the Agent tool with
subagent_type=general-purpose, with the staged diffs at
`/tmp/6bba7dd-*.patch` and read-only access to live source. Same
limitation as the prior review (synaplex-5814658-no-clobber-...);
not a cross-vendor review, so falsification pressure is lower than
a Claude/Codex pair would provide. Future operator with codex on
PATH should re-run for a stronger second opinion.
