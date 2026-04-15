# Playbook: Novel idea intake and pressure test

**Trigger**: the human principal or a lower layer proposes a new idea,
experiment, workflow, capability, or structural change that is not already
covered by standing policy.

**Owner**: supervisor

**Preconditions**:
- The idea is new enough that no existing ADR, playbook, or workspace policy
  clearly settles it.
- The supervisor can identify the affected layer or admit that it cannot yet.

**Outputs**:
- An idea record under `supervisor/ideas/IDEA-*.json`
- A durable markdown artifact under `supervisor/docs/` or `supervisor/decisions/`
  when the idea changes workspace governance
- A refreshed idea-focus artifact under `runtime/.meta/idea-focus-*.md`
- A one-line event in `supervisor/events/supervisor-events.jsonl` if the idea
  produces a decision or delegation
- A disposition of `adopted`, `sandboxed`, `deferred`, or `rejected`

## Steps

1. **Capture the idea in one sentence.**
   Rewrite the proposal as a crisp change statement. Strip away enthusiasm,
   rhetorical framing, and implied implementation.

   If no idea record exists yet, create one:
   ```
   workspace.sh idea new --title "..." --summary "..."
   ```

   **Verify**: the idea can be expressed as "Change X so that Y improves."

2. **Classify the layer impact.**
   Determine whether the idea is:
   - project-local
   - cross-project
   - governance-affecting
   - authority-expanding

   **Verify**: at least one of those labels is explicit.

3. **Name the structure it would disturb.**
   State which current policy, workflow, trace contract, authority boundary, or
   repo shape would change if the idea were adopted.

   **Verify**: the answer names a real existing artifact or says "none."

4. **Pressure-test the idea.**
   Answer, in writing:
   - what recurring judgment would this compress if it works
   - what new complexity would it add
   - what failure mode becomes more likely
   - what the smallest valid test surface is
   - what evidence would count as failure

   **Verify**: both upside and downside are explicit.

5. **Choose a disposition.**
   Use:
   - `adopted` if the fit and evidence are already strong
   - `sandboxed` if the idea deserves a bounded trial
   - `deferred` if timing or prerequisites are wrong
   - `rejected` if the idea adds more structural cost than justified

   **Verify**: the chosen disposition matches the evidence, not the novelty of
   the idea.

6. **Write the next control-plane artifact.**
   Update the idea record with the current disposition, evidence, and next
   step:
   ```
   workspace.sh idea update IDEA-0001 --status sandboxed --next-step "Run bounded trial"
   ```

   - For governance changes: create or update an ADR.
   - For bounded trials: create a scoped plan or handoff naming explicit
     success and stop conditions.
   - For deferred or rejected ideas: record the reason in a durable doc so the
     system does not keep re-litigating the same proposal from scratch.

   **Verify**: there is a durable artifact path to point at.

7. **Refresh the active novelty queue.**
   ```
   workspace.sh idea-focus
   ```

   **Verify**: `/opt/workspace/runtime/.meta/LATEST_IDEA_FOCUS` points to a
   newly written `idea-focus-*.md` file.

## Rollback

- If the idea was prematurely adopted into a broad surface, demote it to
  `sandboxed` or `deferred` in a new ADR or follow-up doc rather than quietly
  pretending the earlier decision never happened.
- If the pressure test was too shallow, rerun this playbook instead of forcing
  implementation to discover the missing reasoning.

## Notes

- The purpose of this playbook is not to suppress novelty. It is to keep
  novelty governable.
- Good pushback changes the shape of an idea before it changes the shape of the
  system.
