#!/usr/bin/env python3
"""Tests for the prompteval harness (ADR-0039).

Run: python3 supervisor/tests/test-prompteval.py
No LLM calls — judges and executors are faked; the point is the contract:
extraction, versioning, grading, gate semantics, lifecycle, the deploy-gate
check, and the hardening from the 2026-07-12 adversarial review (fail-closed
scan, golden/spec hashes, cache invalidation, holdout sealing, advisory
regression filter).
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts" / "lib"))

TMP = Path(tempfile.mkdtemp(prefix="prompteval-test-"))
os.environ["PROMPTEVAL_RUNTIME"] = str(TMP / "runtime")
os.environ["PROMPTEVAL_TELEMETRY"] = str(TMP / "events.jsonl")

from prompteval import check as pe_check  # noqa: E402
from prompteval import core, goldens, grading, llm, registry, runner  # noqa: E402


def make_repo() -> Path:
    repo = Path(tempfile.mkdtemp(prefix="pe-repo-", dir=TMP))
    (repo / "mod.py").write_text(
        'X = 1\nSYSTEM_PROMPT = (\n    "You are a scorer. "\n    "Return JSON."\n)\n',
        encoding="utf-8",
    )
    (repo / "whole-prompt.md").write_text("Do the thing.\n", encoding="utf-8")
    (repo / "region.md").write_text(
        "# doc\n<!-- pe:begin -->\nInner prompt text\n<!-- pe:end -->\n", encoding="utf-8"
    )
    return repo


def write_inventory(repo: Path, extra=None):
    """Baseline inventory covering make_repo's scan-detectable files."""
    prompts = [
        {"file": "mod.py", "id": "p1", "status": "governed"},
        {"file": "whole-prompt.md", "status": "not-a-prompt", "note": "test fixture"},
    ] + (extra or [])
    core.write_json(repo / ".prompteval" / "inventory.json",
                    {"enforce": False, "prompts": prompts})


def write_spec(repo: Path, pid="p1", executor=None, gate=None, judge=None):
    spec = {
        "id": pid,
        "description": "test",
        "owner": "test",
        "source": {"type": "py_var", "file": "mod.py", "var": "SYSTEM_PROMPT"},
        "model": "sonnet",
        "params": {},
        "executor": executor or {"type": "command", "argv": ["python3", str(repo / "adapter.py")]},
        "judge": judge or {"model": "opus"},
        "gate": gate or {"aggregate_floor_delta": 0.02, "trials": 1, "max_unknown_ratio": 0.5},
    }
    core.write_json(repo / ".prompteval" / pid / "spec.json", spec)
    (repo / ".prompteval" / pid / "golden").mkdir(parents=True, exist_ok=True)
    return registry.load_spec(repo, pid)


def echo_adapter(repo: Path, reply: str, count_file: Path | None = None):
    """Fake runtime path: prints a canned reply; optionally counts invocations."""
    counting = ""
    if count_file is not None:
        counting = (
            f"from pathlib import Path\n"
            f"p = Path({str(count_file)!r})\n"
            f"p.write_text(str(int(p.read_text() or '0') + 1) if p.exists() else '1')\n"
        )
    (repo / "adapter.py").write_text(
        "import sys, json\n"
        "payload = json.load(sys.stdin)\n"
        + counting +
        f"print({reply!r})\n",
        encoding="utf-8",
    )


def add_case(spec, input_obj, checks, **kw):
    status = kw.get("status", "active")
    case = goldens.new_case(input_obj, checks, kw.pop("provenance", "synthetic"), **kw)
    target = spec.holdout_path if status == "holdout" else spec.cases_path
    core.append_jsonl(target, case)
    return case


def run_fresh(spec, project="test"):
    return runner.run_eval(spec, project, no_cache=True, log=lambda *_: None)


