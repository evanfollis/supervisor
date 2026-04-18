# Project: atlas

## Current status

- **Active, but not top-priority.** Atlas has real project activity and a clear
  autonomous-research architecture, but several previously surfaced leverage
  items are still open.
- The main integrity risk remains the split claim-hash truncation between two
  write paths, which can silently bifurcate hypothesis identity.
- Atlas still has no meaningful presence in the shared workspace telemetry
  stream, which keeps cross-project synthesis blind to its activity.

## What needs to change

- Unify claim hashing across all claim-write paths.
- Run the overdue adversarial `/review` on the ingest/write-path work.
- Add minimum shared telemetry so atlas can participate in workspace-level
  observation.

## Executive stance

- Maintain pressure through the project lane; this is a meaningful correctness
  and observability issue, but it does not currently justify executive
  implementation.

## Active artifact links

- Routing handoff:
  `/opt/workspace/runtime/.handoff/atlas-synthesis-proposals-2026-04-15T10-48-22Z.md`
- Latest reflection:
  `/opt/workspace/runtime/.meta/atlas-reflection-2026-04-15T14-22-22Z.md`
