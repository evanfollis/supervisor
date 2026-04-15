#!/usr/bin/env python3

import argparse
import glob
import json
import os
import sys
from pathlib import Path


def iso_now():
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path, default):
    if not path.exists():
        return default
    try:
        with path.open() as fh:
            return json.load(fh)
    except Exception:
        return default


def dump_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w") as fh:
        json.dump(data, fh, indent=2, sort_keys=True)
        fh.write("\n")
    tmp.replace(path)


def parse_sessions_conf(path: Path):
    registry = []
    if not path.exists():
        return registry
    with path.open() as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = [part.strip() for part in line.split("|")]
            name = parts[0]
            cwd = parts[1] if len(parts) > 1 else ""
            agent = parts[2] if len(parts) > 2 and parts[2] else "claude"
            role = parts[3] if len(parts) > 3 and parts[3] else ("supervisor" if name == "general" else "project")
            if cwd:
                registry.append(
                    {
                        "session_name": name,
                        "cwd": os.path.normpath(cwd),
                        "agent": agent,
                        "role": role,
                        "kind": "persistent",
                    }
                )
    return registry


def alias_cwds(cwd: str, workspace_root: str):
    aliases = {os.path.normpath(cwd)}
    if cwd.startswith("/opt/workspace/projects/"):
        aliases.add(os.path.normpath(cwd.replace("/opt/workspace/projects/", "/opt/projects/", 1)))
    elif cwd == "/opt/workspace/supervisor":
        aliases.add("/opt/projects/supervisor")

    if cwd == os.path.normpath(workspace_root):
        aliases.add("/opt/projects")

    return sorted(aliases)


def parse_manifest(path: Path):
    try:
        data = json.loads(path.read_text())
    except Exception:
        return None

    if "worktree" in data:
        return {
            "session_name": path.stem,
            "cwd": os.path.normpath(data["worktree"]),
            "agent": data.get("agent", "claude"),
            "role": "feature",
            "kind": "feature",
        }

    if data.get("cwd"):
        return {
            "session_name": data.get("session_name", path.stem),
            "cwd": os.path.normpath(data["cwd"]),
            "agent": data.get("agent", "claude"),
            "role": data.get("role", "project"),
            "kind": data.get("kind", "persistent"),
        }

    return None


def load_registry(sessions_conf: Path, manifests_dir: Path, workspace_root: str):
    base_registry = parse_sessions_conf(sessions_conf)
    registry = []
    seen = set()

    for item in base_registry:
        for alias in alias_cwds(item["cwd"], workspace_root):
            alias_item = dict(item)
            alias_item["cwd"] = alias
            key = (alias_item["session_name"], alias_item["cwd"])
            if key not in seen:
                registry.append(alias_item)
                seen.add(key)

    if manifests_dir.exists():
        for path in sorted(manifests_dir.glob("*.json")):
            item = parse_manifest(path)
            if not item:
                continue
            key = (item["session_name"], item["cwd"])
            if key not in seen:
                registry.append(item)
                seen.add(key)

    for root_cwd in alias_cwds(workspace_root, workspace_root):
        root_item = {
            "session_name": "workspace-root",
            "cwd": root_cwd,
            "agent": "mixed",
            "role": "supervisor",
            "kind": "adhoc",
        }
        key = (root_item["session_name"], root_item["cwd"])
        if key not in seen:
            registry.append(root_item)
            seen.add(key)

    registry.sort(key=lambda item: len(item["cwd"]), reverse=True)
    return registry


def match_registry(cwd: str, registry):
    norm = os.path.normpath(cwd)
    for item in registry:
        base = item["cwd"]
        if norm == base or norm.startswith(base + os.sep):
            return item
    return {
        "session_name": None,
        "cwd": norm,
        "agent": "unknown",
        "role": "unknown",
        "kind": "adhoc",
    }


def codex_text_from_content(content):
    parts = []
    for item in content or []:
        if isinstance(item, dict):
            if item.get("type") in {"input_text", "output_text"} and item.get("text"):
                parts.append(item["text"])
            elif item.get("type") == "text" and item.get("text"):
                parts.append(item["text"])
    return "\n".join(part for part in parts if part).strip()


def claude_message_text(message):
    content = (message or {}).get("content")
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for item in content:
            if not isinstance(item, dict):
                continue
            if item.get("type") == "text" and item.get("text"):
                parts.append(item["text"])
            elif item.get("type") == "thinking" and item.get("thinking"):
                parts.append(item["thinking"])
        return "\n".join(part for part in parts if part).strip()
    return ""


def preview(text: str, limit=280):
    text = " ".join(text.split())
    return text[:limit]