class TestCore(unittest.TestCase):
    def test_hash_contract_stable_and_typed(self):
        v1 = core.artifact_hash("text", "sonnet", {})
        v2 = core.artifact_hash("text", "sonnet", {})
        v3 = core.artifact_hash("text ", "sonnet", {})
        self.assertEqual(v1, v2)
        self.assertNotEqual(v1, v3)
        self.assertTrue(v1.startswith("pv-") and len(v1) == 3 + core.HASH_LEN)
        self.assertNotEqual(core.artifact_hash("t", "sonnet", {}), core.artifact_hash("t", "opus", {}))

    def test_case_id_from_input(self):
        self.assertEqual(core.case_id({"a": 1}), core.case_id({"a": 1}))
        self.assertNotEqual(core.case_id({"a": 1}), core.case_id({"a": 2}))

    def test_run_ids_unique_and_project_keys_disambiguate(self):
        self.assertNotEqual(core.run_id(), core.run_id())
        a = Path(tempfile.mkdtemp(prefix="same-", dir=TMP)) / "repo"
        b = Path(tempfile.mkdtemp(prefix="same-", dir=TMP)) / "repo"
        a.mkdir(); b.mkdir()
        self.assertNotEqual(core.project_key(a), core.project_key(b))


class TestExtraction(unittest.TestCase):
    def setUp(self):
        self.repo = make_repo()

    def test_py_var_folds_adjacent_literals(self):
        text = registry.extract_prompt(self.repo, {"type": "py_var", "file": "mod.py", "var": "SYSTEM_PROMPT"})
        self.assertEqual(text, "You are a scorer. Return JSON.")

    def test_whole_file_and_region(self):
        self.assertEqual(
            registry.extract_prompt(self.repo, {"type": "whole_file", "file": "whole-prompt.md"}),
            "Do the thing.\n",
        )
        self.assertEqual(
            registry.extract_prompt(
                self.repo,
                {"type": "region", "file": "region.md", "begin": "<!-- pe:begin -->", "end": "<!-- pe:end -->"},
            ),
            "Inner prompt text",
        )

    def test_missing_var_raises(self):
        with self.assertRaises(registry.RegistryError):
            registry.extract_prompt(self.repo, {"type": "py_var", "file": "mod.py", "var": "NOPE"})

    def test_spec_hash_covers_adapter_content(self):
        echo_adapter(self.repo, "a")
        spec = write_spec(self.repo)
        h1 = spec.spec_hash()
        echo_adapter(self.repo, "b")  # adapter edit must change the hash
        self.assertNotEqual(h1, spec.spec_hash())

    def test_spec_hash_covers_declared_executor_deps(self):
        echo_adapter(self.repo, "a")
        dep = self.repo / "helper.py"
        dep.write_text("VALUE = 'one'\n", encoding="utf-8")
        spec = write_spec(self.repo, executor={
            "type": "command",
            "argv": ["python3", "adapter.py"],
            "deps": ["helper.py"],
        })
        h1 = spec.spec_hash()
        dep.write_text("VALUE = 'two'\n", encoding="utf-8")
        self.assertNotEqual(h1, spec.spec_hash())

    def test_real_synaplex_scorer_extracts(self):
        synaplex = Path("/opt/workspace/projects/synaplex")
        if not (synaplex / "intake" / "score.py").exists():
            self.skipTest("synaplex not present")
        text = registry.extract_prompt(
            synaplex, {"type": "py_var", "file": "intake/score.py", "var": "SONNET_SYSTEM_PROMPT"}
        )
        self.assertIn("beat editor", text)


