# Adversarial review — PR #1 "Enforce profiled repository contracts" (commit `43e4f37`)

Date: 2026-07-26
Reviewer: general (Claude, executive) — opposing-agent review of a Codex-authored control-plane change
Subject: draft PR https://github.com/evanfollis/supervisor/pull/1
(branch `agent/repository-contract-enforcement`). Reviewed head: **`9e98b5b`** (two commits:
`43e4f37` "Enforce profiled repository contracts" + `9e98b5b` adding root-risk ceiling and
session-mapping validation). Files: `Makefile`, `repo.toml`, `config/repositories.toml`,
`scripts/repository-contract.py`, `tests/test-repository-contract.py`, `docs/architecture.md`,
`README.md`.
Scope: read-only. No branch, PR, project repo, or GitHub state was modified. Behavior was
verified in disposable detached worktrees at `43e4f37` and `9e98b5b`, removed after inspection.
I did not approve or merge the PR.

**Update for `9e98b5b` (second commit):** it adds `workspace-risk-exceeds-root` (root
`agentic_risk` is now a ceiling over its `workspaces.*` risks — a real fix for mixed-risk
semantics) and validates the inventory's `session` against `scripts/lib/sessions.conf`
(`session-unknown` / `session-path-divergence`). Both have tests; the suite is now 6/6 green.
This resolves my minor "session unvalidated" point and partially addresses PR-A4. It does **not**
touch the Makefile: I re-confirmed at `9e98b5b` that `make test` still exits 0 when a test fails,
so **PR-B1 remains blocking**, and PR-A2/A3 stand.

## Verdict: **amend**

The implementation is clean, safely written, and correctly operationalizes several invariants
of the accepted ADR-0050 standard (runtime/generated must be gitignored; per-workspace risk;
repo.toml↔inventory divergence cross-check; honest authority split). But one **blocking**
correctness defect must be fixed before merge — the enforcement tool's own `make check` masks
test failures — and three amendments should land with it. Not `reject`: the core is good and close.

## Evidence gathered (read-only, in a worktree at `43e4f37`)

- Unit tests pass: `python3 tests/test-repository-contract.py` → `Ran 4 tests … OK`.
- Supervisor self-check is green: `python3 scripts/repository-contract.py .` → `checked=1
  findings=0` (exit 0).
- Inventory without `--allow-missing` → **13 findings** (11 repos `declaration-missing`, plus
  synaplex misdeclared); with `--allow-missing` → **3 findings**, all real: `synaplex:
  schema-version: expected 1, found '1.0'`, `name-invalid`, `canonical-repository-invalid`.
  So `--allow-missing` hides only *undeclared* repos; it still catches a *misdeclared* one.
- **Masking demo:** adding `tests/test-aaa-fails.py` (`sys.exit(1)`) plus a later passing test
  and running `make test` → **exit 0**. The failure was swallowed.

## Blocking

### PR-B1 — `make test` (hence `make check`) masks test failures — a direct §3 violation in the enforcement tool

`Makefile` `test` target:

```make
test:
	@for test_file in tests/test-*.py; do python3 "$$test_file"; done
	@for test_file in tests/test-*.sh; do bash "$$test_file"; done
```

The `for … done` runs in one shell with no `set -e`; a non-final failing test does not stop the
loop, and the recipe's exit status is the **last** command's. Demonstrated: a failing
`test-aaa-fails.py` followed by a passing test → `make test` exits 0. `check: contract test
eval` inherits this. ADR-0050 §3 says required checks "must not mask failures"; §13 DoD and §10
CI both key on `make check`. So the tool that enforces "no masked failures" can go green while
tests fail — the single most important defect here.

**Correction (required):** make each iteration fail-fast, e.g.
`@set -e; for f in tests/test-*.py; do python3 "$$f"; done` (and the `.sh` loop), or run under a
real runner (`python3 -m pytest -q` / an explicit failure accumulator). Guard the empty-glob
case (`shopt -s nullglob` or a `[ -e ]` test) so an unmatched `tests/test-*.py` glob doesn't
run a literal filename. Add a regression test asserting `make test` exits non-zero when any
test fails. **Evidence/risk:** false-green CI on the whole portfolio.

## Amend (should land with the fix)

### PR-A2 — runtime/generated artifacts are required to EXIST, contradicting §13 "clean checkout"

`validate_repo` flags `artifact-path-missing` when a listed artifact path is absent, for every
role including `runtime`/`generated`; `test_runtime_artifact_must_exist_and_be_ignored` enshrines
"must exist and be ignored." But §5 externalizes runtime state and §13 requires `make check` to
pass **from a clean checkout**, where gitignored runtime/generated dirs do not exist. So any repo
that declares a repo-relative runtime/generated artifact fails clean-checkout conformance. The
supervisor's own `repo.toml` sidesteps this by listing only `authoritative`/`historical`, so the
rule is currently untested against a real runtime declaration — but it is wrong as written.

**Correction:** for `runtime`/`generated`, check *"gitignored if present"* and drop the
existence requirement (or forbid repo-relative runtime paths entirely, forcing externalization).
Update the test to match. **Risk:** the DoD becomes self-contradictory for exactly the repos the
standard most wants to fix.

### PR-A3 — `--allow-missing` is a blanket bypass while the inventory's `conformance` field is ignored