def event_for_claude(obj, line_no: int, path: Path, registry):
    msg_type = obj.get("type")
    if msg_type not in {"user", "assistant"}:
        return None
    text = claude_message_text(obj.get("message"))
    if not text:
        return None
    cwd = obj.get("cwd") or ""
    meta = match_registry(cwd, registry)
    return {
        "ts": obj.get("timestamp") or iso_now(),
        "source": "claude",
        "session_name": meta.get("session_name"),
        "session_role": meta.get("role"),
        "cwd": cwd,
        "actor": "user" if msg_type == "user" else "assistant",
        "kind": "message",
        "preview": preview(text),
        "char_count": len(text),
        "trace_ref": f"{path}:{line_no}",
        "thread_id": obj.get("sessionId"),
        "direct_human_intervention": msg_type == "user" and meta.get("role") in {"project", "feature"},
    }


def event_for_codex(obj, line_no: int, path: Path, registry, file_meta):
    if obj.get("type") == "session_meta":
        payload = obj.get("payload") or {}
        if payload.get("cwd"):
            file_meta["cwd"] = payload["cwd"]
            file_meta["thread_id"] = payload.get("id")
        return None

    if obj.get("type") != "response_item":
        return None

    payload = obj.get("payload") or {}
    if payload.get("type") != "message":
        return None

    role = payload.get("role")
    if role not in {"user", "assistant"}:
        return None

    text = codex_text_from_content(payload.get("content"))
    if not text:
        return None

    cwd = file_meta.get("cwd", "")
    meta = match_registry(cwd, registry)
    return {
        "ts": obj.get("timestamp") or iso_now(),
        "source": "codex",
        "session_name": meta.get("session_name"),
        "session_role": meta.get("role"),
        "cwd": cwd,
        "actor": role,
        "kind": "message",
        "preview": preview(text),
        "char_count": len(text),
        "trace_ref": f"{path}:{line_no}",
        "thread_id": file_meta.get("thread_id"),
        "direct_human_intervention": role == "user" and meta.get("role") in {"project", "feature"},
    }


def scan_file(path: Path, state: dict, registry, trace_fh):
    key = str(path)
    stat = path.stat()
    entry = state.get(key, {})
    offset = entry.get("offset", 0)

    if stat.st_size < offset:
        offset = 0
        entry["line"] = 0

    file_meta = {"cwd": entry.get("cwd"), "thread_id": entry.get("thread_id")}
    if path.as_posix().startswith("/root/.codex/sessions/"):
        parser = "codex"
    else:
        parser = "claude"

    with path.open("r") as fh:
        if offset:
            fh.seek(offset)
        start_offset = fh.tell()
        while True:
            line_no = 0
            if offset == 0 and fh.tell() == start_offset:
                pass
            line = fh.readline()
            if not line:
                break
            offset = fh.tell()
            try:
                obj = json.loads(line)
            except Exception:
                continue

            line_no = entry.get("line", 0) + 1
            entry["line"] = line_no
            if parser == "claude":
                event = event_for_claude(obj, line_no, path, registry)
            else:
                event = event_for_codex(obj, line_no, path, registry, file_meta)
            if event:
                trace_fh.write(json.dumps(event, sort_keys=True) + "\n")

    if file_meta.get("cwd"):
        entry["cwd"] = file_meta["cwd"]
    if file_meta.get("thread_id"):
        entry["thread_id"] = file_meta["thread_id"]
    entry["offset"] = offset
    entry["mtime"] = int(stat.st_mtime)
    state[key] = entry


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace-root", required=True)
    parser.add_argument("--sessions-conf", required=True)
    parser.add_argument("--manifests-dir", required=True)
    parser.add_argument("--trace-file", required=True)
    parser.add_argument("--state-file", required=True)
    args = parser.parse_args()

    sessions_conf = Path(args.sessions_conf)
    manifests_dir = Path(args.manifests_dir)
    trace_file = Path(args.trace_file)
    state_file = Path(args.state_file)

    registry = load_registry(sessions_conf, manifests_dir, args.workspace_root)
    state = load_json(state_file, {})

    files = []
    files.extend(Path(p) for p in glob.glob("/root/.claude/projects/*/*.jsonl"))
    files.extend(Path(p) for p in glob.glob("/root/.codex/sessions/**/*.jsonl", recursive=True))
    files = sorted(path for path in files if path.is_file())

    trace_file.parent.mkdir(parents=True, exist_ok=True)
    with trace_file.open("a") as trace_fh:
        for path in files:
            scan_file(path, state, registry, trace_fh)

    dump_json(state_file, state)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        sys.exit(1)
