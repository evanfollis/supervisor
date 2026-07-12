"""ID contract, canonical JSON, paths, small IO helpers.

S1-P3: every durable ID in the prompteval store is minted here and only
here. Prompt versions, case IDs, and cache keys all share one scheme:
sha256 over canonical JSON, 16 hex chars, typed prefix.
"""

from __future__ import annotations

import hashlib
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

RUNTIME_ROOT = Path(os.environ.get("PROMPTEVAL_RUNTIME", "/opt/workspace/runtime/prompteval"))
TELEMETRY_PATH = Path(
    os.environ.get("PROMPTEVAL_TELEMETRY", "/opt/workspace/runtime/.telemetry/events.jsonl")
)

HASH_LEN = 16  # one contract; never introduce a second width (S1-P3)


def canonical(obj) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _digest(obj) -> str:
    return hashlib.sha256(canonical(obj).encode("utf-8")).hexdigest()[:HASH_LEN]


def artifact_hash(prompt_text: str, model: str, params: dict) -> str:
    """Version of the immutable (prompt text, model, params) triple."""
    return "pv-" + _digest({"t": prompt_text, "m": model, "p": params or {}})


def case_id(case_input) -> str:
    return "gc-" + _digest(case_input)


def cache_key(obj) -> str:
    return "ck-" + _digest(obj)


def run_id() -> str:
    # uuid suffix: concurrent runs in the same second must not collide
    import uuid

    return ("run-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            + "-" + uuid.uuid4().hex[:6])


def project_key(repo) -> str:
    """Runtime-dir key for a repo: basename + path hash, so two repos with
    the same basename never share cache/status/run directories."""
    from pathlib import Path as _P

    repo = _P(repo).resolve()
    return f"{repo.name}-{_digest(str(repo))[:6]}"


def utcnow_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def epoch_ms() -> int:
    return int(time.time() * 1000)


def read_json(path: Path, default=None):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default


def write_json(path: Path, obj) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def read_jsonl(path: Path) -> list:
    out = []
    try:
        with open(path, encoding="utf-8") as fh:
            for n, line in enumerate(fh, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    out.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise ValueError(f"{path}:{n}: bad JSONL line: {exc}") from exc
    except FileNotFoundError:
        pass
    return out


def append_jsonl(path: Path, obj) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as fh:
        fh.write(canonical(obj) + "\n")
