#!/usr/bin/env python3

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ACTIVE_STATUSES = ["captured", "framed", "pressure_tested", "sandboxed", "deferred"]
CLOSED_STATUSES = ["adopted", "rejected"]
PRIORITY_SCORES = {"low": 0, "medium": 2, "high": 4}
COMPOUND_SCORES = {"low": 0, "medium": 2, "high": 4}
RISK_PENALTY = {"low": 0, "medium": -1, "high": -2}
STATUS_SCORES = {
    "captured": 2,
    "framed": 3,
    "pressure_tested": 4,
    "sandboxed": 3,
    "deferred": 1,
    "adopted": 0,
    "rejected": 0,
}


def now():
    return datetime.now(timezone.utc)


def parse_ts(value):
    if not value:
        return None
    value = value.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(value)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def load_ideas(ideas_dir: Path):
    ideas = []
    for path in sorted(ideas_dir.glob("IDEA-*.json")):
        try:
            payload = json.loads(path.read_text())
        except Exception:
            continue
        payload["_path"] = str(path)
        ideas.append(payload)
    return ideas


def score_idea(idea, ref_now):
    score = 0
    score += STATUS_SCORES.get(idea.get("status"), 0)
    score += PRIORITY_SCORES.get(idea.get("priority", "medium"), 2)
    score += COMPOUND_SCORES.get(idea.get("compoundability", "medium"), 2)
    score += RISK_PENALTY.get(idea.get("risk", "medium"), -1)

    updated = parse_ts(idea.get("updated_at"))
    if updated:
        days_stale = (ref_now - updated).days
        if days_stale >= 7:
            score += 2
        elif days_stale >= 3:
            score += 1

    review_after = parse_ts(idea.get("review_after"))
    due = False
    if review_after and review_after <= ref_now:
        score += 3
        due = True

    if idea.get("scope") == "governance":
        score += 1
    if idea.get("target_layer") == "supervisor":
        score += 1

    return score, due


def one_line(text, limit=120):
    text = " ".join((text or "").split())
    return text[:limit]


def write_markdown(path: Path, ideas, ref_now):
    active = []
    closed = []
    for idea in ideas:
        score, due = score_idea(idea, ref_now)
        item = dict(idea)
        item["_score"] = score
        item["_due"] = due
        if idea.get("status") in ACTIVE_STATUSES:
            active.append(item)
        elif idea.get("status") in CLOSED_STATUSES:
            closed.append(item)

    active.sort(key=lambda x: (x["_due"], x["_score"], x.get("updated_at", "")), reverse=True)
    closed.sort(key=lambda x: x.get("updated_at", ""), reverse=True)

    status_counts = Counter(idea.get("status", "unknown") for idea in ideas)
    lines = []
    lines.append(f"# Idea focus — {ref_now.replace(microsecond=0).isoformat().replace('+00:00', 'Z')}")
    lines.append("")
    lines.append("## Summary")
    lines.append(f"- Active ideas: {len(active)}")
    lines.append(f"- Due for review now: {sum(1 for item in active if item['_due'])}")
    lines.append(f"- Closed ideas tracked: {len(closed)}")
    lines.append(f"- Status counts: {dict(status_counts)}")
    lines.append("")

    lines.append("## Immediate attention")
    immediate = [item for item in active if item["_due"]][:5] or active[:5]
    if not immediate:
        lines.append("- None")
    else:
        for item in immediate:
            lines.append(
                f"- {item['id']} [{item.get('status')}] score={item['_score']} "
                f"priority={item.get('priority','medium')} compoundability={item.get('compoundability','medium')} "
                f"risk={item.get('risk','medium')} — {item.get('title')}"
            )
            lines.append(f"  next: {one_line(item.get('next_step','')) or 'unset'}")
            lines.append(f"  why: {one_line(item.get('summary',''))}")
            lines.append(f"  ref: {item['_path']}")
    lines.append("")

    lines.append("## Active queue")
    if not active:
        lines.append("- None")
    else:
        for item in active[:12]:
            lines.append(
                f"- {item['id']} [{item.get('status')}] score={item['_score']} "
                f"{item.get('title')} | next: {one_line(item.get('next_step','')) or 'unset'}"
            )
    lines.append("")

    lines.append("## Recently closed")
    if not closed:
        lines.append("- None")
    else:
        for item in closed[:8]:
            lines.append(
                f"- {item['id']} [{item.get('status')}] {item.get('title')} | "
                f"updated: {item.get('updated_at','unknown')}"
            )
    lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def write_json(path: Path, ideas, ref_now):
    active = []
    for idea in ideas:
        score, due = score_idea(idea, ref_now)
        item = dict(idea)
        item["score"] = score
        item["due_now"] = due
        if item.get("status") in ACTIVE_STATUSES:
            active.append(item)
    active.sort(key=lambda x: (x["due_now"], x["score"], x.get("updated_at", "")), reverse=True)
    payload = {
        "generated_at": ref_now.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "active_count": len(active),
        "top_active": active[:12],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ideas-dir", required=True)
    parser.add_argument("--meta-dir", required=True)
    parser.add_argument("--latest-pointer", required=True)
    args = parser.parse_args()

    ref_now = now()
    ideas = load_ideas(Path(args.ideas_dir))
    stamp = ref_now.strftime("%Y-%m-%dT%H-%M-%SZ")
    meta_dir = Path(args.meta_dir)
    md_path = meta_dir / f"idea-focus-{stamp}.md"
    json_path = meta_dir / f"idea-focus-{stamp}.json"
    write_markdown(md_path, ideas, ref_now)
    write_json(json_path, ideas, ref_now)
    Path(args.latest_pointer).write_text(str(md_path) + "\n")
    print(str(md_path))


if __name__ == "__main__":
    main()
