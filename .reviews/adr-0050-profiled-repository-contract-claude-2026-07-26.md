# Adversarial review — ADR-0050 (profiled repository contract & agentic safety baseline)

Date: 2026-07-26
Reviewer: general (Claude, executive) — opposing-agent review of a Codex-authored proposal
Subjects:
- `supervisor/decisions/0050-profiled-repository-contract-and-agentic-safety-baseline.md`
- `supervisor/docs/repository-architecture-standard.md`
Scope: read-only. No ADR, standard, repo, charter, service, or GitHub state was modified.
Review path: `supervisor/AGENT.md` §Review path (Claude reviews the opposing agent's proposal).

## Verdict: **amend**

The direction is right and should be adopted: standardize *invariants and navigation*,
not identical trees; separate artifact roles; make containment the safety boundary; one
public-portfolio lifecycle. The core reasoning is sound and the alternatives are correctly
rejected. But four findings are **blocking for adoption as a binding standard** because,
as written, they either silently break an accepted mechanism, set a Definition of Done that
nothing in the workspace can currently meet, or would break the deploy path if the audit is
applied mechanically. Fix B1–B4 and adopt; O1–O6 sharpen it but do not block.

This verdict is `amend`, not `accept`, specifically because ADR-0050's own §13 Definition of
Done and §10 GitHub audit are self-inconsistent with the workspace they govern until B1–B4
land. It is not `reject`: the standard is lean, the exception is already guarded, and the
migration order is well-sequenced.

---

## What survives review (preserve these — they are correct)

- **"Invariants, not identical trees"** with shape profiles that keep framework/domain
  conventions (§Decision, §4). The rejected "one tree" and "cleanest repo as template"
  alternatives are correctly rejected — verified: the repos genuinely differ (Atlas is
  `src/atlas/` src-layout; Synaplex is flat root packages `intake/ lab/ reasoning/ scan/
  editorial/ site/`; context-repository is a published spec bundle).
- **Artifact-role separation** (authoritative / runtime / generated / historical) is a real,
  useful contract.
- **The containment baseline content (§8)** matches current provider guidance and is the
  right *target*.
- **Migration order §12** — fix correctness/containment before cosmetic moves; shims before
  renames; published interfaces move last — is the correct sequencing.
- **The narrow git-canon exception (§5) is defensible and already guarded**, contra a naive
  "runtime never in git" reading: Synaplex's `lab/.canon/` store is guarded by
  `integrity/` (`python -m integrity`) and `lab/canon/` (`store.py`, `serialize.py`,
  `test_canon.py`, `test_conformance.py`); Atlas has `tests/test_canon_adapter.py`. The
  exception is not too permissive *in principle* (see O4 for the one tightening it needs).
- **No generic controller / shared framework** (respects ADR-0049). Correct.

---

## Blocking findings

### B1 — The `AGENTS.md`-canonical flip silently breaks the SessionStart context-load (ADR-0021)

§7 makes `AGENTS.md` the canonical instruction front door and `CLAUDE.md` "a thin adapter …
must not duplicate the charter." But the accepted context-injection mechanism reads
`CLAUDE.md`, hard-coded:

- `/root/.claude/hooks/session-start-context-load.sh:39` — `CLAUDE_MD="$CWD/CLAUDE.md"`
- `:42–46` — it extracts the `context-always-load:` YAML block **from that file only**;
  "No CLAUDE.md or no block: silent no-op."

So the moment the `context-always-load:` block moves into `AGENTS.md` (or `CLAUDE.md` is
trimmed to a stub), every session at that cwd **silently stops injecting ESSENCE.md,
verified-state, active-issues, etc.** — the exact failure ADR-0021 exists to prevent, and it
fails *silently*. No project currently has an `AGENTS.md` (verified: 0 of synaplex/atlas/
command/context-repository), so this is a net-new flip across the whole fleet.

Worse: in Synaplex the `CLAUDE.md` is not merely an instruction file — it is a
**prompteval-governed artifact** registered in `.prompteval/inventory.json` (the Synaplex
charter prompt). Demoting it to a "thin adapter" or moving its content to `AGENTS.md` breaks
the ADR-0039 governance binding unless the inventory is repointed in lockstep. Command's
`.prompteval/inventory.json` similarly whitelists exact `src/lib` builder files by path. So
the instruction-file flip is coupled to *two* accepted mechanisms (ADR-0021 hook, ADR-0039
prompt governance), not one.

**Correction (required):** treat the hook and the prompteval inventories as coupled
consumers. Either (a) teach `session-start-context-load.sh` to read `AGENTS.md` first with a
`CLAUDE.md` fallback, landed *before* any repo flips; or (b) keep the `context-always-load:`
block in `CLAUDE.md` and let `AGENTS.md` be the human/agent prose front door. Any repo whose
`CLAUDE.md` is prompteval-governed (Synaplex) must repoint its `.prompteval/inventory.json`
in the same change. Add the hook to §12 migration order and name ADR-0021/ADR-0039 in
References. **Evidence/risk:** silent loss of the executive/PM orientation bundle → the
carelessness failure class the charter's primary-verification gate is built around; plus a
broken prompt-eval gate.

### B2 — The non-root containment baseline (§8) contradicts the root-running reality with no transition, making §13 unmeetable

§8 requires "run model-controlled code as a non-root project identity … sandbox … default
deny … keep secrets outside the sandbox," and §13 DoD requires "model-controlled execution
meets its declared risk baseline." Verified reality: **everything runs as root** —
`workspace-supervisor-tick.service` and the session units are `User=root`; the live shell is
`whoami=root`; the reflection/tick/executive Claude and Codex sessions all execute as root
with broad workspace and host reach. **Zero** `agentic_risk="agentic"` repo can meet the §8
baseline today, so §13 conformance is unreachable for every agentic repo the moment the
standard is binding.

The standard states the target but gives no path from root→non-root for the observed server,
and §12 migration order lists "tighten service identity and containment" as one step without
acknowledging that this is the single largest and riskiest change (it touches the session
supervisor, the tick sandbox, credential brokerage, and every systemd unit).

The non-root move also has two concrete constraints the inventories surface that §8 does not
account for: (a) Atlas's root runner writes a **git-tracked** file (`graph/causal_graph.json`)
every hour — changing the exec identity changes the owner of a tracked artifact and can break
the commit path; (b) Synaplex's `lab.runner.providers` needs a prepared `PATH` to the
subscription `claude`/`codex` executables (pinned in `deploy/subscription-cli-paths.env`) — a
sandbox that strips `PATH` or blocks those binaries breaks provider execution and collides
with ADR-0036.

**Correction (required):** (1) add an explicit **current-state gap register**: enumerate
which §8 controls exist today (systemd `ProtectSystem=strict`/`ReadWritePaths` on the tick —
real; OS-level Tier-C read-only mount — real) vs which do not (non-root identity, sandboxed
network/proc, capability-token brokerage — absent). (2) Make §13 gate on *"meets its declared
baseline **or** carries a dated, owned exception with a remediation milestone,"* not on full
compliance. (3) Sequence the non-root/sandbox migration as its own ADR-class workstream with
canaries, because it can break the whole session fabric, the two constraints above, and the
credential-broker path. **Evidence/risk:** as written the standard is aspirational prose that
no repo can pass, so it will be ignored or gamed — worse than a smaller baseline that actually
binds. This is the sharpest answer to review point 6: the July-2026 requirements are strong
*in content* but not *enforceable against the observed root-running server* without a
transition plan.

### B3 — Mechanical GitHub branch protection (§10) breaks the push-to-main autodeploy path

`/opt/workspace/CLAUDE.md:197` — "**Deploy path: git push → webhook → autodeploy.** … Push
to main and let the pipeline handle it." Verified: `main` on `evanfollis/synaplex` has **no
branch protection today** (`branches/main/protection` → 404), which is exactly why direct
push-to-main deploys work. §10 mandates "required-branch rules" and §13 DoD includes "tracked
workflow/security configuration passes the portfolio audit." If protection requiring PR
review is applied mechanically (the audit's natural reading), **direct pushes to main are
blocked and every autodeploy breaks.**

§10 does hedge ("branch rules after the required checks are proven stable"), but that hedge is
about *timing*, not about the *incompatibility* with push-to-main deploy. Nothing in the
standard says "do not enable PR-review protection on a repo whose deploy is a push-to-main
webhook."

**Correction (required):** §10 must carve out the autodeploy flow explicitly — enable
*required status checks* without *required PR review* on push-to-main repos, or migrate deploy
to an Actions workflow keyed on protected `main` **before** protection is enabled — and the
portfolio audit must not flag "no PR-review protection" as a defect on autodeploy repos.
**Evidence/risk:** silent breakage of production deploys across the hosted fleet. (Code
scanning is *not* a concern here — all checked repos are PUBLIC, so CodeQL is free; only
private repos would need GHAS. Note that distinction in §10.)

### B4 — The 4–8 KiB instruction / 8 KiB CURRENT_STATE limits collide with the governance surface and would fail every governance repo's DoD

§7 sets `AGENTS.md` "target 4 KiB, hard maximum 8 KiB without an ADR exception" and
`CURRENT_STATE.md` "target 8 KiB," and §13 DoD requires "root instructions are concise."
Verified sizes: supervisor charter `AGENT.md` **28.8 KB**; workspace `CLAUDE.md` **29.8 KB**;
synaplex `CLAUDE.md` **16.6 KB**; atlas `CLAUDE.md` **18.8 KB**; and CURRENT_STATE.md is
**51 KB (synaplex)** and **64 KB (atlas)** — 6–8× the target. Under §13 as written, every
governance and active-research repo is non-conforming on day one, and "make it conform" means
an 8×-content-reduction migration of *load-bearing* state that §12 does not sequence and that
risks dropping governance content.

**Correction (required):** (a) explicitly exempt `control-plane` shape from the 4/8 KiB
instruction target, or set realistic per-shape targets; (b) reframe the limits as
"target + recorded exception," and require the *exception mechanism to be used* for the
charter and the large CURRENT_STATE files rather than pretending 4 KiB is reachable; (c) add
"trim/relocate oversized instruction & state files (behind links, per §7's own just-in-time
rule)" to §12 as an explicit, reviewed step, since it is a content migration, not a move.
**Evidence/risk:** a DoD that nothing passes is not a standard; and a blind trim of a 64 KB
CURRENT_STATE loses the accuracy the charter's radical-truth discipline depends on.

---

## Optional improvements (non-blocking)

### O1 — `repo.toml` `[artifacts]` path lists are an untested second truth source (review points 1 & 10)

The three scalar axes (`shape`/`lifecycle`/`agentic_risk`) plus `canonical_repository` are
small, bounded, and testable — keep them; they are **not** the second-truth-source problem.
The risk is the `[artifacts]` arrays (authoritative/runtime/generated/historical as path
lists): they restate what `.gitignore`, the src-layout, and the "runtime out of git" rule
already encode, and nothing checks they stay accurate — they will drift. **Recommend:** make
`[artifacts]` optional; where present, add a validator that (i) the listed paths exist and
(ii) every `runtime`/`generated` entry is gitignored. If that validator isn't built, drop the
lists rather than ship an unenforced registry.

### O2 — One `agentic_risk` per repo can't express the Skillfoundry monorepo (review point 3)

A monorepo with agentic products *and* static content is forced to a single risk value; the
axes are otherwise orthogonal, but this one collapses under `monorepo`/`context` shapes.
**Recommend:** allow a `[workspaces.<name>] agentic_risk = …` override for `monorepo`/`context`
shapes, or define the root value as "highest risk present" **and** require per-agentic-subtree
declaration. Otherwise the safety baseline is applied at the wrong granularity.

### O3 — Name one authority direction per field across the two registries (review point 1)

ADR-0050 says the central supervisor inventory "does not override each repo's declaration" —
good — but does not say which is read by tooling or what happens on conflict. **Recommend:**
state explicitly: `repo.toml` is authoritative for shape/lifecycle/risk/artifacts; the
central inventory is authoritative for host/session placement and canonical-GitHub mapping;
a validator flags divergence. One direction of truth per field prevents the exact
second-source drift the ADR is trying to avoid.

### O4 — Require the git-canon guard to run in `make check`, not merely be "declared" (review point 5)

The exception is fine and already guarded (see "What survives"). Tighten §5 from "declared and
mechanically guarded" to "the specific guard is **named** in `repo.toml`/`architecture.md`
**and executed by `make check`**," so the guard can't rot away from the exception it licenses.
This closes point 5 without narrowing a legitimate provenance mechanism.

### O5 — `runtime/projects/<slug>/` is a *third* runtime convention (review points 4 & 9)

Existing runtime state already lives at `runtime/prompteval/<slug>`, `runtime/.command-runtime`,
`runtime/releases/command`, `runtime/research/synaplex-*`, `runtime/intake`, `runtime/friction`
— none of which is `runtime/projects/<slug>/{state,sessions,runs,logs,tmp}` (which does not yet
exist). ADR-0012 relocated logs to `runtime/.telemetry`/`.meta`/`.handoff`. Introducing a new
per-project tree adds a parallel convention that code references. **Recommend:** §12 must
include a one-time mapping of existing runtime paths to the new layout **with compatibility
shims for referencing code**, or adopt the existing conventions. Do not ship a fourth
inconsistent runtime root.

### O6 — Sequence "green `make check`" ahead of any GitHub/cosmetic work (review point 9)

CI is nearly absent (synaplex 0 workflows, command 0, context-repository 0, atlas 1) and the
Context section admits "red or absent CI, masked test failures." §12 mostly orders this
correctly (green check at step 5, GitHub at step 10). Make explicit in §13 that conformance is
**per-repo and incremental**, not a portfolio flag day, and that a repo is "conforming" only
after its own `make check` is green from a clean checkout — otherwise the audit will light up
red across the fleet and stall.

---

## Inventory-grounded findings (review points 4 & 5, sharpened)

The five inventories corroborate the verdict and add specifics the standard must absorb.
Highlights (all quoted from the inventories; underlying repos not independently re-opened):

- **B5 (promote to blocking-for-that-migration) — the context-repository `spec/` bundle is the
  single largest cross-repo break surface.** Eight schemas at v0.2.0 `$ref` each other by
  **bare relative filename** (`common.schema.json#/$defs/…`); the `$id` URIs do not resolve
  over the network, so *the interface is filesystem paths + filenames*. Four consumers couple
  to it by hardcoded absolute path, and critically **two have no override at all**: Atlas
  (`src/atlas/adapters/discovery/migrate.py:49-51`, CLI `--schemas` only) and Synaplex
  (`test_conformance.py:29-31` and `reasoning/check_programmes.py:29-36`). Content is
  digest-pinned downstream (Synaplex `EXPECTED_SCHEMA_DIGEST = "eac15d4c32d90f86"`;
  skillfoundry `MANIFEST.json` sha256 @ `f5b0fd0`). **Required for any move:** add env hatches
  to the un-overridable readers *first*, keep `schemas/` and `conformance/` siblings, keep the
  8 schemas co-located, leave a compatibility symlink, and update digests in lockstep. §12's
  "interfaces move last" is the right rule; the standard should name this specific edge as the
  canonical worked example, because getting it wrong silently breaks Atlas and Synaplex CI.

- **O4 (upgraded) — the git-canon "exception" (§5) omits two properties the inventories prove
  are load-bearing, and does not cleanly cover one tracked artifact.**
  (a) **Path stability is itself a published interface**: canon store paths are digest- or
  provenance-bound, so "canon may stay in git" must also say "and its path is a frozen
  interface."
  (b) **Provenance URIs**: skillfoundry-valuation `.canon/**` envelopes embed absolute
  `file:///opt/workspace/projects/.../valuation-context/memory/...` URIs — a move invalidates
  every provenance URI until `migrate` re-runs. The exception must require a provenance-rewrite
  step on any relocation.
  (c) **Coverage gap**: Atlas's `graph/causal_graph.json` is **tracked and rewritten hourly by
  a root service** — a generated *live* scorer output, not append-only canon. It sits in git
  today but is *neither* clean "runtime out of git" *nor* the append-only "exception" as
  worded. The standard needs a third, explicit disposition for "tracked generated live state"
  (either externalize it, or declare it a reviewed reproducibility artifact with a rebuild
  check) rather than leaving it to fall between the two roles.

- **The ADR-0050 Context defect-list is imprecise per repo (minor, but it drives migrations).**
  The inventories show "installed-only units" is accurate for Command (base `command.service`
  off-repo) and Synaplex (`synaplex-inbox.service`) but **over-states Atlas** (its unit is
  tracked at `deploy/atlas-runner.service`, mirrored to `/etc/systemd/system`); and "dormant
  code sharing namespaces" **under-states Command** — its Plane B (`executor.ts::dispatch()` →
  `sendKeys`, `executive.ts::sendExecutiveMessage()`, `review.ts::runCodexReview()`) is *live
  operator-execution capability* quarantined only by an import-edge test
  (`scripts/product-boundary-test.ts`), not dead code. Recommend the ADR cite per-repo evidence
  rather than a generic defect list, since the list will be read as the migration backlog.

