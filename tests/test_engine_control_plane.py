import importlib.util
import re
import sys
import os
import json
import pytest
import subprocess
from contextlib import contextmanager
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


def test_control_plane_registry_has_all_twelve_engines():
    assert VALIDATE_MODULE.validate_registry() == []


@pytest.mark.skipif(os.environ.get("SKILL_ENGINE_LIVE_TESTS") != "1", reason="NOT ASSESSED: opt in to installed-portfolio checks with SKILL_ENGINE_LIVE_TESTS=1")
def test_control_plane_registry_resolves_local_routers():
    workspace_root = Path(__file__).resolve().parents[2]
    # This host's confirmed portfolio comprises eleven installed engines.
    # The full twelve-entry registry is independently checked above.
    assert VALIDATE_MODULE.validate_registry(workspace_root, VALIDATE_MODULE.EXPECTED_ENGINES - {"political"}) == []


def test_control_plane_registry_resolves_fixture_and_reports_missing_contract(tmp_path, monkeypatch):
    data = json.loads(VALIDATE_MODULE.REGISTRY.read_text(encoding="utf-8"))
    for engine in data["engines"]:
        checkout = tmp_path / engine["id"]
        monkeypatch.setenv(f"SKILL_ENGINE_ROOT_{engine['id'].upper().replace('-', '_')}", str(checkout))
        for key in ("router", "adoption_doc"):
            target = checkout / engine[key]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("Fixture contract\n", encoding="utf-8")
    assert VALIDATE_MODULE.validate_registry(tmp_path) == []
    political = next(engine for engine in data["engines"] if engine["id"] == "political")
    (tmp_path / "political" / political["adoption_doc"]).unlink()
    errors = VALIDATE_MODULE.validate_registry(tmp_path)
    assert len(errors) == 1
    assert errors[0].startswith("political: no candidate")
    assert VALIDATE_MODULE.validate_registry(tmp_path, VALIDATE_MODULE.EXPECTED_ENGINES - {"political"}) == []
    assert VALIDATE_MODULE.validate_registry(tmp_path, {"unknown"})


@pytest.mark.parametrize("engine_id", ["business-plan", "proposal", "social-media", "accounting"])
def test_workspace_checkout_precedes_home_duplicate(tmp_path, monkeypatch, engine_id):
    monkeypatch.delenv(f"SKILL_ENGINE_ROOT_{engine_id.upper().replace('-', '_')}", raising=False)
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path / "user"))
    canonical = tmp_path / "workspace" / VALIDATE_MODULE.ENGINE_DIRS[engine_id]
    duplicate = tmp_path / "user" / "source" / "repos" / VALIDATE_MODULE.ENGINE_DIRS[engine_id]
    for checkout in (canonical, duplicate):
        checkout.mkdir(parents=True)
        (checkout / "AGENTS.md").write_text("Fixture\n", encoding="utf-8")
        (checkout / "adoption.md").write_text("Fixture\n", encoding="utf-8")
    assert VALIDATE_MODULE.resolve_engine_dir(tmp_path / "workspace", engine_id, "AGENTS.md", "adoption.md") == canonical
    (canonical / "adoption.md").unlink()
    assert VALIDATE_MODULE.resolve_engine_dir(tmp_path / "workspace", engine_id, "AGENTS.md", "adoption.md") is None


def test_invalid_override_does_not_fall_back(tmp_path, monkeypatch):
    duplicate = tmp_path / "digital-research-skills"
    duplicate.mkdir()
    for name in ("AGENTS.md", "adoption.md"):
        (duplicate / name).write_text("Fixture\n", encoding="utf-8")
    monkeypatch.setenv("SKILL_ENGINE_ROOT_DIGITAL_RESEARCH", str(tmp_path / "absent"))
    assert VALIDATE_MODULE.resolve_engine_dir(tmp_path, "digital-research", "AGENTS.md", "adoption.md") is None


@pytest.mark.parametrize("payload", [[], {"engines": [None]}, {"engines": [{"id": []}]}, {"engines": [{"id": "unknown"}]}])
def test_malformed_registry_reports_errors_without_crashing(tmp_path, monkeypatch, payload):
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(VALIDATE_MODULE, "REGISTRY", registry)
    assert VALIDATE_MODULE.validate_registry(tmp_path)


@pytest.mark.parametrize("unsafe", ["../AGENTS.md", "..\\AGENTS.md", "/AGENTS.md", "C:/AGENTS.md", "", None])
def test_registry_rejects_unsafe_paths(tmp_path, monkeypatch, unsafe):
    data = json.loads(VALIDATE_MODULE.REGISTRY.read_text(encoding="utf-8"))
    data["engines"][0]["router"] = unsafe
    registry = tmp_path / "registry.json"
    registry.write_text(json.dumps(data), encoding="utf-8")
    monkeypatch.setattr(VALIDATE_MODULE, "REGISTRY", registry)
    assert any("router must be" in error for error in VALIDATE_MODULE.validate_registry())


@contextmanager
def directory_link(link, target):
    """Create a link inside the caller's temporary fixture, without admin rights."""
    if os.name == "nt":
        quoted_link = str(link).replace("'", "''")
        quoted_target = str(target).replace("'", "''")
        subprocess.run([
            "powershell", "-NoProfile", "-NonInteractive", "-Command",
            f"New-Item -ItemType Junction -Path '{quoted_link}' -Target '{quoted_target}' -ErrorAction Stop | Out-Null",
        ], check=True, capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
    else:
        link.symlink_to(target, target_is_directory=True)
    try:
        yield
    finally:
        # Remove only this fixture link; never recurse into its target.
        if os.name == "nt":
            link.rmdir()
        else:
            link.unlink()


@pytest.mark.parametrize("external", [False, True])
def test_contract_links_must_stay_inside_selected_checkout(tmp_path, monkeypatch, external):
    checkout = tmp_path / "checkout"
    checkout.mkdir()
    target = (tmp_path if external else checkout) / "actual"
    target.mkdir()
    for filename in ("AGENTS.md", "adoption.md"):
        (target / filename).write_text("Fixture\n", encoding="utf-8")
    monkeypatch.setenv("SKILL_ENGINE_ROOT_SKILLS_WEB_DEV", str(checkout))
    with directory_link(checkout / "linked", target):
        result = VALIDATE_MODULE.resolve_engine_dir(tmp_path, "skills-web-dev", "linked/AGENTS.md", "linked/adoption.md")
        assert result == (None if external else checkout)
        target.rename(target.with_name("moved"))
        assert VALIDATE_MODULE.resolve_engine_dir(tmp_path, "skills-web-dev", "linked/AGENTS.md", "linked/adoption.md") is None


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
