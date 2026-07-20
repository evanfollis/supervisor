#!/usr/bin/env python3
"""action-ledger — the typed diagnosis→execution→closure bridge (dispatch 2026-07-19).

One record per unit of work that a diagnosis, reflection, synthesis proposal,
handoff, or principal directive implies. The ledger is the canonical place where
a recommendation becomes an owned, state-tracked, closeable action — so the
"dispatch inertia" failure class (perfect diagnosis, zero execution) is
mechanically visible instead of silently re-restated every cycle.

Records live git-tracked under supervisor/ledger/ (durable governance state,
like ideas/). Transition telemetry is appended to the runtime spool at
runtime/.telemetry/supervisor-events.jsonl (off the hot path, never in git).

State machine (transitions are validated; illegal moves are refused):

    open ─────► dispatched ──► in_progress ──► done
      │  ╲          │   ╲          │   ╲         ▲
      │   ╲         ▼    ╲         ▼    ╲        │
      └────► blocked ◄────┴────────┴─────┴───────┘
             │  ╲
             ▼   ╲
           open   dropped        done/dropped ──(reopen)──► open

Invariants enforced by `check`:
  - state ∈ STATES
  - done      ⇒ completion_receipt set AND ≥1 acceptance_evidence
  - blocked   ⇒ blocker_class set
  - every recorded transition is a legal edge
  - dedup_key is unique across open records (duplicate recommendations refused)
"""

import argparse
import contextlib
import fcntl
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from action_closure import (
    DEFAULT_ARCHIVE_ROOT,
    SCHEMA_VERSION as CLOSURE_SCHEMA_VERSION,
    ClosureReceiptError,
    validate_receipt,
)

LEDGER_DIR_DEFAULT = "/opt/workspace/supervisor/ledger"
EVENTS_FILE_DEFAULT = "/opt/workspace/runtime/.telemetry/supervisor-events.jsonl"

# --- vocabulary -----------------------------------------------------------

STATES = ["open", "dispatched", "in_progress", "blocked", "done", "dropped"]
TERMINAL = {"done", "dropped"}

# Legal transition edges. Anything not listed is refused by `transition`.
TRANSITIONS = {
    "open":        {"dispatched", "in_progress", "blocked", "done", "dropped"},
    "dispatched":  {"in_progress", "blocked", "done", "dropped", "open"},
    "in_progress": {"done", "blocked", "dropped", "dispatched"},
    "blocked":     {"open", "in_progress", "dispatched", "done", "dropped"},
    "done":        {"open"},      # reopen
    "dropped":     {"open"},      # reopen
}

# Why a reversible, in-scope action did NOT execute. Drives item-4 metrics.
BLOCKER_CLASSES = [
    "capacity",        # subscription CLI throttled / both providers blocked
    "sandbox",         # session sandbox refused a sanctioned command
    "credential",      # missing scoped credential
    "principal-input", # genuinely needs the principal (authority/spend/irreversible/ambiguous)
    "dependency",      # blocked on another ledger item or external system
    "review",          # awaiting adversarial/PM review before it can close
    "external",        # third-party / upstream
    "unknown",
]

# How the action may be executed without escalation (dispatch item 3).
EXEC_CLASSES = [
    "auto",       # reversible + in-scope → execute by default
    "review",     # execute, but requires adversarial/PM review before closing
    "principal",  # requires principal input (authority/spend/irreversible/ambiguous)
]

RISK_LEVELS = ["low", "medium", "high"]


def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_iso(s):
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None


def slugify(text):
    slug = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return slug or "action"


def load_json(path):
    with path.open() as fh:
        return json.load(fh)


def now_epoch_ms():
    return int(datetime.now(timezone.utc).timestamp() * 1000)


@contextlib.contextmanager
def ledger_lock(ledger_dir: Path):
    """Advisory exclusive lock serializing id-mint + dedup + save and the
    read-modify-write of a transition, so concurrent ticks cannot mint the same
    id or clobber each other's writes."""
    ledger_dir.mkdir(parents=True, exist_ok=True)
    lock_path = ledger_dir / ".ledger.lock"
    with open(lock_path, "w") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        try:
            yield
        finally:
            fcntl.flock(fh, fcntl.LOCK_UN)


