#!/usr/bin/env python3
"""Concurrency + lifecycle regression tests for action-ledger.py.

Runnable standalone (`python3 test_action_ledger.py`) or under pytest. Uses real
subprocesses so the fcntl advisory lock is exercised across processes, not just
threads sharing a file descriptor.
"""

import json
import hashlib
import os
import subprocess
import sys
import tempfile
from pathlib import Path

LEDGER_PY = str(Path(__file__).resolve().parents[1] / "action-ledger.py")


class Ledger:
    def __init__(self, root):
        self.root = Path(root)
        self.dir = str(Path(root) / "ledger")
        self.events = str(Path(root) / "events.jsonl")
        self.archive = Path(root) / "archive"

    def _base(self):
        return [sys.executable, LEDGER_PY, "--ledger-dir", self.dir,
                "--events-file", self.events, "--actor", "test"]

    def run(self, *args, check=False, env_extra=None):
        env = {**os.environ, "ACTION_ARCHIVE_ROOT": str(self.archive)}
        env.update(env_extra or {})
        p = subprocess.run(
            self._base() + list(args), capture_output=True, text=True, env=env
        )
        if check and p.returncode != 0:
            raise AssertionError(f"cmd failed {args}: {p.stderr or p.stdout}")
        return p

    def popen(self, *args):
        env = {**os.environ, "ACTION_ARCHIVE_ROOT": str(self.archive)}
        return subprocess.Popen(self._base() + list(args),
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, env=env)

    def records(self):
        return sorted(Path(self.dir).glob("ACT-*.json"))

    def receipt(self, action_id, *, source=None, archive=None, omit=None):
        transcript = self.root / f"{action_id}-verification.txt"
        transcript.write_text("verification passed\n")
        payload = {
            "schema_version": 1,
            "action_id": action_id,
            "completed_at": "2026-07-20T10:00:00Z",
            "code_landed": {
                "status": "not_applicable",
                "reason": "test action has no code",
            },
            "verification_passed": {
                "status": "complete",
                "evidence": [{
                    "kind": "command",
                    "command": "test command",
                    "exit_code": 0,
                    "observed_at": "2026-07-20T10:00:00Z",
                    "transcript_path": str(transcript),
                    "transcript_sha256": hashlib.sha256(
                        transcript.read_bytes()
                    ).hexdigest(),
                }],
            },
            "deployed": {
                "status": "not_applicable",
                "reason": "test action has no deployment",
            },
            "state_projection_refreshed": {
                "status": "not_applicable",
                "reason": "test action has no projection",
            },
            "source_artifact_dispositioned": {
                "status": "not_applicable",
                "reason": "test action has no source artifact",
            },
        }
        if source is not None:
            payload["source_artifact_dispositioned"] = {
                "status": "complete",
                "source_path": str(source),
                "archive_path": str(archive),
                "sha256": hashlib.sha256(Path(source).read_bytes()).hexdigest(),
            }
        if omit:
            payload.pop(omit)
        path = self.root / f"{action_id}-receipt.json"
        path.write_text(json.dumps(payload))
        return path


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
        receipt = L.receipt(rid)
        for to, extra in [("dispatched", []), ("in_progress", []),
                          ("done", ["--completion-receipt", str(receipt)]),
                          ("open", []), ("dispatched", []), ("in_progress", [])]:
            L.run("transition", rid, "--to", to, *extra, check=True)
        rec = json.loads(Path(a).read_text())
        assert rec["reopened_count"] == 1, rec["reopened_count"]
        # metrics must not blow up and dispatch→exec must be non-negative
        m = json.loads(L.run("metrics", "--json", check=True).stdout)
        de = m["dispatch_to_execution_latency_hours"]
        assert de["n"] >= 1 and (de["median"] is None or de["median"] >= 0), de
        print("ok: reopen increments count; dispatch→exec latency non-negative")


def test_done_requires_complete_typed_receipt():
    with tempfile.TemporaryDirectory() as root:
        L = Ledger(root)
        action = L.run("new", "--title", "typed", check=True).stdout.strip()
        rid = json.loads(Path(action).read_text())["id"]
        incomplete = L.receipt(rid, omit="deployed")
        result = L.run(
            "transition", rid, "--to", "done",
            "--completion-receipt", str(incomplete),
        )
        assert result.returncode != 0
        assert "deployed must be an object" in result.stderr
        assert json.loads(Path(action).read_text())["state"] == "open"
        print("ok: incomplete typed receipt cannot create done state")


