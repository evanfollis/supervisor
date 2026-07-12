"""The deploy-gate check: pure local, no LLM calls, fast (ADR-0039 §4).

Fail-closed posture (adversarial review 2026-07-12, finding 2): a repo
with NO .prompteval/ registry does not pass silently — it gets scanned,
and likely prompt artifacts fail the gate with adoption instructions.
A repo with no prompts at all passes. False positives are silenced by
listing the file in inventory.json with status "not-a-prompt".

For every registered prompt:
  - spec parses; source pointer extracts cleanly
  - live (prompt, model, params) version == baseline's accepted version,
    baseline records a passing run             -> else: edit without eval
  - live spec_hash == baseline spec_hash       -> else: pointer/executor/
    judge/gate config drifted since acceptance (finding 5)
  - live golden_hash == baseline golden_hash   -> else: criteria changed
    since acceptance; weakening is never silent (finding 3)
  - golden cases structurally valid; holdouts live ONLY in holdout.jsonl
  - holdout discipline: release-run baseline required when holdouts exist;
    holdout input text must not leak into prompt text or spec (tripwire)
  - inventory: governed entries must map to a real spec whose source.file
    matches; enforced repos fail on ungoverned/unlisted prompts

Returns (ok, failures, warnings); the CLI maps to exit codes.
"""

from __future__ import annotations

from pathlib import Path

from .core import read_json
from .goldens import health, load_all_cases, load_cases, validate_case
from .registry import (
    RegistryError,
    list_specs,
    load_inventory,
    registry_root,
    scan,
)


