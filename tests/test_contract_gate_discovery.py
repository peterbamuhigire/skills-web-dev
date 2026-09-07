"""The evidence gate must inspect the same active roots as the catalogue."""

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("contract_gate_discovery", ROOT / "skills/sdlc-meta/skill-writing/scripts/contract_gate.py")
GATE = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = GATE
spec.loader.exec_module(GATE)


def test_gate_discovers_entire_real_catalogue():
    expected = {
        path.parent for root in ("skills", "00-meta-initialization")
        for path in (ROOT / root).rglob("SKILL.md")
        if path.is_file() and not any(part.startswith(".") for part in path.relative_to(ROOT / root).parts)
    }
    assert set(GATE.iter_skill_dirs()) == expected
    assert len(expected) == 179


def test_missing_skill_is_an_error():
    findings, scanned, exempt = GATE.run_evidence_check("definitely-not-a-skill")
    assert (scanned, exempt) == (0, 0)
    assert any(item.severity == "error" and "no active skills matched" in item.message for item in findings)


def test_empty_catalogue_is_an_error(tmp_path, monkeypatch):
    monkeypatch.setattr(GATE, "REPO_ROOT", tmp_path)
    findings, scanned, _ = GATE.run_evidence_check(None)
    assert scanned == 0
    assert any(item.severity == "error" for item in findings)


def test_directory_named_skill_is_not_a_skill(tmp_path, monkeypatch):
    (tmp_path / "skills/ghost/SKILL.md").mkdir(parents=True)
    monkeypatch.setattr(GATE, "REPO_ROOT", tmp_path)
    assert list(GATE.iter_skill_dirs()) == []
    findings, scanned, _ = GATE.run_evidence_check(None)
    assert scanned == 0
    assert any(item.severity == "error" for item in findings)
    monkeypatch.setattr(sys, "argv", ["contract_gate.py", "--all", "--strict"])
    assert GATE.main() == 1
    valid = tmp_path / "skills/real"
    valid.mkdir()
    (valid / "SKILL.md").write_text("# Real fixture\n", encoding="utf-8")
    assert list(GATE.iter_skill_dirs()) == [valid]


def test_hidden_and_reference_trees_are_excluded(tmp_path, monkeypatch):
    for relative in ("skills/family/valid", "00-meta-initialization/start", "skills/.hidden/ignored", "references/not-active"):
        directory = tmp_path / relative
        directory.mkdir(parents=True)
        (directory / "SKILL.md").write_text("# Fixture\n", encoding="utf-8")
    monkeypatch.setattr(GATE, "REPO_ROOT", tmp_path)
    assert {path.name for path in GATE.iter_skill_dirs()} == {"valid", "start"}
    findings, scanned, _ = GATE.run_evidence_check("skills/family/valid")
    assert scanned == 1
    assert findings[0].message == "missing ## Evidence Produced section"
