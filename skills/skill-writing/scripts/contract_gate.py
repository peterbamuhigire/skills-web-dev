#!/usr/bin/env python3
"""
contract_gate.py — Mechanical enforcement of the Evidence Produced contract
(from validation-contract) and Release Evidence Bundle wellformedness.

Run from the repo root; sibling to quick_validate.py.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

REPO_ROOT = Path(__file__).resolve().parents[2]

EXEMPT_SKILLS = {
    "world-class-engineering",
    "skill-composition-standards",
    "validation-contract",
    "capability-matrix",
    "system-architecture-design",
    "engineering-management-system",
    "git-collaboration-workflow",
    "feature-planning",
    "spec-architect",
    "skill-writing",
}

CANONICAL_CATEGORIES = (
    "Correctness",
    "Security",
    "Data safety",
    "Performance",
    "Operability",
    "UX quality",
    "Release evidence",
)

# When item 1 (normalisation rollout) lands, change to "error".
MISSING_SECTION_SEVERITY = "warning"

DUAL_COMPAT_START = "<!-- dual-compat-start -->"
DUAL_COMPAT_END = "<!-- dual-compat-end -->"

EVIDENCE_HEADING_RE = re.compile(r"^## Evidence Produced\s*$", re.MULTILINE)
SECTION_HEADING_RE = re.compile(r"^## ", re.MULTILINE)
TABLE_HEADER_RE = re.compile(
    r"\|\s*Category\s*\|\s*Artifact\s*\|\s*Format\s*\|\s*Example\s*\|", re.IGNORECASE
)
PLACEHOLDER_RE = re.compile(r"<[^>]+>")


@dataclass
class Finding:
    severity: str  # "error" or "warning"
    path: Path
    line: int
    message: str

    def format(self) -> str:
        rel = self.path.relative_to(REPO_ROOT) if self.path.is_relative_to(REPO_ROOT) else self.path
        tag = "[ERROR]  " if self.severity == "error" else "[WARNING]"
        return f"{tag} {rel}:{self.line}: {self.message}"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def line_of_offset(body: str, offset: int) -> int:
    return body.count("\n", 0, offset) + 1


def find_dual_compat_block(body: str) -> tuple[int, int] | None:
    start = body.find(DUAL_COMPAT_START)
    end = body.find(DUAL_COMPAT_END)
    if start == -1 or end == -1 or end <= start:
        return None
    return start, end


def find_evidence_section(body: str) -> tuple[int, int, int] | None:
    """Return (heading_offset, body_start_offset, body_end_offset) or None."""
    match = EVIDENCE_HEADING_RE.search(body)
    if not match:
        return None
    heading_offset = match.start()
    body_start = match.end()
    next_heading = SECTION_HEADING_RE.search(body, body_start + 1)
    body_end = next_heading.start() if next_heading else len(body)
    return heading_offset, body_start, body_end


def parse_evidence_rows(section_body: str) -> list[tuple[int, list[str]]]:
    """Return list of (relative_line_offset, [cells]) for data rows."""
    rows: list[tuple[int, list[str]]] = []
    for i, raw_line in enumerate(section_body.splitlines()):
        line = raw_line.strip()
        if not line.startswith("|"):
            continue
        if TABLE_HEADER_RE.search(line):
            continue
        if re.match(r"^\|[\s|:-]+\|$", line):  # divider row
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        rows.append((i, cells))
    return rows


def check_evidence_produced(skill_dir: Path) -> list[Finding]:
    findings: list[Finding] = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        return findings  # not a skill directory

    body = read_text(skill_md)

    section = find_evidence_section(body)
    if section is None:
        sev = MISSING_SECTION_SEVERITY
        findings.append(Finding(sev, skill_md, 1, "missing ## Evidence Produced section"))
        return findings

    heading_offset, body_start, body_end = section
    heading_line = line_of_offset(body, heading_offset)

    block = find_dual_compat_block(body)
    if block is None:
        findings.append(
            Finding(
                "error",
                skill_md,
                heading_line,
                "no <!-- dual-compat-start/end --> markers found in skill",
            )
        )
    else:
        start, end = block
        if not (start < heading_offset < end):
            findings.append(
                Finding(
                    "error",
                    skill_md,
                    heading_line,
                    "## Evidence Produced is outside the dual-compat block (Codex consumers won't see it)",
                )
            )

    section_body = body[body_start:body_end]

    if not TABLE_HEADER_RE.search(section_body):
        findings.append(
            Finding(
                "error",
                skill_md,
                heading_line,
                "## Evidence Produced section has no canonical table header",
            )
        )
        return findings

    rows = parse_evidence_rows(section_body)
    if not rows:
        findings.append(
            Finding(
                "error",
                skill_md,
                heading_line,
                "## Evidence Produced table has no data rows",
            )
        )
        return findings

    body_start_line = line_of_offset(body, body_start)
    for relative_line, cells in rows:
        absolute_line = body_start_line + relative_line
        if len(cells) != 4:
            findings.append(
                Finding(
                    "error",
                    skill_md,
                    absolute_line,
                    f"row has {len(cells)} cells; expected 4 (Category | Artifact | Format | Example)",
                )
            )
            continue

        category, artifact, fmt, example = cells

        if category not in CANONICAL_CATEGORIES:
            findings.append(
                Finding(
                    "error",
                    skill_md,
                    absolute_line,
                    f"category '{category}' is not one of the seven canonical names: "
                    + ", ".join(CANONICAL_CATEGORIES),
                )
            )

        if not artifact:
            findings.append(
                Finding("error", skill_md, absolute_line, "Artifact column is empty")
            )
        if not fmt:
            findings.append(
                Finding("error", skill_md, absolute_line, "Format column is empty")
            )
        if not example:
            findings.append(
                Finding("error", skill_md, absolute_line, "Example column is empty")
            )

    return findings


def check_bundle(bundle_path: Path) -> list[Finding]:
    findings: list[Finding] = []
    if not bundle_path.is_file():
        findings.append(
            Finding("error", bundle_path, 1, "bundle file does not exist")
        )
        return findings

    body = read_text(bundle_path)

    expected_sections = [
        f"## {n}. {cat}"
        for n, cat in enumerate(CANONICAL_CATEGORIES, start=1)
    ]
    for heading in expected_sections:
        if heading not in body:
            findings.append(
                Finding(
                    "error",
                    bundle_path,
                    1,
                    f"missing required section: '{heading}'",
                )
            )

    for line_no, raw_line in enumerate(body.splitlines(), start=1):
        line = raw_line.strip()
        if not line.startswith("- "):
            continue
        # bullet of the form "- Label: value"
        match = re.match(r"^-\s+([^:]+):\s*(.*)$", line)
        if not match:
            continue
        label, value = match.group(1).strip(), match.group(2).strip()
        if not value:
            findings.append(
                Finding(
                    "error",
                    bundle_path,
                    line_no,
                    f"bullet '{label}' has empty value",
                )
            )
            continue
        if value.startswith("N/A"):
            tail = value[3:].strip()
            if not tail.startswith("—") and not tail.startswith("-"):
                findings.append(
                    Finding(
                        "error",
                        bundle_path,
                        line_no,
                        f"bullet '{label}' uses N/A without a reason (expected 'N/A — <reason>')",
                    )
                )
            else:
                reason = tail.lstrip("—-").strip()
                if not reason:
                    findings.append(
                        Finding(
                            "error",
                            bundle_path,
                            line_no,
                            f"bullet '{label}' uses N/A with empty reason",
                        )
                    )
            continue
        if PLACEHOLDER_RE.search(value):
            findings.append(
                Finding(
                    "warning",
                    bundle_path,
                    line_no,
                    f"bullet '{label}' still contains placeholder '{value}'",
                )
            )

    return findings


def check_inputs_outputs(skill_dir: Path) -> list[Finding]:
    """Stub: Inputs Contract / Outputs Contract checking deferred until
    skill-composition-standards defines the table form."""
    return []


def iter_skill_dirs() -> Iterable[Path]:
    for path in sorted(REPO_ROOT.iterdir()):
        if not path.is_dir():
            continue
        if path.name.startswith("."):
            continue
        if not (path / "SKILL.md").is_file():
            continue
        yield path


def run_evidence_check(skill_filter: str | None) -> tuple[list[Finding], int, int]:
    findings: list[Finding] = []
    scanned = 0
    exempt = 0
    for skill_dir in iter_skill_dirs():
        name = skill_dir.name
        if skill_filter and name != skill_filter:
            continue
        if name in EXEMPT_SKILLS:
            exempt += 1
            continue
        scanned += 1
        findings.extend(check_evidence_produced(skill_dir))
    return findings, scanned, exempt


def emit(findings: list[Finding]) -> None:
    for f in findings:
        print(f.format(), file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Mechanical enforcement of validation-contract declarations."
    )
    parser.add_argument(
        "--evidence",
        action="store_true",
        help="Run Evidence Produced check across specialist skills.",
    )
    parser.add_argument(
        "--bundle",
        metavar="PATH",
        help="Run Release Evidence Bundle check on the given file.",
    )
    parser.add_argument(
        "--skill",
        metavar="NAME",
        help="Limit Evidence check to one skill directory name.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as errors (exit 1 instead of 0).",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run --evidence on the whole repo (default if no other action).",
    )
    args = parser.parse_args()

    do_evidence = args.evidence or args.all or (not args.bundle and not args.skill)
    if args.skill:
        do_evidence = True

    all_findings: list[Finding] = []
    summary_parts: list[str] = []

    if do_evidence:
        findings, scanned, exempt = run_evidence_check(args.skill)
        all_findings.extend(findings)
        errors = sum(1 for f in findings if f.severity == "error")
        warnings = sum(1 for f in findings if f.severity == "warning")
        summary_parts.append(
            f"evidence: scanned {scanned} | {errors} errors | {warnings} warnings | {exempt} exempt"
        )

    if args.bundle:
        bundle_path = Path(args.bundle)
        if not bundle_path.is_absolute():
            bundle_path = (REPO_ROOT / bundle_path).resolve()
        bundle_findings = check_bundle(bundle_path)
        all_findings.extend(bundle_findings)
        errors = sum(1 for f in bundle_findings if f.severity == "error")
        warnings = sum(1 for f in bundle_findings if f.severity == "warning")
        summary_parts.append(
            f"bundle: {bundle_path.name} | {errors} errors | {warnings} warnings"
        )

    emit(all_findings)
    print("contract-gate: " + " | ".join(summary_parts))

    has_errors = any(f.severity == "error" for f in all_findings)
    has_warnings = any(f.severity == "warning" for f in all_findings)

    if has_errors:
        return 1
    if has_warnings and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
