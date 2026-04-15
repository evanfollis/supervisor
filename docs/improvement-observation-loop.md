# Improvement Observation Loop

System inconsistencies and agent behavioral failures are fuel for improvement.

The purpose of this loop is not blame or verbosity. The purpose is to capture
examples of failure precisely enough that later analysis can identify the
general issue rather than overfitting to the surface incident.

## What to capture

- system design mismatches
- control-plane blind spots
- behavioral tendencies that repeatedly distort judgment
- transport failures
- prompt-shape failures that degrade reasoning
- contradictions between declared policy and actual behavior

## Where to capture it

Append runtime observations to:

- `/opt/workspace/runtime/.telemetry/improvement-observations.jsonl`

Keep durable current implications in:

- `system/active-issues.md`
- relevant `projects/*.md`
- ADRs when the issue implies a policy change

## Rule

Do not brush off mistakes once they are noticed. If an inconsistency,
oversight, or recurring behavioral distortion is visible, capture it in the
runtime observation log and then decide whether it needs:

- a current-state issue
- a policy change
- a tooling change
- a future finetuning/generalization pass