def save_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    # pid-unique tmp so a stray unlocked writer can never collide on the tmp path.
    tmp = path.with_suffix(f".{os.getpid()}.tmp")
    with tmp.open("w") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)
        fh.write("\n")
        fh.flush()
        os.fsync(fh.fileno())
    tmp.replace(path)
    fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def append_event(events_file, event_type, ref, note):
    """Append one telemetry line carrying the canonical workspace event shape
    (project/source/eventType/level/timestamp/sourceType, S1-P2) alongside the
    legacy fields (ts/agent/type/ref/note) for backward compatibility."""
    p = Path(events_file)
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            # canonical (S1-P2): timestamp is epoch milliseconds (integer)
            "project": "supervisor",
            "source": "action-ledger",
            "eventType": event_type,
            "level": "info",
            "timestamp": now_epoch_ms(),
            "sourceType": os.environ.get("WORKSPACE_SOURCE_TYPE", "system"),
            # legacy / human-readable (kept for existing readers)
            "ts": now_iso(),
            "agent": os.environ.get("WORKSPACE_AGENT", "unknown"),
            "type": event_type,
            "ref": ref,
            "note": (note or "")[:160],
        }
        with p.open("a") as fh:
            fh.write(json.dumps(payload, sort_keys=True) + "\n")
    except OSError as exc:
        # Telemetry must never block the ledger transition (ADR-0043 nonblocking).
        print(f"warn: could not append event: {exc}", file=sys.stderr)


def next_id(ledger_dir):
    max_n = 0
    for path in ledger_dir.glob("ACT-*.json"):
        m = re.match(r"ACT-(\d{4})-", path.name)
        if m:
            max_n = max(max_n, int(m.group(1)))
    return f"ACT-{max_n + 1:04d}"


def all_records(ledger_dir):
    out = []
    for path in sorted(ledger_dir.glob("ACT-*.json")):
        try:
            out.append((path, load_json(path)))
        except (OSError, json.JSONDecodeError):
            continue
    return out


def find_path(ledger_dir, act_id):
    matches = sorted(ledger_dir.glob(f"{act_id}-*.json"))
    if not matches:
        raise SystemExit(f"action not found: {act_id}")
    if len(matches) > 1:
        raise SystemExit(f"ambiguous action id: {act_id}")
    return matches[0]


def find_by_dedup(ledger_dir, dedup_key):
    """Return an existing NON-TERMINAL record with this dedup_key, if any.

    Terminal (done/dropped) records do not suppress a new generation: a
    recommendation that recurs after its prior instance closed is legitimately
    new, re-openable work — not a duplicate to swallow forever. This matches the
    `check` invariant, which enforces dedup uniqueness only among non-terminal
    records.
    """
    if not dedup_key:
        return None, None
    for path, payload in all_records(ledger_dir):
        if payload.get("dedup_key") == dedup_key and payload.get("state") not in TERMINAL:
            return path, payload
    return None, None


# --- commands -------------------------------------------------------------

def cmd_new(args):
    ledger_dir = Path(args.ledger_dir)
    ledger_dir.mkdir(parents=True, exist_ok=True)

    # Validate arguments before taking the lock (cheap, no shared state).
    if args.state == "blocked" and not args.blocker_class:
        raise SystemExit("refuse: state=blocked requires --blocker-class")
    if args.state == "done":
        raise SystemExit(
            "refuse: create the action non-terminal, then transition to done "
            "with a typed completion receipt"
        )

    # Serialize dedup-check + id-mint + save so concurrent ticks cannot mint the
    # same ACT id or race on the same dedup_key.
    with ledger_lock(ledger_dir):
        _recover_pending_transactions_locked(ledger_dir)
        if args.dedup_key:
            existing_path, existing = find_by_dedup(ledger_dir, args.dedup_key)
            if existing_path is not None:
                append_event(args.events_file, "action_duplicate_suppressed",
                             str(existing_path), f"{existing['id']} dedup {args.dedup_key}")
                print(str(existing_path))
                return

        act_id = next_id(ledger_dir)
        slug = slugify(args.slug or args.title)
        ts = now_iso()
        record = {
            "id": act_id,
            "slug": slug,
            "title": args.title,
            "summary": args.summary or "",
            "source": args.source or "",
            "owner": args.owner or "general",
            "risk": args.risk,
            "reversible": bool(args.reversible),
            "exec_class": args.exec_class,
            "state": args.state,
            "attempt_count": 0,
            "reopened_count": 0,
            "blocker_class": args.blocker_class,
            "acceptance_evidence": list(args.evidence or []),
            "completion_receipt": args.completion_receipt or "",
            "dedup_key": args.dedup_key or "",
            "created_at": ts,
            "updated_at": ts,
            "last_transition_at": ts,
            "transitions": [
                {"ts": ts, "actor": args.actor, "from": None, "to": args.state,
                 "note": (args.note or "created")[:200]}
            ],
        }
        path = ledger_dir / f"{act_id}-{slug}.json"
        save_json(path, record)
    append_event(args.events_file, "action_logged", str(path),
                 f"{act_id} {args.state} {args.title}")
    print(str(path))


