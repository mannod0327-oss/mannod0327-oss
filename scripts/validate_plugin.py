#!/usr/bin/env python3
"""Validate the ECC plugin tree.

Checks manifests, skill and command frontmatter, cross-references between
documents, and the repository conventions ECC requires. Exits non-zero on the
first category of failure so CI stops before anything ships.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLUGIN = ROOT / "plugins" / "ecc"
SKILL_DIR = PLUGIN / "skills" / "ecc"
REFERENCES = SKILL_DIR / "references"
COMMANDS = PLUGIN / "commands"

REQUIRED_REFERENCES = {
    "policy.md",
    "stack.md",
    "intake.md",
    "review.md",
    "release.md",
    "reporting.md",
}
REQUIRED_COMMANDS = {"start.md", "review.md", "release.md", "report.md"}

FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)


def read_frontmatter(path: Path) -> dict[str, str]:
    match = FRONTMATTER.match(path.read_text(encoding="utf-8"))
    if match is None:
        raise ValueError(f"{path.relative_to(ROOT)}: missing YAML frontmatter")
    fields: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if not line.strip() or line.lstrip() != line:
            continue
        key, sep, value = line.partition(":")
        if sep:
            fields[key.strip()] = value.strip()
    return fields


def check_manifests(errors: list[str]) -> None:
    marketplace = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
    plugin = json.loads((PLUGIN / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))

    entries = [p for p in marketplace.get("plugins", []) if p.get("name") == "ecc"]
    if not entries:
        errors.append("marketplace.json: no plugin entry named 'ecc'")
        return

    entry = entries[0]
    if entry.get("source") != "./plugins/ecc":
        errors.append(f"marketplace.json: source is {entry.get('source')!r}, expected './plugins/ecc'")
    if entry.get("version") != plugin.get("version"):
        errors.append(
            f"version mismatch: marketplace.json {entry.get('version')!r} "
            f"!= plugin.json {plugin.get('version')!r}"
        )
    for field in ("name", "version", "description", "author"):
        if not plugin.get(field):
            errors.append(f"plugin.json: missing or empty {field!r}")


def check_config(errors: list[str]) -> None:
    config = json.loads((ROOT / "ecc.config.json").read_text(encoding="utf-8"))
    company = config.get("company", {})
    if company.get("short_name") != "ECC":
        errors.append("ecc.config.json: company.short_name must be 'ECC'")
    for key in ("legal_name", "primary_contact", "security_contact"):
        if not company.get(key, "").strip():
            errors.append(f"ecc.config.json: company.{key} must not be empty")
    for key in ("secrets_in_repo", "high_impact_actions", "client_data_egress", "completion_claims"):
        if key not in config.get("policy", {}):
            errors.append(f"ecc.config.json: policy.{key} is not set")


def check_skill(errors: list[str]) -> None:
    skill = SKILL_DIR / "SKILL.md"
    fields = read_frontmatter(skill)
    if fields.get("name") != "ecc":
        errors.append(f"SKILL.md: name is {fields.get('name')!r}, expected 'ecc'")
    description = fields.get("description", "")
    if len(description) < 40:
        errors.append("SKILL.md: description is too short to route on")
    if not any(word in description.lower() for word in ("do not use", "not for")):
        errors.append("SKILL.md: description must say when not to use the skill")

    body = skill.read_text(encoding="utf-8")
    for name in sorted(REQUIRED_REFERENCES):
        if f"references/{name}" not in body:
            errors.append(f"SKILL.md: does not route to references/{name}")


def check_references(errors: list[str]) -> None:
    present = {p.name for p in REFERENCES.glob("*.md")}
    for missing in sorted(REQUIRED_REFERENCES - present):
        errors.append(f"references/: missing {missing}")
    for extra in sorted(present - REQUIRED_REFERENCES):
        errors.append(f"references/: unexpected file {extra} (update REQUIRED_REFERENCES if intended)")
    for name in sorted(present & REQUIRED_REFERENCES):
        text = (REFERENCES / name).read_text(encoding="utf-8")
        if not text.startswith("# "):
            errors.append(f"references/{name}: must open with a level-1 heading")
        if not text.endswith("\n"):
            errors.append(f"references/{name}: must end with a newline")


def check_commands(errors: list[str]) -> None:
    present = {p.name for p in COMMANDS.glob("*.md")}
    for missing in sorted(REQUIRED_COMMANDS - present):
        errors.append(f"commands/: missing {missing}")
    for name in sorted(present):
        path = COMMANDS / name
        fields = read_frontmatter(path)
        if not fields.get("description"):
            errors.append(f"commands/{name}: missing description")
        body = path.read_text(encoding="utf-8")
        if "${CLAUDE_PLUGIN_ROOT}" not in body:
            errors.append(f"commands/{name}: must reference ${{CLAUDE_PLUGIN_ROOT}} to load its reference")
        for ref in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([^\s`]+)", body):
            if not (PLUGIN / ref).is_file():
                errors.append(f"commands/{name}: references missing file {ref}")


def check_conventions(errors: list[str]) -> None:
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or ".git/" in path.as_posix():
            continue
        if path.suffix not in {".md", ".json", ".py", ".yml", ".ini", ".txt"}:
            continue
        data = path.read_bytes()
        if b"\r\n" in data:
            errors.append(f"{path.relative_to(ROOT)}: CRLF line endings, expected LF")
        if data and not data.endswith(b"\n"):
            errors.append(f"{path.relative_to(ROOT)}: missing trailing newline")


def main() -> int:
    errors: list[str] = []
    for check in (
        check_manifests,
        check_config,
        check_skill,
        check_references,
        check_commands,
        check_conventions,
    ):
        try:
            check(errors)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{check.__name__}: {exc}")

    if errors:
        for error in errors:
            print(f"FAIL {error}", file=sys.stderr)
        print(f"\n{len(errors)} problem(s) found.", file=sys.stderr)
        return 1

    print("ECC plugin validates.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
