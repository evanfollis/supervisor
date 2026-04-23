# FR-0035 — Canon CI absent for phase-0 fixtures

**Filed**: 2026-04-23
**Source**: polarity schema audit (context-repo handoff `context-repo-polarity-holistic-audit-2026-04-23T19-25Z`)
**Status**: open — FR candidate, not yet promoted to ADR or action

## Observation

Canon's own phase-0 test fixtures at `spec/discovery-framework/phase-0/cases/atlas/*.md` are not validated against the canon JSON schemas. Two phase-0 cases (`04-kill-early.md:59`, `11-misleading.md:105`) use `polarity: "ambiguous"`, which is not in the v0.1.0 `Evidence.polarity` enum. This drift went undetected for the entire life of v0.1.0 — surfaced incidentally during an unrelated audit.

Phase-0 fixtures are the spec's own test bed — if they don't pass validation, the spec and its fixtures are out of sync and readers of the spec are trusting a contract that hasn't been mechanically checked against its own examples.

## Scope

- **In scope of this FR**: phase-0 fixtures vs schemas validation gap.
- **Out of scope**: live-envelope validation. `skillfoundry-harness/src/skillfoundry_harness/discovery_adapter/migrate.py` uses `jsonschema.Draft202012Validator` to check adapter-emitted envelopes at migration time (this is how the `weakens_assumption` error was caught originally). Atlas `.canon/` envelopes are schema-clean today (`supports`/`contradicts`/`neutral` only) but appear to go through a different path — if they don't validate, that's a sibling gap worth its own note.

## Why it matters

1. **Spec-and-fixture divergence compounds silently.** Without CI, a schema change that breaks fixtures goes unnoticed until someone runs a validation manually. The `weakens_assumption` and `ambiguous` drifts together show how the polarity surface has been under-audited for ~7+ weeks.
2. **Adversarial review can't catch this.** Review artifacts in `supervisor/.reviews/` reason about text; they don't mechanically execute the schema. A CI run does.
3. **Other enums may have analogous drift.** A one-time audit won't find future drift. CI does.

## Proposed action (not yet authorized)

Add a CI step — bash script or pytest under `spec/discovery-framework/ci/` or `supervisor/scripts/` — that walks every phase-0 case fixture and validates the embedded envelopes against the relevant schema. Failure ≡ spec-fixture divergence; blocks further spec changes until reconciled.

Implementation sketch:

```python
# spec/discovery-framework/ci/validate-phase-0.py
# For each *.md in phase-0/cases/:
#   extract JSON code blocks with "object_type": "..."
#   validate against schemas/{object_type.lower()}.schema.json
#   collect failures → exit non-zero if any
```

Runs on every push to context-repository main. Failure message: `FIXTURE DRIFT: phase-0/cases/<case>.md:<line> polarity='ambiguous' not in enum ['supports','contradicts','neutral']`.

Either a dependency on jsonschema (small, vendored is fine) or a hand-rolled validator for the subset of JSON-Schema features the canon actually uses. Either works.

## Why this is FR-class not ADR-class

This is a gap-closure mechanic, not an architectural decision. The decision ("canon fixtures should be validated against canon schemas") is self-evident. What's missing is the mechanic. An ADR would be over-process; an FR that can be assigned and closed is right-sized.

## Dependencies

- Adversarial review on the polarity schema proposal (`docs/polarity-schema-v0.1.1-audit.md`) may reveal schema changes that affect fixtures. CI landing before v0.1.1 creates a fixture-reconciliation choke point; landing after v0.1.1 means fewer known-failures to start with. Either order works.
- No ADR-class prerequisites.

## References

- Handoff: `runtime/.handoff/context-repo-polarity-holistic-audit-2026-04-23T19-25Z.md`
- Related proposal: `projects/context-repository/docs/polarity-schema-v0.1.1-audit.md`
- Schemas: `projects/context-repository/spec/discovery-framework/schemas/*.schema.json`
- Fixtures: `projects/context-repository/spec/discovery-framework/phase-0/cases/atlas/*.md`
- Live validator (works today): `projects/skillfoundry/skillfoundry-harness/src/skillfoundry_harness/discovery_adapter/migrate.py`

## Escalation

No urgency flag. This is a medium-priority correctness gap. File and let the next canon-owning session pick it up when spec-review capacity is available.
