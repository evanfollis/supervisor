"""Prompt registry: specs, extraction pointers, drift detection.

A prompt does not have to move out of code to be governed. The spec
carries a source pointer; extract() returns the live prompt text from
the repo, and the gate compares its artifact hash against the accepted
baseline. Supported extraction types:

  whole_file  — the file is the prompt (supervisor *-prompt.md)
  region      — text between begin/end marker lines in a file
  py_var      — a module-level string constant in a Python file (AST;
                adjacent-literal concatenation folds to one constant)
  regex       — first capture group of a pattern (last resort; for TS
                template literals etc.)

spec.json shape:
{
  "id": "intake-scorer-system",
  "description": "...",
  "owner": "synaplex",
  "source": {"type": "py_var", "file": "intake/score.py",
             "var": "SONNET_SYSTEM_PROMPT"},
  "model": "sonnet",
  "params": {},                       # sampling params bundled into version
  "executor": {...},                  # see runner.py
  "judge": {"model": "opus"},
  "gate": {"aggregate_floor_delta": 0.02, "trials": 1,
           "max_unknown_ratio": 0.2}
}
"""

from __future__ import annotations

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path

from .core import artifact_hash, read_json

REGISTRY_DIRNAME = ".prompteval"
RESERVED = {"inventory.json", "README.md"}


class RegistryError(Exception):
    pass


@dataclass
class PromptSpec:
    prompt_id: str
    repo: Path
    spec: dict
    path: Path = field(default=None)

    @property
    def dir(self) -> Path:
        return self.repo / REGISTRY_DIRNAME / self.prompt_id

    @property
    def cases_path(self) -> Path:
        return self.dir / "golden" / "cases.jsonl"

    @property
    def holdout_path(self) -> Path:
        return self.dir / "golden" / "holdout.jsonl"

    @property
    def candidates_path(self) -> Path:
        return self.dir / "golden" / "candidates.jsonl"

    @property
    def baseline_path(self) -> Path:
        return self.dir / "baseline.json"

    def extract(self) -> str:
        return extract_prompt(self.repo, self.spec["source"])

    def version(self) -> str:
        return artifact_hash(
            self.extract(), self.spec.get("model", ""), self.spec.get("params", {})
        )

    def spec_hash(self) -> str:
        """Hash of the harness-relevant spec surface: source pointer,
        executor config (plus content of any executor argv entries that are
        readable files, so adapter edits invalidate), judge and gate config.
        Stored in the baseline; drift forces a fresh eval — repointing the
        source at different text or swapping the executor cannot silently
        keep an old accepted baseline."""
        from .core import _digest

        argv_files = {}
        for arg in (self.spec.get("executor") or {}).get("argv", []):
            path = Path(arg)
            if not path.is_absolute():
                path = self.repo / arg
            if path.is_file():
                try:
                    argv_files[arg] = _digest(path.read_text(encoding="utf-8"))
                except OSError:
                    argv_files[arg] = "unreadable"
        return "sh-" + _digest(
            {
                "source": self.spec.get("source"),
                "executor": self.spec.get("executor"),
                "argv_files": argv_files,
                "judge": self.spec.get("judge"),
                "gate": self.spec.get("gate"),
            }
        )


def registry_root(repo: Path) -> Path:
    return Path(repo) / REGISTRY_DIRNAME


def load_spec(repo: Path, prompt_id: str) -> PromptSpec:
    path = registry_root(repo) / prompt_id / "spec.json"
    spec = read_json(path)
    if spec is None:
        raise RegistryError(f"no spec at {path}")
    for key in ("id", "source", "model", "executor"):
        if key not in spec:
            raise RegistryError(f"{path}: missing required key '{key}'")
    if spec["id"] != prompt_id:
        raise RegistryError(f"{path}: id '{spec['id']}' != directory '{prompt_id}'")
    return PromptSpec(prompt_id=prompt_id, repo=Path(repo), spec=spec, path=path)


def list_specs(repo: Path) -> list[PromptSpec]:
    root = registry_root(repo)
    if not root.is_dir():
        return []
    out = []
    for entry in sorted(root.iterdir()):
        if entry.is_dir() and (entry / "spec.json").exists():
            out.append(load_spec(repo, entry.name))
    return out


def load_inventory(repo: Path) -> dict:
    inv = read_json(registry_root(repo) / "inventory.json", default=None)
    return inv or {"enforce": False, "prompts": []}


# --------------------------------------------------------------------------
# Extraction
# --------------------------------------------------------------------------


def extract_prompt(repo: Path, source: dict) -> str:
    stype = source.get("type")
    file_path = Path(repo) / source.get("file", "")
    if not file_path.is_file():
        raise RegistryError(f"source file not found: {file_path}")
    text = file_path.read_text(encoding="utf-8")

    if stype == "whole_file":
        return text

    if stype == "region":
        begin, end = source.get("begin"), source.get("end")
        if not begin or not end:
            raise RegistryError("region source needs 'begin' and 'end' markers")
        try:
            start = text.index(begin) + len(begin)
            stop = text.index(end, start)
        except ValueError as exc:
            raise RegistryError(f"region markers not found in {file_path}") from exc
        return text[start:stop].strip("\n")

    if stype == "py_var":
        var = source.get("var")
        if not var:
            raise RegistryError("py_var source needs 'var'")
        tree = ast.parse(text, filename=str(file_path))
        for node in ast.walk(tree):
            targets = []
            if isinstance(node, ast.Assign):
                targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                targets = [node.target.id]
            if var in targets:
                value = node.value
                if isinstance(value, ast.Constant) and isinstance(value.value, str):
                    return value.value
                raise RegistryError(
                    f"{file_path}: {var} is not a plain string constant "
                    "(f-strings/calls not extractable — use 'region' markers)"
                )
        raise RegistryError(f"{file_path}: no module-level assignment to {var}")

    if stype == "regex":
        pattern = source.get("pattern")
        if not pattern:
            raise RegistryError("regex source needs 'pattern' with one capture group")
        match = re.search(pattern, text, re.DOTALL)
        if not match or not match.groups():
            raise RegistryError(f"{file_path}: pattern found no capture: {pattern}")
        return match.group(1)

    raise RegistryError(f"unknown source type: {stype}")


# --------------------------------------------------------------------------
# Scan — heuristic prompt discovery for inventory seeding
# --------------------------------------------------------------------------

_PROMPT_HINTS = (
    re.compile(r"^You are ", re.MULTILINE),
    re.compile(r"--append-system-prompt"),
    re.compile(r"\bsystem\s*[=:]\s*[\[\"'f(]"),
    re.compile(r"SYSTEM_PROMPT|system_prompt|buildPrompt|Prompt\s*=\s*`", re.IGNORECASE),
)
_SCAN_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".sh", ".md"}
_SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", ".next", ".prompteval"}


def scan(repo: Path) -> list[dict]:
    """Best-effort inventory of likely prompt artifacts in a repo."""
    findings = []
    repo = Path(repo)
    for path in sorted(repo.rglob("*")):
        if not path.is_file() or path.suffix not in _SCAN_SUFFIXES:
            continue
        if any(part in _SKIP_DIRS for part in path.relative_to(repo).parts):
            continue
        rel = str(path.relative_to(repo))
        if path.name.endswith("-prompt.md") or path.name == "SKILL.md":
            findings.append({"file": rel, "reason": "prompt-file naming convention"})
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        hits = [h.pattern for h in _PROMPT_HINTS if h.search(text)]
        if hits:
            findings.append({"file": rel, "reason": f"matched: {', '.join(hits[:2])}"})
    return findings
