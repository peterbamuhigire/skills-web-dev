import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


VALIDATE_MODULE = load_module(
    "validate_engine_control_plane",
    ROOT / "scripts" / "validate_engine_control_plane.py",
)
COMPLIANCE_SCRIPT = (
    ROOT
    / "skills"
    / "sdlc-meta"
    / "skill-engine-audit"
    / "scripts"
    / "engine_compliance.py"
)
COMPLIANCE_MODULE = load_module("engine_compliance", COMPLIANCE_SCRIPT)

EXPECTED_ACTIVE_SKILL_COUNT = 179
EXPECTED_CLAUDE_BRIDGE = "# Claude Code repository memory\n\n@AGENTS.md\n"
PORTABLE_SECTION_ALIASES = {
    "Use When": ("Use When",),
    "Do Not Use When": ("Do Not Use When", "Degraded mode"),
    "Required Inputs": ("Required Inputs", "Inputs"),
    "Workflow": ("Workflow", "Operating contract", "Decision rules"),
    "Quality Standards": (
        "Quality Standards",
        "Capability contract",
        "Capability and permission boundaries",
        "Non-negotiables",
    ),
    "Anti-Patterns": ("Anti-Patterns", "Domain anti-patterns"),
    "Outputs": ("Outputs",),
    "References": ("References", "Read next", "Companion Skills", "Companion skills"),
}


def portable_contract_failures(text: str) -> list[str]:
    """Check that the governing contract is in one portable block.

    The generic engine assessor checks for headings anywhere in the document.
    Governing skills also need those headings inside the one dual-compat block
    so Claude and Codex receive the same contract.
    """
    start_marker = "<!-- dual-compat-start -->"
    end_marker = "<!-- dual-compat-end -->"
    starts = [match.start() for match in re.finditer(re.escape(start_marker), text)]
    ends = [match.start() for match in re.finditer(re.escape(end_marker), text)]
    if len(starts) != 1 or len(ends) != 1 or ends[0] <= starts[0]:
        return ["dual-compat marker pair"]

    portable_body = text[starts[0] + len(start_marker) : ends[0]]
    failures = []
    for required, aliases in PORTABLE_SECTION_ALIASES.items():
        if not any(
            re.search(rf"^##\s+{re.escape(alias)}\s*$", portable_body, re.MULTILINE | re.IGNORECASE)
            for alias in aliases
        ):
            failures.append(required)
    return failures


def bridge_failures(text: str) -> list[str]:
    return [] if text == EXPECTED_CLAUDE_BRIDGE else ["bridge is not the canonical thin import"]


def count_surface_mismatches(surface_texts: dict[str, str], expected: str) -> dict[str, list[str | None]]:
    surfaces = {
        "README.md": r"\| Active `SKILL\.md` files \| (\d+) \|",
        "AGENTS.md": r"Active `SKILL\.md` files: (\d+)\.",
        "docs/skill-routing-index.md": r"\| Active `SKILL\.md` files \| (\d+) \|",
        "docs/overview/README.md": r"Current active catalog size is (\d+) skills\.",
        "docs/overview/PROJECT_BRIEF.md": r"active skill count is (\d+),",
        "docs/plans/NEXT_FEATURES.md": r"The current count is (\d+) after",
        "docs/skill-aliases.yml": r"current_active_skill_count: (\d+)",
    }
    mismatches = {}
    for relative, pattern in surfaces.items():
        matches = re.findall(pattern, surface_texts[relative])
        if len(matches) != 1 or matches[0] != expected:
            mismatches[relative] = matches or [None]
    return mismatches


def test_control_plane_registry_has_all_eleven_engines():
    assert VALIDATE_MODULE.validate_registry() == []


def test_control_plane_registry_resolves_local_routers():
    workspace_root = Path(__file__).resolve().parents[2]
    assert VALIDATE_MODULE.validate_registry(workspace_root) == []