`config/repositories.toml` carries `conformance = "migrating"` per repo, but
`repository-contract.py` never reads it; `--allow-missing` blanket-filters
`declaration-missing`/`front-door-missing`/`architecture-missing` for the whole inventory. This
cannot distinguish a legitimately not-yet-migrated repo from one that **regressed** (deleted its
`repo.toml` after conforming) — both pass. As migration completes, `--allow-missing` will either
stay on forever (permanently masking non-adoption) or flip off in a big-bang that lights up every
still-unmigrated repo.

**Correction:** drive the gate from `conformance`: a repo marked `conforming` must be fully
validated (no allowance); only `migrating` repos may omit a declaration; and an unknown/absent
`conformance` is itself a finding. Then `--allow-missing` is unnecessary or narrowly scoped, and
conformance ratchets forward per-repo instead of by a global flag. **Risk:** silent, indefinite
non-adoption behind a green inventory check.

### PR-A4 — the check's green is much weaker than "ADR-0050 conformant"; say so

`repository-contract.py`'s docstring is "Validate ADR-0050 repository declarations and front
doors," and it does exactly that: declaration well-formedness, front-door file **existence**,
artifact gitignore, name/remote divergence, workspace-risk *values*. It does **not** validate §7
(instruction size / thin-adapter — the supervisor's `AGENTS.md`/`CLAUDE.md` are 28 KB symlinks to
the charter and pass on existence alone), §8 (the containment baseline — for a repo that declares
`agentic_risk = "agentic"` and runs as root, the check asserts nothing about isolation), the
shape-specific profiles (§4), or artifact-list **completeness** (the supervisor omits `ledger/`,
`friction/`, `ideas/`, `handoffs/`, `systemd/` from its artifact roles and still passes). So a
green `make contract` means "the thin declaration is well-formed," not "conforms to the standard."

**Correction:** state the scope honestly in the script docstring and `docs/architecture.md`
("declaration + front-door presence validator; it does not verify §7/§8/§4 or artifact-list
completeness"), so a green is not misread as full conformance — or add those gates. This is the
answer to "does the 564-line implementation earn its complexity": yes for what it validates, but
it must not be marketed as enforcing the parts of ADR-0050 where the substance (containment,
instruction discipline) actually lives.

## What is correct and should be preserved

- The validator is safe: `subprocess.run([...])` arg-lists (no shell), read-only `git
  check-ignore`, `tomllib`, frozen `Finding` dataclass, `--json` output. No injection, network,
  or credential surface.
- It implements real, tested invariants that were only recommendations in the ADR review:
  runtime/generated must be gitignored (`artifact-path-tracked-risk`), per-workspace
  `agentic_risk` (`workspace-risk-invalid`), root risk is a ceiling over workspace risk
  (`workspace-risk-exceeds-root`, added in `9e98b5b`), repo.toml↔inventory
  `name`/`canonical_repository` divergence, and — new in `9e98b5b` — the inventory `session` is
  validated against `sessions.conf` with a repo-path-within-session-root check
  (`session-unknown`, `session-path-divergence`). These are the kind of tested invariants that
  justify the line count.
- The validator itself does **not** mask: `main` returns `1 if findings else 0` via
  `SystemExit(main())`, so `make contract` correctly fails on findings (only `make test` masks —
  PR-B1). (An earlier piped measurement of exit code reflected `tail`, not the validator; the code
  path is correct.)
- `docs/architecture.md` is honest and resolves two of my ADR-0050 review concerns: it keeps
  `CLAUDE.md` as a working symlink so the ADR-0021 SessionStart hook still finds `context-always-
  load` (my ADR review B1), and it cleanly states the authority split — `repositories.toml`
  authoritative for host/session/GitHub, `repo.toml` authoritative for shape/lifecycle/risk/
  artifacts (my ADR review O3).
- `--allow-missing` still catches misdeclared repos (it flagged synaplex's malformed `repo.toml`),
  so it is a bootstrap allowance, not a total bypass.

## Minor / optional

- `Path.exists()` follows symlinks and returns true for a directory named `README.md`; front-door
  presence is existence-only. Low risk.
- `schema_version != 1` is int-strict: a TOML float `1.0` passes (`1.0 == 1`) while the string
  `"1.0"` fails (as synaplex hit). Harmless inconsistency; consider coercing/int-checking.
- The inventory's `session` is now validated against `sessions.conf` (`9e98b5b`); the `path` and
  `conformance` fields are still unvalidated for well-formedness. Optional.
- `make eval` runs `scripts/prompteval check .` unconditionally in `check`; a repo without a
  `.prompteval/` should no-op cleanly rather than error — confirm per shape.

## Pointer for the two malformed declarations surfaced (domain-owned, not this PR)

The inventory run shows `synaplex/repo.toml` is already present but malformed
(`schema_version = "1.0"`, bad `name`/`canonical_repository`). That is the synaplex migration
session's to fix, not this PR — but it is good evidence the validator works, and it should be
routed to synaplex rather than silently carried under `--allow-missing`.

## Bottom line

Fix PR-B1 before merge (it defeats the tool's own purpose and is empirically demonstrated).
Land PR-A2/A3/A4 with it (clean-checkout runtime rule; conformance-driven gating; honest scope).
The structure, safety, and the invariants it does test are good — this is a close `amend`, not a
`reject`.
