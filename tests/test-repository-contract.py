import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "repository-contract.py"
SPEC = importlib.util.spec_from_file_location("repository_contract", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class RepositoryContractTest(unittest.TestCase):
    def make_repo(self, declaration: str) -> Path:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        subprocess.run(["git", "init", "-q", str(root)], check=True)
        for relative in (
            "README.md",
            "Makefile",
            "AGENTS.md",
            "CLAUDE.md",
            "docs/architecture.md",
        ):
            path = root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("test\n", encoding="utf-8")
        (root / "repo.toml").write_text(declaration, encoding="utf-8")
        return root

    def test_minimal_application_is_valid(self) -> None:
        root = self.make_repo(
            """
schema_version = 1
name = "example"
shape = "application"
lifecycle = "active"
agentic_risk = "none"
canonical_repository = "https://github.com/evanfollis/example"
"""
        )
        self.assertEqual([], MODULE.validate_repo(root, expected_name="example"))

    def test_inventory_divergence_is_reported(self) -> None:
        root = self.make_repo(
            """
schema_version = 1
name = "other"
shape = "library"
lifecycle = "maintained"
agentic_risk = "model-assisted"
canonical_repository = "https://github.com/evanfollis/other"
"""
        )
        codes = {
            finding.code
            for finding in MODULE.validate_repo(
                root,
                expected_name="expected",
                expected_remote="https://github.com/evanfollis/expected",
            )
        }
        self.assertIn("name-divergence", codes)
        self.assertIn("canonical-repository-divergence", codes)

    def test_absent_runtime_artifact_may_be_declared_when_ignored(self) -> None:
        root = self.make_repo(
            """
schema_version = 1
name = "example"
shape = "service"
lifecycle = "active"
agentic_risk = "agentic"
canonical_repository = "https://github.com/evanfollis/example"

[artifacts]
runtime = ["var/"]
"""
        )
        (root / ".gitignore").write_text("var/\n", encoding="utf-8")
        self.assertEqual([], MODULE.validate_repo(root))

    def test_mixed_risk_workspace_is_validated(self) -> None:
        root = self.make_repo(
            """
schema_version = 1
name = "example"
shape = "monorepo"
lifecycle = "active"
agentic_risk = "agentic"
canonical_repository = "https://github.com/evanfollis/example"

[workspaces.static]
agentic_risk = "none"

[workspaces.runner]
agentic_risk = "invalid"
"""
        )
        findings = MODULE.validate_repo(root)
        self.assertEqual(["workspace-risk-invalid"], [finding.code for finding in findings])

    def test_workspace_risk_cannot_exceed_root(self) -> None:
        root = self.make_repo(
            """
schema_version = 1
name = "example"
shape = "monorepo"
lifecycle = "active"
agentic_risk = "none"
canonical_repository = "https://github.com/evanfollis/example"

[workspaces.runner]
agentic_risk = "agentic"
"""
        )
        findings = MODULE.validate_repo(root)
        self.assertEqual(
            ["workspace-risk-exceeds-root"], [finding.code for finding in findings]
        )

    def test_session_projection_must_contain_repository(self) -> None:
        root = self.make_repo(
            """
schema_version = 1
name = "example"
shape = "library"
lifecycle = "active"
agentic_risk = "none"
canonical_repository = "https://github.com/evanfollis/example"
"""
        )
        config = root / "config"
        config.mkdir()
        (config / "sessions.conf").write_text(
            "example|/different/root|claude|project\n", encoding="utf-8"
        )
        inventory = config / "repositories.toml"
        inventory.write_text(
            f"""
schema_version = 1
session_inventory = "sessions.conf"

[[repositories]]
name = "example"
path = "{root}"
session = "example"
canonical_repository = "https://github.com/evanfollis/example"
conformance = "conforming"
""",
            encoding="utf-8",
        )
        findings, checked = MODULE.validate_inventory(inventory, allow_missing=False)
        self.assertEqual(1, checked)
        self.assertIn("session-path-divergence", {finding.code for finding in findings})

    def test_conforming_repository_cannot_bypass_missing_declaration(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        config = root / "config"
        repository = root / "repository"
        config.mkdir()
        repository.mkdir()
        (config / "sessions.conf").write_text(
            f"example|{repository}|claude|project\n", encoding="utf-8"
        )
        inventory = config / "repositories.toml"
        inventory.write_text(
            f"""
schema_version = 1
session_inventory = "sessions.conf"

[[repositories]]
name = "example"
path = "{repository}"
session = "example"
canonical_repository = "https://github.com/evanfollis/example"
conformance = "conforming"
""",
            encoding="utf-8",
        )
        findings, _ = MODULE.validate_inventory(inventory, allow_missing=True)
        self.assertIn("declaration-missing", {finding.code for finding in findings})

    def test_make_test_propagates_an_early_failure(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        shutil.copy(Path(__file__).parents[1] / "Makefile", root / "Makefile")
        tests = root / "tests"
        tests.mkdir()
        (tests / "test-aaa-fails.py").write_text(
            "raise SystemExit(17)\n", encoding="utf-8"
        )
        (tests / "test-zzz-passes.py").write_text(
            "raise SystemExit(0)\n", encoding="utf-8"
        )
        result = subprocess.run(
            ["make", "test"],
            cwd=root,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        self.assertNotEqual(0, result.returncode)


if __name__ == "__main__":
    unittest.main()
