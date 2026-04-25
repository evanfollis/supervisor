---
from: synthesis-translator
to: general
date: 2026-04-24T03-35-50Z
priority: high
task_id: synthesis-throttled-eventtype-telemetry
source_synthesis: /opt/workspace/runtime/.meta/cross-cutting-2026-04-24T03-26-55Z.md
source_proposal: Proposal 3 — Add `throttled` event type to telemetry schema
---

# Add `throttled` event type to telemetry schema

The current `eventType` vocabulary does not distinguish designed throttling from genuine failures. This produces false-positive escalation signals in meta-scan and the S3-P2 stuck monitor.

## Proposed change

**`/opt/workspace/CLAUDE.md`** — add to the Architecture Governance section, after the `sourceType` rule (line 141):

```
- **`eventType` must distinguish failures from designed throttling (S1-P2 addendum).**
  `eventType: "failure"` is reserved for genuinely unrecoverable errors. Designed rate-limiting,
  cap hits, and expected backpressure must emit `eventType: "throttled"` (or `"info"` for
  purely informational events). Meta-scan, S3-P2 monitors, and adversarial review automation
  all key on `eventType` — a `failure` on a designed behavior is a false positive that
  degrades the escalation surface.
```

## Rationale

**Synaplex** (02:40Z): *"`eventType: 'failure'` emitted for expected daily-cap truncation — pollutes meta-scan... 4 [of 9 events] are 'daily cap hit: 1077+ items dropped' — expected, correct throttling behavior."* The friction module has no `throttled` or `info` event type, so designed behavior is recorded as failure. Meta-scan, adversarial review automation, and the S3-P2 stuck monitor all read `eventType` — a `failure` on a cap hit produces false-positive escalation signal.

This is a signal-quality degradation issue: channels designed to carry high-priority signal (telemetry events, INBOX) are degraded by expected events filed at the wrong severity.

## Verification before action (required)

- Read `/opt/workspace/CLAUDE.md` at the Architecture Governance section (around line 141) to confirm the amendment is not already present.
- Check git log: `git log --oneline supervisor/ | grep -i "throttle\|eventtype"` to see if a related amendment has landed.
- If the `eventType` section already includes guidance on throttled/info distinction, write a completion report stating "already documented in-file" rather than re-applying.

## Acceptance criteria

- The amendment is added to `/opt/workspace/CLAUDE.md` in the Architecture Governance section, immediately after the `sourceType` rule.
- The text explicitly names the three consumers (meta-scan, S3-P2 monitors, adversarial review automation) to justify the importance.
- The amended CLAUDE.md is committed with a message explaining that designed throttling must not pollute failure signals.
- No code changes required — this is a documentation/governance amendment only.
- Completion report at `runtime/.handoff/general-synthesis-throttled-eventtype-complete-<iso>.md`.

## Escalation

URGENT if:
- The amendment already exists in `/opt/workspace/CLAUDE.md`. Document and close without re-applying.
- Conflict detected with existing telemetry rules or S1-P2 guidance. Surface the conflict in the completion report.
