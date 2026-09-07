#!/usr/bin/env python3
"""Audit skill engines against the portable skill-writing contract.

Default mode is read-only. --fix-safe only repairs deterministic metadata,
exact known boilerplate, and mojibake; domain judgement remains manual.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

import yaml


SECTIONS = ("Use When", "Do Not Use When", "Required Inputs", "Workflow", "Quality Standards", "Anti-Patterns", "Outputs", "References")
COMPATIBILITY = ["claude-code", "codex"]
FRONTMATTER_RE = re.compile(r"^\ufeff?---\r?\n(.*?)\r?\n---\r?\n?", re.DOTALL)
MOJIBAKE = ("Ã", "Â", "â€", "â†", "âœ", "ðŸ", "\ufffd")
KNOWN_BOILERPLATE = (
    "- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.\n",
    "- The request only needs a trivial answer and none of this skill's constraints or references materially help.\n",
    "- Confirm the desired deliverable: design, code, review, migration plan, audit, or documentation.\n",
    "- Read this `SKILL.md` first, then load only the referenced deep-dive files that are necessary for the task.\n",
    "- Apply the ordered guidance, checklists, and decision rules in this skill instead of cherry-picking isolated snippets.\n",
    "- Produce the deliverable with assumptions, risks, and follow-up work made explicit when they matter.\n",
    "- Keep outputs execution-oriented, concise, and aligned with the repository's baseline engineering standards.\n",
    "- Preserve compatibility with existing project conventions unless the skill explicitly requires a stronger standard.\n",
    "- Prefer deterministic, reviewable steps over vague advice or tool-specific magic.\n",
    "- Treating examples as copy-paste truth without checking fit, constraints, or failure modes.\n",
    "- Loading every reference file by default instead of using progressive disclosure.\n",
    "- A concrete result that fits the task: implementation guidance, review findings, architecture decisions, templates, or generated artifacts.\n",
    "- Clear assumptions, tradeoffs, or unresolved gaps when the task cannot be completed from available context alone.\n",
    "- References used, companion skills, or follow-up actions when they materially improve execution.\n",
)


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--active-root", action="append", default=[])
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--details", action="store_true")
    parser.add_argument("--fix-safe", action="store_true")
    return parser.parse_args()


def repair_mojibake(text: str) -> str:
    candidate = text
    for _ in range(3):
        if not any(marker in candidate for marker in MOJIBAKE):
            break
        improved = candidate
        for encoding in ("cp1252", "latin1"):
            try:
                decoded = candidate.encode(encoding).decode("utf-8")
            except (UnicodeEncodeError, UnicodeDecodeError):
                continue
            if sum(decoded.count(m) for m in MOJIBAKE) < sum(improved.count(m) for m in MOJIBAKE):
                improved = decoded
        if improved == candidate:
            break
        candidate = improved
    return candidate


def parse(path: Path) -> tuple[dict, str, str, list[str]]:
    raw = path.read_text(encoding="utf-8", errors="replace")
    match = FRONTMATTER_RE.match(raw)
    if not match:
        return {}, raw, raw, ["frontmatter"]
    try:
        frontmatter = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        return {}, raw[match.end():], raw, ["frontmatter-yaml"]
    if not isinstance(frontmatter, dict):
        return {}, raw[match.end():], raw, ["frontmatter-type"]
    return frontmatter, raw[match.end():], raw, []


def heading(body: str, name: str) -> bool:
    return re.search(rf"^##\s+{re.escape(name)}\s*$", body, re.MULTILINE | re.IGNORECASE) is not None


def assess(path: Path, root: Path) -> dict:
    frontmatter, body, raw, errors = parse(path)
    description = frontmatter.get("description", "")
    metadata = frontmatter.get("metadata")
    metadata = metadata if isinstance(metadata, dict) else {}
    section_groups = {
        "Use When": (["Use When"], "use_when"),
        "Do Not Use When": (["Do Not Use When", "Degraded mode"], "do_not_use_when"),
        "Required Inputs": (["Required Inputs", "Inputs"], "required_inputs"),
        "Workflow": (["Workflow", "Operating contract", "Decision rules"], "workflow"),
        "Quality Standards": (["Quality Standards", "Capability contract", "Capability and permission boundaries", "Non-negotiables"], "quality_standards"),
        "Anti-Patterns": (["Anti-Patterns", "Domain anti-patterns"], "anti_patterns"),
        "Outputs": (["Outputs"], "outputs"),
        "References": (["References", "Read next", "Companion Skills"], "references"),
    }
    anti_sections = re.findall(
        r"^##\s+(?:Domain\s+)?Anti-Patterns\s*$([\s\S]*?)(?=^##\s|\Z)",
        body,
        re.MULTILINE | re.IGNORECASE,
    )
    checks = {
        "unique_description": len(re.findall(r"^description\s*:", FRONTMATTER_RE.match(raw).group(1), re.MULTILINE)) == 1 if FRONTMATTER_RE.match(raw) else False,
        "identity": frontmatter.get("name") == path.parent.name,
        "trigger": isinstance(description, str) and description.strip().lower().startswith("use when") and len(description.strip()) <= 350,
        "portable_metadata": metadata.get("portable") is True and valid_compatibility(metadata.get("compatible_with")),
        "portable_sections": all(
            any(heading(body, alias) for alias in aliases) or bool(metadata.get(metadata_key))
            for aliases, metadata_key in section_groups.values()
        ),
        "input_contract": bool(re.search(r"^##\s+(?:Required )?Inputs\s*$", body, re.MULTILINE | re.IGNORECASE) and (re.search(r"^##\s+(?:Required )?Inputs\s*$[\s\S]{0,1400}\|", body, re.MULTILINE | re.IGNORECASE) or re.search(r"^##\s+(?:Required )?Inputs\s*$[\s\S]{0,300}\bNone\b", body, re.MULTILINE | re.IGNORECASE))),
        "output_contract": heading(body, "Outputs"),
        "decision_rules": bool(re.search(r"^##\s+Decision", body, re.MULTILINE | re.IGNORECASE)),
        "five_anti_patterns": sum(
            len(re.findall(r"^\s*[-*]\s+|^\s*\d+\.\s+", section, re.MULTILINE))
            for section in anti_sections
        ) >= 5,
        "capability_contract": bool(re.search(r"capabilit|permission", body, re.IGNORECASE)),
        "degraded_mode": bool(re.search(r"fallback|read-only|when .{0,40} unavailable|if .{0,40} unavailable", body, re.IGNORECASE)),
        "encoding_clean": not any(marker in raw for marker in MOJIBAKE),
        "line_limit": len(raw.splitlines()) <= 500,
        "no_empty_contract_sections": not bool(
            re.search(
                r"^##\s+(?:Use When|Do Not Use When|Required Inputs|Workflow|Quality Standards|Anti-Patterns|Outputs|References)\s*$\n(?=\s*(?:##|<!-- dual-compat-end -->))",
                body,
                re.MULTILINE | re.IGNORECASE,
            )
        ),
    }
    failed = [name for name, passed in checks.items() if not passed] + errors
    return {"path": path.relative_to(root).as_posix(), "score": sum(checks.values()), "possible": len(checks), "failed": failed}


def valid_compatibility(value: object) -> bool:
    """Require the canonical runtimes without discarding additional adapters."""
    return (
        isinstance(value, list)
        and all(isinstance(item, str) and item.strip() for item in value)
        and len(value) == len(set(value))
        and set(COMPATIBILITY) <= set(value)
    )


def safe_fix(path: Path) -> bool:
    raw = path.read_text(encoding="utf-8", errors="replace")
    fixed = repair_mojibake(raw)
    match = FRONTMATTER_RE.match(fixed)
    if match:
        try:
            frontmatter = yaml.safe_load(match.group(1)) or {}
        except yaml.YAMLError:
            frontmatter = None
        if isinstance(frontmatter, dict):
            metadata = frontmatter.get("metadata")
            if not isinstance(metadata, dict):
                metadata = {}
            metadata["portable"] = True
            existing = metadata.get("compatible_with", [])
            extras = [item for item in existing if isinstance(item, str) and item.strip() and item.casefold() not in COMPATIBILITY] if isinstance(existing, list) else []
            metadata["compatible_with"] = list(dict.fromkeys([*COMPATIBILITY, *extras]))
            frontmatter["metadata"] = metadata
            prefix = "---\n" + yaml.safe_dump(frontmatter, sort_keys=False, allow_unicode=True, width=1000).strip() + "\n---\n"
            fixed = prefix + fixed[match.end():]
            fixed = re.sub(
                r"^##\s+(?:Use When|Do Not Use When|Required Inputs|Workflow|Quality Standards|Anti-Patterns|Outputs|References)\s*$\n(?=\s*(?:##|<!-- dual-compat-end -->))",
                "",
                fixed,
                flags=re.MULTILINE | re.IGNORECASE,
            )
    for line in KNOWN_BOILERPLATE:
        fixed = fixed.replace(line, "")
    fixed = re.sub(
        r"^- The task is unrelated to `[^`]+` or would be better handled by a more specific companion skill\.\n",
        "",
        fixed,
        flags=re.MULTILINE,
    )
    fixed = re.sub(
        r"^- Gather relevant project context, constraints, and the concrete problem to solve(?:; load `[^`]+` only as needed)?\.\n",
        "",
        fixed,
        flags=re.MULTILINE,
    )
    if fixed == raw:
        return False
    path.write_text(fixed, encoding="utf-8", newline="\n")
    return True


def main() -> int:
    args = arguments()
    root = args.root.resolve()
    active = args.active_root or ["skills"]
    files = sorted(path for relative in active for path in (root / relative).rglob("SKILL.md") if path.is_file())
    changed = [path.relative_to(root).as_posix() for path in files if args.fix_safe and safe_fix(path)]
    results = [assess(path, root) for path in files]
    failures: Counter[str] = Counter()
    groups: dict[str, list[int]] = defaultdict(list)
    for result in results:
        failures.update(result["failed"])
        parts = Path(result["path"]).parts
        groups[parts[1] if len(parts) > 2 else parts[0]].append(result["score"])
    payload = {
        "root": str(root), "skills": len(results), "changed": changed,
        "fully_compliant": sum(not result["failed"] for result in results),
        "failure_counts": dict(sorted(failures.items())),
        "group_average": {group: round(sum(scores) / len(scores), 2) for group, scores in sorted(groups.items())},
        "results": results if args.details or args.json else [],
    }
    if args.json:
        print(json.dumps(payload, indent=2))
    else:
        print(f"engine-compliance: {root}")
        print(f"- skills: {payload['skills']}")
        print(f"- fully compliant: {payload['fully_compliant']}")
        print(f"- safe fixes applied: {len(changed)}")
        print("- failure counts:")
        for name, count in payload["failure_counts"].items():
            print(f"  - {name}: {count}")
        if args.details:
            for result in results:
                if result["failed"]:
                    print(f"- {result['path']}: {', '.join(result['failed'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
