---
id: FR-0023
title: sourceType mandate has no migration path for pre-mandate services
status: open
date: 2026-04-17
source: supervisor-tick-2026-04-17T10-49-44Z
---

Status: open

## What happened

The workspace mandate (S1-P2, CLAUDE.md) requires all active runtime systems to emit
a `sourceType` field so meta-scan can distinguish real traffic from smoke/cron.

The skillfoundry `preflight` service predates this mandate and emits structured JSON
telemetry to journalctl without `sourceType`. The tick that fixed preflight's slug
alignment (2026-04-17T09:16Z) explicitly noted this gap: "preflight telemetry lacks
`sourceType` field — events from automated test calls are indistinguishable from
real-user events in the journal."

## Why it matters

The mandate is only effective if it covers all active services. Pre-mandate services
are exempt by default because there is no enforcement path and no declared migration
SLA. Result: meta-scan still cannot distinguish smoke from signal for preflight, which
is the primary signal source for the skillfoundry commercial hypothesis.

## Root cause

The sourceType mandate was added as a new-code rule, not a migration obligation.
No upgrade path was specified for services already in production.

## What a fix looks like

1. For each active service predating the mandate, add `sourceType` to the telemetry
   emission (typically a one-liner in the structured-log call).
2. Add a compliance check to the preflight/reflect gate, or at minimum list pre-mandate
   services explicitly in CLAUDE.md as acknowledged exceptions with a migration date.
3. The skillfoundry `preflight` service is the highest-priority case (primary commercial
   signal source). Estimated effort: small (one-liner in `src/lib/skill-config.ts`).

## Affected services

- `skillfoundry-products/products/preflight` — confirmed missing (tick 2026-04-17T09:16Z)
- Other pre-S1-P2 services: audit needed
