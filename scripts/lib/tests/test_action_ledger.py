#!/usr/bin/env python3
"""Concurrency + lifecycle regression tests for action-ledger.py.

Runnable standalone (`python3 test_action_ledger.py`) or under pytest. Uses real
subprocesses so the fcntl advisory lock is exercised across processes, not just
threads sharing a file descriptor.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

LEDGER_PY = str(Path(__file__).resolve().parents[1] / "action-ledger.py")


class Ledger:
    def __init__(self, root):
        self.dir = str(Path(root) / "ledger")
        self.events = str(Path(root) / "events.jsonl")

    def _base(self):
        return [sys.executable, LEDGER_PY, "--ledger-dir", self.dir,
                "--events-file", self.events, "--actor", "test"]

    def run(self, *args, check=False):
        p = subprocess.run(self._base() + list(args), capture_output=True, text=True)
        if check and p.returncode != 0:
            raise AssertionError(f"cmd failed {args}: {p.stderr or p.stdout}")
        return p

    def popen(self, *args):
        return subprocess.Popen(self._base() + list(args),
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    def records(self):
        return sorted(Path(self.dir).glob("ACT-*.json"))


def test_concurrent_new_mints_unique_ids():
    with tempfile.TemporaryDirectory() as root:
        L = Ledger(root)
        n = 16
        procs = [L.popen("new", "--title", f"c{i}", "--reversible") for i in range(n)]
        for p in procs:
            p.wait()
        recs = L.records()
        assert len(recs) == n, f"expected {n} records, got {len(recs)} (id collision/clobber)"
        ids = {json.loads(p.read_text())["id"] for p in recs}
        assert len(ids) == n, f"duplicate ids minted under concurrency: {sorted(ids)}"
        assert L.run("check").returncode == 0, "ledger invalid after concurrent new"
        print(f"ok: {n} concurrent new -> {n} unique ids, check OK")


def test_concurrent_transitions_do_not_corrupt():
    with tempfile.TemporaryDirectory() as root:
        L = Ledger(root)
        out = L.run("new", "--title", "race", "--reversible", check=True).stdout.strip()
        rid = json.loads(Path(out).read_text())["id"]
        # two concurrent transitions out of `open`; the lock serializes them
        p1 = L.popen("transition", rid, "--to", "in_progress")
        p2 = L.popen("transition", rid, "--to", "blocked", "--blocker-class", "dependency")
        p1.wait(); p2.wait()
        assert L.run("check").returncode == 0, "record corrupted by concurrent transitions"
        rec = json.loads(next(iter(L.records())).read_text())
        assert rec["state"] in ("in_progress", "blocked"), rec["state"]
        # transition chain stayed continuous (check already enforces this)
        print(f"ok: concurrent transitions serialized, final={rec['state']}, check OK")


def test_dedup_suppresses_while_non_terminal():
    with tempfile.TemporaryDirectory() as root:
        L = Ledger(root)
        a = L.run("new", "--title", "x", "--dedup-key", "K", check=True).stdout.strip()
        b = L.run("new", "--title", "x again", "--dedup-key", "K", check=True).stdout.strip()
        assert a == b, "non-terminal duplicate must be suppressed (same path)"
        assert len(L.records()) == 1
        # and the suppression emitted a real event
        events = [json.loads(l) for l in Path(L.events).read_text().splitlines() if l.strip()]
        assert any(e.get("eventType") == "action_duplicate_suppressed" for e in events)
        print("ok: dedup suppresses while non-terminal + emits suppression event")


def test_dedup_allows_new_generation_after_terminal():
    with tempfile.TemporaryDirectory() as root:
        L = Ledger(root)
        a = L.run("new", "--title", "x", "--dedup-key", "K", check=True).stdout.strip()
        rid = json.loads(Path(a).read_text())["id"]
        L.run("transition", rid, "--to", "dropped", check=True)  # terminal
        b = L.run("new", "--title", "x recurs", "--dedup-key", "K", check=True).stdout.strip()
        assert a != b, "a recurrence after a TERMINAL prior must create a new record"
        assert len(L.records()) == 2
        assert L.run("check").returncode == 0, "two records (1 terminal, 1 active) must pass check"
        print("ok: terminal record does not suppress a new generation")


def test_reopen_increments_and_latency_is_after_dispatch():
    with tempfile.TemporaryDirectory() as root:
        L = Ledger(root)
        a = L.run("new", "--title", "loop", "--reversible", check=True).stdout.strip()
        rid = json.loads(Path(a).read_text())["id"]
        for to, extra in [("dispatched", []), ("in_progress", []),
                          ("done", ["--completion-receipt", "r1", "--evidence", "e1"]),
                          ("open", []), ("dispatched", []), ("in_progress", [])]:
            L.run("transition", rid, "--to", to, *extra, check=True)
        rec = json.loads(Path(a).read_text())
        assert rec["reopened_count"] == 1, rec["reopened_count"]
        # metrics must not blow up and dispatch→exec must be non-negative
        m = json.loads(L.run("metrics", "--json", check=True).stdout)
        de = m["dispatch_to_execution_latency_hours"]
        assert de["n"] >= 1 and (de["median"] is None or de["median"] >= 0), de
        print("ok: reopen increments count; dispatch→exec latency non-negative")


def test_check_catches_state_mismatch():
    with tempfile.TemporaryDirectory() as root:
        L = Ledger(root)
        a = L.run("new", "--title", "tamper", "--reversible", check=True).stdout.strip()
        rec = json.loads(Path(a).read_text())
        rec["state"] = "done"  # tamper: state no longer matches last transition.to
        Path(a).write_text(json.dumps(rec))
        assert L.run("check").returncode == 1, "check must reject state != last transition.to"
        print("ok: check catches state/transition mismatch")


TESTS = [v for k, v in sorted(globals().items()) if k.startswith("test_")]


def main():
    failures = 0
    for t in TESTS:
        try:
            t()
        except AssertionError as exc:
            failures += 1
            print(f"FAIL: {t.__name__}: {exc}")
    print(f"\n{len(TESTS) - failures}/{len(TESTS)} passed")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