class TestGrading(unittest.TestCase):
    def test_deterministic_checks(self):
        out = '{"score": 72, "rationale": "solid primary source"}'
        self.assertTrue(grading.run_deterministic_check({"kind": "json_valid"}, out)[0])
        self.assertTrue(grading.run_deterministic_check(
            {"kind": "json_schema", "required": ["score", "rationale"], "types": {"score": "number"}}, out)[0])
        self.assertTrue(grading.run_deterministic_check(
            {"kind": "numeric_band", "path": "score", "min": 60, "max": 100}, out)[0])
        self.assertFalse(grading.run_deterministic_check(
            {"kind": "numeric_band", "path": "score", "min": 80}, out)[0])
        self.assertTrue(grading.run_deterministic_check(
            {"kind": "contains", "value": "PRIMARY source"}, out)[0])
        self.assertTrue(grading.run_deterministic_check(
            {"kind": "not_contains", "value": "hype"}, out)[0])

    def test_json_schema_rejects_bool_as_number(self):
        ok, _ = grading.run_deterministic_check(
            {"kind": "json_schema", "required": ["score"], "types": {"score": "number"}},
            '{"score": true}',
        )
        self.assertFalse(ok)

    def test_verdict_parsing(self):
        self.assertEqual(
            grading.parse_verdict('reasoning...\n{"verdict": "pass", "reason": "ok"}'),
            ("pass", "ok"),
        )
        self.assertEqual(grading.parse_verdict("no json here")[0], "unknown")
        v, _ = grading.parse_verdict(
            'example: {"verdict": "fail", "reason": "x"}\nfinal: {"verdict": "pass", "reason": "y"}'
        )
        self.assertEqual(v, "pass")

    def test_judge_majority_and_ties(self):
        replies = iter(
            ['{"verdict": "pass", "reason": "a"}', '{"verdict": "fail", "reason": "b"}',
             '{"verdict": "pass", "reason": "c"}']
        )
        v, _ = grading.run_judge_check(
            {"failure_mode": "x", "rubric": "r"}, {}, "out", "opus", trials=3,
            caller=lambda p, m: next(replies),
        )
        self.assertEqual(v, "pass")
        replies = iter(['{"verdict": "pass"}', '{"verdict": "fail"}'])
        v, _ = grading.run_judge_check(
            {"failure_mode": "x", "rubric": "r"}, {}, "out", "opus", trials=2,
            caller=lambda p, m: next(replies),
        )
        self.assertEqual(v, "unknown")

    def test_judge_trials_wired_from_spec(self):
        repo = make_repo()
        echo_adapter(repo, "free text")
        spec = write_spec(repo, judge={"model": "opus", "trials": 3})
        add_case(spec, {"t": "jt"}, [{"kind": "judge", "failure_mode": "fm", "rubric": "r"}])
        calls = []
        original = grading.call_judge_cli
        grading.call_judge_cli = lambda p, m, timeout=240: (
            calls.append(1), '{"verdict": "pass", "reason": "ok"}')[1]
        try:
            run_fresh(spec)
        finally:
            grading.call_judge_cli = original
        self.assertEqual(len(calls), 3)  # spec.judge.trials, not hardcoded 1


