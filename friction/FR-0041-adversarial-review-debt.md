---
id: FR-0041
title: Adversarial review debt accumulating — no systematic detection
severity: HIGH
status: open
created: 2026-04-27
---

# FR-0041: Adversarial review debt accumulating

## Pattern

- Atlas `90bd5fc` (203-line S3-P2 escalation gate): 3rd reflection carry-forward,
  no review artifact. A dedup bug was subsequently found in that code.
- ADR-0031: shipped without cross-agent review. 8+ reflection windows elapsed.
- ADR-0032: shipped without cross-agent review. 6+ reflection windows elapsed.
- URGENT-adr-review-gap has been deferred by 8+ consecutive tick sessions.

The review mechanism exists (`.reviews/` directory, cross-agent review in charter).
Nobody invokes it systematically. There is no automated detection of review debt
(no gate in the reflection prompt scanning for commits >100 insertions without a
matching `.reviews/` artifact).

## Root cause

Adversarial review is triggered by a rule in the charter but has no automated
enforcement. In practice it requires either a human reminder or a self-motivated
session to initiate. Neither fires reliably.

## Consequences

- Structural bugs escape undetected (dedup bug in atlas found post-ship)
- ADR governance lacks the cross-agent pressure test it was designed to have
- Carry-forwards grow monotonically without a ceiling

## Fix direction

1. Add a paragraph to `reflect-prompt.md` instructing the reflection agent to
   scan for commits >100 insertions lacking a `.reviews/` artifact (Tier-C, see
   INBOX `proposal-review-debt-scan-2026-04-26T15-33-43Z.md`)
2. ADR-0031 and ADR-0032 reviews remain URGENT (see INBOX items)
