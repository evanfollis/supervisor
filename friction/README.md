# Friction

This surface captures friction points as durable artifacts the moment
they're noticed during supervisor work. Friction is the raw material
for system improvement; leaving it in session transcripts is how it
gets lost.

Think of this as policy-search input:

- friction records are the reward/error signal
- charter, playbooks, prompts, and state surfaces are the current policy
- repeated friction means the policy needs refinement
- resolved recurring friction is evidence the policy improved

## What belongs here

- Moments where the system made the supervisor do extra work it
  shouldn't have had to do.
- Moments where a truth source turned out to be stale, incomplete, or
  missing.
- Moments where a rule the supervisor imposed on itself turned out to
  be self-imposed, not principal-set.
- Moments where a whole class of problem almost shipped because no
  check existed.
- Principal-surfaced drag factors ("you had to prompt me to do X").

## What does not belong here

- Individual bug fixes in project code — those belong to project
  sessions.
- Tactical TODOs — those belong to tasks or `active-issues.md`.
- Philosophical design musings without a concrete failure instance —
  those belong to `docs/` or `ideas/`.

## File shape

`FR-NNNN-<slug>.md`:

```
# FR-NNNN: <title>

Captured: <iso-date>
Source: <session|reflection|synthesis|principal>
Status: open | mitigated | resolved | promoted-to-<ref>

## What happened
## Why it matters
## Root cause / failure class
## Proposed fix
## References
```

## Promotion paths

- A friction that points at a structural gap → ADR.
- A friction that recurs → `ideas/IDEA-NNNN-…` for pressure testing.
- A friction that's local and fixable → direct work + mark resolved.
- A friction already handled in this or a later session → mark
  `resolved` with a short note; keep the record.

Do not delete resolved entries. Their existence is the learning trail.

## Discipline

- **Hunt friction during work**, not only at end of session.
- **Every supervisor session extracts friction before close.** Zero
  extracted is a signal to look harder, not a sign the session was
  smooth.
- **Promote compounding friction.** If three frictions share a root
  cause, open an ADR.
- **Tune policy from friction.** Do not just record drag; update the
  governing surfaces that caused it when the fix is clear.
- **Use transcripts as behavioral telemetry.** They are where you see
  hesitation, passivity, repeated principal prompts, and self-imposed
  gates. They are not authoritative fact sources; disagreements between
  transcript and current truth sources are friction to capture.
