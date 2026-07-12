"""prompteval CLI.

  prompteval scan [REPO]                       discover likely prompts
  prompteval register [REPO] --id ID --file F --type T [...]
  prompteval show [REPO] --id ID               extracted text + version
  prompteval check [REPO]                      deploy gate (no LLM calls, fail-closed)
  prompteval run [REPO] --id ID [--release] [--update-baseline] [--no-cache] [--yes]
  prompteval status [REPO] [--id ID]           health + escalation events
  prompteval score [REPO] --id ID              per-case scores for optimizers
  prompteval align [REPO] --id ID              judge TPR/TNR vs human labels
  prompteval capture [REPO] --id ID --from-jsonl GLOB --fields a,b,c [...]
  prompteval promote [REPO] --id ID --plan plan.json

Exit codes: 0 ok / gate passed; 1 failure; 3 throttled (blocked, not failed).
"""

from __future__ import annotations

import argparse
import glob as globmod
import json
import sys
from pathlib import Path

from .check import check_repo
from .core import (
    RUNTIME_ROOT,
    project_key,
    read_json,
    read_jsonl,
    utcnow_iso,
    write_json,
)
from .goldens import append_candidate, health, promote
from .grading import GradingError, run_judge_check
from .registry import RegistryError, list_specs, load_spec, registry_root, scan
from .runner import RunError, Throttled, run_eval, update_baseline
from .telemetry import emit


def _repo(args) -> Path:
    return Path(args.repo).resolve()


def _project(repo: Path) -> str:
    return repo.name


def cmd_scan(args) -> int:
    repo = _repo(args)
    findings = scan(repo)
    if not findings:
        print("no likely prompt artifacts found")
        return 0
    for f in findings:
        print(f"  {f['file']}  — {f['reason']}")
    print(f"\n{len(findings)} likely prompt artifact(s). Seed {registry_root(repo)}/inventory.json")
    return 0


def cmd_register(args) -> int:
    repo = _repo(args)
    source = {"type": args.type, "file": args.file}
    if args.type == "py_var":
        if not args.var:
            print("--var required for py_var", file=sys.stderr)
            return 1
        source["var"] = args.var
    elif args.type == "region":
        if not (args.begin and args.end):
            print("--begin/--end required for region", file=sys.stderr)
            return 1
        source.update(begin=args.begin, end=args.end)
    elif args.type == "regex":
        if not args.pattern:
            print("--pattern required for regex", file=sys.stderr)
            return 1
        source["pattern"] = args.pattern

    spec = {
        "id": args.id,
        "description": args.description or "",
        "owner": _project(repo),
        "source": source,
        "model": args.model,
        "params": {},
        "executor": {"type": args.executor, "user_template": args.user_template or ""},
        "judge": {"model": args.judge_model},
        "gate": {"aggregate_floor_delta": 0.02, "trials": args.trials,
                 "max_unknown_ratio": 0.2},
        "created": utcnow_iso(),
    }
    spec_dir = registry_root(repo) / args.id
    if (spec_dir / "spec.json").exists() and not args.force:
        print(f"{spec_dir}/spec.json exists (use --force to overwrite)", file=sys.stderr)
        return 1
    write_json(spec_dir / "spec.json", spec)
    (spec_dir / "golden").mkdir(parents=True, exist_ok=True)
    (spec_dir / "golden" / "cases.jsonl").touch()
    (spec_dir / "golden" / "holdout.jsonl").touch()
    # verify the pointer extracts before declaring success
    try:
        loaded = load_spec(repo, args.id)
        version = loaded.version()
    except RegistryError as exc:
        print(f"registered but extraction FAILS: {exc}", file=sys.stderr)
        return 1
    print(f"registered {args.id} at {spec_dir}\n  live version: {version}")
    print(f"  next: add golden cases to {spec_dir}/golden/cases.jsonl, then "
          f"`prompteval run [REPO] --id {args.id} --update-baseline`")
    return 0


def cmd_show(args) -> int:
    repo = _repo(args)
    spec = load_spec(repo, args.id)
    text = spec.extract()
    print(f"# {args.id}  version={spec.version()}  model={spec.spec.get('model')}")
    print(f"# source: {json.dumps(spec.spec['source'])}")
    print("-" * 72)
    print(text)
    return 0