def _fsync_directory(path):
    fd = os.open(path, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def _finish_source_move(source, archive):
    """Finish a durable, no-clobber source disposition.

    A hard link makes the archive durable before the inbox name is removed. If
    the process dies between those operations, recovery sees both names, proves
    they identify the same inode, and removes the source name. Requiring one
    filesystem is deliberate: cross-filesystem copy/delete cannot provide this
    crash invariant without a more complex content-addressed transaction.
    """
    archive.parent.mkdir(parents=True, exist_ok=True)
    if source.exists() and not archive.exists():
        try:
            os.link(source, archive, follow_symlinks=False)
        except FileExistsError as exc:
            raise RuntimeError(f"refuse: source archive collision: {archive}") from exc
        except OSError as exc:
            raise RuntimeError(
                "refuse: source and archive must share a filesystem for "
                f"transactional disposition: {source} -> {archive}: {exc}"
            ) from exc
        with archive.open("rb") as handle:
            os.fsync(handle.fileno())
        _fsync_directory(archive.parent)
    if source.exists() and archive.exists():
        try:
            same = os.path.samefile(source, archive)
        except OSError as exc:
            raise RuntimeError(f"refuse: cannot compare source and archive: {exc}") from exc
        if not same:
            raise RuntimeError(
                f"refuse: source/archive collision contains different files: {archive}"
            )
        source.unlink()
        _fsync_directory(source.parent)
    if source.exists() or not archive.exists():
        raise RuntimeError(
            f"refuse: incomplete source disposition: {source} -> {archive}"
        )


def _transaction_dir(ledger_dir):
    return ledger_dir / ".transactions"


def _recover_transaction_locked(journal_path, ledger_dir):
    """Roll one prepared closure transaction forward to its only valid end."""
    journal = load_json(journal_path)
    if journal.get("schema_version") != 1 or journal.get("operation") != "close":
        raise RuntimeError(f"refuse: invalid closure transaction journal: {journal_path}")
    ledger_path = Path(journal.get("ledger_path", ""))
    try:
        ledger_path.resolve(strict=False).relative_to(ledger_dir.resolve(strict=False))
    except ValueError as exc:
        raise RuntimeError(
            f"refuse: transaction ledger path escapes ledger root: {ledger_path}"
        ) from exc
    after_record = journal.get("after_record")
    if not isinstance(after_record, dict) or after_record.get("state") != "done":
        raise RuntimeError(f"refuse: invalid transaction terminal record: {journal_path}")
    source = Path(journal["source"])
    archive = Path(journal["archive"])
    _finish_source_move(source, archive)
    save_json(ledger_path, after_record)
    journal_path.unlink()
    _fsync_directory(journal_path.parent)


def _recover_pending_transactions_locked(ledger_dir):
    transaction_dir = _transaction_dir(ledger_dir)
    if not transaction_dir.exists():
        return
    for journal_path in sorted(transaction_dir.glob("*.json")):
        _recover_transaction_locked(journal_path, ledger_dir)


def _consistent_records(ledger_dir):
    """Return a snapshot after rolling prepared closure transactions forward."""
    with ledger_lock(ledger_dir):
        _recover_pending_transactions_locked(ledger_dir)
        return all_records(ledger_dir)


def cmd_transition(args):
    ledger_dir = Path(args.ledger_dir)
    to = args.to
    if to not in STATES:
        raise SystemExit(f"refuse: unknown state {to!r}")

    # Serialize the whole read-modify-write so a concurrent transition on the
    # same record cannot be lost (last-writer-wins clobber).
    with ledger_lock(ledger_dir):
        _recover_pending_transactions_locked(ledger_dir)
        path = find_path(ledger_dir, args.act_id)
        rec = load_json(path)
        original_rec = json.loads(json.dumps(rec))
        frm = rec["state"]
        source_move = None

        if to not in TRANSITIONS.get(frm, set()):
            raise SystemExit(
                f"refuse: illegal transition {frm} -> {to} "
                f"(legal from {frm}: {sorted(TRANSITIONS.get(frm, set()))})")

        if to == "blocked":
            blocker = args.blocker_class or rec.get("blocker_class")
            if not blocker:
                raise SystemExit("refuse: -> blocked requires --blocker-class")
            rec["blocker_class"] = blocker
        else:
            # leaving a blocked state clears the blocker unless re-declared
            if frm == "blocked" and to != "blocked":
                rec["blocker_class"] = args.blocker_class or None

        if args.evidence:
            for e in args.evidence:
                if e not in rec["acceptance_evidence"]:
                    rec["acceptance_evidence"].append(e)
        if to == "done":
            if not args.completion_receipt:
                raise SystemExit(
                    "refuse: -> done requires --completion-receipt pointing to "
                    "a typed JSON receipt"
                )
            receipt_path = Path(args.completion_receipt)
            archive_root = Path(
                os.environ.get("ACTION_ARCHIVE_ROOT", str(DEFAULT_ARCHIVE_ROOT))
            )
            try:
                closure, source_move = validate_receipt(
                    receipt_path,
                    action_id=rec["id"],
                    record_source=rec.get("source", ""),
                    source_root=ledger_dir.parent,
                    archive_root=archive_root,
                )
            except ClosureReceiptError as exc:
                raise SystemExit(f"refuse: invalid completion receipt: {exc}") from exc
            rec["completion_receipt"] = str(receipt_path)
            rec["closure_schema_version"] = CLOSURE_SCHEMA_VERSION
            rec["closure"] = closure
            if str(receipt_path) not in rec["acceptance_evidence"]:
                rec["acceptance_evidence"].append(str(receipt_path))

        if to == "in_progress":
            rec["attempt_count"] = int(rec.get("attempt_count", 0)) + 1
        if frm in TERMINAL and to == "open":
            rec["reopened_count"] = int(rec.get("reopened_count", 0)) + 1
            stale_receipt = rec.get("completion_receipt")
            rec["completion_receipt"] = ""
            rec.pop("closure", None)
            rec.pop("closure_schema_version", None)
            if stale_receipt in rec.get("acceptance_evidence", []):
                rec["acceptance_evidence"].remove(stale_receipt)

        if args.owner:
            rec["owner"] = args.owner
        if args.exec_class:
            rec["exec_class"] = args.exec_class

        ts = now_iso()
        rec["state"] = to
        rec["updated_at"] = ts
        rec["last_transition_at"] = ts
        rec.setdefault("transitions", []).append(
            {"ts": ts, "actor": args.actor, "from": frm, "to": to,
             "note": (args.note or "")[:200]})
        if source_move is not None:
            source, archive = source_move
            transaction_dir = _transaction_dir(ledger_dir)
            transaction_dir.mkdir(parents=True, exist_ok=True)
            journal_path = transaction_dir / f"{rec['id']}-close.json"
            if journal_path.exists():
                raise SystemExit(
                    f"refuse: closure transaction already exists: {journal_path}"
                )
            save_json(journal_path, {
                "schema_version": 1,
                "operation": "close",
                "prepared_at": now_iso(),
                "ledger_path": str(path),
                "source": str(source),
                "archive": str(archive),
                "before_record": original_rec,
                "after_record": rec,
            })
            _finish_source_move(source, archive)
            if os.environ.get("ACTION_LEDGER_TEST_CRASH_AFTER_ARCHIVE") == "1":
                os._exit(97)
            save_json(path, rec)
            journal_path.unlink()
            _fsync_directory(journal_path.parent)
        else:
            save_json(path, rec)

    append_event(args.events_file, "action_transition", str(path),
                 f"{rec['id']} {frm}->{to} {args.note or ''}")
    print(str(path))


def cmd_list(args):
    ledger_dir = Path(args.ledger_dir)
    for path, rec in _consistent_records(ledger_dir):
        if args.state and rec.get("state") != args.state:
            continue
        if args.owner and rec.get("owner") != args.owner:
            continue
        if args.open and rec.get("state") in TERMINAL:
            continue
        summary = " ".join((rec.get("summary", "") or "").split())
        print(f"{rec['id']}\t{rec.get('state',''):11}\t{rec.get('exec_class',''):9}\t"
              f"{rec.get('owner',''):16}\t{rec.get('blocker_class') or '-':14}\t"
              f"{rec.get('title','')}\t{summary[:80]}")


def cmd_show(args):
    ledger_dir = Path(args.ledger_dir)
    with ledger_lock(ledger_dir):
        _recover_pending_transactions_locked(ledger_dir)
        record = load_json(find_path(ledger_dir, args.act_id))
    print(json.dumps(record, indent=2, sort_keys=True))


def cmd_check(args):
    """Machine-checkable invariants. Exit 1 on any violation."""
    ledger_dir = Path(args.ledger_dir)
    records = _consistent_records(ledger_dir)
    problems = []
    seen_dedup = {}
    for path, rec in records:
        rid = rec.get("id", path.name)
        st = rec.get("state")
        # identity: id well-formed and filename agrees
        if not re.match(r"^ACT-\d{4}$", str(rid)):
            problems.append(f"{path.name}: id {rid!r} is not ACT-NNNN")
        elif not path.name.startswith(f"{rid}-"):
            problems.append(f"{rid}: filename {path.name} does not match id")
        if st not in STATES:
            problems.append(f"{rid}: invalid state {st!r}")
        if st == "done" and (not rec.get("completion_receipt") or not rec.get("acceptance_evidence")):
            problems.append(f"{rid}: done without completion_receipt+acceptance_evidence")
        if st == "done" and rec.get("closure_schema_version") is not None:
            if rec.get("closure_schema_version") != CLOSURE_SCHEMA_VERSION:
                problems.append(
                    f"{rid}: unsupported closure_schema_version "
                    f"{rec.get('closure_schema_version')!r}"
                )
            else:
                try:
                    closure, _ = validate_receipt(
                        Path(rec.get("completion_receipt", "")),
                        action_id=rid,
                        record_source=rec.get("source", ""),
                        source_root=ledger_dir.parent,
                        archive_root=Path(
                            os.environ.get(
                                "ACTION_ARCHIVE_ROOT", str(DEFAULT_ARCHIVE_ROOT)
                            )
                        ),
                    )
                    if rec.get("closure") != closure:
                        problems.append(f"{rid}: embedded closure differs from receipt")
                except ClosureReceiptError as exc:
                    problems.append(f"{rid}: invalid typed closure receipt: {exc}")
        if st == "blocked" and not rec.get("blocker_class"):
            problems.append(f"{rid}: blocked without blocker_class")
        if rec.get("exec_class") not in EXEC_CLASSES:
            problems.append(f"{rid}: invalid exec_class {rec.get('exec_class')!r}")
        if rec.get("risk") not in RISK_LEVELS:
            problems.append(f"{rid}: invalid risk {rec.get('risk')!r}")
        if not isinstance(rec.get("reversible"), bool):
            problems.append(f"{rid}: reversible must be a boolean")
        for tf in ("created_at", "updated_at", "last_transition_at"):
            if parse_iso(rec.get(tf)) is None:
                problems.append(f"{rid}: unparseable {tf}={rec.get(tf)!r}")
        # transition chain: first.from is null; each from == previous.to; each
        # edge legal; and the record's state == the last transition's `to`.
        trans = rec.get("transitions", [])
        if not trans:
            problems.append(f"{rid}: no transitions recorded")
        else:
            prev_to = None
            for i, t in enumerate(trans):
                frm, to = t.get("from"), t.get("to")
                if i == 0:
                    if frm is not None:
                        problems.append(f"{rid}: first transition.from must be null")
                else:
                    if frm != prev_to:
                        problems.append(
                            f"{rid}: transition {i} from={frm!r} breaks chain (prev.to={prev_to!r})")
                    elif to not in TRANSITIONS.get(frm, set()):
                        problems.append(f"{rid}: illegal recorded transition {frm}->{to}")
                prev_to = to
            if prev_to != st:
                problems.append(f"{rid}: state {st!r} != last transition.to {prev_to!r}")
        # dedup uniqueness across non-terminal records
        dk = rec.get("dedup_key")
        if dk and st not in TERMINAL:
            if dk in seen_dedup:
                problems.append(f"{rid}: duplicate dedup_key {dk!r} (also {seen_dedup[dk]})")
            else:
                seen_dedup[dk] = rid
    if problems:
        print("action-ledger check FAIL:", file=sys.stderr)
        for p in problems:
            print(f"  ✗ {p}", file=sys.stderr)
        sys.exit(1)
    n = len(records)
    print(f"action-ledger check OK — {n} record(s), all invariants hold")


def _latency_hours(a, b):
    da, db = parse_iso(a), parse_iso(b)
    if not da or not db:
        return None
    return round((db - da).total_seconds() / 3600.0, 2)


def _first_transition_to(rec, states):
    for t in rec.get("transitions", []):
        if t.get("to") in states:
            return t.get("ts")
    return None


def _dispatch_exec_latency_hours(rec):
    """Hours from the dispatch that actually preceded execution to that
    execution. A reopen can leave an earlier in_progress before a later
    dispatch, so pair each execution with the most recent PRIOR dispatch and
    only count a non-negative interval."""
    last_dispatch = None
    for t in rec.get("transitions", []):
        to = t.get("to")
        if to == "dispatched":
            last_dispatch = t.get("ts")
        elif to in ("in_progress", "done") and last_dispatch is not None:
            lat = _latency_hours(last_dispatch, t.get("ts"))
            if lat is not None and lat >= 0:
                return lat
    return None


def _count_suppression_events(events_file):
    """Count real dedup-suppression events (action_duplicate_suppressed) from the
    telemetry stream. Returns None if the stream cannot be read — we never infer
    'suppressed' from records sharing a dedup_key, which measures something else."""
    p = Path(events_file)
    if not p.exists():
        return None
    n = 0
    try:
        with p.open() as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    ev = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if ev.get("eventType") == "action_duplicate_suppressed" \
                        or ev.get("type") == "action_duplicate_suppressed":
                    n += 1
    except OSError:
        return None
    return n


def cmd_metrics(args):
    """Item-4 metrics computed from the ledger's own transition lineage."""
    ledger_dir = Path(args.ledger_dir)
    recs = [r for _, r in _consistent_records(ledger_dir)]
    now = datetime.now(timezone.utc)
    total = len(recs)
    by_state = {}
    diag_to_dispatch, dispatch_to_exec = [], []
    reopened = 0
    blocker_hist = {}
    stale = []

    for r in recs:
        by_state[r.get("state")] = by_state.get(r.get("state"), 0) + 1
        d = _first_transition_to(r, {"dispatched"})
        if d:
            lat = _latency_hours(r.get("created_at"), d)
            if lat is not None and lat >= 0:
                diag_to_dispatch.append(lat)
        de = _dispatch_exec_latency_hours(r)
        if de is not None:
            dispatch_to_exec.append(de)
        if int(r.get("reopened_count", 0)) > 0:
            reopened += 1
        if r.get("state") == "blocked":
            bc = r.get("blocker_class") or "unknown"
            blocker_hist[bc] = blocker_hist.get(bc, 0) + 1
        if r.get("state") not in TERMINAL:
            age = _latency_hours(r.get("created_at"), now.isoformat())
            if age is not None and age >= args.stale_hours:
                stale.append((r.get("id"), round(age / 24.0, 1)))

    suppressed = _count_suppression_events(args.events_file)
    done = by_state.get("done", 0)
    dropped = by_state.get("dropped", 0)
    closable = total - dropped
    closure_rate = round(done / closable, 3) if closable else None

    def _median(xs):
        if not xs:
            return None
        xs = sorted(xs)
        m = len(xs) // 2
        return xs[m] if len(xs) % 2 else round((xs[m - 1] + xs[m]) / 2, 2)

    out = {
        "generated_at": now_iso(),
        "total_actions": total,
        "by_state": by_state,
        "closure_rate": closure_rate,
        "diagnosis_to_dispatch_latency_hours": {
            "median": _median(diag_to_dispatch), "n": len(diag_to_dispatch)},
        "dispatch_to_execution_latency_hours": {
            "median": _median(dispatch_to_exec), "n": len(dispatch_to_exec)},
        "reopened_work": reopened,
        "duplicate_recommendations_suppressed": suppressed,
        "stale_queue": {
            "threshold_days": round(args.stale_hours / 24.0, 1),
            "count": len(stale),
            "items": [{"id": i, "age_days": a} for i, a in sorted(stale, key=lambda x: -x[1])],
        },
        "reasons_execution_did_not_happen": blocker_hist,
    }
    if args.json:
        print(json.dumps(out, indent=2, sort_keys=True))
    else:
        print(f"actions={total}  closure_rate={closure_rate}  "
              f"open={by_state.get('open',0)} dispatched={by_state.get('dispatched',0)} "
              f"in_progress={by_state.get('in_progress',0)} blocked={by_state.get('blocked',0)} "
              f"done={done} dropped={dropped}")
        print(f"diag→dispatch median={out['diagnosis_to_dispatch_latency_hours']['median']}h  "
              f"dispatch→exec median={out['dispatch_to_execution_latency_hours']['median']}h  "
              f"reopened={reopened}  dup_suppressed={suppressed}")
        if stale:
            print(f"stale (≥{out['stale_queue']['threshold_days']}d): " +
                  ", ".join(f"{i}({a}d)" for i, a in stale))
        if blocker_hist:
            print("blockers: " + ", ".join(f"{k}={v}" for k, v in sorted(blocker_hist.items())))
    if args.out:
        save_json(Path(args.out), out)


def build_parser():
    p = argparse.ArgumentParser(description="Typed action/closure ledger (diagnosis→execution bridge).")
    p.add_argument("--ledger-dir", default=LEDGER_DIR_DEFAULT)
    p.add_argument("--events-file", default=EVENTS_FILE_DEFAULT)
    p.add_argument("--actor", default=os.environ.get("WORKSPACE_AGENT", "unknown"))
    sub = p.add_subparsers(dest="command", required=True)

    n = sub.add_parser("new", help="log a new action")
    n.add_argument("--title", required=True)
    n.add_argument("--summary")
    n.add_argument("--slug")
    n.add_argument("--source", help="provenance: inbox file, synthesis cycle, handoff, directive")
    n.add_argument("--owner", default="general")
    n.add_argument("--risk", default="medium", choices=RISK_LEVELS)
    n.add_argument("--reversible", action="store_true")
    n.add_argument("--exec-class", default="auto", choices=EXEC_CLASSES)
    n.add_argument("--state", default="open", choices=STATES)
    n.add_argument("--blocker-class", choices=BLOCKER_CLASSES)
    n.add_argument("--evidence", action="append")
    n.add_argument("--completion-receipt")
    n.add_argument("--dedup-key", help="idempotency key; duplicate is suppressed")
    n.add_argument("--note")
    n.set_defaults(func=cmd_new)

    t = sub.add_parser("transition", help="move an action to a new state (validated)")
    t.add_argument("act_id")
    t.add_argument("--to", required=True, choices=STATES)
    t.add_argument("--blocker-class", choices=BLOCKER_CLASSES)
    t.add_argument("--evidence", action="append")
    t.add_argument("--completion-receipt")
    t.add_argument("--owner")
    t.add_argument("--exec-class", choices=EXEC_CLASSES)
    t.add_argument("--note")
    t.set_defaults(func=cmd_transition)

    ls = sub.add_parser("list", help="list actions")
    ls.add_argument("--state", choices=STATES)
    ls.add_argument("--owner")
    ls.add_argument("--open", action="store_true", help="only non-terminal")
    ls.set_defaults(func=cmd_list)

    sh = sub.add_parser("show", help="show one action")
    sh.add_argument("act_id")
    sh.set_defaults(func=cmd_show)

    ck = sub.add_parser("check", help="verify ledger invariants (exit 1 on violation)")
    ck.set_defaults(func=cmd_check)

    mt = sub.add_parser("metrics", help="closure/latency metrics from ledger lineage")
    mt.add_argument("--json", action="store_true")
    mt.add_argument("--out", help="also write JSON projection to this path")
    mt.add_argument("--stale-hours", type=float, default=168.0)
    mt.set_defaults(func=cmd_metrics)

    return p


def main():
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
