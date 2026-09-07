from __future__ import annotations

import importlib.util
import json
import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).parents[1]
SPEC = importlib.util.spec_from_file_location("ensure_model_policy", ROOT / ".codex" / "ensure_model_policy.py")
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class CodexModelPolicyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.home = Path(self.tmp.name) / "codex"

    def tearDown(self):
        self.tmp.cleanup()

    def run_cli(self, *args):
        return MODULE.main([*args, "--runtime", "codex", "--codex-home", str(self.home)])

    def test_apply_check_and_preserve_unrelated_settings(self):
        self.home.mkdir(parents=True)
        original = 'model = "old"\nreview_model = "old-review"\nmodel_reasoning_effort = "high"\nnotify = ["keep"]\n\n[projects."C:\\\\keep"]\ntrust_level = "trusted"\n'
        (self.home / "config.toml").write_text(original, encoding="utf-8")
        (self.home / "AGENTS.md").write_text("User instructions.\n", encoding="utf-8")
        self.assertEqual(self.run_cli("--apply"), 0)
        self.assertEqual(self.run_cli("--check"), 0)
        text = (self.home / "config.toml").read_text(encoding="utf-8")
        self.assertIn('model_reasoning_effort = "high"', text)
        self.assertIn('notify = ["keep"]', text)
        self.assertIn('[projects."C:\\\\keep"]', text)

    def test_apply_is_idempotent_without_touching_bytes_or_mtime(self):
        self.assertEqual(self.run_cli("--apply"), 0)
        files = {p: (p.read_bytes(), p.stat().st_mtime_ns) for p in self.home.rglob("*") if p.is_file() and "backups" not in p.parts}
        time.sleep(0.01)
        self.assertEqual(self.run_cli("--apply"), 0)
        for path, (data, mtime) in files.items():
            self.assertEqual(path.read_bytes(), data)
            self.assertEqual(path.stat().st_mtime_ns, mtime)

    def test_missing_config_check_is_error_and_claude_is_noop(self):
        self.assertEqual(self.run_cli("--check"), 1)
        self.assertEqual(MODULE.main(["--apply", "--runtime", "claude", "--codex-home", str(self.home)]), 0)
        self.assertFalse(self.home.exists())

    def test_malformed_config_fails_without_writes(self):
        self.home.mkdir(parents=True)
        path = self.home / "config.toml"
        path.write_text("[broken\n", encoding="utf-8")
        before = path.read_bytes()
        self.assertEqual(self.run_cli("--apply"), 2)
        self.assertEqual(path.read_bytes(), before)
        self.assertFalse((self.home / "AGENTS.md").exists())

    def test_malformed_markers_fail_without_writes(self):
        self.home.mkdir(parents=True)
        (self.home / "config.toml").write_text('model = "x"\nreview_model = "y"\n', encoding="utf-8")
        doc = self.home / "AGENTS.md"
        doc.write_text(f"{MODULE.START}\nunterminated\n", encoding="utf-8")
        before = {p: p.read_bytes() for p in self.home.rglob("*") if p.is_file()}
        self.assertEqual(self.run_cli("--apply"), 2)
        self.assertEqual({p: p.read_bytes() for p in before}, before)

    def test_markers_in_reverse_order_fail(self):
        self.home.mkdir(parents=True)
        (self.home / "config.toml").write_text('model = "x"\nreview_model = "y"\n', encoding="utf-8")
        (self.home / "AGENTS.md").write_text(f"{MODULE.END}\n{MODULE.START}\n", encoding="utf-8")
        self.assertEqual(self.run_cli("--apply"), 2)

    def test_custom_agent_and_managed_extra_settings_are_safe(self):
        self.home.mkdir(parents=True)
        (self.home / "config.toml").write_text('[agents.custom]\nmodel = "keep"\n\n', encoding="utf-8")
        self.assertEqual(self.run_cli("--apply"), 0)
        self.assertIn('[agents.custom]\nmodel = "keep"', (self.home / "config.toml").read_text(encoding="utf-8"))

        config = (self.home / "config.toml").read_text(encoding="utf-8")
        config = config.replace('[agents.worker]\n', '[agents.worker]\nsandbox_mode = "keep"\n', 1)
        (self.home / "config.toml").write_text(config, encoding="utf-8")
        self.assertEqual(self.run_cli("--apply"), 2)

    def test_existing_role_restrictions_fail_closed(self):
        self.assertEqual(self.run_cli("--apply"), 0)
        role = self.home / "agents" / "worker.toml"
        role.write_text(role.read_text(encoding="utf-8") + '\nsandbox_mode = "read-only"\n', encoding="utf-8")
        before = role.read_bytes()
        self.assertEqual(self.run_cli("--apply"), 2)
        self.assertEqual(role.read_bytes(), before)

    def test_existing_custom_config_file_fails_closed(self):
        self.home.mkdir(parents=True)
        (self.home / "config.toml").write_text('[agents.worker]\nconfig_file = "personal.toml"\ndescription = "personal"\n', encoding="utf-8")
        before = (self.home / "config.toml").read_bytes()
        self.assertEqual(self.run_cli("--apply"), 2)
        self.assertEqual((self.home / "config.toml").read_bytes(), before)

    def test_relative_home_managed_config_file_is_adoptable(self):
        self.home.mkdir(parents=True)
        (self.home / "config.toml").write_text(
            '[agents.default]\nconfig_file = "agents/default.toml"\ndescription = "legacy"\n',
            encoding="utf-8",
        )
        self.assertEqual(self.run_cli("--apply"), 0)
        self.assertEqual(self.run_cli("--check"), 0)

    def test_managed_roles_followed_by_unrelated_table_are_stable(self):
        self.home.mkdir(parents=True)
        self.assertEqual(self.run_cli("--apply"), 0)
        config = self.home / "config.toml"
        config.write_text(config.read_text(encoding="utf-8") + '\n[projects."C:\\\\keep"]\ntrust_level = "trusted"\n', encoding="utf-8")
        self.assertEqual(self.run_cli("--apply"), 0)
        before = (self.home / "config.toml").read_bytes()
        self.assertEqual(self.run_cli("--apply"), 0)
        self.assertEqual((self.home / "config.toml").read_bytes(), before)
        self.assertIn('[projects."C:\\\\keep"]', (self.home / "config.toml").read_text(encoding="utf-8"))

    def test_role_drift_is_corrected(self):
        self.assertEqual(self.run_cli("--apply"), 0)
        role = self.home / "agents" / "worker.toml"
        role.write_text("name = 'drift'\n", encoding="utf-8")
        self.assertEqual(self.run_cli("--check"), 1)
        self.assertEqual(self.run_cli("--apply"), 0)
        self.assertEqual(self.run_cli("--check"), 0)

    def test_symlink_destination_is_rejected(self):
        if not hasattr(os, "symlink"):
            self.skipTest("symlink unsupported")
        self.home.mkdir(parents=True)
        outside = Path(self.tmp.name) / "outside"
        outside.mkdir()
        (self.home / "agents").symlink_to(outside, target_is_directory=True)
        self.assertEqual(self.run_cli("--apply"), 2)
        self.assertFalse((outside / "worker.toml").exists())

    def test_write_failure_rolls_back_existing_files(self):
        self.assertEqual(self.run_cli("--apply"), 0)
        before = {p: p.read_bytes() for p in self.home.rglob("*") if p.is_file() and "backups" not in p.parts}
        calls = {"n": 0}
        original = MODULE.atomic_write

        def fail(path, data):
            calls["n"] += 1
            if calls["n"] == 2:
                raise OSError("synthetic write failure")
            return original(path, data)

        (self.home / "config.toml").write_text((self.home / "config.toml").read_text() + "\n# drift\n", encoding="utf-8")
        (self.home / "AGENTS.md").write_text("drift\n", encoding="utf-8")
        with patch.object(MODULE, "atomic_write", side_effect=fail):
            self.assertEqual(self.run_cli("--apply"), 2)
        self.assertGreaterEqual(calls["n"], 2)
        self.assertEqual((self.home / "config.toml").read_text(encoding="utf-8").endswith("# drift\n"), True)
        self.assertEqual((self.home / "AGENTS.md").read_text(encoding="utf-8"), "drift\n")

    def test_backup_symlink_is_rejected(self):
        if not hasattr(os, "symlink"):
            self.skipTest("symlink unsupported")
        self.home.mkdir(parents=True)
        outside = Path(self.tmp.name) / "outside-backups"
        outside.mkdir()
        (self.home / "backups").symlink_to(outside, target_is_directory=True)
        self.assertEqual(self.run_cli("--apply"), 2)
        self.assertFalse(any(outside.iterdir()))

    def test_complex_merge_fails_closed(self):
        self.home.mkdir(parents=True)
        (self.home / "config.toml").write_text('model.foo = "bad"\n', encoding="utf-8")
        before = (self.home / "config.toml").read_bytes()
        self.assertEqual(self.run_cli("--apply"), 2)
        self.assertEqual((self.home / "config.toml").read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
