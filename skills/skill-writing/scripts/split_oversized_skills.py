#!/usr/bin/env python3
"""
Split oversized SKILL.md files into lean entrypoints plus deep-dive references.
"""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MAX_LINES = 500
TARGET_PREFIX_LINES = 430


def build_summary(skill_name: str, ref_path: str, moved_headings: list[str]) -> str:
    bullets = "\n".join(f"- `{heading}`" for heading in moved_headings[:12])
    if len(moved_headings) > 12:
        bullets += "\n- Additional deep-dive sections continue in the reference file."

    return (
        "## Additional Guidance\n\n"
        f"Extended guidance for `{skill_name}` was moved to "
        f"[{ref_path}]({ref_path}) to keep this entrypoint compact and fast to load.\n\n"
        "Use that deep dive for:\n"
        f"{bullets}\n"
    )


def split_skill(skill_md: Path) -> bool:
    lines = skill_md.read_text(encoding="utf-8").splitlines()
    if len(lines) <= MAX_LINES:
        return False

    heading_indexes = [
        idx for idx, line in enumerate(lines)
        if line.startswith("## ") and idx > 80
    ]
    split_at = None
    moved_headings: list[str] = []
    for idx in heading_indexes:
        tail = lines[idx:]
        headings = [line[3:].strip() for line in tail if line.startswith("## ")]
        estimated_total = idx + len(headings) + 8
        if idx <= TARGET_PREFIX_LINES and len(tail) >= 20 and estimated_total <= MAX_LINES:
            split_at = idx
            moved_headings = headings
            break

    if split_at is None:
        return False

    prefix = "\n".join(lines[:split_at]).rstrip() + "\n\n"
    moved = "\n".join(lines[split_at:]).rstrip() + "\n"

    references_dir = skill_md.parent / "references"
    references_dir.mkdir(exist_ok=True)
    ref_name = "skill-deep-dive.md"
    ref_path = references_dir / ref_name

    skill_name = skill_md.parent.name
    ref_body = (
        f"# {skill_name} Deep Dive\n\n"
        f"This file contains the extended guidance moved out of "
        f"[../SKILL.md](../SKILL.md) so the skill entrypoint stays under the repository size limit.\n\n"
        "## Included Sections\n\n"
        + "\n".join(f"- `{heading}`" for heading in moved_headings)
        + "\n\n"
        + moved
    )
    ref_path.write_text(ref_body, encoding="utf-8", newline="\n")

    summary = build_summary(skill_name, f"references/{ref_name}", moved_headings)
    skill_md.write_text(prefix + summary, encoding="utf-8", newline="\n")
    return True


def main() -> None:
    changed = 0
    for skill_md in sorted(REPO_ROOT.glob("*/SKILL.md")):
        if split_skill(skill_md):
            changed += 1
            print(skill_md.relative_to(REPO_ROOT))
    print(f"Split {changed} oversized skills.")


if __name__ == "__main__":
    main()
