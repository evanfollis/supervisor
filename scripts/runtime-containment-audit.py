#!/usr/bin/env python3
"""Report containment gaps in workspace-related systemd services.

This is an observation tool, not a unit-file mutator. It keeps the transition
from broad host authority to scoped execution measurable without pretending
that a structural repository check proves runtime containment.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

DEFAULT_PATTERNS = (
    "workspace-session@*.service",
    "workspace-supervisor-*.service",
    "atlas-*.service",
    "command*.service",
    "preflight*.service",
    "synaplex-*.service",
)

PROPERTIES = (
    "User",
    "Group",
    "DynamicUser",
    "NoNewPrivileges",
    "ProtectSystem",
    "ProtectHome",
    "PrivateTmp",
    "PrivateDevices",
    "ProtectKernelTunables",
    "ProtectKernelModules",
    "ProtectControlGroups",
    "RestrictSUIDSGID",
    "LockPersonality",
    "RestrictNamespaces",
    "CapabilityBoundingSet",
    "AmbientCapabilities",
    "IPAddressDeny",
    "IPAddressAllow",
    "ReadWritePaths",
    "FragmentPath",
    "LoadState",
    "ActiveState",
)

YES_CONTROLS = (
    "NoNewPrivileges",
    "PrivateTmp",
    "PrivateDevices",
    "ProtectKernelTunables",
    "ProtectKernelModules",
    "ProtectControlGroups",
    "RestrictSUIDSGID",
    "LockPersonality",
    "RestrictNamespaces",
)

DANGEROUS_CAPABILITIES = {
    "cap_dac_override",
    "cap_dac_read_search",
    "cap_net_admin",
    "cap_net_raw",
    "cap_setgid",
    "cap_setuid",
    "cap_sys_admin",
    "cap_sys_module",
    "cap_sys_ptrace",
    "cap_sys_rawio",
}

SEVERITY_RANK = {"info": 0, "low": 1, "medium": 2, "high": 3, "critical": 4}


@dataclass(frozen=True)
class Finding:
    unit: str
    severity: str
    code: str
    detail: str


def run_systemctl(*args: str) -> str:
    process = subprocess.run(
        ["systemctl", *args],
        check=False,
        capture_output=True,
        text=True,
    )
    if process.returncode:
        raise RuntimeError(process.stderr.strip() or "systemctl failed")
    return process.stdout


def discover_units(patterns: Iterable[str]) -> list[str]:
    unit_files = run_systemctl(
        "list-unit-files", "--type=service", "--no-legend", "--no-pager"
    )
    loaded_units = run_systemctl(
        "list-units", "--type=service", "--all", "--no-legend", "--no-pager"
    )
    available = {
        line.split()[0]
        for output in (unit_files, loaded_units)
        for line in output.splitlines()
        if line.strip()
    }
    return sorted(
        unit
        for unit in available
        if not unit.endswith("@.service")
        if any(fnmatch.fnmatchcase(unit, pattern) for pattern in patterns)
    )


def parse_properties(output: str) -> dict[str, str]:
    properties: dict[str, str] = {}
    for line in output.splitlines():
        key, separator, value = line.partition("=")
        if separator:
            properties[key] = value
    return properties


def inspect_unit(unit: str) -> dict[str, str]:
    output = run_systemctl(
        "show", unit, "--no-pager", *[f"--property={name}" for name in PROPERTIES]
    )
    return parse_properties(output)


def assess(unit: str, properties: dict[str, str]) -> list[Finding]:
    findings: list[Finding] = []
    if properties.get("LoadState") != "loaded":
        return [
            Finding(
                unit,
                "high",
                "unit-not-loaded",
                f"LoadState={properties.get('LoadState', '<missing>')}",
            )
        ]

    user = properties.get("User", "")
    dynamic_user = properties.get("DynamicUser", "no")
    is_agent_session = unit.startswith("workspace-session@")
    if (not user or user == "root") and dynamic_user != "yes":
        findings.append(
            Finding(
                unit,
                "critical" if is_agent_session else "high",
                "shared-root-identity",
                "service executes as root instead of a project-scoped identity",
            )
        )

    for control in YES_CONTROLS:
        if properties.get(control) != "yes":
            findings.append(
                Finding(
                    unit,
                    "high" if control == "NoNewPrivileges" else "medium",
                    f"{control.lower()}-disabled",
                    f"{control}={properties.get(control, '<missing>')}",
                )
            )

    protect_system = properties.get("ProtectSystem", "no")
    if protect_system not in {"full", "strict"}:
        findings.append(
            Finding(
                unit,
                "high",
                "filesystem-not-readonly",
                f"ProtectSystem={protect_system}",
            )
        )

    capability_set = set(properties.get("CapabilityBoundingSet", "").split())
    dangerous = sorted(capability_set & DANGEROUS_CAPABILITIES)
    if dangerous:
        findings.append(
            Finding(
                unit,
                "high",
                "broad-capability-set",
                "dangerous capabilities retained: " + ", ".join(dangerous),
            )
        )

    ambient = properties.get("AmbientCapabilities", "").strip()
    if ambient:
        findings.append(
            Finding(
                unit,
                "high",
                "ambient-capabilities",
                f"AmbientCapabilities={ambient}",
            )
        )

    if not properties.get("IPAddressDeny") and not properties.get("IPAddressAllow"):
        findings.append(
            Finding(
                unit,
                "low",
                "network-policy-undeclared",
                "no systemd IP allow/deny policy is declared",
            )
        )
    return findings


def render_text(
    units: list[dict[str, object]], findings: list[Finding]
) -> str:
    lines = [
        f"runtime containment audit: {len(units)} unit(s), {len(findings)} finding(s)"
    ]
    for finding in findings:
        lines.append(
            f"{finding.severity.upper():8} {finding.unit}: "
            f"{finding.code} — {finding.detail}"
        )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--unit", action="append", default=[])
    parser.add_argument("--pattern", action="append", default=[])
    parser.add_argument(
        "--include-inactive",
        action="store_true",
        help="also assess matching installed units that are not currently active",
    )
    parser.add_argument("--json", action="store_true")
    parser.add_argument(
        "--fail-on",
        choices=tuple(SEVERITY_RANK),
        help="return non-zero when this severity or higher is observed",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="write the report atomically to this path in addition to stdout",
    )
    args = parser.parse_args(argv)

    try:
        unit_names = sorted(
            set(args.unit)
            or set(discover_units(tuple(args.pattern) or DEFAULT_PATTERNS))
        )
        inspected: list[dict[str, object]] = []
        findings: list[Finding] = []
        for unit in unit_names:
            properties = inspect_unit(unit)
            if (
                not args.include_inactive
                and not args.unit
                and properties.get("ActiveState") != "active"
            ):
                continue
            inspected.append({"name": unit, "properties": properties})
            findings.extend(assess(unit, properties))
    except RuntimeError as error:
        print(f"runtime containment audit failed: {error}", file=sys.stderr)
        return 2

    findings.sort(
        key=lambda finding: (
            -SEVERITY_RANK[finding.severity],
            finding.unit,
            finding.code,
        )
    )
    payload = {
        "schema_version": 1,
        "units": inspected,
        "findings": [asdict(finding) for finding in findings],
        "summary": {
            "units": len(inspected),
            "findings": len(findings),
            "by_severity": {
                severity: sum(
                    finding.severity == severity for finding in findings
                )
                for severity in SEVERITY_RANK
            },
        },
    }
    rendered = (
        json.dumps(payload, indent=2, sort_keys=True)
        if args.json
        else render_text(inspected, findings)
    )
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        temporary = args.output.with_suffix(args.output.suffix + ".tmp")
        temporary.write_text(rendered + "\n", encoding="utf-8")
        temporary.replace(args.output)

    if args.fail_on:
        threshold = SEVERITY_RANK[args.fail_on]
        if any(SEVERITY_RANK[finding.severity] >= threshold for finding in findings):
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