class TestRunnerAndGate(unittest.TestCase):
    def setUp(self):
        self.repo = make_repo()
        write_inventory(self.repo)

    def test_pass_run_updates_baseline_then_edit_trips_check(self):
        echo_adapter(self.repo, '{"score": 72, "rationale": "primary source"}')
        spec = write_spec(self.repo)
        add_case(spec, {"title": "MCP spec update"}, [
            {"kind": "json_valid"},
            {"kind": "numeric_band", "path": "score", "min": 50, "max": 100},
        ])
        report = run_fresh(spec)
        self.assertTrue(report["gate"]["passed"])
        runner.update_baseline(spec, report)

        ok, failures, _ = pe_check.check_repo(self.repo)
        self.assertTrue(ok, failures)

        mod = self.repo / "mod.py"
        mod.write_text(mod.read_text().replace("You are a scorer.", "You are a harsh scorer."))
        ok, failures, _ = pe_check.check_repo(self.repo)
        self.assertFalse(ok)
        self.assertTrue(any("edited without eval" in f for f in failures))

    def test_golden_set_weakening_trips_check(self):
        echo_adapter(self.repo, '{"score": 72}')
        spec = write_spec(self.repo)
        case = add_case(spec, {"title": "weakenable"}, [
            {"kind": "numeric_band", "path": "score", "min": 50},
        ])
        runner.update_baseline(spec, run_fresh(spec))
        ok, failures, _ = pe_check.check_repo(self.repo)
        self.assertTrue(ok, failures)
        # weaken the check without re-running -> golden hash mismatch
        with open(spec.cases_path, encoding="utf-8") as fh:
            rows = [json.loads(l) for l in fh]
        rows[0]["checks"] = [{"kind": "json_valid"}]
        spec.cases_path.write_text("".join(json.dumps(r) + "\n" for r in rows))
        ok, failures, _ = pe_check.check_repo(self.repo)
        self.assertFalse(ok)
        self.assertTrue(any("golden set changed" in f for f in failures))
        # same for quietly flipping must_pass
        rows[0]["checks"] = [{"kind": "numeric_band", "path": "score", "min": 50}]
        rows[0]["must_pass"] = False
        spec.cases_path.write_text("".join(json.dumps(r) + "\n" for r in rows))
        ok, failures, _ = pe_check.check_repo(self.repo)
        self.assertFalse(ok)
        self.assertTrue(any("golden set changed" in f for f in failures))

    def test_spec_drift_trips_check(self):
        echo_adapter(self.repo, '{"score": 72}')
        spec = write_spec(self.repo)
        add_case(spec, {"title": "specdrift"}, [{"kind": "json_valid"}])
        runner.update_baseline(spec, run_fresh(spec))
        echo_adapter(self.repo, '{"score": 5}')  # adapter edit = spec drift
        ok, failures, _ = pe_check.check_repo(self.repo)
        self.assertFalse(ok)
        self.assertTrue(any("drifted since baseline" in f for f in failures))

    def test_baseline_records_and_checks_model_identity(self):
        echo_adapter(self.repo, '{"score": 72}')
        spec = write_spec(self.repo)
        add_case(spec, {"title": "identity"}, [{"kind": "json_valid"}])
        baseline = runner.update_baseline(spec, run_fresh(spec))
        self.assertEqual(baseline["model"], "sonnet")
        self.assertEqual(baseline["params"], {})
        self.assertEqual(baseline["judge_model"], "opus")

        baseline["model"] = "different-model"
        core.write_json(spec.baseline_path, baseline)
        ok, failures, _ = pe_check.check_repo(self.repo)
        self.assertFalse(ok)
        self.assertTrue(any("accepted model" in f for f in failures))

    def test_paired_regression_blocks_but_not_for_advisory(self):
        echo_adapter(self.repo, '{"score": 72, "rationale": "x"}')
        spec = write_spec(self.repo)
        gating = add_case(spec, {"title": "gating"}, [{"kind": "numeric_band", "path": "score", "min": 50}])
        add_case(spec, {"title": "advisory"}, [{"kind": "numeric_band", "path": "score", "min": 50}],
                 must_pass=False)
        runner.update_baseline(spec, run_fresh(spec))
        echo_adapter(self.repo, '{"score": 10, "rationale": "x"}')
        # advisory + gating both fail now; only the gating case may block.
        report2 = runner.run_eval(spec, "test", no_cache=True, log=lambda *_: None)
        self.assertFalse(report2["gate"]["passed"])
        joined = " ".join(report2["gate"]["reasons"])
        self.assertIn(gating["id"], joined)
        self.assertNotIn("advisory", joined)
        regression_reasons = [r for r in report2["gate"]["reasons"] if "regression" in r]
        for reason in regression_reasons:
            self.assertNotIn(
                [c for c in report2["cases"] if report2["cases"][c]["must_pass"] is False][0],
                reason,
            )

    def test_unknown_ratio_fails_run(self):
        echo_adapter(self.repo, "free text output")
        spec = write_spec(self.repo, gate={"aggregate_floor_delta": 0.02, "trials": 1,
                                           "max_unknown_ratio": 0.2})
        add_case(spec, {"title": "unk"}, [{"kind": "judge", "failure_mode": "fm", "rubric": "r"}],
                 must_pass=False)
        original = grading.call_judge_cli
        grading.call_judge_cli = lambda p, m, timeout=240: "no verdict json at all"
        try:
            report = run_fresh(spec)
        finally:
            grading.call_judge_cli = original
        self.assertFalse(report["gate"]["passed"])
        self.assertTrue(any("unknown ratio" in r for r in report["gate"]["reasons"]))

    def test_holdout_excluded_unless_release(self):
        echo_adapter(self.repo, '{"score": 72}')
        spec = write_spec(self.repo)
        add_case(spec, {"title": "hx"}, [{"kind": "json_valid"}])
        add_case(spec, {"title": "sealed"}, [{"kind": "json_valid"}], status="holdout")
        report = run_fresh(spec)
        self.assertEqual(len(report["cases"]), 1)
        report_rel = runner.run_eval(spec, "test", release=True, no_cache=True,
                                     log=lambda *_: None)
        self.assertEqual(len(report_rel["cases"]), 2)

    def test_refuses_baseline_from_failing_or_cached_run(self):
        echo_adapter(self.repo, "not json")
        spec = write_spec(self.repo)
        add_case(spec, {"title": "refuse"}, [{"kind": "json_valid"}])
        report = run_fresh(spec)
        self.assertFalse(report["gate"]["passed"])
        with self.assertRaises(runner.RunError):
            runner.update_baseline(spec, report)
        # cached run refuses baseline unless explicitly allowed
        echo_adapter(self.repo, '{"ok": 1}')
        spec2 = write_spec(self.repo, pid="p2")
        core.write_json(self.repo / ".prompteval" / "p2" / "spec.json",
                        {**json.loads((self.repo / ".prompteval" / "p2" / "spec.json").read_text()),
                         "source": {"type": "whole_file", "file": "whole-prompt.md"}})
        spec2 = registry.load_spec(self.repo, "p2")
        add_case(spec2, {"title": "cached"}, [{"kind": "json_valid"}])
        cached_report = runner.run_eval(spec2, "test", log=lambda *_: None)  # cache-enabled
        self.assertTrue(cached_report["gate"]["passed"])
        with self.assertRaises(runner.RunError):
            runner.update_baseline(spec2, cached_report)
        runner.update_baseline(spec2, cached_report, allow_cached=True)  # explicit override

    def test_cache_hit_when_unchanged_miss_when_adapter_changes(self):
        counter = self.repo / "count.txt"
        echo_adapter(self.repo, '{"score": 72}', count_file=counter)
        spec = write_spec(self.repo)
        add_case(spec, {"title": "cachesem"}, [{"kind": "json_valid"}])
        runner.run_eval(spec, "test", log=lambda *_: None)
        self.assertEqual(counter.read_text(), "1")
        runner.run_eval(spec, "test", log=lambda *_: None)  # unchanged -> cache hit
        self.assertEqual(counter.read_text(), "1")
        echo_adapter(self.repo, '{"score": 72, "v": 2}', count_file=counter)
        runner.run_eval(spec, "test", log=lambda *_: None)  # adapter changed -> miss
        self.assertEqual(counter.read_text(), "2")

    def test_subscription_session_limit_is_throttled(self):
        with self.assertRaises(runner.Throttled):
            runner._run_cli(
                [
                    "python3", "-c",
                    "import sys; sys.stderr.write(\"You've hit your session limit\"); sys.exit(1)",
                ],
                None,
                5,
                retries=0,
            )

    def test_provider_fallback_and_call_telemetry(self):
        out = llm.run_with_fallback(
            [
                llm.CliCall(
                    "claude", "sonnet",
                    [
                        "python3", "-c",
                        "import sys; sys.stderr.write(\"You've hit your session limit\"); sys.exit(1)",
                    ],
                    input_text="primary prompt",
                ),
                llm.CliCall(
                    "codex", "default",
                    ["python3", "-c", "print('fallback ok')"],
                    input_text="fallback prompt",
                    fallback_from="claude",
                ),
            ],
            timeout=5,
            retries=0,
            role="executor",
            project="test",
            prompt_id="p1",
            case_id="c1",
            trial=0,
        )
        self.assertEqual(out.strip(), "fallback ok")
        events = core.read_jsonl(Path(os.environ["PROMPTEVAL_TELEMETRY"]))
        calls = [e for e in events if e.get("eventType") == "llm_call"
                 and e.get("promptId") == "p1" and e.get("caseId") == "c1"]
        self.assertEqual([c["provider"] for c in calls[-2:]], ["claude", "codex"])
        self.assertEqual(calls[-2]["status"], "throttled")
        self.assertEqual(calls[-1]["status"], "success")
        self.assertGreater(calls[-1]["latencyMs"], -1)
        self.assertEqual(calls[-1]["tokenSource"], "estimated_chars_div_4")

    def test_all_providers_blocked_is_one_throttle(self):
        with self.assertRaises(llm.AllProvidersThrottled):
            llm.run_with_fallback(
                [
                    llm.CliCall(
                        "claude", "sonnet",
                        ["python3", "-c",
                         "import sys; sys.stderr.write(\"usage limit\"); sys.exit(1)"],
                    ),
                    llm.CliCall(
                        "codex", "default",
                        ["python3", "-c",
                         "import sys; sys.stderr.write(\"rate limit\"); sys.exit(1)"],
                        fallback_from="claude",
                    ),
                ],
                timeout=5,
                retries=0,
            )


