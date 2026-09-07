"""Additional adapters must not hide or erase the two required runtimes."""

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load(relative):
    spec = importlib.util.spec_from_file_location(Path(relative).stem, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SCANNER = load("skills/sdlc-meta/skill-engine-audit/scripts/engine_compliance.py")
VALIDATOR = load("skills/sdlc-meta/skill-writing/scripts/quick_validate.py")


@pytest.mark.parametrize("runtimes,accepted", [
    (["claude-code", "codex"], True),
    (["codex", "claude-code", "gemini-cli"], True),
    (["Codex", "codex"], False),
    (["claude-code", "codex", "codex"], False),
    (["claude-code"], False),
    (["claude-code", "codex", {}], False),
    ("claude-code,codex", False),
    (None, False),
])
def test_validators_agree_on_runtime_contract(runtimes, accepted):
    assert SCANNER.valid_compatibility(runtimes) is accepted
    errors = []
    VALIDATOR.validate_frontmatter({
        "name": "example", "description": "Use when checking a fixture.",
        "metadata": {"portable": True, "compatible_with": runtimes},
    }, Path("example"), errors)
    assert (not errors) is accepted


def test_safe_fix_preserves_additional_runtime_and_is_idempotent(tmp_path):
    target = tmp_path / "SKILL.md"
    target.write_text("---\nname: example\ndescription: Use when checking adapters.\nmetadata:\n  portable: true\n  compatible_with: [claude-code, codex, gemini-cli]\n---\n# Example\n", encoding="utf-8")
    SCANNER.safe_fix(target)
    metadata, _, _, errors = SCANNER.parse(target)
    assert not errors
    assert metadata["metadata"]["compatible_with"] == ["claude-code", "codex", "gemini-cli"]
    assert SCANNER.safe_fix(target) is False


@pytest.mark.parametrize("length,accepted", [(350, True), (351, False), (1024, False)])
def test_description_limit_matches_catalogue_policy(length, accepted):
    errors = []
    VALIDATOR.validate_frontmatter({
        "name": "example", "description": "Use when " + "x" * (length - 9),
        "metadata": {"portable": True, "compatible_with": ["claude-code", "codex"]},
    }, Path("example"), errors)
    assert (not errors) is accepted
