"""Golden sets: provenance-labeled cases, lifecycle, freshness, flywheel.

File layout inside <spec-dir>/golden/:
  cases.jsonl      — active / smoke / retired cases (the working set)
  holdout.jsonl    — SEALED holdout cases, kept in a separate file so that
                     iteration/optimization workflows reading the working
                     set never even load them. Sealing is honor-system for
                     agents plus tripwires (contamination scan, release-only
                     execution, golden-hash in baseline) — a repo-local
                     store cannot cryptographically hide data from its own
                     operators, and the ADR says so explicitly.
  candidates.jsonl — captured production interactions awaiting curation

Case shape (one per line):
{
  "id": "gc-<hash>",              # minted from input by core.case_id
  "input": {...},                  # variables the executor renders
  "checks": [ {...}, ... ],        # see grading.py
  "provenance": "synthetic|production|human",
  "status": "active|candidate|holdout|smoke|retired",
  "created": "<iso>",
  "last_validated": "<iso>",       # last time a human/agent confirmed the
                                   # case still reflects reality
  "source": "<where this came from>",
  "notes": "<optional>",
  "must_pass": true                # default true; false = advisory case
}

Lifecycle:
  candidates.jsonl (captured production traffic) --promote--> active
  active --saturated--> smoke   (still run, cheap early-warning tier)
  active --stale/obsolete--> retired  (kept for history, never run)
  holdout: sealed; only `run --release` touches it (ADR-0039 §5).
"""

from __future__ import annotations

import json
from pathlib import Path

from .core import append_jsonl, canonical, case_id, read_jsonl, utcnow_iso


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8"
    )

PROVENANCES = {"synthetic", "production", "human"}
STATUSES = {"active", "candidate", "holdout", "smoke", "retired"}
STALE_DAYS = 90


class GoldenError(Exception):
    pass


def validate_case(case: dict, path: str = "") -> list[str]:
    problems = []
    where = f"{path} case {case.get('id', '?')}"
    for key in ("id", "input", "checks", "provenance", "status", "created"):
        if key not in case:
            problems.append(f"{where}: missing '{key}'")
    if case.get("provenance") not in PROVENANCES:
        problems.append(f"{where}: bad provenance {case.get('provenance')!r}")
    if case.get("status") not in STATUSES:
        problems.append(f"{where}: bad status {case.get('status')!r}")
    if not isinstance(case.get("checks"), list) or not case.get("checks"):
        problems.append(f"{where}: checks must be a non-empty list")
    expected = case_id(case.get("input"))
    if case.get("id") and case["id"] != expected:
        problems.append(
            f"{where}: id does not match input hash ({expected}) — "
            "inputs are immutable; changed input = new case"
        )
    return problems


def load_cases(path: Path, statuses=None) -> list[dict]:
    cases = read_jsonl(path)
    if statuses is None:
        return cases
    return [c for c in cases if c.get("status") in statuses]


def load_all_cases(spec_dir: Path) -> list[dict]:
    """Working set + sealed holdouts (gate checks need both)."""
    return load_cases(spec_dir / "golden" / "cases.jsonl") + load_cases(
        spec_dir / "golden" / "holdout.jsonl"
    )


def runnable_cases(spec_dir: Path, release: bool = False) -> list[dict]:
    cases = load_cases(spec_dir / "golden" / "cases.jsonl", {"active", "smoke"})
    if release:
        cases += load_cases(spec_dir / "golden" / "holdout.jsonl", {"holdout"})
    return cases


def golden_hash(spec_dir: Path, gate_cfg: dict) -> str:
    """Hash of everything that defines what the gate measures: case ids,
    checks, statuses, must_pass, provenance, and the gate config. Stored in
    the baseline; a mismatch at check time means criteria changed since the
    last accepted run — which requires a fresh eval, so criteria weakening
    is always visible as a new run + reviewable diff, never silent.
    """
    from .core import _digest

    material = sorted(
        canonical(
            {
                "id": c.get("id"),
                "checks": c.get("checks"),
                "status": c.get("status"),
                "must_pass": c.get("must_pass", True),
                "provenance": c.get("provenance"),
            }
        )
        for c in load_all_cases(spec_dir)
        if c.get("status") != "retired"
    )
    return "gh-" + _digest({"cases": material, "gate": gate_cfg})


def new_case(
    input_obj,
    checks: list,
    provenance: str,
    source: str = "",
    status: str = "active",
    notes: str = "",
    must_pass: bool = True,
) -> dict:
    if provenance not in PROVENANCES:
        raise GoldenError(f"bad provenance {provenance!r}")
    if status not in STATUSES:
        raise GoldenError(f"bad status {status!r}")
    now = utcnow_iso()
    return {
        "id": case_id(input_obj),
        "input": input_obj,
        "checks": checks,
        "provenance": provenance,
        "status": status,
        "created": now,
        "last_validated": now,
        "source": source,
        "notes": notes,
        "must_pass": must_pass,
    }


