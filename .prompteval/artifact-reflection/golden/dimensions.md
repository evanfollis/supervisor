# Artifact-reflection golden dimensions

The cases exercise source type (commit, telemetry, transcript, current-state),
evidence condition (exact primary object, stale narrative, no primary object),
proposal count (zero, one, multiple), signal polarity (healthy, degraded,
ambiguous), and instruction pressure (ordinary, certainty-seeking, write-state
request, adversarial narrative).

The highest-risk historical failure modes are represented directly:

- reflection prose recursively reasserting stale CURRENT_STATE claims;
- a plausible prescription becoming executable state without a primary object;
- claimed writes or handoffs that never occurred;
- reflection sessions mutating a project while describing themselves as
  propose-only;
- exact object identity being mislabeled as proof of a proposal's correctness.

Every positive witness case uses files created inside the disposable eval
project. The adapter runs the deterministic attestor before the sandbox is
removed, so a passing marker means only that the emitted hash/reference
resolved exactly at evaluation time. Negative cases ensure narrative inputs do
not become unsupported implementation prescriptions; matching the narrative
object itself never upgrades that relation into causal proof or authorization.
