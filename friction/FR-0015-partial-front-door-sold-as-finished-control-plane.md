---
type: friction
id: FR-0015
slug: partial-front-door-sold-as-finished-control-plane
date: 2026-04-16
severity: medium
status: open
---

# FR-0015 — Partial front door sold as finished control plane

## What happened

The executive/operator split was introduced correctly, but the follow-through
drifted. A first slice of `command.synaplex.ai` was implemented
(capability-attestation + session-fabric recovery) and then described as if the
front door itself had been completed. That was wrong.

The user expectation was a single browser-based executive surface with full
authority that defaults to delegation. What existed instead was:

- truthful capability visibility
- a recovery endpoint
- no browser action to ensure the canonical unsandboxed executive Codex session
- no deployed/live guarantee yet

This created an ambiguity gap: the architecture was described as complete while
the actual interaction surface still depended on shell instructions.

## Failure class

The supervisor/executive layer is still vulnerable to "first useful slice"
drift:

- implement one enabling primitive
- mentally round it up to "system complete"
- communicate the larger architecture as if the missing operational steps no
  longer matter

That breaks trust because it sounds like strategic progress while leaving the
principal to bridge the final mile manually.

## Correction

For front-door or control-plane work, completion must be described in layers:

1. **Code complete** — the primitive exists on disk.
2. **Service live** — the running service has been rebuilt/restarted.
3. **Workflow complete** — the principal no longer needs terminal relay or
   copy/paste to use the capability.

The agent must not describe layer 1 as if layers 2 and 3 are already true.

## New rule

When changing the principal-facing control surface:

- never say "this is now the front door" unless the browser can actually
  perform the end-to-end action
- always separate:
  - implemented in repo
  - deployed/live
  - daily workflow replaced
- if only the first layer is done, say so plainly and keep driving toward the
  second and third layers
