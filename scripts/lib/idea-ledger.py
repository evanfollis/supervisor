#!/usr/bin/env python3

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


VALID_STATUSES = [
    "captured",
    "framed",
    "pressure_tested",
    "adopted",
    "sandboxed",
    "deferred",
    "rejected",
]

VALID_LEVELS = ["low", "medium", "high"]


def now_iso():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug or "idea"


def load_json(path: Path):
    with path.open() as fh:
        return json.load(fh)


def save_json(path: Path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w") as fh:
        json.dump(payload, fh, indent=2, sort_keys=True)
        fh.write("\n")
    tmp.replace(path)


def append_event(events_file: Path, event_type: str, ref: str, note: str):
    events_file.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "ts": now_iso(),
        "agent": os.environ.get("WORKSPACE_AGENT", "unknown"),
        "type": event_type,
        "ref": ref,
        "note": note[:120],
    }
    with events_file.open("a") as fh:
        fh.write(json.dumps(payload, sort_keys=True) + "\n")


def next_id(ideas_dir: Path) -> str:
    max_n = 0
    for path in ideas_dir.glob("IDEA-*.json"):
        match = re.match(r"IDEA-(\d{4})-", path.name)
        if match:
            max_n = max(max_n, int(match.group(1)))
    return f"IDEA-{max_n + 1:04d}"


def find_idea_path(ideas_dir: Path, idea_id: str) -> Path:
    matches = sorted(ideas_dir.glob(f"{idea_id}-*.json"))
    if not matches:
        raise SystemExit(f"idea not found: {idea_id}")
    if len(matches) > 1:
        raise SystemExit(f"ambiguous idea id: {idea_id}")
    return matches[0]


def find_by_source(ideas_dir: Path, source: str):
    for path in sorted(ideas_dir.glob("IDEA-*.json")):
        try:
            payload = load_json(path)
        except (OSError, json.JSONDecodeError):
            continue
        if payload.get("source") == source:
            return path, payload
    return None, None


def cmd_new(args):
    ideas_dir = Path(args.ideas_dir)
    ideas_dir.mkdir(parents=True, exist_ok=True)

    if args.idempotency_source:
        existing_path, existing_payload = find_by_source(ideas_dir, args.idempotency_source)
        if existing_path is not None:
            print(str(existing_path))
            return

    idea_id = next_id(ideas_dir)
    slug = slugify(args.title if args.slug is None else args.slug)
    ts = now_iso()
    payload = {
        "id": idea_id,
        "slug": slug,
        "title": args.title,
        "status": args.status,
        "summary": args.summary,
        "proposer": args.proposer,
        "scope": args.scope,
        "target_layer": args.target_layer,
        "priority": args.priority,
        "compoundability": args.compoundability,
        "risk": args.risk,
        "review_after": args.review_after,
        "created_at": ts,
        "updated_at": ts,
        "disturbs": args.disturbs or [],
        "evidence": args.evidence or [],
        "artifacts": args.artifacts or [],
        "next_step": args.next_step or "",
        "disposition_rationale": args.disposition_rationale or "",
    }
    if args.idempotency_source:
        payload["source"] = args.idempotency_source
    path = ideas_dir / f"{idea_id}-{slug}.json"
    save_json(path, payload)
    append_event(Path(args.events_file), "idea_logged", str(path), f"{idea_id} {args.status} {args.title}")
    print(str(path))


def cmd_update(args):
    ideas_dir = Path(args.ideas_dir)
    path = find_idea_path(ideas_dir, args.idea_id)
    payload = load_json(path)
    changed = False

    for field in [
        "status",
        "summary",
        "scope",
        "target_layer",
        "next_step",
        "disposition_rationale",
        "priority",
        "compoundability",
        "risk",
        "review_after",
    ]:
        value = getattr(args, field)
        if value is not None and payload.get(field) != value:
            payload[field] = value
            changed = True

    for field, additions in [("disturbs", args.add_disturbs), ("evidence", args.add_evidence), ("artifacts", args.add_artifacts)]:
        if additions:
            current = payload.setdefault(field, [])
            for item in additions:
                if item not in current:
                    current.append(item)
                    changed = True

    if args.title is not None and payload.get("title") != args.title:
        payload["title"] = args.title
        changed = True

    if args.note or changed:
        payload["updated_at"] = now_iso()
        payload.pop("history", None)
        save_json(path, payload)
        append_event(Path(args.events_file), "idea_updated", str(path), f"{payload['id']} {payload['status']} {payload['title']}")

    print(str(path))


