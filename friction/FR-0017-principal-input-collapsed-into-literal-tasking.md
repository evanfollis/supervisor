# FR-0017: Principal input collapsed into literal tasking instead of strategic intent interpretation

Captured: 2026-04-15
Source: principal
Status: open

## What happened

The principal stated that they should be able to "dump my thoughts to you" and
have the executive interpret intent from shared history and the target system,
then shape the projects accordingly. Instead, the experience still felt too
close to ordinary ChatGPT-style task handling: the principal remained the
integrator, had to chase low-level follow-ups, and saw too much literal
execution instead of strategic shaping.

## Why it matters

This is the core value proposition of the whole workspace. If the principal
still has to translate strategy into lower-level project instructions, then the
system has not created leverage; it has only created a more elaborate shell
around the same interaction pattern.

## Root cause / failure class

**The executive has not yet made intent interpretation a first-class operating
responsibility.**

It still too easily treats principal input as:

- task request
- bug report
- local design comment

instead of first classifying it as:

- strategic intent
- architecture pressure
- policy correction
- delegation signal
- friction signal

## Proposed fix

1. Amend the executive charter and role definition so principal input is
   explicitly interpreted before it is executed or delegated.
2. Treat interaction-derived signals as part of IDEA-0002, not as incidental
   sentiment.
3. Require the executive to translate principal input into:
   - what is true now
   - what the system should change structurally
   - which project(s) need pressure
   - what should become policy
4. Treat moments where the principal has to re-explain the intended level of
   abstraction as friction to harvest immediately.

## References

- Principal message 2026-04-15: "I should be able to dump my thoughts to you..."
- Principal message 2026-04-15: "Right now it feels like ... I am just using ChatGPT."
- `/opt/workspace/supervisor/system/active-ideas.md`
- `/opt/workspace/supervisor/roles/executive.md`