class TestCheckDiscipline(unittest.TestCase):
    def test_fail_closed_scan_blocks_registryless_prompt_repo(self):
        repo = make_repo()  # has likely prompts, no .prompteval/
        ok, failures, _ = pe_check.check_repo(repo)
        self.assertFalse(ok)
        self.assertTrue(any("no .prompteval/ registry" in f for f in failures))

    def test_promptless_repo_passes(self):
        repo = Path(tempfile.mkdtemp(prefix="pe-clean-", dir=TMP))
        (repo / "README.md").write_text("nothing promptlike here\n")
        ok, failures, _ = pe_check.check_repo(repo)
        self.assertTrue(ok, failures)

    def test_unlisted_likely_prompt_fails_with_registry(self):
        repo = make_repo()
        write_inventory(repo)
        echo_adapter(repo, "{}")
        spec = write_spec(repo)
        add_case(spec, {"t": 1}, [{"kind": "json_valid"}])
        runner.update_baseline(spec, run_fresh(spec))
        (repo / "sneaky-prompt.md").write_text("You are a sneaky new prompt.\n")
        ok, failures, _ = pe_check.check_repo(repo)
        self.assertFalse(ok)
        self.assertTrue(any("sneaky-prompt.md" in f for f in failures))

    def test_governed_mapping_verified(self):
        repo = make_repo()
        write_inventory(repo)  # claims mod.py governed by spec p1
        # ...but no spec exists
        (repo / ".prompteval").mkdir(exist_ok=True)
        ok, failures, _ = pe_check.check_repo(repo)
        self.assertFalse(ok)
        self.assertTrue(any("does not exist" in f for f in failures))

    def test_holdout_file_discipline_and_contamination(self):
        repo = make_repo()
        write_inventory(repo)
        echo_adapter(repo, '{"score": 72}')
        spec = write_spec(repo)
        add_case(spec, {"title": "hd"}, [{"kind": "json_valid"}])
        add_case(spec, {"title": "You are a scorer. Return JSON."},  # leaks prompt text
                 [{"kind": "json_valid"}], status="holdout")
        report = run_fresh(spec)  # non-release
        runner.update_baseline(spec, report)
        ok, failures, _ = pe_check.check_repo(repo)
        self.assertFalse(ok)
        joined = " ".join(failures)
        self.assertIn("not a release run", joined)
        self.assertIn("contamination", joined)
        # holdout case hiding in cases.jsonl is a failure
        core.append_jsonl(spec.cases_path,
                          goldens.new_case({"misplaced": 1}, [{"kind": "json_valid"}],
                                           "synthetic", status="holdout"))
        ok, failures, _ = pe_check.check_repo(repo)
        self.assertTrue(any("holdouts live only in golden/holdout.jsonl" in f for f in failures))

    def test_enforced_inventory_fails_on_ungoverned(self):
        repo = make_repo()
        core.write_json(repo / ".prompteval" / "inventory.json", {
            "enforce": True,
            "prompts": [
                {"file": "mod.py", "status": "ungoverned"},
                {"file": "whole-prompt.md", "status": "not-a-prompt", "note": "fixture"},
            ],
        })
        ok, failures, _ = pe_check.check_repo(repo)
        self.assertFalse(ok)
        self.assertTrue(any("ungoverned" in f for f in failures))

    def test_case_input_immutability(self):
        case = goldens.new_case({"a": 1}, [{"kind": "json_valid"}], "synthetic")
        case["input"] = {"a": 2}
        problems = goldens.validate_case(case)
        self.assertTrue(any("id does not match input hash" in p for p in problems))


