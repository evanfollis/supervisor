# FR-0036: Local context-repository meaning missed

Captured: 2026-04-25T12:18:42Z
Source: principal
Status: open

## What happened

In a workspace-root executive conversation about agent memory, the principal
asked how the DPM paper compared to "context-repository or other recent views
on agent memory." The executive treated `context-repository` as an external
public term, searched the web, and compared DPM primarily against Letta's public
"Context Repositories" framing before checking the workspace-local
`projects/context-repository/` repo, `CLAUDE.md`, or ADR-0031.

## Why it matters

`context-repository` is a named in-house substrate in the workspace. Root
`CLAUDE.md` identifies it as the host for L1 canon and as the canonical contract
source for governed repos. ADR-0031 explicitly separates local context repos,
canon, knowledge system, and runtime memory surfaces. Missing that local meaning
caused a category error in a principal-facing architecture comparison.

## Root cause / failure class

The executive satisfied the "recent views" part of the question with web search
before grounding the in-workspace term. This is a local-canon lookup failure:
when a principal uses a named workspace artifact, the executive must check local
front doors and decisions before treating the phrase as a public concept.

## Proposed fix

Add or strengthen a workspace-root heuristic: for any named internal-looking
artifact (`context-repository`, canon, atlas, skillfoundry, command, synaplex,
pressure queue, etc.), search local workspace truth surfaces first
(`CLAUDE.md`, `supervisor/decisions/`, relevant project `CURRENT_STATE.md` /
`README.md`) before external research or comparison.

The corrected comparison should frame DPM against the accepted four-layer split:
agent context repositories, canon, knowledge system, and runtime memory/retrieval
surfaces.

## References

- `/opt/workspace/CLAUDE.md`
- `/opt/workspace/projects/context-repository/README.md`
- `/opt/workspace/projects/context-repository/CURRENT_STATE.md`
- `/opt/workspace/projects/context-repository/docs/agent-context-repo-pattern.md`
- `/opt/workspace/supervisor/decisions/0031-explicit-layer-separation-for-context-canon-knowledge-and-memory.md`