def append_candidate(spec_dir: Path, input_obj, source: str, observed_output=None) -> dict | None:
    """Flywheel intake: record a real interaction as a candidate case.

    Dedup by input hash across candidates AND existing cases. The captured
    output is stored as reference material for whoever curates checks at
    promotion time — it is not itself a check (outputs are graded against
    criteria, not string-matched to history).
    """
    cid = case_id(input_obj)
    cand_path = spec_dir / "golden" / "candidates.jsonl"
    cases_path = spec_dir / "golden" / "cases.jsonl"
    seen = {c.get("id") for c in read_jsonl(cand_path)} | {c.get("id") for c in read_jsonl(cases_path)}
    if cid in seen:
        return None
    entry = {
        "id": cid,
        "input": input_obj,
        "observed_output": observed_output,
        "provenance": "production",
        "status": "candidate",
        "created": utcnow_iso(),
        "source": source,
    }
    append_jsonl(cand_path, entry)
    return entry


def promote(spec_dir: Path, case_ids: list[str], checks_by_id: dict) -> list[dict]:
    """Move curated candidates into cases.jsonl as active production cases.

    Promotion is deliberate: the curator supplies checks per case (criteria,
    not copied outputs). Promoted candidates are removed from the pool.
    """
    cand_path = spec_dir / "golden" / "candidates.jsonl"
    cases_path = spec_dir / "golden" / "cases.jsonl"
    candidates = read_jsonl(cand_path)
    by_id = {c["id"]: c for c in candidates}
    promoted = []
    for cid in case_ids:
        if cid not in by_id:
            raise GoldenError(f"candidate {cid} not found in {cand_path}")
        if cid not in checks_by_id:
            raise GoldenError(f"no checks supplied for {cid} — promotion requires criteria")
        cand = by_id[cid]
        case = new_case(
            cand["input"],
            checks_by_id[cid],
            provenance="production",
            source=cand.get("source", ""),
            notes=f"promoted from candidate captured {cand.get('created', '?')}",
        )
        append_jsonl(cases_path, case)
        promoted.append(case)
    remaining = [c for c in candidates if c["id"] not in set(case_ids)]
    _write_jsonl(cand_path, remaining)
    return promoted


def set_status(spec_dir: Path, case_id_: str, status: str) -> dict:
    """Change a case's status, moving it between cases.jsonl and the sealed
    holdout.jsonl when the transition crosses that boundary."""
    if status not in STATUSES:
        raise GoldenError(f"bad status {status!r}")
    cases_path = spec_dir / "golden" / "cases.jsonl"
    holdout_path = spec_dir / "golden" / "holdout.jsonl"
    working, holdouts = read_jsonl(cases_path), read_jsonl(holdout_path)
    hit = None
    for c in working + holdouts:
        if c["id"] == case_id_:
            c["status"] = status
            hit = c
    if hit is None:
        raise GoldenError(f"case {case_id_} not found under {spec_dir}/golden/")
    merged = working + holdouts
    _write_jsonl(cases_path, [c for c in merged if c["status"] != "holdout"])
    new_holdouts = [c for c in merged if c["status"] == "holdout"]
    if new_holdouts or holdout_path.exists():
        _write_jsonl(holdout_path, new_holdouts)
    return hit


def _age_days(iso: str | None, now) -> int | None:
    from datetime import datetime, timezone

    try:
        return (now - datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)).days
    except (TypeError, ValueError):
        return None


def health(spec_dir: Path, baseline: dict | None) -> dict:
    """Freshness/saturation/provenance/backlog report for one golden set.

    Candidate backlog is first-class (adversarial review 2026-07-12,
    finding 9): a flywheel that captures but never promotes is a stalled
    flywheel, and that must surface with the same weight as staleness.
    """
    from datetime import datetime, timezone

    cases = load_all_cases(spec_dir)
    candidates = read_jsonl(spec_dir / "golden" / "candidates.jsonl")
    now = datetime.now(timezone.utc)
    active = [c for c in cases if c["status"] in ("active", "smoke", "holdout")]
    stale = []
    for c in active:
        age = _age_days(c.get("last_validated") or c.get("created"), now)
        if age is None or age > STALE_DAYS:
            stale.append({"id": c["id"], "age_days": age})
    prov = {p: sum(1 for c in active if c.get("provenance") == p) for p in PROVENANCES}
    total = max(1, len(active))
    saturation_streak = (baseline or {}).get("all_pass_streak", 0)
    cand_ages = [a for a in (_age_days(c.get("created"), now) for c in candidates)
                 if a is not None]
    return {
        "cases_total": len(cases),
        "cases_active": len(active),
        "provenance": prov,
        "production_ratio": round(prov.get("production", 0) / total, 3),
        "stale_cases": stale,
        "all_pass_streak": saturation_streak,
        "saturated": saturation_streak >= 5,
        "candidate_backlog": len(candidates),
        "candidate_oldest_days": max(cand_ages) if cand_ages else 0,
    }