def test_control_plane_registry_resolves_local_adoption_documents():
    workspace_root = Path(__file__).resolve().parents[2]
    assert VALIDATE_MODULE.validate_registry(workspace_root) == []


def test_governing_skills_meet_current_authoring_contract():
    failures = {}
    for relative in (
        "skills/sdlc-meta/engine-control-plane/SKILL.md",
        "skills/sdlc-meta/kaizen-improvement-system/SKILL.md",
    ):
        result = COMPLIANCE_MODULE.assess(ROOT / relative, ROOT)
        assert result["score"] == 14
        assert result["possible"] == 14
        if result["failed"]:
            failures[relative] = result["failed"]
        portable_failures = portable_contract_failures(
            (ROOT / relative).read_text(encoding="utf-8")
        )
        if portable_failures:
            failures[relative] = ["portable_contract_scope", *portable_failures]
    assert failures == {}


def test_claude_bridge_is_thin_and_imports_canonical_agents_guide():
    bridge = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
    assert bridge_failures(bridge) == []


def test_governing_contract_mutation_is_rejected(tmp_path):
    source = (ROOT / "skills/sdlc-meta/engine-control-plane/SKILL.md").read_text(
        encoding="utf-8"
    )
    mutated = source.replace("## Workflow\n", "Moved workflow contract.\n", 1).replace(
        "<!-- dual-compat-end -->",
        "<!-- dual-compat-end -->\n## Workflow\nMoved workflow contract.\n",
        1,
    )
    mutated_path = tmp_path / "engine-control-plane" / "SKILL.md"
    mutated_path.parent.mkdir()
    mutated_path.write_text(mutated, encoding="utf-8")

    # Keep the mutation in a temporary skill-shaped path, then apply the
    # independent governing-scope check to the resulting file content.
    assert portable_contract_failures(mutated_path.read_text(encoding="utf-8")) == [
        "Workflow"
    ]


def test_claude_bridge_mutation_is_rejected():
    mutated = EXPECTED_CLAUDE_BRIDGE.rstrip("\n") + "\n- duplicated canonical guidance\n"
    assert "@AGENTS.md" in mutated
    assert len(mutated.splitlines()) <= 4
    assert bridge_failures(mutated) == ["bridge is not the canonical thin import"]


def test_current_active_count_matches_filesystem_and_documented_surfaces():
    active_roots = (ROOT / "skills", ROOT / "00-meta-initialization")
    active_count = sum(
        1
        for active_root in active_roots
        for skill_md in active_root.rglob("SKILL.md")
        if not any(part.startswith(".") for part in skill_md.relative_to(active_root).parts)
    )
    assert active_count == EXPECTED_ACTIVE_SKILL_COUNT
    expected = str(active_count)
    surface_texts = {
        relative: (ROOT / relative).read_text(encoding="utf-8")
        for relative in (
            "README.md",
            "AGENTS.md",
            "docs/skill-routing-index.md",
            "docs/overview/README.md",
            "docs/overview/PROJECT_BRIEF.md",
            "docs/plans/NEXT_FEATURES.md",
            "docs/skill-aliases.yml",
        )
    }
    assert count_surface_mismatches(surface_texts, expected) == {}


def test_count_surface_mutation_is_rejected():
    surface_texts = {
        relative: (ROOT / relative).read_text(encoding="utf-8")
        for relative in (
            "README.md",
            "AGENTS.md",
            "docs/skill-routing-index.md",
            "docs/overview/README.md",
            "docs/overview/PROJECT_BRIEF.md",
            "docs/plans/NEXT_FEATURES.md",
            "docs/skill-aliases.yml",
        )
    }
    surface_texts["README.md"] = surface_texts["README.md"].replace(
        "| Active `SKILL.md` files | 179 |",
        "| Active `SKILL.md` files | 178 |",
        1,
    )
    assert count_surface_mismatches(surface_texts, str(EXPECTED_ACTIVE_SKILL_COUNT)) == {
        "README.md": ["178"]
    }
