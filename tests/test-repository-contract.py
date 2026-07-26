import importlib.util
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

    def test_runtime_artifact_must_exist_and_be_ignored(self) -> None:
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
        codes = {finding.code for finding in MODULE.validate_repo(root)}
        self.assertIn("artifact-path-missing", codes)
        self.assertIn("artifact-path-tracked-risk", codes)

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


if __name__ == "__main__":
    unittest.main()
