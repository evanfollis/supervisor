#!/usr/bin/env python3
"""Per-project metrics rollup.

Reads Claude (`~/.claude/projects/*/*.jsonl`) and Codex (`~/.codex/sessions/**/*.jsonl`)
session transcripts, attributes each session to a project via its cwd, and
aggregates three metrics per project:

  - threads      : number of distinct sessions in the window
  - compute_ms   : wall-clock time during which the agent was actively
                   processing (summed per-turn durations, not session span)
  - tokens       : total input + output tokens (cache-creation + cache-read
                   counted under input; reasoning tokens counted under output)

"Thread" counting matches the user's framing: one session (one JSONL file)
= one thread, regardless of subagent fan-out. Multiple independent tasks
dispatched to the same PM that spawn separate sessions count separately.

Project attribution comes from session cwd:
  /opt/workspace                          -> admin
  /opt/workspace/supervisor               -> admin
  /opt/workspace/projects/<name>          -> <name>
  /opt/workspace/projects/career-os/<x>   -> x  (mentor, recruiter)
  /opt/workspace/projects/skillfoundry/*  -> skillfoundry
  /opt/workspace/projects/context-*       -> context-repo
  /opt/projects/*                         -> same mapping (legacy symlinks)
  unmapped                                -> admin (default fallback)

Output: JSON at /opt/workspace/runtime/.metrics/<window>.json and a LATEST
pointer. Windows: today (UTC), 24h, 7d, all-time.

Usage: metrics-rollup.py [--window today|24h|7d|all] [--out <dir>]
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterator

# -- Project attribution ---------------------------------------------------

def project_for_cwd(cwd: str | None) -> str:
    if not cwd:
        return "admin"
    c = cwd.rstrip("/")
    # Legacy supervisor path maps to admin, not a project.
    if c == "/opt/projects/supervisor" or c.startswith("/opt/projects/supervisor/"):
        return "admin"
    # Normalize other legacy /opt/projects paths to /opt/workspace/projects.
    if c.startswith("/opt/projects/"):
        c = c.replace("/opt/projects/", "/opt/workspace/projects/", 1)
    if c == "/opt/workspace" or c.startswith("/opt/workspace/supervisor") or c == "/root" or c.startswith("/root/"):
        return "admin"
    if c == "/opt/projects":
        return "admin"
    if c.startswith("/opt/workspace/runtime"):
        return "admin"
    if c.startswith("/opt/workspace/projects/career-os/mentor"):
        return "mentor"
    if c.startswith("/opt/workspace/projects/career-os/recruiter"):
        return "recruiter"
    if c.startswith("/opt/workspace/projects/skillfoundry"):
        return "skillfoundry"
    if c.startswith("/opt/workspace/projects/context-repository"):
        return "context-repo"
    if c.startswith("/opt/workspace/projects/command"):
        return "command"
    if c.startswith("/opt/workspace/projects/atlas"):
        return "atlas"
    # Fallback: take the first path component after /opt/workspace/projects/.
    prefix = "/opt/workspace/projects/"
    if c.startswith(prefix):
        rest = c[len(prefix):].split("/", 1)[0]
        return rest or "admin"
    return "admin"


# -- Timestamp parsing -----------------------------------------------------

def parse_ts(raw: str | None) -> datetime | None:
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except Exception:
        return None


# -- Claude JSONL extraction -----------------------------------------------

def project_from_claude_dir(dir_name: str) -> str:
    """Attribute a Claude project dir to a workspace project.

    Claude's encoding (slashes -> hyphens) is lossy: '/a/b-c' collides with
    '/a-b-c' as both encode to '-a-b-c'. Hard-code known directories rather
    than round-trip decode.
    """
    mapping = {
        "-opt-workspace": "admin",
        "-opt-workspace-supervisor": "admin",
        "-root": "admin",
        "-opt-projects": "admin",
        "-opt-workspace-projects-command": "command",
        "-opt-projects-command": "command",
        "-opt-workspace-projects-atlas": "atlas",
        "-opt-projects-atlas": "atlas",
        "-opt-workspace-projects-context-repository": "context-repo",
        "-opt-projects-context-repository": "context-repo",
        "-opt-workspace-projects-career-os-mentor": "mentor",
        "-opt-projects-mentor": "mentor",
        "-opt-workspace-projects-career-os-recruiter": "recruiter",
        "-opt-projects-recruiter": "recruiter",
        "-opt-workspace-projects-skillfoundry-skillfoundry-harness": "skillfoundry",
        "-opt-projects-skillfoundry-skillfoundry-harness": "skillfoundry",
        "-opt-workspace-projects-skillfoundry-skillfoundry-valuation-context": "skillfoundry",
        "-opt-workspace-projects-skillfoundry": "skillfoundry",
    }
    return mapping.get(dir_name, "admin")


@dataclass
class SessionSummary:
    project: str
    source: str                 # "claude" or "codex"
    session_id: str
    first_ts: datetime | None = None
    last_ts: datetime | None = None
    compute_ms: int = 0          # sum of per-turn durations
    input_tokens: int = 0        # includes cache_creation + cache_read
    output_tokens: int = 0       # includes reasoning tokens for Codex
    turn_count: int = 0


def extract_claude_session(path: Path) -> SessionSummary | None:
    project = project_from_claude_dir(path.parent.name)
    summary = SessionSummary(project=project, source="claude", session_id=path.stem)
    prior_ts: datetime | None = None
    try:
        with path.open("r", encoding="utf-8", errors="replace") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                except Exception:
                    continue
                ts = parse_ts(entry.get("timestamp"))
                if ts:
                    if summary.first_ts is None or ts < summary.first_ts:
                        summary.first_ts = ts
                    if summary.last_ts is None or ts > summary.last_ts:
                        summary.last_ts = ts
                msg = entry.get("message")
                if isinstance(msg, dict) and msg.get("role") == "assistant":
                    # A turn completed. Attribute compute window from prior entry ts.
                    if prior_ts and ts:
                        delta = int((ts - prior_ts).total_seconds() * 1000)
                        if 0 < delta < 30 * 60 * 1000:  # cap 30min to ignore idle gaps
                            summary.compute_ms += delta
                    summary.turn_count += 1
                    usage = msg.get("usage") or {}
                    if isinstance(usage, dict):
                        summary.input_tokens += int(usage.get("input_tokens") or 0)
                        summary.input_tokens += int(usage.get("cache_creation_input_tokens") or 0)
                        summary.input_tokens += int(usage.get("cache_read_input_tokens") or 0)
                        summary.output_tokens += int(usage.get("output_tokens") or 0)
                if ts:
                    prior_ts = ts
    except FileNotFoundError:
        return None
    if summary.first_ts is None:
        return None
    return summary


# -- Codex JSONL extraction -----------------------------------------------

def extract_codex_session(path: Path) -> SessionSummary | None:
    cwd = None
    session_id = path.stem
    prior_ts: datetime | None = None
    summary = SessionSummary(project="admin", source="codex", session_id=session_id)
    last_total_input = 0
    last_total_output = 0
    try:
        with path.open("r", encoding="utf-8", errors="replace") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    entry = json.loads(line)
                except Exception:
                    continue
                ts = parse_ts(entry.get("timestamp"))
                if ts:
                    if summary.first_ts is None or ts < summary.first_ts:
                        summary.first_ts = ts
                    if summary.last_ts is None or ts > summary.last_ts:
                        summary.last_ts = ts
                etype = entry.get("type")
                payload = entry.get("payload") or {}
                if etype == "session_meta" and isinstance(payload, dict):
                    cwd = payload.get("cwd")
                    session_id = payload.get("id") or session_id
                elif etype == "event_msg" and isinstance(payload, dict):
                    inner_type = payload.get("type")
                    if inner_type == "token_count":
                        info = payload.get("info") or {}
                        total = info.get("total_token_usage") or {}
                        # Codex reports cumulative totals; track delta per event.
                        new_input = int(total.get("input_tokens") or 0) + int(total.get("cached_input_tokens") or 0)
                        new_output = int(total.get("output_tokens") or 0) + int(total.get("reasoning_output_tokens") or 0)
                        summary.input_tokens += max(0, new_input - last_total_input)
                        summary.output_tokens += max(0, new_output - last_total_output)
                        last_total_input = new_input
                        last_total_output = new_output
                        summary.turn_count += 1
                        if prior_ts and ts:
                            delta = int((ts - prior_ts).total_seconds() * 1000)
                            if 0 < delta < 30 * 60 * 1000:
                                summary.compute_ms += delta
                if ts:
                    prior_ts = ts
    except FileNotFoundError:
        return None
    if summary.first_ts is None:
        return None
    summary.project = project_for_cwd(cwd)
    summary.session_id = session_id
    return summary


# -- Aggregation -----------------------------------------------------------

@dataclass
class ProjectRollup:
    project: str
    threads: int = 0
    compute_ms: int = 0
    input_tokens: int = 0
    output_tokens: int = 0
    by_source: dict[str, dict[str, int]] = field(default_factory=lambda: defaultdict(lambda: {"threads": 0, "compute_ms": 0, "input_tokens": 0, "output_tokens": 0}))


def window_filter(summary: SessionSummary, start: datetime | None, end: datetime | None) -> bool:
    if not summary.last_ts:
        return False
    if start and summary.last_ts < start:
        return False
    if end and summary.first_ts and summary.first_ts > end:
        return False
    return True


def aggregate(summaries: Iterator[SessionSummary], start: datetime | None, end: datetime | None) -> dict[str, ProjectRollup]:
    rollup: dict[str, ProjectRollup] = defaultdict(lambda: ProjectRollup(project=""))
    for s in summaries:
        if not window_filter(s, start, end):
            continue
        r = rollup[s.project]
        r.project = s.project
        r.threads += 1
        r.compute_ms += s.compute_ms
        r.input_tokens += s.input_tokens
        r.output_tokens += s.output_tokens
        bs = r.by_source[s.source]
        bs["threads"] += 1
        bs["compute_ms"] += s.compute_ms
        bs["input_tokens"] += s.input_tokens
        bs["output_tokens"] += s.output_tokens
    return rollup


def iter_all_sessions() -> Iterator[SessionSummary]:
    # Claude
    claude_root = Path("/root/.claude/projects")
    if claude_root.exists():
        for project_dir in claude_root.iterdir():
            if not project_dir.is_dir():
                continue
            for jsonl in project_dir.glob("*.jsonl"):
                s = extract_claude_session(jsonl)
                if s:
                    yield s
    # Codex
    codex_root = Path("/root/.codex/sessions")
    if codex_root.exists():
        for jsonl in codex_root.rglob("*.jsonl"):
            s = extract_codex_session(jsonl)
            if s:
                yield s


# -- Main ------------------------------------------------------------------

def window_bounds(window: str) -> tuple[datetime | None, datetime | None]:
    now = datetime.now(timezone.utc)
    if window == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return start, now
    if window == "1h":
        return now - timedelta(hours=1), now
    if window == "24h":
        return now - timedelta(hours=24), now
    if window == "7d":
        return now - timedelta(days=7), now
    if window == "30d":
        return now - timedelta(days=30), now
    if window == "all":
        return None, None
    raise SystemExit(f"unknown window: {window}")


def compute_downtime_ms(rollup: dict[str, ProjectRollup], start: datetime | None, end: datetime | None) -> dict[str, int]:
    if not start or not end:
        return {p: 0 for p in rollup}
    window_ms = int((end - start).total_seconds() * 1000)
    return {p: max(0, window_ms - r.compute_ms) for p, r in rollup.items()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--window", default="today", choices=["1h", "today", "24h", "7d", "30d", "all"])
    ap.add_argument("--out", default="/opt/workspace/runtime/.metrics")
    ap.add_argument("--print", action="store_true", help="print summary to stdout")
    args = ap.parse_args()

    start, end = window_bounds(args.window)
    sessions = list(iter_all_sessions())
    rollup = aggregate(iter(sessions), start, end)
    downtime = compute_downtime_ms(rollup, start, end)

    doc = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "window": args.window,
        "window_start": start.isoformat() if start else None,
        "window_end": end.isoformat() if end else None,
        "projects": {
            p: {
                "threads": r.threads,
                "compute_ms": r.compute_ms,
                "compute_minutes": round(r.compute_ms / 60000, 2),
                "downtime_ms": downtime.get(p, 0),
                "downtime_minutes": round(downtime.get(p, 0) / 60000, 2),
                "input_tokens": r.input_tokens,
                "output_tokens": r.output_tokens,
                "total_tokens": r.input_tokens + r.output_tokens,
                "by_source": dict(r.by_source),
            }
            for p, r in sorted(rollup.items(), key=lambda kv: -kv[1].compute_ms)
        },
    }

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{args.window}.json"
    out_path.write_text(json.dumps(doc, indent=2))
    latest = out_dir / "LATEST.json"
    latest.write_text(json.dumps(doc, indent=2))

    if args.print:
        print(f"Window: {args.window}  ({start.isoformat() if start else 'beginning'} .. {end.isoformat() if end else 'now'})")
        for p, data in doc["projects"].items():
            print(f"  {p:14}  threads={data['threads']:<4}  compute={data['compute_minutes']:>7.2f}m  down={data['downtime_minutes']:>7.2f}m  in={data['input_tokens']:>10}  out={data['output_tokens']:>8}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
