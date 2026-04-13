#!/usr/bin/env python3
"""
Repository-grade validator for portable skills.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
ALLOWED_FRONTMATTER_KEYS = {"name", "description", "license", "allowed-tools", "metadata"}
REQUIRED_SECTIONS = [
    "Use When",
    "Do Not Use When",
    "Required Inputs",
    "Workflow",
    "Quality Standards",
    "Anti-Patterns",
    "Outputs",
    "References",
]
MAX_MARKDOWN_LINES = 500
DUAL_COMPAT_START = "<!-- dual-compat-start -->"
DUAL_COMPAT_END = "<!-- dual-compat-end -->"
NONPORTABLE_SNIPPETS = {
    "skills/": "Do not assume a top-level `skills/` directory inside skill content.",
    ".github/copilot-instructions.md": "Do not reference unavailable repo-local Copilot instructions.",
    "chat.customAgentInSubagent.enabled": "Do not require VS Code-specific settings in portable skills.",
    "latest VS Code Insiders build": "Do not require a specific editor build in portable skills.",
}


def read_utf8(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"{path.name} is not valid UTF-8: {exc}") from exc


def parse_frontmatter(content: str) -> tuple[dict, str]:
    if not content.startswith("---"):
        raise ValueError("No YAML frontmatter found")

    match = re.match(r"^---\n(.*?)\n---\n?", content, re.DOTALL)
    if not match:
        raise ValueError("Invalid frontmatter format")

    frontmatter_text = match.group(1)
    try:
        frontmatter = yaml.safe_load(frontmatter_text)
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML in frontmatter: {exc}") from exc

    if not isinstance(frontmatter, dict):
        raise ValueError("Frontmatter must be a YAML dictionary")

    body = content[match.end() :]
    return frontmatter, body


def line_count(text: str) -> int:
    return len(text.splitlines())


def iter_markdown_links(text: str) -> list[str]:
    return re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)


def is_external_link(target: str) -> bool:
    return (
        "://" in target
        or target.startswith("mailto:")
        or target.startswith("#")
    )


def strip_anchor(target: str) -> str:
    return target.split("#", 1)[0].strip()


def validate_frontmatter(frontmatter: dict, skill_dir: Path, errors: list[str]) -> None:
    unexpected = set(frontmatter.keys()) - ALLOWED_FRONTMATTER_KEYS
    if unexpected:
        errors.append(
            "Unexpected key(s) in SKILL.md frontmatter: "
            + ", ".join(sorted(unexpected))
        )

    name = frontmatter.get("name")
    if name is None:
        errors.append("Missing `name` in frontmatter.")
    elif not isinstance(name, str):
        errors.append(f"`name` must be a string, got {type(name).__name__}.")
    else:
        stripped = name.strip()
        if stripped != skill_dir.name:
            errors.append(f"`name` must match the directory name `{skill_dir.name}`.")
        if not re.fullmatch(r"[a-z0-9-]+", stripped or ""):
            errors.append("`name` must use hyphen-case.")
        if stripped.startswith("-") or stripped.endswith("-") or "--" in stripped:
            errors.append("`name` cannot start/end with `-` or contain `--`.")
        if len(stripped) > 64:
            errors.append("`name` exceeds 64 characters.")

    description = frontmatter.get("description")
    if description is None:
        errors.append("Missing `description` in frontmatter.")
    elif not isinstance(description, str):
        errors.append(f"`description` must be a string, got {type(description).__name__}.")
    else:
        stripped = description.strip()
        if not stripped:
            errors.append("`description` must not be empty.")
        if "<" in stripped or ">" in stripped:
            errors.append("`description` cannot contain angle brackets.")
        if len(stripped) > 1024:
            errors.append("`description` exceeds 1024 characters.")

    metadata = frontmatter.get("metadata")
    if not isinstance(metadata, dict):
        errors.append("`metadata` must exist and be a mapping for portable skills.")
        return

    if metadata.get("portable") is not True:
        errors.append("`metadata.portable` must be `true`.")

    compatible = metadata.get("compatible_with")
    if compatible != ["claude-code", "codex"]:
        errors.append("`metadata.compatible_with` must equal ['claude-code', 'codex'].")


def validate_portable_sections(body: str, errors: list[str]) -> None:
    if DUAL_COMPAT_START not in body or DUAL_COMPAT_END not in body:
        errors.append("Portable contract markers are missing.")
        return

    contract = re.search(
        rf"{re.escape(DUAL_COMPAT_START)}(.*?){re.escape(DUAL_COMPAT_END)}",
        body,
        re.DOTALL,
    )
    if not contract:
        errors.append("Portable contract markers are malformed.")
        return

    contract_text = contract.group(1)
    for section in REQUIRED_SECTIONS:
        if re.search(rf"^##\s+{re.escape(section)}\s*$", contract_text, re.MULTILINE) is None:
            errors.append(f"Portable section missing: `## {section}`.")


def validate_markdown_file(path: Path, errors: list[str]) -> None:
    text = read_utf8(path)
    count = line_count(text)
    if path.name == "SKILL.md" and count > MAX_MARKDOWN_LINES:
        errors.append(
            f"{path.relative_to(REPO_ROOT)} exceeds {MAX_MARKDOWN_LINES} lines ({count})."
        )

    if "\ufffd" in text:
        errors.append(
            f"{path.relative_to(REPO_ROOT)} contains replacement characters."
        )


def validate_local_links(skill_dir: Path, skill_md: Path, body: str, errors: list[str]) -> None:
    for target in iter_markdown_links(body):
        clean = strip_anchor(target)
        if not clean or is_external_link(clean):
            continue

        resolved = (skill_md.parent / clean).resolve()
        try:
            resolved.relative_to(REPO_ROOT.resolve())
        except ValueError:
            errors.append(f"Link points outside the repository: `{target}`.")
            continue

        if not resolved.exists():
            errors.append(f"Broken local link: `{target}`.")

    for snippet, reason in NONPORTABLE_SNIPPETS.items():
        if snippet in body:
            errors.append(f"Nonportable content `{snippet}` found. {reason}")


def validate_skill(skill_path: Path) -> tuple[bool, list[str]]:
    errors: list[str] = []
    skill_path = skill_path.resolve()
    skill_md = skill_path / "SKILL.md"

    if not skill_md.exists():
        return False, ["SKILL.md not found."]

    try:
        raw = read_utf8(skill_md)
    except ValueError as exc:
        return False, [str(exc)]

    try:
        frontmatter, body = parse_frontmatter(raw)
    except ValueError as exc:
        return False, [str(exc)]

    validate_frontmatter(frontmatter, skill_path, errors)
    validate_portable_sections(body, errors)
    validate_local_links(skill_path, skill_md, body, errors)

    for md_file in sorted(skill_path.rglob("*.md")):
        try:
            validate_markdown_file(md_file, errors)
        except ValueError as exc:
            errors.append(str(exc))

    return not errors, errors


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python -X utf8 quick_validate.py <skill_directory>")
        return 1

    skill_dir = Path(sys.argv[1])
    valid, errors = validate_skill(skill_dir)
    if valid:
        print("Skill is valid.")
        return 0

    print("Skill validation failed:")
    for error in errors:
        print(f"- {error}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
