#!/usr/bin/env python3
"""Report agent-harness readiness across governed workspace repos."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


ROOT = Path("/opt/workspace")
SUPERVISOR = ROOT / "supervisor"
PROJECTS_CONF = SUPERVISOR / "scripts/lib/projects.conf"
STALE_DAYS = 7
LARGE_INSTRUCTION_LINES = 350


@dataclass
class Project:
    name: str
    path: Path


@dataclass
class Finding:
    severity: str
    project: str
    check: str
    message: str
    path: str | None = None


def load_projects(path: Path) -> list[Project]:
    projects: list[Project] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split("|")
        if len(parts) < 2:
            continue
        projects.append(Project(parts[0], Path(parts[1])))
    return projects


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(errors="replace")


def front_door(project: Project) -> Path | None:
    names = ["CURRENT_STATE.md", "CONTEXT.md"]
    if project.name == "supervisor":
        names.append("system/status.md")
    for name in names:
        candidate = project.path / name
        if candidate.exists():
            return candidate
    return None


def parse_updated(text: str) -> datetime | None:
    patterns = [
        r"^updated:\s*([^\n]+)$",
        r"^\*\*Last updated\*\*:\s*([^\n]+)$",
        r"^Last updated:\s*([^\n]+)$",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.MULTILINE)
        if not match:
            continue
        raw = match.group(1).strip()
        raw = raw.split("—", 1)[0].strip()
        raw = raw.split(" ", 1)[0].strip()
        raw = raw.split(" ", 1)[0].strip() if re.match(r"\d{4}-\d{2}-\d{2}$", raw.split(" ", 1)[0]) else raw
        if re.match(r"\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}", raw):
            date_part, time_part = raw.split("T", 1)
            raw = f"{date_part}T{time_part.replace('-', ':', 2)}"
        raw = raw.replace("Z", "+00:00")
        for candidate in (raw, raw.replace("T", " ")):
            try:
                parsed = datetime.fromisoformat(candidate)
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=timezone.utc)
                return parsed.astimezone(timezone.utc)
            except ValueError:
                pass
    return None


def has_package(project: Project) -> bool:
    return (project.path / "package.json").exists()


def package_mentions_browser_automation(project: Project) -> bool:
    package_path = project.path / "package.json"
    if not package_path.exists():
        return False
    try:
        data = json.loads(package_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    deps = {}
    for key in ("dependencies", "devDependencies", "optionalDependencies"):
        deps.update(data.get(key, {}))
    names = " ".join(deps.keys()).lower()
    return any(token in names for token in ("playwright", "puppeteer", "webdriverio", "selenium"))


def has_check_script(project: Project) -> bool:
    package_path = project.path / "package.json"
    if package_path.exists():
        try:
            data = json.loads(package_path.read_text(encoding="utf-8"))
            scripts = data.get("scripts", {})
            if any(name in scripts for name in ("check", "test", "smoke", "typecheck")):
                return True
        except json.JSONDecodeError:
            pass
    for candidate in ("Makefile", "pyproject.toml", "pytest.ini"):
        if (project.path / candidate).exists():
            return True
    return False


def qa_plan_exists(project: Project) -> bool:
    candidates = [
        project.path / "docs/QA.md",
        project.path / "docs/qa.md",
        project.path / "QA.md",
        project.path / "tests/QA.md",
    ]
    return any(path.exists() for path in candidates)


def instruction_files(project: Project) -> Iterable[Path]:
    seen: set[Path] = set()
    for name in ("CLAUDE.md", "AGENTS.md", "AGENT.md"):
        path = project.path / name
        if path.exists() and path.resolve() not in seen:
            seen.add(path.resolve())
            yield path


def check_project(project: Project) -> list[Finding]:
    findings: list[Finding] = []
    if not project.path.exists():
        return [
            Finding("fail", project.name, "project.exists", "Configured project path is missing.", str(project.path))
        ]

    door = front_door(project)
    if door is None:
        findings.append(Finding("fail", project.name, "front-door.exists", "Missing CURRENT_STATE.md or CONTEXT.md.", rel(project.path)))
    else:
        text = read_text(door)
        updated = parse_updated(text)
        if updated is None:
            findings.append(Finding("warn", project.name, "front-door.updated", "Front door has no parseable updated timestamp.", rel(door)))
        else:
            age_days = (datetime.now(timezone.utc) - updated).total_seconds() / 86400
            if age_days > STALE_DAYS:
                findings.append(Finding("warn", project.name, "front-door.freshness", f"Front door is {age_days:.1f} days old.", rel(door)))
        if len(text.splitlines()) > 220:
            findings.append(Finding("warn", project.name, "front-door.size", "Front door is long; consider moving history/detail into depth docs.", rel(door)))

    for path in instruction_files(project):
        text = read_text(path)
        line_count = len(text.splitlines())
        if line_count > LARGE_INSTRUCTION_LINES:
            findings.append(Finding("warn", project.name, "instructions.size", f"{path.name} is {line_count} lines; use it as a map, not an encyclopedia.", rel(path)))
        if "context-always-load:" not in text and project.name != "supervisor":
            findings.append(Finding("info", project.name, "instructions.context-load", f"{path.name} has no context-always-load declaration.", rel(path)))

    if has_package(project):
        if not has_check_script(project):
            findings.append(Finding("warn", project.name, "checks.script", "package.json has no check/test/smoke/typecheck script.", rel(project.path / "package.json")))
        if not package_mentions_browser_automation(project):
            findings.append(Finding("info", project.name, "browser-qa.runtime", "No browser automation dependency found.", rel(project.path / "package.json")))

    if has_package(project) and not qa_plan_exists(project):
        findings.append(Finding("info", project.name, "qa-plan.exists", "No docs/QA.md or equivalent found.", rel(project.path)))

    return findings


def render(findings: list[Finding], projects: list[Project]) -> str:
    counts = {severity: sum(1 for f in findings if f.severity == severity) for severity in ("fail", "warn", "info")}
    lines = [
        "# Workspace Harness Check",
        "",
        f"Projects scanned: {len(projects)}",
        f"Findings: {counts['fail']} fail, {counts['warn']} warn, {counts['info']} info",
        "",
    ]
    if not findings:
        lines.append("No findings.")
        return "\n".join(lines)

    severity_order = {"fail": 0, "warn": 1, "info": 2}
    for finding in sorted(findings, key=lambda f: (severity_order[f.severity], f.project, f.check)):
        path = f" ({finding.path})" if finding.path else ""
        lines.append(f"- **{finding.severity.upper()}** `{finding.project}` `{finding.check}`{path}: {finding.message}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true", help="exit non-zero on fail/warn findings")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args()

    projects = load_projects(PROJECTS_CONF)
    findings = [finding for project in projects for finding in check_project(project)]

    if args.json:
        print(json.dumps({
            "projectsScanned": len(projects),
            "findings": [finding.__dict__ for finding in findings],
        }, indent=2))
    else:
        print(render(findings, projects))

    if args.strict and any(f.severity == "fail" for f in findings):
        return 2
    if args.strict and any(f.severity == "warn" for f in findings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