class TestFlywheel(unittest.TestCase):
    def setUp(self):
        self.repo = make_repo()
        write_inventory(self.repo)
        echo_adapter(self.repo, '{"score": 72}')
        self.spec = write_spec(self.repo)

    def test_capture_dedup_promote(self):
        added = goldens.append_candidate(self.spec.dir, {"title": "t1"}, "src", "out1")
        self.assertIsNotNone(added)
        self.assertIsNone(goldens.append_candidate(self.spec.dir, {"title": "t1"}, "src"))
        promoted = goldens.promote(
            self.spec.dir, [added["id"]], {added["id"]: [{"kind": "json_valid"}]}
        )
        self.assertEqual(promoted[0]["provenance"], "production")
        self.assertEqual(core.read_jsonl(self.spec.candidates_path), [])
        c2 = goldens.append_candidate(self.spec.dir, {"title": "t2"}, "src")
        with self.assertRaises(goldens.GoldenError):
            goldens.promote(self.spec.dir, [c2["id"]], {})

    def test_health_ratio_and_backlog(self):
        add_case(self.spec, {"t": 1}, [{"kind": "json_valid"}], provenance="synthetic")
        add_case(self.spec, {"t": 2}, [{"kind": "json_valid"}], provenance="production")
        goldens.append_candidate(self.spec.dir, {"t": 3}, "src")
        h = goldens.health(self.spec.dir, None)
        self.assertEqual(h["cases_active"], 2)
        self.assertEqual(h["production_ratio"], 0.5)
        self.assertEqual(h["candidate_backlog"], 1)

    def test_set_status_moves_across_holdout_boundary(self):
        case = add_case(self.spec, {"t": "mover"}, [{"kind": "json_valid"}])
        goldens.set_status(self.spec.dir, case["id"], "holdout")
        self.assertEqual(len(core.read_jsonl(self.spec.holdout_path)), 1)
        self.assertFalse(any(c["id"] == case["id"]
                             for c in core.read_jsonl(self.spec.cases_path)))
        goldens.set_status(self.spec.dir, case["id"], "active")
        self.assertEqual(core.read_jsonl(self.spec.holdout_path), [])


