#!/usr/bin/env python3
"""
Upgrade repository skills to a dual-compatible Claude Code and Codex format.

This script preserves the existing body of each skill while injecting a compact
portable contract section that gives both tools a consistent execution surface.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
MARKER_START = "<!-- dual-compat-start -->"
MARKER_END = "<!-- dual-compat-end -->"

PLUGIN_BLOCK_RE = re.compile(
    r"(^|\n)## Required Plugins\s*\n\s*\n\*\*Superpowers plugin:\*\*.*?(?=\n## |\n# |\Z)",
    re.DOTALL,
)
FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\n?", re.DOTALL)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    match = FRONTMATTER_RE.match(text)
    if not match:
        raise ValueError("Missing YAML frontmatter")
    frontmatter_text = match.group(1)
    try:
        frontmatter = yaml.safe_load(frontmatter_text)
    except yaml.YAMLError:
        frontmatter = parse_simple_frontmatter(frontmatter_text)
    if not isinstance(frontmatter, dict):
        raise ValueError("Frontmatter must be a mapping")
    body = text[match.end() :].lstrip("\n")
    return frontmatter, body


def parse_simple_frontmatter(frontmatter_text: str) -> dict:
    result: dict[str, object] = {}
    current_key: str | None = None
    for raw_line in frontmatter_text.splitlines():
        if raw_line.strip() == "":
            continue
        if raw_line.startswith((" ", "\t")) and current_key:
            previous = str(result.get(current_key, ""))
            result[current_key] = (previous + " " + raw_line.strip()).strip()
            continue
        if ":" not in raw_line:
            continue
        key, value = raw_line.split(":", 1)
        current_key = key.strip()
        result[current_key] = value.strip()
    return result


def dump_frontmatter(frontmatter: dict) -> str:
    return "---\n" + yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True).strip() + "\n---\n\n"


def normalize_frontmatter(frontmatter: dict, skill_name: str) -> dict:
    frontmatter = dict(frontmatter)
    frontmatter["name"] = str(frontmatter.get("name", skill_name)).strip()
    description = str(frontmatter.get("description", "")).strip()
    if description == "":
        description = f"Use when working on {skill_name.replace('-', ' ')} tasks."

    description = description.replace("Claude Code skills", "skills")
    description = description.replace("Claude Code", "Claude Code and Codex")
    frontmatter["description"] = description

    metadata = frontmatter.get("metadata")
    if not isinstance(metadata, dict):
        metadata = {}

    compatibility = frontmatter.pop("compatibility", None)
    if compatibility:
        metadata["compatibility_notes"] = str(compatibility).strip()

    metadata["portable"] = True
    metadata["compatible_with"] = ["claude-code", "codex"]
    frontmatter["metadata"] = metadata
    return frontmatter


def replace_plugin_block(body: str) -> str:
    replacement = (
        "\n## Platform Notes\n\n"
        "- Claude Code: use Superpowers or similar helpers when they are available and materially useful.\n"
        "- Codex: apply this skill normally; do not treat optional plugins as a prerequisite.\n"
    )
    return PLUGIN_BLOCK_RE.sub(replacement, body)


def build_contract(skill_dir: Path, description: str) -> str:
    available = []
    for folder in [
        "references",
        "examples",
        "templates",
        "scripts",
        "protocols",
        "sections",
        "documentation",
    ]:
        if (skill_dir / folder).exists():
            available.append(folder)

    input_note = "relevant project context, constraints, and the concrete problem to solve"
    if available:
        input_note += f"; load `{', '.join(available)}` only as needed"

    references_lines = []
    if (skill_dir / "references").exists():
        references_lines.append("- Use the `references/` directory for deep detail after reading the core workflow below.")
    if (skill_dir / "examples").exists():
        references_lines.append("- Use the `examples/` directory for concrete patterns when implementation shape matters.")
    if (skill_dir / "templates").exists():
        references_lines.append("- Use the `templates/` directory when the task needs a structured deliverable.")
    if (skill_dir / "scripts").exists():
        references_lines.append("- Use the `scripts/` directory for repository-native automation before inventing new tooling.")
    if (skill_dir / "protocols").exists():
        references_lines.append("- Use the `protocols/` directory for formal execution order or handoff rules.")
    if (skill_dir / "sections").exists():
        references_lines.append("- Use the `sections/` directory for modular deep dives and load only the parts relevant to the task.")
    if (skill_dir / "documentation").exists():
        references_lines.append("- Use the `documentation/` directory for supporting implementation detail or migration notes.")
    if not references_lines:
        references_lines.append("- Use the links and companion skills already referenced in this file when deeper context is needed.")

    return "\n".join(
        [
            MARKER_START,
            "## Use When",
            "",
            f"- {description}",
            "- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.",
            "",
            "## Do Not Use When",
            "",
            f"- The task is unrelated to `{skill_dir.name}` or would be better handled by a more specific companion skill.",
            "- The request only needs a trivial answer and none of this skill's constraints or references materially help.",
            "",
            "## Required Inputs",
            "",
            f"- Gather {input_note}.",
            "- Confirm the desired deliverable: design, code, review, migration plan, audit, or documentation.",
            "",
            "## Workflow",
            "",
            "- Read this `SKILL.md` first, then load only the referenced deep-dive files that are necessary for the task.",
            "- Apply the ordered guidance, checklists, and decision rules in this skill instead of cherry-picking isolated snippets.",
            "- Produce the deliverable with assumptions, risks, and follow-up work made explicit when they matter.",
            "",
            "## Quality Standards",
            "",
            "- Keep outputs execution-oriented, concise, and aligned with the repository's baseline engineering standards.",
            "- Preserve compatibility with existing project conventions unless the skill explicitly requires a stronger standard.",
            "- Prefer deterministic, reviewable steps over vague advice or tool-specific magic.",
            "",
            "## Anti-Patterns",
            "",
            "- Treating examples as copy-paste truth without checking fit, constraints, or failure modes.",
            "- Loading every reference file by default instead of using progressive disclosure.",
            "",
            "## Outputs",
            "",
            "- A concrete result that fits the task: implementation guidance, review findings, architecture decisions, templates, or generated artifacts.",
            "- Clear assumptions, tradeoffs, or unresolved gaps when the task cannot be completed from available context alone.",
            "- References used, companion skills, or follow-up actions when they materially improve execution.",
            "",
            "## References",
            "",
            *references_lines,
            MARKER_END,
            "",
        ]
    )


def inject_contract(body: str, contract: str) -> str:
    if MARKER_START in body and MARKER_END in body:
        body = re.sub(
            rf"{re.escape(MARKER_START)}.*?{re.escape(MARKER_END)}\n*",
            contract,
            body,
            flags=re.DOTALL,
        )
        return body

    heading_match = re.search(r"^# .+$", body, re.MULTILINE)
    if heading_match:
        insert_at = heading_match.end()
        return body[:insert_at] + "\n\n" + contract + body[insert_at:].lstrip("\n")
    return contract + body


def upgrade_skill(skill_md: Path) -> None:
    raw = skill_md.read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(raw)
    frontmatter = normalize_frontmatter(frontmatter, skill_md.parent.name)
    body = replace_plugin_block(body)
    contract = build_contract(skill_md.parent, frontmatter["description"])
    body = inject_contract(body, contract)
    upgraded = dump_frontmatter(frontmatter) + body.rstrip() + "\n"
    skill_md.write_text(upgraded, encoding="utf-8", newline="\n")


def main() -> None:
    for skill_md in sorted(REPO_ROOT.glob("*/SKILL.md")):
        upgrade_skill(skill_md)


if __name__ == "__main__":
    main()
