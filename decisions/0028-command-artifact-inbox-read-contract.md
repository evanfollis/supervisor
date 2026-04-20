# ADR-0028: Command artifact inbox — read-only, code-path-only allowlist

Date: 2026-04-20
Status: proposed
Author: command session (claude), acting on principal approval 2026-04-20T15:xxZ
Note: status demoted `accepted → proposed` 2026-04-20T16:xxZ by general
session — adversarial review not yet run; command PM session is not the
acceptance authority per charter. Route through
`supervisor/scripts/lib/adversarial-review.sh` before promoting.
Handoff: `runtime/.handoff/command-artifact-inbox-route-2026-04-20T15-55Z.md`

## Context

The principal needs a browser-accessible surface for reading long-form
artifacts (research notes, scouting docs, cross-cutting syntheses)
produced elsewhere in the workspace. The stopgap — a private cloudflared
path `command.synaplex.ai/_inbox/<nonce>/...` serving pre-rendered HTML
from `/opt/workspace/runtime/inbox/` via `synaplex-inbox.service` — works
but sits outside command's auth envelope and relies on URL-nonce secrecy.

The durable fix lives in command: a route that inherits command's
existing password + JWT auth and renders markdown on demand from a narrow
set of workspace locations.

## Decision

Command exposes `/artifacts` (list view) and `/artifacts/<source>/<path>`
(doc view) behind the existing middleware. The route reads workspace
markdown through a **code-path-only source allowlist**, not a generic
filesystem proxy.

### V1 source allowlist (hardcoded in `src/lib/artifacts.ts`)

| source id    | root path                                 | shape                                          |
| ------------ | ----------------------------------------- | ---------------------------------------------- |
| `research`   | `/opt/workspace/runtime/research/`        | recursive tree, `.md` only                     |
| `syntheses` | `/opt/workspace/runtime/.meta/`           | flat, only files matching `cross-cutting-*.md` |

`.meta/` is **not** mounted wholesale. The `syntheses` source re-applies
the `cross-cutting-*.md` regex on every read — per-project reflections,
maintenance reports, health snapshots, and handoff state remain
out-of-band.

`supervisor/handoffs/ARCHIVE/` is listed in the handoff as optional and
deferred to a later pass.

### Read contract

- Extension allowlist: `.md` only. Pre-baked `.html` siblings in
  `runtime/research/` are ignored (the point of retiring the stopgap is to
  stop serving pre-rendered HTML).
- Path resolution: `path.resolve(ROOT, requested)` → `fs.realpathSync`
  (collapses symlinks) → assert the resolved path equals ROOT or starts
  with `ROOT + path.sep`. String-prefix check alone is insufficient
  (`/opt/workspace/runtime/research-evil/...` would match a naive prefix
  test on `/opt/workspace/runtime/research`).
- Reject before resolving: empty segments, `..`, null bytes, absolute
  paths, any segment starting with `/`.
- Markdown renders server-side on every request via `react-markdown` +
  `remark-gfm` + `rehype-slug` (heading anchors). No build-time
  pre-rendering — acceptance criterion is "reload reflects file changes."
- No write path. Read-only.

### Out of scope for V1

- Search across artifacts.
- Agent-generated artifact posting (needs separate write-path + authn
  design).
- Retirement of the cloudflared `/_inbox` stopgap, `synaplex-inbox.service`,
  `/opt/workspace/runtime/inbox/`, `inbox-render.py`, `inbox-server.py` —
  left in place until the principal confirms the new route end-to-end.
  Retirement is a separate cleanup pass.

## Consequences

- `src/lib/artifacts.ts` is the single audit surface for what command is
  allowed to read. Any future source addition is an ADR-class change that
  touches this file and its allowlist.
- Sources must be explicit and typed. No "generic markdown browser" mode.
- The reader is a file reader behind auth; the path-resolution logic is
  the whole security story. Smoke extends to cover the traversal-attack
  case alongside happy-path rendering.

## Alternatives considered

- **Continue the cloudflared `/_inbox` stopgap.** Rejected — sits outside
  the auth envelope, URL-nonce is the entire access control, and
  pre-rendered HTML decouples browser output from source-of-truth.
- **Generic filesystem proxy with a deny-list.** Rejected — deny-lists
  over a live workspace tree are perpetually one oversight away from
  exposing `.env`, session transcripts, or private keys.
- **Per-source API routes instead of one parameterized route.** Rejected
  for V1 — the security posture is identical and the shared resolver keeps
  the audit surface small. Per-source handlers become attractive only when
  a source has genuinely different semantics (e.g. a write path).

## Provenance

Principal ask captured in handoff
`runtime/.handoff/command-artifact-inbox-route-2026-04-20T15-55Z.md`,
from the workspace-root executive session on 2026-04-20. This ADR lands
alongside the implementing code.