class TestCLISmoke(unittest.TestCase):
    def test_cli_end_to_end(self):
        repo = make_repo()
        echo_adapter(repo, '{"score": 72}')
        env = {**os.environ}
        cli = ["/opt/workspace/supervisor/scripts/prompteval"]

        r = subprocess.run(cli + ["register", str(repo), "--id", "p1", "--file", "mod.py",
                                  "--type", "py_var", "--var", "SYSTEM_PROMPT",
                                  "--executor", "command"],
                           capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 0, r.stderr)
        spec_path = repo / ".prompteval" / "p1" / "spec.json"
        spec = json.loads(spec_path.read_text())
        spec["executor"] = {"type": "command", "argv": ["python3", str(repo / "adapter.py")]}
        spec_path.write_text(json.dumps(spec))
        write_inventory(repo)

        case = goldens.new_case({"title": "cli-x"}, [{"kind": "json_valid"}], "synthetic")
        core.append_jsonl(repo / ".prompteval" / "p1" / "golden" / "cases.jsonl", case)

        r = subprocess.run(cli + ["run", str(repo), "--id", "p1", "--no-cache",
                                  "--update-baseline"],
                           capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        self.assertIn("GATE: PASS", r.stdout)

        r = subprocess.run(cli + ["check", str(repo)], capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 0, r.stdout)

        r = subprocess.run(cli + ["score", str(repo), "--id", "p1"],
                           capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('"aggregate"', r.stdout)

        r = subprocess.run(cli + ["run", str(repo), "--id", "p1", "--release"],
                           capture_output=True, text=True, env=env)
        self.assertEqual(r.returncode, 1)
        self.assertIn("holdout", r.stderr.lower())


if __name__ == "__main__":
    try:
        unittest.main(verbosity=1)
    finally:
        shutil.rmtree(TMP, ignore_errors=True)