def check_repo(repo: Path) -> tuple[bool, list[str], list[str]]:
    repo = Path(repo)
    failures: list[str] = []
    warnings: list[str] = []

    has_registry = registry_root(repo).is_dir()
    inventory = load_inventory(repo)
    listed_files = {e.get("file") for e in inventory.get("prompts", [])}

    def listed(file: str) -> bool:
        # inventory "file" entries may be fnmatch globs (e.g. "docs/*.md"
        # as not-a-prompt) so recurring false-positive classes are silenced
        # once, not file-by-file
        from fnmatch import fnmatch

        return file in listed_files or any(fnmatch(file, pat) for pat in listed_files)

    # 0. fail-closed scan: unregistered likely prompts block, always
    scan_findings = [f for f in scan(repo) if not listed(f["file"])]
    if scan_findings:
        if not has_registry:
            failures.append(
                f"repo has {len(scan_findings)} likely prompt artifact(s) and no "
                f".prompteval/ registry — run the create-eval-loop skill "
                f"(first hit: {scan_findings[0]['file']})"
            )
        else:
            for f in scan_findings:
                failures.append(
                    f"inventory: likely prompt not listed: {f['file']} "
                    f"({f['reason']}) — govern it or list it with status "
                    f"'not-a-prompt' and a reason"
                )

    specs = []
    try:
        specs = list_specs(repo)
    except RegistryError as exc:
        failures.append(f"registry: {exc}")

    spec_by_id = {s.prompt_id: s for s in specs}

    for spec in specs:
        pid = spec.prompt_id
        gate_cfg = spec.spec.get("gate") or {}

        # 1. extraction + version/spec/golden hashes vs baseline
        try:
            live_version = spec.version()
            live_spec_hash = spec.spec_hash()
        except RegistryError as exc:
            failures.append(f"{pid}: extraction failed — {exc}")
            continue

        rerun = f"(run `prompteval run --id {pid} --no-cache --update-baseline`)"
        baseline = read_json(spec.baseline_path)
        if baseline is None:
            failures.append(f"{pid}: no baseline — {rerun}")
        elif not baseline.get("passed"):
            failures.append(f"{pid}: baseline is not a passing run")
        else:
            # Keep the accepted execution identity human-readable as well as
            # folded into prompt_version/spec_hash.  A legacy baseline that
            # predates these fields must be regenerated; silently accepting
            # it would preserve evidence whose model provenance is opaque.
            expected_identity = {
                "model": spec.spec.get("model"),
                "params": spec.spec.get("params", {}),
                "judge_model": (spec.spec.get("judge") or {}).get("model"),
            }
            for field, expected in expected_identity.items():
                if field not in baseline:
                    failures.append(
                        f"{pid}: baseline lacks {field} provenance {rerun}"
                    )
                elif baseline.get(field) != expected:
                    failures.append(
                        f"{pid}: accepted {field} {baseline.get(field)!r} != "
                        f"live {expected!r} {rerun}"
                    )
            if baseline.get("prompt_version") != live_version:
                failures.append(
                    f"{pid}: prompt edited without eval — live {live_version} != "
                    f"accepted {baseline.get('prompt_version')} {rerun}"
                )
            if baseline.get("spec_hash") != live_spec_hash:
                failures.append(
                    f"{pid}: spec/executor/adapter drifted since baseline "
                    f"acceptance {rerun}"
                )
            from .goldens import golden_hash

            if baseline.get("golden_hash") != golden_hash(spec.dir, gate_cfg):
                failures.append(
                    f"{pid}: golden set changed since baseline acceptance — "
                    f"criteria edits require a fresh eval {rerun}"
                )

        # 2. golden set validity + holdout file discipline
        working = load_cases(spec.cases_path)
        holdouts = load_cases(spec.holdout_path)
        if not working and not holdouts:
            failures.append(f"{pid}: golden set empty ({spec.cases_path})")
        for case in working + holdouts:
            for problem in validate_case(case, path=pid):
                failures.append(problem)
        misplaced = [c["id"] for c in working if c.get("status") == "holdout"]
        if misplaced:
            failures.append(
                f"{pid}: holdout case(s) in cases.jsonl: {', '.join(misplaced)} — "
                f"holdouts live only in golden/holdout.jsonl (sealed file)"
            )
        stray = [c["id"] for c in holdouts if c.get("status") != "holdout"]
        if stray:
            failures.append(
                f"{pid}: non-holdout case(s) in holdout.jsonl: {', '.join(stray)}"
            )

        # 3. holdout discipline + contamination tripwire (prompt AND spec)
        if holdouts:
            if baseline and baseline.get("passed") and not baseline.get("release"):
                failures.append(
                    f"{pid}: holdout cases exist but baseline is not a release "
                    f"run — accept baselines with `run --release`"
                )
            try:
                surfaces = {"prompt": spec.extract(),
                            "spec.json": spec.path.read_text(encoding="utf-8")}
            except (RegistryError, OSError):
                surfaces = {}
            for c in holdouts:
                for surface_name, surface in surfaces.items():
                    if any(len(frag) >= 24 and frag in surface
                           for frag in _string_leaves(c.get("input"))):
                        failures.append(
                            f"{pid}: holdout {c['id']} input text appears in "
                            f"{surface_name} — holdout contamination"
                        )
                        break
        else:
            active = [c for c in working if c.get("status") == "active"]
            if len(active) >= 12:
                warnings.append(
                    f"{pid}: no holdout cases — seal a few before optimizing this prompt"
                )

        # 4. freshness (warn here; escalation cadence lives in `status`)
        h = health(spec.dir, baseline)
        if h["stale_cases"]:
            warnings.append(f"{pid}: {len(h['stale_cases'])} stale case(s) >90d unvalidated")
        if h["saturated"]:
            warnings.append(
                f"{pid}: all-pass streak {h['all_pass_streak']} — set is saturating; "
                f"rotate cases to smoke or add harder ones"
            )
        if h["candidate_backlog"]:
            warnings.append(
                f"{pid}: {h['candidate_backlog']} unpromoted candidate(s), oldest "
                f"{h['candidate_oldest_days']}d — curate the flywheel"
            )

    # 5. inventory / coverage ratchet
    for entry in inventory.get("prompts", []):
        status = entry.get("status")
        if status == "governed":
            spec = spec_by_id.get(entry.get("id") or "")
            if spec is None:
                failures.append(
                    f"inventory: {entry.get('file')} marked governed but spec "
                    f"'{entry.get('id')}' does not exist"
                )
            elif spec.spec.get("source", {}).get("file") != entry.get("file"):
                failures.append(
                    f"inventory: {entry.get('file')} marked governed but spec "
                    f"'{entry.get('id')}' sources {spec.spec.get('source', {}).get('file')} "
                    f"— pointer drift"
                )
        elif status == "not-a-prompt":
            if not entry.get("note"):
                warnings.append(
                    f"inventory: {entry.get('file')} is 'not-a-prompt' without a "
                    f"reason note"
                )
        elif inventory.get("enforce"):
            failures.append(
                f"inventory: ungoverned prompt {entry.get('file')!r} in enforced "
                f"repo — run the create-eval-loop skill on it"
            )
        else:
            warnings.append(f"inventory: ungoverned prompt {entry.get('file')!r}")

    return (not failures), failures, warnings


def _string_leaves(obj):
    if isinstance(obj, str):
        yield obj
    elif isinstance(obj, dict):
        for v in obj.values():
            yield from _string_leaves(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _string_leaves(v)
