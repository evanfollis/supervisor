# Promotion Criteria

Promotion is the act of converting repeated lower-level judgment into explicit
policy. It should be earned, not assumed.

## Promote only when the pattern is stable

A resolution is promotable when all of the following are true:

1. it has succeeded more than once
2. it is legible enough to explain without replaying the full transcript
3. its boundaries are clear enough to state when it does not apply
4. its blast radius is acceptable for the layer receiving the delegation

## Evidence standard

Before promoting, gather:

- at least two concrete instances of the same underlying issue
- the actual local resolution used
- why that resolution appears reusable
- what would make the policy unsafe

If the pattern is high-blast-radius, require stronger evidence than "it worked
twice."

## Promotion targets

Choose the narrowest artifact that can carry the policy:

- `playbooks/` for recurring procedures
- `decisions/` for workspace architectural choices
- project or workspace `CLAUDE.md` / `AGENTS.md` for standing behavioral rules
- code or automation only when the policy is mature enough to deserve hard
  enforcement

## Do not promote when

- the observed issue is still poorly understood
- the "pattern" is just two unrelated symptoms
- the local resolution depended on hidden operator judgment
- the promoted behavior would reduce needed escalation quality

## Promotion packet

Every promotion proposal should answer:

- `pattern`
- `evidence`
- `target_artifact`
- `scope`
- `known_non_applications`
- `rollback_plan`

## Ratchet rule

Delegation should expand one-way only after evidence. Do not widen authority
because a higher layer is tired of dealing with the issue.
