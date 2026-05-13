#!/usr/bin/env python3
"""
Repository-level guardrails for the active skills catalog.

This script intentionally does not move, delete, or rewrite skills. It scans the
active catalog roots and reports loader risks that matter during consolidation.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import yaml


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ACTIVE_ROOTS = (
    "skills",
    "doctrine/skills",
    "00-meta-initialization",
)
DEFAULT_MAX_ACTIVE_SKILLS = 200
MAX_DESCRIPTION_CHARS = 1024
MAX_SKILL_MD_LINES = 500
FRONTMATTER_RE = re.compile(r"^\ufeff?---\r?\n(.*?)\r?\n---\r?\n?", re.DOTALL)


@dataclass(frozen=True)
class SkillRecord:
    path: Path
    relpath: Path
    line_count: int
    frontmatter: dict | None

    @property
    def name(self) -> str | None:
        if not isinstance(self.frontmatter, dict):
            return None
        value = self.frontmatter.get("name")
        return value.strip() if isinstance(value, str) else None

    @property
    def description(self) -> str | None:
        if not isinstance(self.frontmatter, dict):
            return None
        value = self.frontmatter.get("description")
        return value if isinstance(value, str) else None


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    path: Path | None
    message: str

    def format(self) -> str:
        location = f" {self.path}" if self.path is not None else ""
        return f"[{self.severity.upper()}] {self.code}:{location} {self.message}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check repository-level skill catalog guardrails."
    )
    parser.add_argument(
        "--root",
        action="append",
        dest="roots",
        help=(
            "Active catalog root relative to the repository root. "
            "May be supplied more than once. Defaults to skills, doctrine/skills, "
            "and 00-meta-initialization."
        ),
    )
    parser.add_argument(
        "--max-active",
        type=int,
        default=DEFAULT_MAX_ACTIVE_SKILLS,
        help=f"Maximum active SKILL.md files allowed. Default: {DEFAULT_MAX_ACTIVE_SKILLS}.",
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Print findings but exit 0. Useful before the catalog is below the cap.",
    )
    return parser.parse_args()


def active_roots(root_args: list[str] | None) -> list[Path]:
    roots = root_args if root_args else list(DEFAULT_ACTIVE_ROOTS)
    resolved: list[Path] = []
    for raw in roots:
        path = (REPO_ROOT / raw).resolve()
        if path.exists():
            resolved.append(path)
    return resolved


def iter_skill_files(roots: Iterable[Path]) -> list[Path]:
    paths: dict[Path, None] = {}
    for root in roots:
        for skill_md in root.rglob("SKILL.md"):
            if any(part.startswith(".") for part in skill_md.relative_to(root).parts):
                continue
            paths[skill_md.resolve()] = None
    return sorted(paths)


def relpath(path: Path) -> Path:
    try:
        return path.relative_to(REPO_ROOT)
    except ValueError:
        return path


def read_skill(path: Path) -> tuple[str | None, Finding | None]:
    try:
        return path.read_text(encoding="utf-8"), None
    except UnicodeDecodeError as exc:
        return None, Finding(
            "error",
            "utf8",
            relpath(path),
            f"SKILL.md is not valid UTF-8: {exc}",
        )


def parse_frontmatter(path: Path, content: str) -> tuple[dict | None, Finding | None]:
    match = FRONTMATTER_RE.match(content)
    if match is None:
        return None, Finding(
            "error",
            "frontmatter",
            relpath(path),
            "missing or malformed YAML frontmatter",
        )

    try:
        parsed = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        return None, Finding(
            "error",
            "frontmatter-yaml",
            relpath(path),
            f"invalid YAML frontmatter: {exc}",
        )

    if not isinstance(parsed, dict):
        return None, Finding(
            "error",
            "frontmatter",
            relpath(path),
            "frontmatter must be a YAML mapping",
        )

    return parsed, None


def collect_records(paths: list[Path]) -> tuple[list[SkillRecord], list[Finding]]:
    records: list[SkillRecord] = []
    findings: list[Finding] = []

    for path in paths:
        content, read_error = read_skill(path)
        if read_error is not None:
            findings.append(read_error)
            continue
        assert content is not None

        frontmatter, fm_error = parse_frontmatter(path, content)
        if fm_error is not None:
            findings.append(fm_error)

        record = SkillRecord(
            path=path,
            relpath=relpath(path),
            line_count=len(content.splitlines()),
            frontmatter=frontmatter,
        )
        records.append(record)

    return records, findings


def check_count(records: list[SkillRecord], max_active: int) -> list[Finding]:
    if len(records) <= max_active:
        return []
    return [
        Finding(
            "error",
            "active-count",
            None,
            f"{len(records)} active SKILL.md files exceeds cap {max_active}",
        )
    ]


def check_duplicate_names(records: list[SkillRecord]) -> list[Finding]:
    by_name: dict[str, list[SkillRecord]] = defaultdict(list)
    for record in records:
        if record.name:
            by_name[record.name].append(record)

    findings: list[Finding] = []
    for name, duplicates in sorted(by_name.items()):
        if len(duplicates) < 2:
            continue
        paths = ", ".join(str(record.relpath) for record in duplicates)
        findings.append(
            Finding(
                "error",
                "duplicate-name",
                None,
                f"frontmatter name `{name}` appears in {paths}",
            )
        )
    return findings


def check_descriptions(records: list[SkillRecord]) -> list[Finding]:
    findings: list[Finding] = []
    for record in records:
        description = record.description
        if description is None:
            continue
        length = len(description.strip())
        if length > MAX_DESCRIPTION_CHARS:
            findings.append(
                Finding(
                    "error",
                    "description-length",
                    record.relpath,
                    f"description is {length} characters; max is {MAX_DESCRIPTION_CHARS}",
                )
            )
    return findings


def check_line_counts(records: list[SkillRecord]) -> list[Finding]:
    findings: list[Finding] = []
    for record in records:
        if record.line_count > MAX_SKILL_MD_LINES:
            findings.append(
                Finding(
                    "error",
                    "skill-lines",
                    record.relpath,
                    f"SKILL.md has {record.line_count} lines; max is {MAX_SKILL_MD_LINES}",
                )
            )
    return findings


def main() -> int:
    args = parse_args()
    roots = active_roots(args.roots)
    paths = iter_skill_files(roots)
    records, findings = collect_records(paths)

    findings.extend(check_count(records, args.max_active))
    findings.extend(check_duplicate_names(records))
    findings.extend(check_descriptions(records))
    findings.extend(check_line_counts(records))

    print("skill-catalog-guardrails:")
    print(f"- repo: {REPO_ROOT}")
    print("- active roots:")
    for root in roots:
        print(f"  - {relpath(root)}")
    print(f"- active SKILL.md files: {len(records)}")
    print(f"- max active SKILL.md files: {args.max_active}")
    print(f"- findings: {len(findings)}")

    for finding in findings:
        print(finding.format())

    if findings and not args.report_only:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
