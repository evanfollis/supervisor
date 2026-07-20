#!/usr/bin/env python3
"""Write model-state provenance for one reflection window.

The reflection text is an interpretation. This sidecar records which model
states generated the indexed assistant messages it could inspect, plus the
model state of the reflector itself. Failure to produce this derivative index
must never block the reflection artifact or the object-level pipeline.
"""

from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path


def parse_ts(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError):
        return None


def cwd_aliases(project_dir: str) -> set[str]:
    norm = os.path.normpath(project_dir)
    aliases = {norm}
    if norm.startswith("/opt/workspace/projects/"):
        aliases.add(norm.replace("/opt/workspace/projects/", "/opt/projects/", 1))
    return aliases


def build_manifest(
    trace_file: Path,
    project_dir: str,
    hours: int,
    reflector_provider: str,
    reflector_model: str,
    reflector_effort: str,
    reflector_invocation_manifest: str = "",
    now: datetime | None = None,
) -> dict:
    now = now or datetime.now(timezone.utc)
    start = now - timedelta(hours=hours)
    aliases = cwd_aliases(project_dir)
    groups: dict[tuple[str, str, str], dict] = defaultdict(
        lambda: {"message_count": 0, "first_ts": None, "last_ts": None, "trace_refs": []}
    )
    source_messages = 0
    unknown_model_messages = 0
    synthetic_model_messages = 0

    if trace_file.exists():
        with trace_file.open(encoding="utf-8") as fh:
            for line in fh:
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if event.get("actor") != "assistant" or os.path.normpath(event.get("cwd") or "") not in aliases:
                    continue
                ts = parse_ts(event.get("ts"))
                if ts is None or ts < start or ts > now:
                    continue
                source_messages += 1
                model = event.get("model")
                if not model:
                    unknown_model_messages += 1
                    continue
                if str(model).startswith("<"):
                    synthetic_model_messages += 1
                    continue
                key = (
                    event.get("model_provider") or "unknown",
                    model,
                    event.get("reasoning_effort") or "unknown",
                )
                group = groups[key]
                group["message_count"] += 1
                stamp = ts.isoformat().replace("+00:00", "Z")
                group["first_ts"] = min(group["first_ts"] or stamp, stamp)
                group["last_ts"] = max(group["last_ts"] or stamp, stamp)
                ref = event.get("trace_ref")
                if ref and len(group["trace_refs"]) < 5:
                    group["trace_refs"].append(ref)

    models = []
    for (provider, model, effort), data in sorted(groups.items()):
        models.append({
            "provider": provider,
            "model": model,
            "reasoning_effort": effort,
            **data,
        })

    return {
        "schema_version": 1,
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        "window": {
            "start": start.isoformat().replace("+00:00", "Z"),
            "end": now.isoformat().replace("+00:00", "Z"),
            "hours": hours,
        },
        "subject": {"project_dir": os.path.normpath(project_dir), "trace_file": str(trace_file)},
        "reflector": {
            "provider": reflector_provider,
            "model": reflector_model,
            "reasoning_effort": reflector_effort,
            "invocation_manifest": reflector_invocation_manifest,
        },
        "source_assistant_message_count": source_messages,
        "unknown_model_message_count": unknown_model_messages,
        "synthetic_model_message_count": synthetic_model_messages,
        "source_models": models,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trace-file", type=Path, required=True)
    parser.add_argument("--project-dir", required=True)
    parser.add_argument("--hours", type=int, default=12)
    parser.add_argument("--reflector-provider", required=True)
    parser.add_argument("--reflector-model", required=True)
    parser.add_argument("--reflector-effort", required=True)
    parser.add_argument("--reflector-invocation-manifest", default="")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    manifest = build_manifest(
        args.trace_file,
        args.project_dir,
        args.hours,
        args.reflector_provider,
        args.reflector_model,
        args.reflector_effort,
        args.reflector_invocation_manifest,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    tmp = args.output.with_suffix(args.output.suffix + ".tmp")
    tmp.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
