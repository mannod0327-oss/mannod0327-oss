"""Regression tests for the ECC plugin tree and its validator.

The validator is only useful if it fails on broken input, so each test corrupts
one thing in a temporary copy of the repository and asserts the specific
failure is reported.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = ROOT / "scripts" / "validate_plugin.py"
PLUGIN = ROOT / "plugins" / "ecc"


def run_validator(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / "scripts" / "validate_plugin.py")],
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A throwaway copy of the plugin tree that a test may corrupt."""
    target = tmp_path / "repo"
    target.mkdir()
    for item in (".claude-plugin", "plugins", "scripts", "ecc.config.json"):
        source = ROOT / item
        destination = target / item
        if source.is_dir():
            shutil.copytree(source, destination)
        else:
            shutil.copy2(source, destination)
    return target


def test_repository_validates() -> None:
    result = run_validator(ROOT)
    assert result.returncode == 0, result.stderr


def test_detects_version_mismatch(repo: Path) -> None:
    path = repo / "plugins" / "ecc" / ".claude-plugin" / "plugin.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["version"] = "9.9.9"
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    result = run_validator(repo)
    assert result.returncode == 1
    assert "version mismatch" in result.stderr


def test_detects_missing_reference(repo: Path) -> None:
    (repo / "plugins" / "ecc" / "skills" / "ecc" / "references" / "policy.md").unlink()

    result = run_validator(repo)
    assert result.returncode == 1
    assert "missing policy.md" in result.stderr


def test_detects_command_pointing_at_missing_file(repo: Path) -> None:
    path = repo / "plugins" / "ecc" / "commands" / "review.md"
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("references/review.md", "references/nope.md"), encoding="utf-8")

    result = run_validator(repo)
    assert result.returncode == 1
    assert "references missing file" in result.stderr


def test_detects_crlf(repo: Path) -> None:
    path = repo / "plugins" / "ecc" / "skills" / "ecc" / "references" / "stack.md"
    path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))

    result = run_validator(repo)
    assert result.returncode == 1
    assert "CRLF" in result.stderr


def test_detects_blank_legal_name(repo: Path) -> None:
    path = repo / "ecc.config.json"
    config = json.loads(path.read_text(encoding="utf-8"))
    config["company"]["legal_name"] = "   "
    path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

    result = run_validator(repo)
    assert result.returncode == 1
    assert "legal_name" in result.stderr


def test_config_carries_the_company_name() -> None:
    config = json.loads((ROOT / "ecc.config.json").read_text(encoding="utf-8"))
    assert config["company"]["short_name"] == "ECC"
    assert config["company"]["legal_name"] == "Elite Coding Company"


def test_detects_unset_policy(repo: Path) -> None:
    path = repo / "ecc.config.json"
    config = json.loads(path.read_text(encoding="utf-8"))
    del config["policy"]["completion_claims"]
    path.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")

    result = run_validator(repo)
    assert result.returncode == 1
    assert "policy.completion_claims" in result.stderr


@pytest.mark.parametrize("name", ["start.md", "review.md", "release.md", "report.md"])
def test_every_command_has_a_description(name: str) -> None:
    text = (PLUGIN / "commands" / name).read_text(encoding="utf-8")
    assert text.startswith("---\n")
    assert "\ndescription: " in text.split("\n---\n", 1)[0]


def test_policy_states_all_four_rules() -> None:
    text = (PLUGIN / "skills" / "ecc" / "references" / "policy.md").read_text(encoding="utf-8")
    for heading in (
        "## 1. Secrets and credentials",
        "## 2. Human approval for high-impact actions",
        "## 3. Client and personal data",
        "## 4. Evidence before completion",
    ):
        assert heading in text, f"policy.md lost {heading!r}"


def test_no_secret_shaped_literals_in_tree() -> None:
    """The plugin tells people not to commit credentials; it must not commit any."""
    markers = ("-----BEGIN", "AKIA", "ghp_")
    offenders = []
    for path in PLUGIN.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            # policy.md names these markers deliberately, inside backticks.
            if marker in text and f"`{marker}`" not in text:
                offenders.append(f"{path.relative_to(ROOT)}: {marker}")
    assert not offenders, offenders