def cmd_check(args) -> int:
    repo = _repo(args)
    ok, failures, warnings = check_repo(repo)
    for w in warnings:
        print(f"  warn: {w}")
    for f in failures:
        print(f"  FAIL: {f}")
    n = len(list_specs(repo)) if registry_root(repo).is_dir() else 0
    if ok:
        print(f"prompteval check PASS — {n} governed prompt(s), {len(warnings)} warning(s)")
        return 0
    print(f"prompteval check FAIL — {len(failures)} failure(s)")
    emit(_project(repo), "failure", f"gate check failed: {failures[0]}", ref=str(repo))
    return 1


def cmd_run(args) -> int:
    repo = _repo(args)
    project = _project(repo)
    spec = load_spec(repo, args.id)
    if args.release and not args.yes:
        print("--release runs the sealed holdout tier. Holdouts must never be used\n"
              "for iteration — only for accepting a final baseline. Re-run with --yes\n"
              "to confirm this is a release acceptance, not a tuning loop.",
              file=sys.stderr)
        return 1
    try:
        report = run_eval(spec, project, release=args.release, no_cache=args.no_cache,
                          storage_key=project_key(repo))
    except Throttled as exc:
        print(f"THROTTLED (blocked, not failed): {exc}", file=sys.stderr)
        emit(project, "throttled", f"{args.id}: eval run throttled", ref=args.id)
        return 3
    except (RunError, RegistryError) as exc:
        print(f"run error: {exc}", file=sys.stderr)
        emit(project, "failure", f"{args.id}: eval run error: {exc}", ref=args.id)
        return 1

    gate = report["gate"]
    print(f"\nrun {report['run_id']}  version={report['prompt_version']}  "
          f"aggregate={report['aggregate']}  unknown_ratio={report['judge_unknown_ratio']}")
    for cid, r in sorted(report["cases"].items()):
        flag = "PASS" if r["pass"] else ("pass@k" if r["pass_any"] else "FAIL")
        print(f"  {flag:6} {cid} ({r['provenance']},{r['status']})")
    if gate["passed"]:
        print("GATE: PASS")
        emit(project, "info", f"{args.id}: eval run passed ({report['aggregate']})",
             ref=report["report_path"])
        if args.update_baseline:
            try:
                baseline = update_baseline(spec, report,
                                           allow_cached=args.allow_cached_baseline)
            except RunError as exc:
                print(f"baseline NOT updated: {exc}", file=sys.stderr)
                return 1
            print(f"baseline updated -> {baseline['prompt_version']} "
                  f"(all_pass_streak={baseline['all_pass_streak']})")
        return 0
    print("GATE: FAIL")
    for reason in gate["reasons"]:
        print(f"  - {reason}")
    emit(project, "failure", f"{args.id}: eval gate failed: {gate['reasons'][0]}",
         ref=report["report_path"])
    return 1


def cmd_status(args) -> int:
    repo = _repo(args)
    project = _project(repo)
    specs = [load_spec(repo, args.id)] if args.id else list_specs(repo)
    if not specs:
        print("no governed prompts")
        return 0
    status_path = RUNTIME_ROOT / project_key(repo) / "status.json"
    prior = read_json(status_path) or {}
    out = {"ts": utcnow_iso(), "project": project, "prompts": {}}
    for spec in specs:
        h = health(spec.dir, read_json(spec.baseline_path))
        flags = []
        if h["stale_cases"]:
            flags.append("stale")
        if h["saturated"]:
            flags.append("saturated")
        if h["cases_active"] and h["production_ratio"] < 0.5:
            flags.append("synthetic-majority")
        if h["candidate_backlog"] >= 10 or h["candidate_oldest_days"] > 30:
            flags.append("candidate-backlog")
        streak = prior.get("prompts", {}).get(spec.prompt_id, {}).get("flag_streak", 0)
        streak = streak + 1 if flags else 0
        out["prompts"][spec.prompt_id] = {**h, "flags": flags, "flag_streak": streak}
        line = (f"{spec.prompt_id}: {h['cases_active']} active "
                f"(prod ratio {h['production_ratio']}, streak {h['all_pass_streak']})")
        if flags:
            line += f"  [{', '.join(flags)}] x{streak}"
        print(line)
        # S3-P2: persistent decay escalates instead of rotting quietly
        if streak >= 3:
            emit(project, "escalated",
                 f"{spec.prompt_id}: golden-set decay flags {flags} for {streak} "
                 f"consecutive status runs", ref=spec.prompt_id, source_type=args.source_type)
    write_json(status_path, out)
    return 0


