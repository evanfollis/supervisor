"""Runner: executors, eval runs, caching, baseline comparison, the gate.

Executor config (spec.json "executor") — how to get an output from the
prompt under test for one case. All LLM paths are subscription CLIs
(ADR-0036):

  {"type": "claude_cli",
   "user_template": "Beat: {beat}\\n\\nItem:\\n  title: {title}\\n..."}
      Renders user_template with the case input dict (str.format), runs
      `claude -p --model <spec.model> --append-system-prompt <prompt>`.

  {"type": "codex_cli", "user_template": "..."}
      Cross-family execution: system + user concatenated through
      `codex exec --skip-git-repo-check --sandbox read-only`.

  {"type": "command", "argv": ["python3", "path/to/adapter.py"]}
      Project-owned adapter: receives {"prompt_text", "model", "params",
      "input"} as JSON on stdin, prints the raw model output on stdout.
      This is how a project points evals at its real runtime path.

Gate semantics (ADR-0039 §4): a run PASSES iff
  1. every runnable must-pass case passes in ALL trials (pass^k), and
  2. no case that passed at baseline fails now (paired regression), and
  3. aggregate pass rate >= baseline aggregate - gate.aggregate_floor_delta, and
  4. judge "unknown" verdicts / judge checks <= gate.max_unknown_ratio.
A THROTTLED run (provider rate limit) is not-run, never failed.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from .core import (
    RUNTIME_ROOT,
    cache_key,
    read_json,
    run_id as make_run_id,
    utcnow_iso,
    write_json,
)
from .goldens import runnable_cases
from .grading import (
    DETERMINISTIC_KINDS,
    GradingError,
    run_deterministic_check,
    run_judge_check,
)
from .llm import AllProvidersThrottled, CliCall, LLMCallError, is_throttle, run_with_fallback
from .registry import PromptSpec


class Throttled(Exception):
    """Provider rate limit — run is blocked, not failed (S1-P2 addendum)."""


class RunError(Exception):
    pass


DEFAULT_GATE = {"aggregate_floor_delta": 0.02, "trials": 1, "max_unknown_ratio": 0.2}


# --------------------------------------------------------------------------
# Executors
# --------------------------------------------------------------------------


def _render_user(template: str, case_input) -> str:
    if not template:
        return json.dumps(case_input, ensure_ascii=False)
    if isinstance(case_input, dict):
        class _Default(dict):
            def __missing__(self, key):
                return ""
        return template.format_map(_Default(case_input))
    return template.format(input=case_input)


def _run_cli(cmd: list[str], stdin_text: str | None, timeout: int,
             retries: int = 1, cwd: Path | None = None) -> str:
    """Run an executor command. Nonzero exits get `retries` re-attempts:
    subscription CLIs intermittently exit 1 with no diagnostic (observed
    2026-07-12), and a single bounded retry separates transient harness
    noise from real failures without masking the latter. Error messages
    include stdout as well — the CLIs sometimes put the error there.
    """
    import time

    last_err = ""
    for attempt in range(retries + 1):
        try:
            proc = subprocess.run(
                cmd, input=stdin_text, capture_output=True, text=True,
                timeout=timeout, check=False, cwd=str(cwd) if cwd else None,
            )
        except FileNotFoundError as exc:
            raise RunError(f"executor binary not found: {cmd[0]}") from exc
        except subprocess.TimeoutExpired as exc:
            raise RunError(f"executor timed out after {timeout}s") from exc
        if proc.returncode == 0:
            return proc.stdout
        diag = ((proc.stderr or "").strip() or (proc.stdout or "").strip())[-400:]
        if is_throttle(diag):
            raise Throttled(diag)
        last_err = f"executor exited {proc.returncode}: {diag or '<no output>'}"
        if attempt < retries:
            time.sleep(5)
    raise RunError(last_err)


def _codex_cmd(model: str) -> list[str]:
    cmd = [
        "codex",
        "-c",
        'approval_policy="untrusted"',
        "exec",
        "--skip-git-repo-check",
        "--sandbox",
        "read-only",
    ]
    if model:
        cmd += ["--model", model]
    return cmd + ["-"]


def _claude_text_cmd(model: str, *args: str) -> list[str]:
    return [
        "claude",
        "-p",
        "--tools",
        "",
        "--disable-slash-commands",
        "--model",
        model,
        *args,
    ]


def execute_case(spec: PromptSpec, prompt_text: str, case_input, timeout: int = 300,
                 project: str = "", case_id: str = "", trial: int | None = None) -> str:
    ex = spec.spec["executor"]
    etype = ex.get("type")
    model = spec.spec.get("model", "sonnet")

    if etype == "claude_cli":
        user = _render_user(ex.get("user_template", ""), case_input)
        codex_model = ex.get("codex_fallback_model", "")
        codex_input = f"{prompt_text}\n\n---\n\n{user}"
        try:
            return run_with_fallback([
                CliCall("claude", model,
                        _claude_text_cmd(model, "--append-system-prompt", prompt_text, user),
                        input_text=prompt_text + "\n" + user),
                CliCall("codex", codex_model, _codex_cmd(codex_model),
                        stdin_text=codex_input, input_text=codex_input,
                        fallback_from="claude"),
            ], timeout=timeout, role="executor", project=project,
                prompt_id=spec.prompt_id, case_id=case_id, trial=trial)
        except AllProvidersThrottled as exc:
            raise Throttled(str(exc)) from exc
        except LLMCallError as exc:
            raise RunError(str(exc)) from exc
    if etype == "codex_cli":
        user = _render_user(ex.get("user_template", ""), case_input)
        full = f"{prompt_text}\n\n---\n\n{user}"
        claude_model = ex.get("claude_fallback_model", "sonnet")
        try:
            return run_with_fallback([
                CliCall("codex", model, _codex_cmd(model),
                        stdin_text=full, input_text=full),
                CliCall("claude", claude_model,
                        _claude_text_cmd(claude_model, "--append-system-prompt", prompt_text, user),
                        input_text=prompt_text + "\n" + user,
                        fallback_from="codex"),
            ], timeout=timeout, role="executor", project=project,
                prompt_id=spec.prompt_id, case_id=case_id, trial=trial)
        except AllProvidersThrottled as exc:
            raise Throttled(str(exc)) from exc
        except LLMCallError as exc:
            raise RunError(str(exc)) from exc
    if etype == "command":
        argv = ex.get("argv")
        if not argv:
            raise RunError("command executor needs 'argv'")
        command_timeout = int(ex.get("timeout", timeout))
        payload = json.dumps(
            {
                "prompt_text": prompt_text,
                "model": model,
                "params": spec.spec.get("params", {}),
                "input": case_input,
                "telemetry": {
                    "project": project,
                    "prompt_id": spec.prompt_id,
                    "case_id": case_id,
                    "trial": trial,
                },
            },
            ensure_ascii=False,
        )
        return _run_cli(argv, payload, command_timeout, cwd=spec.repo)
    raise RunError(f"unknown executor type: {etype}")


# --------------------------------------------------------------------------
# Caching — (version, case, trial) keyed; re-runs after unrelated edits are free
# --------------------------------------------------------------------------


def _cache_dir(project: str, prompt_id: str) -> Path:
    return RUNTIME_ROOT / project / prompt_id / "cache"


def cached_execute(spec: PromptSpec, storage_key: str, telemetry_project: str,
                   prompt_text: str, version: str, case: dict, trial: int,
                   no_cache: bool = False) -> str:
    # spec_hash in the key: executor/adapter/source-pointer changes must
    # invalidate cached outputs (review finding 4 — a cache hit produced by
    # different wiring is not evidence about the current wiring)
    key = cache_key({"v": version, "s": spec.spec_hash(), "c": case["id"], "t": trial})
    path = _cache_dir(storage_key, spec.prompt_id) / f"{key}.json"
    if not no_cache:
        hit = read_json(path)
        if hit is not None:
            return hit["output"]
    output = execute_case(spec, prompt_text, case["input"], project=telemetry_project,
                          case_id=case["id"], trial=trial)
    write_json(path, {"version": version, "case": case["id"], "trial": trial,
                      "ts": utcnow_iso(), "output": output})
    return output


# --------------------------------------------------------------------------
# Run + gate
# --------------------------------------------------------------------------


def grade_output(spec: PromptSpec, case: dict, output: str, judge_trials: int,
                 project: str = "", trial: int | None = None) -> dict:
    """Grade one output against a case's checks. Deterministic checks run
    first; if any required deterministic check fails, judge checks are
    skipped (no reason to spend judge calls on structurally broken output).
    """
    judge_model = (spec.spec.get("judge") or {}).get("model", "opus")
    results, det_failed = [], False
    for check in case["checks"]:
        kind = check.get("kind")
        required = check.get("required", True)
        if kind in DETERMINISTIC_KINDS:
            try:
                passed, detail = run_deterministic_check(check, output)
            except GradingError as exc:
                passed, detail = False, f"check error: {exc}"
            results.append({"kind": kind, "required": required,
                            "verdict": "pass" if passed else "fail", "detail": detail})
            if required and not passed:
                det_failed = True
        elif kind == "judge":
            if det_failed:
                results.append({"kind": "judge", "required": required,
                                "failure_mode": check.get("failure_mode"),
                                "verdict": "skipped",
                                "detail": "skipped: required deterministic check failed"})
                continue
            try:
                verdict, detail = run_judge_check(
                    check, case["input"], output,
                    model=judge_model, trials=judge_trials,
                    telemetry_context={
                        "project": project,
                        "prompt_id": spec.prompt_id,
                        "case_id": case["id"],
                        "trial": trial,
                    },
                )
            except GradingError as exc:
                if str(exc).startswith("THROTTLED"):
                    raise Throttled(str(exc)) from exc
                verdict, detail = "unknown", f"judge error: {exc}"
            results.append({"kind": "judge", "required": required,
                            "failure_mode": check.get("failure_mode"),
                            "verdict": verdict, "detail": detail})
        else:
            results.append({"kind": kind, "required": required, "verdict": "fail",
                            "detail": f"unknown check kind '{kind}'"})
    required_ok = all(
        r["verdict"] == "pass" for r in results if r["required"] and r["verdict"] != "skipped"
    ) and not det_failed
    return {"checks": results, "pass": required_ok}


def run_eval(spec: PromptSpec, project: str, release: bool = False,
             no_cache: bool = False, log=print, storage_key: str | None = None) -> dict:
    """Execute + grade the golden set for the prompt's CURRENT live version.

    storage_key: runtime-dir key (core.project_key) — collision-proof
    across same-named repos; `project` stays the human-readable name used
    in reports and telemetry.
    """
    storage_key = storage_key or project
    prompt_text = spec.extract()
    version = spec.version()
    gate_cfg = {**DEFAULT_GATE, **(spec.spec.get("gate") or {})}
    trials = max(1, int(gate_cfg.get("trials", 1)))
    judge_trials = max(1, int((spec.spec.get("judge") or {}).get("trials", 1)))
    cases = runnable_cases(spec.dir, release=release)
    if not cases:
        raise RunError(f"{spec.prompt_id}: no runnable cases — golden set is empty")

    case_results, judge_total, judge_unknown = {}, 0, 0
    for i, case in enumerate(cases, 1):
        log(f"  [{i}/{len(cases)}] {case['id']} ({case.get('provenance')},{case.get('status')})")
        trial_passes, trial_details = [], []
        for t in range(trials):
            output = cached_execute(spec, storage_key, project, prompt_text, version,
                                    case, t, no_cache=no_cache)
            graded = grade_output(spec, case, output, judge_trials=judge_trials,
                                  project=project, trial=t)
            trial_passes.append(graded["pass"])
            trial_details.append(graded["checks"])
            for chk in graded["checks"]:
                if chk["kind"] == "judge" and chk["verdict"] != "skipped":
                    judge_total += 1
                    if chk["verdict"] == "unknown":
                        judge_unknown += 1
        case_results[case["id"]] = {
            "pass": all(trial_passes),            # pass^k
            "pass_any": any(trial_passes),        # pass@k (reported, not gated)
            "trials": trials,
            "trial_results": [
                {"trial": index, "pass": passed, "checks": checks}
                for index, (passed, checks) in enumerate(zip(trial_passes, trial_details))
            ],
            "must_pass": case.get("must_pass", True),
            "status": case.get("status"),
            "provenance": case.get("provenance"),
            # Retained for compatibility with existing report consumers.
            "checks": trial_details[-1],
        }

    gated = [r for cid, r in case_results.items() if r["status"] in ("active", "holdout")]
    aggregate = round(sum(1 for r in gated if r["pass"]) / max(1, len(gated)), 4)
    unknown_ratio = round(judge_unknown / judge_total, 4) if judge_total else 0.0

    from .goldens import golden_hash

    report = {
        "run_id": make_run_id(),
        "ts": utcnow_iso(),
        "prompt_id": spec.prompt_id,
        "project": project,
        "prompt_version": version,
        "spec_hash": spec.spec_hash(),
        "golden_hash": golden_hash(spec.dir, gate_cfg),
        "model": spec.spec.get("model"),
        "params": spec.spec.get("params", {}),
        "judge_model": (spec.spec.get("judge") or {}).get("model"),
        "release": release,
        "trials": trials,
        "cached_allowed": not no_cache,
        "cases": case_results,
        "aggregate": aggregate,
        "judge_unknown_ratio": unknown_ratio,
    }
    report["gate"] = evaluate_gate(report, read_json(spec.baseline_path), gate_cfg)
    out_path = RUNTIME_ROOT / storage_key / spec.prompt_id / "runs" / f"{report['run_id']}.json"
    write_json(out_path, report)
    report["report_path"] = str(out_path)
    return report


def evaluate_gate(report: dict, baseline: dict | None, gate_cfg: dict) -> dict:
    reasons = []
    must_fail = [cid for cid, r in report["cases"].items()
                 if r["must_pass"] and r["status"] in ("active", "holdout") and not r["pass"]]
    if must_fail:
        reasons.append(f"must-pass cases failed: {', '.join(must_fail[:5])}"
                       + (f" (+{len(must_fail)-5} more)" if len(must_fail) > 5 else ""))
    if baseline and baseline.get("passed"):
        # paired regression applies only to gating cases: an advisory
        # (must_pass=false) case is exploratory by contract and must not
        # gate through the back door (review finding 7)
        regressions = [
            cid for cid, r in report["cases"].items()
            if r["must_pass"] and not r["pass"]
            and (baseline.get("cases") or {}).get(cid, {}).get("pass") is True
        ]
        if regressions:
            reasons.append(f"paired regression vs baseline {baseline.get('prompt_version')}: "
                           + ", ".join(regressions[:5]))
        floor = (baseline.get("aggregate") or 0) - gate_cfg["aggregate_floor_delta"]
        if report["aggregate"] < floor:
            reasons.append(f"aggregate {report['aggregate']} < floor {round(floor, 4)}")
    if report["judge_unknown_ratio"] > gate_cfg["max_unknown_ratio"]:
        reasons.append(
            f"judge unknown ratio {report['judge_unknown_ratio']} > "
            f"{gate_cfg['max_unknown_ratio']} — rubric or cases need work"
        )
    return {"passed": not reasons, "reasons": reasons}


def update_baseline(spec: PromptSpec, report: dict, allow_cached: bool = False) -> dict:
    """Accept a passing run as the new baseline (the only write path).

    Baseline acceptance requires FRESH outputs by default (review finding
    4): a cached output proves nothing about current wiring beyond what the
    cache key captures. allow_cached exists for the explicit case where the
    only change since the cached run is provably inside the key (and the
    caller says so on the record — the flag is stored in the baseline).
    """
    if not report["gate"]["passed"]:
        raise RunError("refusing to update baseline from a failing run")
    if report.get("cached_allowed") and not allow_cached:
        raise RunError(
            "refusing to accept a baseline from a cache-enabled run — "
            "re-run with --no-cache (or pass --allow-cached-baseline explicitly)"
        )
    prior = read_json(spec.baseline_path) or {}
    all_pass = all(r["pass"] for r in report["cases"].values())
    same_set = set(report["cases"]) == set((prior.get("cases") or {}))
    streak = (prior.get("all_pass_streak", 0) + 1) if (all_pass and same_set) else (1 if all_pass else 0)
    baseline = {
        "prompt_version": report["prompt_version"],
        "spec_hash": report["spec_hash"],
        "golden_hash": report["golden_hash"],
        "model": report.get("model"),
        "params": report.get("params", {}),
        "judge_model": report.get("judge_model"),
        "run_id": report["run_id"],
        "ts": report["ts"],
        "release": report["release"],
        "passed": True,
        "accepted_from_cache": bool(report.get("cached_allowed")),
        "aggregate": report["aggregate"],
        "cases": {cid: {"pass": r["pass"], "must_pass": r["must_pass"]}
                  for cid, r in report["cases"].items()},
        "all_pass_streak": streak,
    }
    write_json(spec.baseline_path, baseline)
    return baseline
