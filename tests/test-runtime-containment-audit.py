#!/usr/bin/env python3
"""Hermetic tests for the live systemd containment auditor."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "runtime-containment-audit.py"
SPEC = importlib.util.spec_from_file_location("runtime_containment_audit", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def hardened_properties() -> dict[str, str]:
    return {
        "LoadState": "loaded",
        "User": "atlas",
        "DynamicUser": "no",
        "NoNewPrivileges": "yes",
        "ProtectSystem": "strict",
        "PrivateTmp": "yes",
        "PrivateDevices": "yes",
        "ProtectKernelTunables": "yes",
        "ProtectKernelModules": "yes",
        "ProtectControlGroups": "yes",
        "RestrictSUIDSGID": "yes",
        "LockPersonality": "yes",
        "RestrictNamespaces": "yes",
        "CapabilityBoundingSet": "",
        "AmbientCapabilities": "",
        "IPAddressDeny": "any",
        "IPAddressAllow": "localhost",
    }


class RuntimeContainmentAuditTests(unittest.TestCase):
    def test_default_patterns_cover_every_hosted_service_family(self):
        self.assertEqual(
            MODULE.DEFAULT_PATTERNS,
            (
                "workspace-session@*.service",
                "workspace-supervisor-*.service",
                "atlas-*.service",
                "command*.service",
                "preflight*.service",
                "synaplex-*.service",
            ),
        )

    def test_hardened_unit_has_no_findings(self):
        self.assertEqual(MODULE.assess("atlas-runner.service", hardened_properties()), [])

    def test_root_agent_session_is_critical(self):
        properties = hardened_properties()
        properties["User"] = "root"
        findings = MODULE.assess("workspace-session@atlas.service", properties)
        self.assertIn(
            ("critical", "shared-root-identity"),
            {(finding.severity, finding.code) for finding in findings},
        )

    def test_default_unit_exposes_primary_controls(self):
        properties = {
            "LoadState": "loaded",
            "User": "root",
            "DynamicUser": "no",
            "NoNewPrivileges": "no",
            "ProtectSystem": "no",
            "CapabilityBoundingSet": "cap_sys_admin cap_net_raw",
        }
        codes = {finding.code for finding in MODULE.assess("command.service", properties)}
        self.assertTrue(
            {
                "shared-root-identity",
                "nonewprivileges-disabled",
                "filesystem-not-readonly",
                "broad-capability-set",
                "network-policy-undeclared",
            }.issubset(codes)
        )

    def test_unloaded_unit_short_circuits(self):
        findings = MODULE.assess("missing.service", {"LoadState": "not-found"})
        self.assertEqual([finding.code for finding in findings], ["unit-not-loaded"])

    def test_property_parser_preserves_equals_in_value(self):
        parsed = MODULE.parse_properties("User=atlas\nReadWritePaths=/a=/b\n")
        self.assertEqual(parsed["ReadWritePaths"], "/a=/b")


if __name__ == "__main__":
    unittest.main()