def test_done_archives_matching_source_and_check_revalidates_receipt():
    with tempfile.TemporaryDirectory() as root:
        L = Ledger(root)
        source = Path(root) / "source-handoff.md"
        source.write_text("work contract")
        archive = L.archive / "2026-07-20" / source.name
        action = L.run(
            "new", "--title", "archive source", "--source", str(source),
            check=True,
        ).stdout.strip()
        rid = json.loads(Path(action).read_text())["id"]
        receipt = L.receipt(rid, source=source, archive=archive)
        L.run(
            "transition", rid, "--to", "done",
            "--completion-receipt", str(receipt),
            check=True,
        )
        assert not source.exists()
        assert archive.read_text() == "work contract"
        rec = json.loads(Path(action).read_text())
        assert rec["closure_schema_version"] == 1
        assert str(receipt) in rec["acceptance_evidence"]
        assert L.run("check").returncode == 0
        print("ok: done atomically archives source and typed receipt revalidates")


def test_crash_after_archive_is_recovered_before_next_observation():
    with tempfile.TemporaryDirectory() as root:
        L = Ledger(root)
        source = Path(root) / "crash-source.md"
        source.write_text("recover me")
        archive = L.archive / "2026-07-20" / source.name
        action = L.run(
            "new", "--title", "crash recovery", "--source", str(source),
            check=True,
        ).stdout.strip()
        rid = json.loads(Path(action).read_text())["id"]
        receipt = L.receipt(rid, source=source, archive=archive)
        crashed = L.run(
            "transition", rid, "--to", "done",
            "--completion-receipt", str(receipt),
            env_extra={"ACTION_LEDGER_TEST_CRASH_AFTER_ARCHIVE": "1"},
        )
        assert crashed.returncode == 97
        assert archive.exists() and not source.exists()
        assert json.loads(Path(action).read_text())["state"] == "open"
        # `check` recovers prepared transactions before exposing ledger state.
        assert L.run("check").returncode == 0
        assert json.loads(Path(action).read_text())["state"] == "done"
        assert not list((Path(L.dir) / ".transactions").glob("*.json"))
        print("ok: crash after archive rolls forward from durable journal")


def test_archive_collision_fails_closed_without_clobbering_either_file():
    with tempfile.TemporaryDirectory() as root:
        L = Ledger(root)
        source = Path(root) / "source.md"
        source.write_text("source")
        archive = L.archive / "2026-07-20" / source.name
        archive.parent.mkdir(parents=True)
        archive.write_text("existing archive")
        action = L.run(
            "new", "--title", "collision", "--source", str(source), check=True,
        ).stdout.strip()
        rid = json.loads(Path(action).read_text())["id"]
        receipt = L.receipt(rid, source=source, archive=archive)
        result = L.run(
            "transition", rid, "--to", "done",
            "--completion-receipt", str(receipt),
        )
        assert result.returncode != 0
        assert source.read_text() == "source"
        assert archive.read_text() == "existing archive"
        assert json.loads(Path(action).read_text())["state"] == "open"
        print("ok: archive collision fails closed without clobbering")


def test_code_landed_requires_commit_reachable_from_remote_ref():
    with tempfile.TemporaryDirectory() as root:
        L = Ledger(root)
        repository = Path(root) / "repo"
        remote = Path(root) / "remote.git"
        subprocess.run(["git", "init", "--bare", str(remote)], check=True, capture_output=True)
        subprocess.run(["git", "init", "-b", "main", str(repository)], check=True, capture_output=True)
        subprocess.run(
            ["git", "-C", str(repository), "config", "user.email", "test@example.com"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(repository), "config", "user.name", "Test"],
            check=True,
        )
        (repository / "proof.txt").write_text("proof")
        subprocess.run(["git", "-C", str(repository), "add", "proof.txt"], check=True)
        subprocess.run(["git", "-C", str(repository), "commit", "-m", "proof"], check=True, capture_output=True)
        commit = subprocess.run(
            ["git", "-C", str(repository), "rev-parse", "HEAD"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
        subprocess.run(["git", "-C", str(repository), "remote", "add", "origin", str(remote)], check=True)

        action = L.run("new", "--title", "durability proof", check=True).stdout.strip()
        rid = json.loads(Path(action).read_text())["id"]
        receipt = L.receipt(rid)
        payload = json.loads(receipt.read_text())
        payload["code_landed"] = {
            "status": "complete",
            "repository": str(repository),
            "commit": commit,
            "remote_ref": "origin/main",
        }
        receipt.write_text(json.dumps(payload))
        rejected = L.run(
            "transition", rid, "--to", "done", "--completion-receipt", str(receipt)
        )
        assert rejected.returncode != 0
        assert "remote_ref is not present" in rejected.stderr

        subprocess.run(
            ["git", "-C", str(repository), "push", "-u", "origin", "main"],
            check=True, capture_output=True,
        )
        L.run(
            "transition", rid, "--to", "done", "--completion-receipt", str(receipt),
            check=True,
        )
        assert json.loads(Path(action).read_text())["state"] == "done"
        print("ok: code_landed refuses local-only SHA and accepts remote-reachable commit")


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
