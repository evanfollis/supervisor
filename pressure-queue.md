# Pressure Queue

This file tracks items the supervisor has decided to keep pushing until they
are structurally resolved, clearly delegated, or explicitly deprioritized.

It is not a backlog. It is the curated list of pressure the supervisor is
actively holding on behalf of the principal.

## Current pressure

### Context repository redesign must become operational, not abstract

- Owner: supervisor -> `context-repo` PM
- Why pressure exists: the redesign has already shown one round of drift toward
  schemas and governance abstraction instead of current-state operational
  surfaces.
- What "better" looks like: the repo becomes a live context repository with
  compressed current-state surfaces, explicit truth-source boundaries, and no
  dependence on transcript replay.

### Command must stop being a `/review` enforcement exception

- Owner: supervisor -> `command` PM
- Why pressure exists: the shared review gate is live, but `command` still has
  no git repo, which makes the most obvious enforcement surface the weakest one.
- What "better" looks like: `command` is on normal git footing and the review
  gate becomes real there instead of nominal.

### Command login double-submission cannot remain ambient

- Owner: supervisor -> `command` PM
- Why pressure exists: the login double-submission issue has been unresolved
  for 34+ days and 10+ reflection cycles despite a small known implementation
  option, so it is now evidence of drift rather than a normal backlog item.
- Status note: as of 2026-07-12, this remains 34+ days unresolved and should
  stay visible until the `command` PM lands a fix or records an explicit
  disposition.
- What "better" looks like: the next attended `command` session either ships
  the small fix, records an explicit won't-fix verdict, or explains why a
  different login-flow correction is the accepted path.

### Telemetry minimum contract still needs to exist

- Owner: supervisor
- Why pressure exists: meta-scan and cross-project reasoning remain noisy while
  events have no minimum required shape.
- What "better" looks like: a minimum event contract exists and projects are
  graded against it.

### PM autonomy must become an explicit managed outcome

- Owner: supervisor
- Why pressure exists: the stack still relies too much on the principal
  correcting the supervisor and the supervisor correcting PMs in one-off ways.
- What "better" looks like: repeated nudges convert into policy, prompts,
  checklists, telemetry, or delegated standards that reduce future supervision.

### Executive must preserve latent structure, not mirror literal phrasing

- Owner: executive / supervisor
- Why pressure exists: the top layer still risks collapsing principal input
  into literal tasking or deferential compliance instead of interpreting and
  protecting the deeper architecture the principal is building toward.
- What "better" looks like: principal interaction is treated as strategic
  signal; the executive pushes back when needed, clarifies the intended
  structure, and shapes PM behavior around that structure.

### Executive must not relapse into direct project implementation under pressure

- Owner: executive / supervisor
- Why pressure exists: when `command` felt strategically important and visibly
  broken, the executive bypassed the PM layer and started doing project work
  directly instead of reshaping the `command` PM and holding an acceptance bar.
- What "better" looks like: acute importance raises PM pressure, architecture
  clarity, and acceptance rigor; it does not silently collapse the stack back
  into "executive edits project code."

### Command must become a real executive control plane, not a stitched-together shell relay

- Owner: supervisor -> `command` PM
- Why pressure exists: `command` is accumulating useful slices, but it still
  too often behaves like UI over tmux/session mechanisms rather than one clean
  executive abstraction.
- What "better" looks like: one canonical task model, one canonical executive
  lane model, and a browser surface that hides mechanism instead of forcing the
  principal to reason about it.

### Persistent session recovery must stop depending on principal intervention

- Owner: supervisor / workspace infrastructure
- Why pressure exists: after reboot, the persistent PM/session layer dropped
  out, and the attached supervisor harness could not restore it because tmux
  socket access is blocked even though file writes are allowed.
- What "better" looks like: session recovery is reachable from the supervisor's
  normal operating surface, or the system clearly exposes a sanctioned host-side
  recovery path that does not require the principal to rediscover it.

### Project sessions cannot run their own mandatory eval gates (sandbox vs ADR-0039)

- Owner: supervisor / workspace infrastructure -> then `command` PM
- Why pressure exists: ADR-0039 makes a passing `prompteval` baseline a
  fail-closed precondition for every project deploy, but the project-session
  sandbox blocks the subscription-CLI calls prompteval needs (`command`'s
  session hit an approval-reviewer wall on external-provider calls + baseline
  mutation and escalated for *principal approval*). The identical run is
  unblocked from the operator surface. So a mandatory, autonomous, zero-cost
  gate is unreachable by the layer that owns it — which stalled `command`'s
  deploy gate for 6 reflection cycles and, on 2026-07-17, pulled the executive
  into running the baselines directly. This is the mechanism behind the
  standing "executive must not relapse into direct project implementation"
  pressure: the PM keeps routing sanctioned work up because it physically
  cannot run it down here.
- What "better" looks like: a sanctioned bridge so a project session can run
  its own `prompteval` release baselines without a false principal-approval
  wall — either a scoped allowlist/sandbox exception for the specific
  `prompteval run` command, or an explicit operator-run baseline capability the
  PM invokes by handoff to `general` (not by escalating to the principal).
  Until then, blocked baseline runs route to `general`, never to the principal.
  Candidate for an ADR once the sandbox posture is decided with the principal.