def cmd_capture(args) -> int:
    repo = _repo(args)
    spec = load_spec(repo, args.id)
    fields = [f.strip() for f in args.fields.split(",")] if args.fields else None
    added = skipped = 0
    for path in sorted(globmod.glob(args.from_jsonl)):
        for row in read_jsonl(Path(path)):
            if args.limit and added >= args.limit:
                break
            input_obj = {k: row.get(k) for k in fields} if fields else row
            observed = row.get(args.output_field) if args.output_field else None
            entry = append_candidate(spec.dir, input_obj, source=f"capture:{path}",
                                     observed_output=observed)
            if entry:
                added += 1
            else:
                skipped += 1
    print(f"captured {added} candidate(s), {skipped} duplicate(s) skipped "
          f"-> {spec.candidates_path}")
    emit(_project(repo), "info", f"{args.id}: captured {added} production candidates",
         ref=str(spec.candidates_path))
    return 0


def cmd_score(args) -> int:
    """Machine-readable per-case scores from the latest run — the interface
    external optimizers (GEPA/DSPy-style) consume. Holdout results are
    stripped unless --include-holdout: optimizers must not see them."""
    repo = _repo(args)
    runs_dir = RUNTIME_ROOT / project_key(repo) / args.id / "runs"
    runs = sorted(runs_dir.glob("run-*.json")) if runs_dir.is_dir() else []
    if not runs:
        print(f"no runs recorded for {args.id}", file=sys.stderr)
        return 1
    report = read_json(runs[-1])
    cases = {
        cid: {"pass": r["pass"], "pass_any": r["pass_any"], "must_pass": r["must_pass"],
              "provenance": r["provenance"]}
        for cid, r in report["cases"].items()
        if args.include_holdout or r["status"] != "holdout"
    }
    print(json.dumps({
        "prompt_id": report["prompt_id"], "prompt_version": report["prompt_version"],
        "run_id": report["run_id"], "ts": report["ts"],
        "aggregate": report["aggregate"], "gate": report["gate"], "cases": cases,
    }, indent=2))
    return 0


def cmd_align(args) -> int:
    """Judge alignment against human labels (TPR/TNR).

    Reads <spec-dir>/judge/alignment.jsonl; each line:
      {"failure_mode": "...", "rubric": "...", "case_input": {...},
       "output": "...", "human_verdict": "pass"|"fail"}
    Convention: positive class = "fail" (the judge's job is catching
    failures). TPR = judged-fail when human says fail; TNR = judged-pass
    when human says pass. Unknown verdicts are reported separately and
    count against alignment.
    """
    repo = _repo(args)
    spec = load_spec(repo, args.id)
    entries = read_jsonl(spec.dir / "judge" / "alignment.jsonl")
    if not entries:
        print(f"no alignment labels at {spec.dir}/judge/alignment.jsonl\n"
              f"Add one each time a human disputes or confirms a judge verdict.",
              file=sys.stderr)
        return 1
    model = (spec.spec.get("judge") or {}).get("model", "opus")
    trials = max(1, int((spec.spec.get("judge") or {}).get("trials", 1)))
    tp = tn = fp = fn = unknown = 0
    for i, e in enumerate(entries, 1):
        check = {"kind": "judge", "failure_mode": e.get("failure_mode"),
                 "rubric": e.get("rubric", "")}
        try:
            verdict, detail = run_judge_check(check, e.get("case_input"),
                                              e.get("output", ""), model, trials)
        except GradingError as exc:
            print(f"  [{i}] judge error: {exc}", file=sys.stderr)
            unknown += 1
            continue
        human = e.get("human_verdict")
        if verdict == "unknown":
            unknown += 1
        elif human == "fail":
            tp += verdict == "fail"; fn += verdict == "pass"
        elif human == "pass":
            tn += verdict == "pass"; fp += verdict == "fail"
        agree = "AGREE" if verdict == human else "DISAGREE"
        print(f"  [{i}] human={human} judge={verdict} {agree}")
    n_fail, n_pass = tp + fn, tn + fp
    print(f"\nlabels: {len(entries)}  unknown: {unknown}")
    if n_fail:
        print(f"TPR (catches real failures): {tp}/{n_fail} = {tp/n_fail:.2f}")
    if n_pass:
        print(f"TNR (avoids false alarms):  {tn}/{n_pass} = {tn/n_pass:.2f}")
    if (n_fail and tp / n_fail < 0.8) or (n_pass and tn / n_pass < 0.8):
        print("judge alignment below 0.8 — revise the rubric before trusting this judge as a gate")
        return 1
    return 0