- **The universal contract genuinely does not fit part of Skillfoundry.** Its six declarative
  context lineages and its **non-git coordination root** have no Python package, build, or test
  — `repo.toml` + `Makefile` + `make check` + src-layout have no meaningful target there, and
  `skillfoundry-agents` CI is *structurally* red (its `check_workspace.py` requires gitignored
  `context/` mounts absent from any clean checkout, so "green `make check` from a clean
  checkout" is currently impossible by construction). The standard should state that `context`
  shape and non-repo roots are exempt from the code-command contract, and that a red check
  caused by required-but-absent mounts is a containment/fixture defect to fix, not a Makefile
  to add.

- **Command is the reference model, not a migration target** — it already keeps all durable
  state out of the tree (`workspacePaths.ts` → `/opt/workspace/runtime/...`) and runs the
  service only from an immutable release dir. The standard should cite Command as the worked
  example of the runtime/authoritative split rather than implying every repo is equally far
  from conformance.

## Coverage of the ten requested pressure-tests

1. **`repo.toml` second source / bounded scope** → scalars are bounded (keep); `[artifacts]`
   lists are the unenforced second source (O1); dual-registry authority under-specified (O3).
2. **`Makefile` as universal discovery** → acceptable as a *thin delegator* (the standard
   already forbids moving logic into Make); for JS/Astro repos it is redundant-but-harmless
   and buys the universal `make check`. Require `make` present; profile exempt is correct.
   No blocking issue.
3. **shape/lifecycle/risk complete/orthogonal/enforceable** → mostly orthogonal and small
   enough to avoid a taxonomy project; the one real gap is per-subtree risk in monorepo (O2).
   `profile` doubling as shape + exemption is acceptable.
4. **path/semantic invariants damaged** → the dominant break surface is the
   context-repository `spec/` bundle with four hardcoded consumers, **two without any override**
   (Atlas `migrate.py:49-51`, Synaplex `test_conformance.py`/`check_programmes.py`) — see **B5**
   in "Inventory-grounded findings." Also: Synaplex's flat multi-root layout vs the
   Python-service `src/<pkg>/` mandate (resolve by classifying Synaplex `monorepo`/exception,
   not `service`); skillfoundry-valuation `.canon/` provenance URIs; Atlas's tracked hourly
   `graph/causal_graph.json`. §12's "interfaces move last, with compatibility paths" is the
   right rule; the standard should adopt the schema edge as its canonical worked example.
5. **runtime exception too permissive** → No, it is defensible and already guarded; tighten
   per O4.
6. **July-2026 requirements strong/specific enough for the root server** → strong in content,
   **not enforceable** against the root-running reality without a transition (B2).
7. **GitHub settings not to apply mechanically** → branch protection vs push-to-main
   autodeploy (B3); code scanning is free for these public repos (note the public/private
   split in §10).
8. **conflicts with ADRs / CLAUDE.md** → ADR-0021 (B1); §7 size limits vs the actual charter
   and CURRENT_STATE files (B4); the AGENTS.md-canonical convention is a net-new flip. No hard
   contradiction with ADR-0012/0036/0039/0043/0049 — the standard is consistent with them.
9. **migration sequencing / rollback / dirty-tree** → §12 is sound; add runtime-path
   reconciliation (O5), incremental conformance (O6). Note: with concurrent active sessions and
   preserved WIP the norm here, §12's "attribute dirty files and identify live writers" (step
   1) should also require that a repo has no *other* session actively writing before a
   structural move — the standard says preserve dirty files but not "don't race a live
   session."
10. **complexity to remove** → the `[artifacts]` registry (O1) is the main un-tested-invariant
    complexity; everything else earns its keep.

---

## Bottom line

Accept the *architecture* after folding in B1–B5. The standard's spine — profiled invariants,
artifact roles, containment-as-boundary, one portfolio lifecycle, interfaces-move-last — is
correct and worth the maintenance cost. But it must (B1) not silently break the ADR-0021
context-load or the ADR-0039 prompt-governance binding, (B2) register the root→non-root gap
and make its DoD meetable, (B3) not break push-to-main autodeploy via mechanical branch rules,
(B4) reconcile its instruction/state size limits with the 28–64 KB governance surface it
actually governs, and (B5) name and sequence the context-repository `spec/` published-interface
migration (env-hatch the no-override readers first). O1–O6 are recommended but optional. The
standard should also cite Command as the reference model and exempt Skillfoundry's declarative
lineages / non-git root from the code-command contract.
