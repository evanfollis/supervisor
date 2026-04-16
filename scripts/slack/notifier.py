#!/usr/bin/env python3
"""
Slack notifier — Stage 1 scaffold.

Reads existing workspace artifacts and posts status cards to Slack.
See decisions/0011-slack-mobile-io-surface.md and
docs/slack-signal-intake-and-policy-automation-plan.md.

Run modes:
  --once         scan sources, post what's new, exit (systemd timer uses this)
  --daemon       scan in a loop (N seconds, for interactive/dev use)
  --dry-run      log what WOULD be posted; no Slack API calls

The notifier is the only writer to Slack. Agents never call this directly.
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Iterator


# ---------- paths + config ----------

SUPERVISOR_ROOT = Path(os.environ.get("SUPERVISOR_ROOT", "/opt/workspace/supervisor"))
RUNTIME_ROOT = Path(os.environ.get("RUNTIME_ROOT", "/opt/workspace/runtime"))
META_DIR = RUNTIME_ROOT / ".meta"
TELEMETRY_DIR = RUNTIME_ROOT / ".telemetry"

STATE_FILE = RUNTIME_ROOT / ".slack-state.json"
HEARTBEAT_FILE = RUNTIME_ROOT / ".slack-notifier-heartbeat"
OUTBOUND_LOG = TELEMETRY_DIR / "slack-outbound.jsonl"

CHANNEL_SUPERVISOR = os.environ.get("SLACK_CHANNEL_SUPERVISOR", "#supervisor-loop")
CHANNEL_OPS = os.environ.get("SLACK_CHANNEL_OPS", "#workspace-ops")
SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN", "")


# ---------- event model ----------


@dataclass
class Card:
    """A status card to post to Slack."""
    channel: str
    glyph: str          # e.g. ":large_green_circle:"
    headline: str       # 6-10 words, plain English, no paths
    summary: str        # 1-2 sentences
    action_hint: str = ""
    thread: dict = field(default_factory=dict)   # artifact_path, runtime, event_ref, extras
    dedupe_key: str = ""   # source-unique key used to avoid reposting


# ---------- state / checkpoint ----------


def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except json.JSONDecodeError:
            return {}
    return {}


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = STATE_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2, sort_keys=True))
    tmp.replace(STATE_FILE)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


# ---------- sources ----------
#
# Each source yields Card objects the notifier has not yet posted. Sources are
# responsible for their own checkpointing via the shared state dict.


def source_supervisor_events(state: dict) -> Iterator[Card]:
    path = SUPERVISOR_ROOT / "events" / "supervisor-events.jsonl"
    if not path.exists():
        return
    key = "supervisor_events_offset"
    offset = state.get(key, 0)
    with path.open("rb") as fh:
        fh.seek(offset)
        while True:
            line = fh.readline()
            if not line:
                state[key] = fh.tell()
                return
            try:
                ev = json.loads(line.decode("utf-8"))
            except json.JSONDecodeError:
                continue
            card = card_for_supervisor_event(ev)
            if card is not None:
                yield card


def card_for_supervisor_event(ev: dict) -> Card | None:
    t = ev.get("type", "")
    ref = ev.get("ref", "")
    note = ev.get("note", "")
    agent = ev.get("agent", "unknown")
    # Events that are too noisy to post individually
    routine_types = {
        "handoff_received", "synthesis_reviewed",
        "project_tick_started",  # fire-and-forget; only report on outcome
    }
    if t in routine_types:
        return None

    glyph_by_type = {
        "decision_recorded":       ":memo:",
        "idea_logged":             ":bulb:",
        "idea_updated":            ":bulb:",
        "escalated":               ":red_circle:",
        "delegated":               ":arrow_right:",
        "feature_opened":          ":sparkles:",
        "feature_closed":          ":white_check_mark:",
        "project_tick_succeeded":  ":large_green_circle:",
        "project_tick_failed":     ":orange_circle:",
        "project_tick_escalated":  ":red_circle:",
    }
    glyph = glyph_by_type.get(t, ":information_source:")

    headlines = {
        "decision_recorded":       "New ADR recorded",
        "idea_logged":             "New idea in ledger",
        "idea_updated":            "Idea ledger updated",
        "escalated":               "Supervisor escalation raised",
        "delegated":               "Supervisor delegated work",
        "feature_opened":          "Feature session opened",
        "feature_closed":          "Feature session closed",
        "project_tick_succeeded":  f"Project tick done: {agent}",
        "project_tick_failed":     f"Project tick FAILED: {agent}",
        "project_tick_escalated":  f"Project tick needs human input: {agent}",
    }
    headline = headlines.get(t, f"Supervisor event: {t}")
    summary = note or "(no note)"

    # Route: escalations → #supervisor-loop (principal-facing);
    # project tick outcomes → #workspace-ops; everything else → #supervisor-loop.
    if t in {"project_tick_succeeded", "project_tick_failed"}:
        channel = CHANNEL_OPS
    elif t == "project_tick_escalated":
        channel = CHANNEL_SUPERVISOR
    else:
        channel = CHANNEL_SUPERVISOR

    return Card(
        channel=channel,
        glyph=glyph,
        headline=headline,
        summary=summary,
        thread={"artifact": ref, "runtime": agent, "event_type": t, "ts": ev.get("ts", "")},
        dedupe_key=f"supervisor_event:{ev.get('ts','')}:{t}:{ref}",
    )


def source_latest_synthesis(state: dict) -> Iterator[Card]:
    pointer = META_DIR / "LATEST_SYNTHESIS"
    if not pointer.exists():
        return
    target = pointer.read_text().strip()
    if not target:
        return
    key = "latest_synthesis_target"
    if state.get(key) == target:
        return
    state[key] = target
    filename = Path(target).name
    yield Card(
        channel=CHANNEL_SUPERVISOR,
        glyph=":brain:",
        headline="New cross-cutting synthesis landed",
        summary=f"A workspace-wide synthesis pass just wrote {filename}. Worth a supervisor read.",
        action_hint="Reply `status:` for liveness.",
        thread={"artifact": target, "runtime": "system", "event_type": "synthesis_ready"},
        dedupe_key=f"synthesis:{target}",
    )


def source_new_adrs(state: dict) -> Iterator[Card]:
    adr_dir = SUPERVISOR_ROOT / "decisions"
    if not adr_dir.exists():
        return
    seen = set(state.get("adrs_seen", []))
    current = {
        p.name
        for pattern in ("ADR-*.md", "0*.md")
        for p in adr_dir.glob(pattern)
    }
    new = sorted(current - seen)
    for name in new:
        path = adr_dir / name
        title = name
        try:
            with path.open() as fh:
                first = fh.readline().strip().lstrip("# ").strip()
                if first:
                    title = first
        except OSError:
            pass
        yield Card(
            channel=CHANNEL_SUPERVISOR,
            glyph=":memo:",
            headline="New ADR added",
            summary=title,
            thread={"artifact": str(path), "runtime": "system", "event_type": "adr_added"},
            dedupe_key=f"adr:{name}",
        )
    state["adrs_seen"] = sorted(current)


def source_health_status(state: dict) -> Iterator[Card]:
    health = RUNTIME_ROOT / ".health-status.txt"
    if not health.exists():
        return
    content = health.read_text(errors="replace").strip()
    digest = f"{len(content)}:{content[:200]}"
    if state.get("health_digest") == digest:
        return
    state["health_digest"] = digest
    first_line = content.splitlines()[0] if content else "(empty)"
    degraded = any(marker in content.lower() for marker in ("fail", "degrad", "error", "critical"))
    yield Card(
        channel=CHANNEL_OPS,
        glyph=":red_circle:" if degraded else ":large_green_circle:",
        headline="Host health updated" if not degraded else "Host health degraded",
        summary=first_line[:200],
        thread={"artifact": str(health), "runtime": "system", "event_type": "health_update"},
        dedupe_key=f"health:{digest}",
    )


SOURCES: list[tuple[str, Callable[[dict], Iterator[Card]]]] = [
    ("supervisor_events", source_supervisor_events),
    ("latest_synthesis", source_latest_synthesis),
    ("new_adrs", source_new_adrs),
    ("health_status", source_health_status),
]


# ---------- slack client ----------


def slack_post(channel: str, text: str, blocks: list | None = None) -> dict:
    """Live post to Slack via chat.postMessage. Raises on non-2xx/ok=false."""
    if not SLACK_BOT_TOKEN:
        raise RuntimeError("SLACK_BOT_TOKEN not set")
    payload = {"channel": channel, "text": text}
    if blocks is not None:
        payload["blocks"] = blocks
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://slack.com/api/chat.postMessage",
        data=data,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
        },
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        body = json.loads(resp.read())
    if not body.get("ok"):
        raise RuntimeError(f"slack error: {body.get('error')}")
    return body


def slack_post_thread(channel: str, thread_ts: str, text: str) -> None:
    payload = {"channel": channel, "thread_ts": thread_ts, "text": text}
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://slack.com/api/chat.postMessage",
        data=data,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
        },
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        json.loads(resp.read())


# ---------- post pipeline ----------


def card_to_text(card: Card) -> str:
    parts = [f"{card.glyph} *{card.headline}*", card.summary]
    if card.action_hint:
        parts.append(f"_{card.action_hint}_")
    return "\n".join(parts)


def card_thread_text(card: Card) -> str:
    fields = []
    for key in ("artifact", "runtime", "event_type", "ts"):
        value = card.thread.get(key)
        if value:
            fields.append(f"{key}: `{value}`")
    return "\n".join(fields) if fields else "(no refs)"


def append_outbound(entry: dict) -> None:
    OUTBOUND_LOG.parent.mkdir(parents=True, exist_ok=True)
    with OUTBOUND_LOG.open("a") as fh:
        fh.write(json.dumps(entry, sort_keys=True) + "\n")


def post_card(card: Card, dry_run: bool) -> dict:
    entry = {
        "ts": now_iso(),
        "channel": card.channel,
        "glyph": card.glyph,
        "headline": card.headline,
        "summary": card.summary,
        "action_hint": card.action_hint,
        "thread": card.thread,
        "dedupe_key": card.dedupe_key,
        "mode": "dry_run" if dry_run else "live",
    }
    if dry_run:
        entry["posted"] = False
        append_outbound(entry)
        return entry
    try:
        resp = slack_post(card.channel, card_to_text(card))
        entry["posted"] = True
        entry["channel_id"] = resp.get("channel")
        entry["message_ts"] = resp.get("ts")
        thread_text = card_thread_text(card)
        if thread_text and resp.get("ts"):
            try:
                slack_post_thread(resp["channel"], resp["ts"], thread_text)
                entry["thread_posted"] = True
            except (urllib.error.URLError, RuntimeError) as exc:
                entry["thread_error"] = str(exc)
    except (urllib.error.URLError, RuntimeError) as exc:
        entry["posted"] = False
        entry["error"] = str(exc)
    append_outbound(entry)
    return entry


# ---------- heartbeat ----------


def write_heartbeat(state: dict, last_error: str | None = None) -> None:
    HEARTBEAT_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "ts": now_iso(),
        "last_error": last_error,
        "sources": sorted({name for name, _ in SOURCES}),
        "state_keys": sorted(state.keys()),
    }
    tmp = HEARTBEAT_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True))
    tmp.replace(HEARTBEAT_FILE)


# ---------- main ----------


def run_once(dry_run: bool) -> int:
    state = load_state()
    posted = 0
    errored = 0
    last_error = None
    already_posted = set(state.get("dedupe_keys", []))

    for name, fn in SOURCES:
        try:
            for card in fn(state):
                if card.dedupe_key and card.dedupe_key in already_posted:
                    continue
                entry = post_card(card, dry_run)
                if entry.get("posted") or dry_run:
                    posted += 1
                    if card.dedupe_key:
                        already_posted.add(card.dedupe_key)
                else:
                    errored += 1
                    last_error = entry.get("error")
        except Exception as exc:  # noqa: BLE001 -- source failures must not crash the loop
            errored += 1
            last_error = f"source {name}: {exc}"
            print(f"source {name} failed: {exc}", file=sys.stderr)

    state["dedupe_keys"] = sorted(already_posted)[-5000:]
    save_state(state)
    write_heartbeat(state, last_error)
    print(f"notifier: posted={posted} errored={errored} dry_run={dry_run}")
    return 0 if errored == 0 else 2


def run_daemon(interval: int, dry_run: bool) -> int:
    while True:
        run_once(dry_run)
        time.sleep(interval)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--once", action="store_true", help="single pass, exit")
    mode.add_argument("--daemon", action="store_true", help="continuous loop")
    parser.add_argument("--interval", type=int, default=60, help="daemon sleep seconds")
    parser.add_argument("--dry-run", action="store_true", help="log only, no Slack API")
    args = parser.parse_args(argv)

    if not args.dry_run and not SLACK_BOT_TOKEN:
        print("SLACK_BOT_TOKEN unset and --dry-run not passed; refusing to run live.", file=sys.stderr)
        return 3

    if args.once:
        return run_once(args.dry_run)
    return run_daemon(args.interval, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
