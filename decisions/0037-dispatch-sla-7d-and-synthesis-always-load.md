# ADR-0037: Relax dispatch SLA to 7d; add LATEST_SYNTHESIS to always-load

Date: 2026-07-11
Status: accepted

## Context

Two CLAUDE.md-level defects surfaced by 25+ consecutive synthesis cycles
(C114–C138), both confirmed against live state during the attended session
of 2026-07-11:

1. **Dispatch SLA (24h) is a false-violation generator.** The rule "the
   executive must dispatch a delegated project session within 24h" of a
   synthesis proposal assumed near-daily attended contact. Observed contact
   cadence over the last ~5 weeks produced 28 consecutive formal breaches
   (C110–C137) with zero informational value — every breach restated "no
   attended session occurred," which the reflection loop already records.
   A rule violated 100% of the time under normal operation measures the
   wrong thing.

2. **The always-load context set describes a month-old workspace.** During
   unattended stretches, `system/active-issues.md` and
   `system/verified-state.md` in the always-load set go stale (32+ days at
   time of writing; active-issues claimed INBOX=156 vs reality 331, commits
   ahead 224 vs 603). Meanwhile the accurate, live-verified diagnosis is
   regenerated every ~12h at `runtime/.meta/LATEST_SYNTHESIS` but was NOT
   in the always-load path. Cold-start sessions therefore operated on an
   actively misleading map. This session experienced the failure directly:
   the injected context was stale-bannered and truncated while the
   synthesis held the true state.

## Decision

Amend `/opt/workspace/CLAUDE.md`:

1. In "Automated Self-Reflection Loop" → dispatch obligation: change
   "within 24h" to "within 7d, or before any external deadline named in
   the proposal if that is sooner". Breach escalation semantics unchanged.
2. Add a session-start directive (Session Awareness section): every
   workspace session must read `runtime/.meta/LATEST_SYNTHESIS` before
   trusting `active-issues.md` / `verified-state.md` claims older than
   their `updated:` gate. **Not** raw injection into `context-always-load`
   — adversarial review (Codex, 2026-07-11) showed the aggregate already
   exceeds the 30KB cap by ~21KB, so a tail entry would silently never
   inject; and generated synthesis files contain their own code fences,
   which can break the hook's markdown-fence wrapper and promote generated
   text into live prompt context.

Companion action (same session): rewrite `system/active-issues.md` from
live sources — it was 32 days stale, actively misleading (claimed
INBOX=156 vs 331, commits-ahead=224 vs 603), and the dominant consumer of
the 30KB cap.

## Review

Codex adversarial review 2026-07-11: VERDICT ACCEPT-WITH-CHANGES.
Incorporated: SLA urgency override; directive instead of injection (cap +
fence findings). Deferred as follow-ups: hook freshness check keys on
`updated:` not `generated:`; fence-escaping in the injection wrapper —
both only matter if generated files are ever injected, which this
decision now avoids.

## Consequences

- Dispatch breaches become signal again: a 7d breach means a full week of
  synthesis proposals ignored, which genuinely warrants escalation.
- Every cold-start session at `/opt/workspace` reads the latest
  cross-cutting synthesis — the one surface that is live-verified every
  ~12h — closing the stale-map failure class rather than asking humans to
  keep active-issues.md fresh by hand.
- The 30KB aggregate cap pressure worsens slightly; the synthesis lands at
  the tail so truncation hits it last only if upstream files shrink.
  The cap collision remains tracked separately
  (synaplex-always-load-cap-collision).

## Alternatives considered

- **Keep 24h SLA, add exception for unattended windows**: more rule
  surface to maintain; the 7d number achieves the same discrimination with
  one token changed.
- **Regenerate active-issues.md automatically instead of loading the
  synthesis**: duplicates the synthesis pipeline; two write paths to one
  truth surface violates the S1-P3 reconciliation rule.
- **Do nothing**: 28 consecutive false breaches and a 32-day-stale
  cold-start map are measured harms; the status quo is the worst option.