def cmd_promote(args) -> int:
    repo = _repo(args)
    spec = load_spec(repo, args.id)
    plan = read_json(Path(args.plan))
    if not isinstance(plan, dict) or not plan:
        print("--plan must be a JSON object {case_id: [checks...]}", file=sys.stderr)
        return 1
    promoted = promote(spec.dir, list(plan.keys()), plan)
    for case in promoted:
        print(f"promoted {case['id']} (production)")
    print("baseline is now stale relative to the golden set — re-run "
          f"`prompteval run [REPO] --id {args.id} --update-baseline`")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="prompteval", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)

    def repo_arg(sp):
        sp.add_argument("repo", nargs="?", default=".", help="repo root (default: cwd)")

    sp = sub.add_parser("scan");    repo_arg(sp)
    sp = sub.add_parser("register"); repo_arg(sp)
    sp.add_argument("--id", required=True)
    sp.add_argument("--file", required=True, help="source file, repo-relative")
    sp.add_argument("--type", required=True,
                    choices=["whole_file", "region", "py_var", "regex"])
    sp.add_argument("--var"); sp.add_argument("--begin"); sp.add_argument("--end")
    sp.add_argument("--pattern"); sp.add_argument("--description")
    sp.add_argument("--model", default="sonnet")
    sp.add_argument("--judge-model", default="opus")
    sp.add_argument("--executor", default="claude_cli",
                    choices=["claude_cli", "codex_cli", "command"])
    sp.add_argument("--user-template", default="")
    sp.add_argument("--trials", type=int, default=1)
    sp.add_argument("--force", action="store_true")

    sp = sub.add_parser("show"); repo_arg(sp); sp.add_argument("--id", required=True)
    sp = sub.add_parser("check"); repo_arg(sp)

    sp = sub.add_parser("run"); repo_arg(sp)
    sp.add_argument("--id", required=True)
    sp.add_argument("--release", action="store_true")
    sp.add_argument("--update-baseline", action="store_true")
    sp.add_argument("--no-cache", action="store_true")
    sp.add_argument("--allow-cached-baseline", action="store_true",
                    help="accept a baseline from a cache-enabled run (on the record)")
    sp.add_argument("--yes", action="store_true")

    sp = sub.add_parser("score"); repo_arg(sp)
    sp.add_argument("--id", required=True)
    sp.add_argument("--include-holdout", action="store_true")

    sp = sub.add_parser("align"); repo_arg(sp)
    sp.add_argument("--id", required=True)

    sp = sub.add_parser("status"); repo_arg(sp)
    sp.add_argument("--id")
    sp.add_argument("--source-type", default="system", choices=["system", "cron"])

    sp = sub.add_parser("capture"); repo_arg(sp)
    sp.add_argument("--id", required=True)
    sp.add_argument("--from-jsonl", required=True, help="glob of JSONL files")
    sp.add_argument("--fields", help="comma-separated input fields to keep")
    sp.add_argument("--output-field", help="field holding the observed output")
    sp.add_argument("--limit", type=int, default=25)

    sp = sub.add_parser("promote"); repo_arg(sp)
    sp.add_argument("--id", required=True)
    sp.add_argument("--plan", required=True,
                    help="JSON file: {case_id: [checks...], ...}")
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    handlers = {
        "scan": cmd_scan, "register": cmd_register, "show": cmd_show,
        "check": cmd_check, "run": cmd_run, "status": cmd_status,
        "capture": cmd_capture, "promote": cmd_promote,
        "score": cmd_score, "align": cmd_align,
    }
    try:
        return handlers[args.cmd](args)
    except (RegistryError, RunError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