def cmd_list(args):
    ideas_dir = Path(args.ideas_dir)
    rows = []
    for path in sorted(ideas_dir.glob("IDEA-*.json")):
        payload = load_json(path)
        if args.status and payload.get("status") != args.status:
            continue
        rows.append(payload)

    for payload in rows:
        summary = " ".join(payload.get("summary", "").split())
        print(
            f"{payload['id']}\t{payload.get('status','')}\t{payload.get('scope','')}\t"
            f"{payload.get('target_layer','')}\t{payload.get('title','')}\t{summary[:100]}"
        )


def cmd_show(args):
    path = find_idea_path(Path(args.ideas_dir), args.idea_id)
    payload = load_json(path)
    print(json.dumps(payload, indent=2, sort_keys=True))


def build_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ideas-dir", default="/opt/workspace/supervisor/ideas")
    parser.add_argument("--events-file", default="/opt/workspace/supervisor/events/supervisor-events.jsonl")
    parser.add_argument("--actor", default=os.environ.get("WORKSPACE_AGENT", "unknown"))
    sub = parser.add_subparsers(dest="command", required=True)

    new = sub.add_parser("new")
    new.add_argument("--title", required=True)
    new.add_argument("--summary", required=True)
    new.add_argument("--slug")
    new.add_argument("--status", default="captured", choices=VALID_STATUSES)
    new.add_argument("--proposer", default="human")
    new.add_argument("--scope", default="cross-project")
    new.add_argument("--target-layer", default="supervisor")
    new.add_argument("--priority", default="medium", choices=VALID_LEVELS)
    new.add_argument("--compoundability", default="medium", choices=VALID_LEVELS)
    new.add_argument("--risk", default="medium", choices=VALID_LEVELS)
    new.add_argument("--review-after")
    new.add_argument("--disturbs", action="append")
    new.add_argument("--evidence", action="append")
    new.add_argument("--artifacts", action="append")
    new.add_argument("--next-step")
    new.add_argument("--disposition-rationale")
    new.add_argument("--note")
    new.add_argument(
        "--idempotency-source",
        help=(
            "Provenance key (e.g. 'slack:C01234:1712345678.123456'). "
            "If an existing idea record has a matching 'source' field, "
            "no new record is created and the existing path is printed."
        ),
    )
    new.set_defaults(func=cmd_new)

    update = sub.add_parser("update")
    update.add_argument("idea_id")
    update.add_argument("--title")
    update.add_argument("--status", choices=VALID_STATUSES)
    update.add_argument("--summary")
    update.add_argument("--scope")
    update.add_argument("--target-layer")
    update.add_argument("--priority", choices=VALID_LEVELS)
    update.add_argument("--compoundability", choices=VALID_LEVELS)
    update.add_argument("--risk", choices=VALID_LEVELS)
    update.add_argument("--review-after")
    update.add_argument("--next-step")
    update.add_argument("--disposition-rationale")
    update.add_argument("--add-disturbs", action="append")
    update.add_argument("--add-evidence", action="append")
    update.add_argument("--add-artifacts", action="append")
    update.add_argument("--note")
    update.set_defaults(func=cmd_update)

    ls = sub.add_parser("list")
    ls.add_argument("--status", choices=VALID_STATUSES)
    ls.set_defaults(func=cmd_list)

    show = sub.add_parser("show")
    show.add_argument("idea_id")
    show.set_defaults(func=cmd_show)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
