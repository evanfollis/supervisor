# ADR-0031: Explicit layer separation for context, canon, knowledge, and memory

Date: 2026-04-23
Status: accepted
Accepted: 2026-04-23
Author: executive, workspace-root session
References: ADR-0027, IDEA-0005, context-repository pattern spec, canon v0.1.0

## Context

The workspace had converged on several strong ideas, but the boundary lines
between them were still easy to blur in conversation:

- `context-repository` hosts the **agent context repo pattern** in `docs/`
  and the **canon spec** in `spec/discovery-framework/`.
- synaplex's **knowledge system** was defined in ADR-0027 as a durable layer
  above canon, but its relation to context repos and runtime memory surfaces
  was still implicit.
- recent Q2 2026 memory-system research introduced a fourth concern:
  **runtime memory surfaces** (file-based memory, MCP servers, vendor-managed
  memory stores) that help agents retrieve and write context, but are not the
  same thing as formal truth.

That produced recurring ambiguity:

- comparing `context-repository` to Graphiti / mem0 / vendor memory products
  as if they occupied the same layer
- treating canon as if it were the knowledge system
- treating a context repo as if it were a cross-pod truth layer
- treating runtime memory tooling as if it were a source of truth rather than
  a retrieval interface

This ADR makes the stack explicit so the system can stop relying on oral
tradition for the distinction.

## Decision

The workspace stack is explicitly four-layered.

### 1. Agent context repositories

Definition: per-agent or per-repo **operational state surfaces** that make
sessions resumable without starting cold.

Examples:

- `CURRENT_STATE.md`
- `index.md`
- repo-local `CLAUDE.md` always-load declarations
- repo-specific depth files used for orientation and local state

Properties:

- mutable, overwritten-to-current-state
- optimized for cold orientation and ongoing operational work
- local to an agent/repo/domain
- not a formal truth model
- not a cross-pod invariant store

The pattern for this layer is specified in:
`projects/context-repository/docs/agent-context-repo-pattern.md`

### 2. Canon

Definition: the **formal obligations and provenance model** for claims,
evidence, decisions, policy, promotion, realization, and replay/audit.

Examples:

- `projects/context-repository/spec/discovery-framework/canon.md`
- related schemas, audit questions, and validator rules
- emitted envelopes in project `.canon/` stores

Properties:

- append-only, provenance-preserving, validation-first
- optimized for replay, audit, and governance integrity
- the formal substrate that constrains what must be answerable
- not a retrieval runtime
- not the full knowledge system

Canon answers: "What was claimed, what evidence existed, what decision was
made, under what policy/exposure, with what artifact provenance?"

Canon does **not** answer: "What is the cheapest/fastest/best runtime memory
interface for agents right now?"

### 3. Knowledge system

Definition: the accumulating body of **validated invariants and reusable
methodologies** that persists across pod lifecycles and can be projected into
publication, education, command, and future pods.

Properties:

- derived from canonized evidence/decisions plus review outputs
- durable across pod lifecycles
- should become bitemporal/supersession-aware
- should support projections and consumption tracking
- distinct from both local context repos and formal canon

The knowledge system is the semantic layer that says:
"Given the canonized record, what currently-best invariants have survived
criticism strongly enough to become reusable system knowledge?"

Its physical home remains open and is tracked by IDEA-0005.

### 4. Memory and retrieval surfaces

Definition: the **runtime interfaces** agents use to read, write, search,
summarize, or project context/knowledge across sessions.

Examples:

- Claude Code auto memory (`MEMORY.md` + topic files)
- Anthropic memory tool
- Anthropic Managed Agents memory stores
- Graphiti MCP
- vendor-managed memory banks/stores
- future synaplex MCP memory surfaces

Properties:

- replaceable
- chosen for retrieval quality, ergonomics, latency, interoperability,
  privacy, and cost
- may read from or write into local context repos, canon-backed projections,
  or separate stores
- not authoritative by themselves

This layer is where runtime memory products compete. It is not where formal
truth lives.

## Co-location rule

`projects/context-repository/` intentionally co-locates **two** concerns:

1. the agent-context-repo pattern lab in `docs/`
2. the canon spec in `spec/discovery-framework/`

That co-location is allowed, but the distinction must be explicit in every
front-door description of the repo. The repo is **not** itself the synaplex
knowledge system, and it is **not** a production memory-runtime service.

## Consequences

### Evaluation discipline

When evaluating alternatives, compare like with like:

- Graphiti / mem0 / vendor memory stores compete with **memory/retrieval
  surfaces**
- canon competes with other **truth/provenance/governance substrates**
- context repos compete with other **operational front-door / resumability
  patterns**
- the knowledge system competes with other **curated invariant layers**

Cross-layer comparisons are category errors unless explicitly framed as such.

### synaplex architecture

For synaplex:

- pods maintain local context repos for their own operational state
- pods emit canon envelopes through their adapters
- the knowledge system is built above canon, not by replacing it
- runtime memory surfaces may expose knowledge-system projections to agents,
  but those surfaces are delivery mechanisms, not truth sources

### IDEA-0005 scope

IDEA-0005 is specifically about the **physical home and artifact shape of the
knowledge system**. It is not a decision about:

- whether canon should exist
- whether context repos should exist
- whether file-based memory should be replaced by a vendor memory tool

Those are separate questions on separate layers.

### context-repository fitness judgment

The correct judgment of `context-repository` is now explicit:

- strong as a pattern lab for agent context repos
- strong as the home of canon
- not intended to be the entire runtime memory system
- not sufficient by itself to serve as the full synaplex knowledge system

That is not a failure. It is a layer boundary.

## Follow-on implications

1. Front-door and shaping docs must use the four-layer vocabulary explicitly.
2. References to the knowledge-system physical-home decision point must point
   to IDEA-0005.
3. The next IDEA-0005 design pass should assume this ADR's layer split and
   decide only the knowledge-system layer.
4. Future memory-tool debates should state whether they concern:
   local context repos, canon storage, knowledge-system projections, or
   runtime retrieval surfaces.

## Provenance

Accepted to resolve recurring ambiguity surfaced by:

- ADR-0027's open design question on the knowledge-system physical home
- the Q2 2026 memory-systems research artifact
- direct executive comparison of `context-repository` against modern memory
  systems on 2026-04-23

