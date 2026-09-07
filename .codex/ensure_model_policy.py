#!/usr/bin/env python3
"""Install and verify the repository's Codex-only model policy.

The shipped policy is authoritative; this module only performs narrow,
fail-closed textual edits to the Codex home.  It deliberately never touches
Claude settings or unrelated Codex settings.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import stat
import sys
import tempfile
import tomllib
from pathlib import Path

START = "<!-- chwezi-codex-model-policy:start -->"
END = "<!-- chwezi-codex-model-policy:end -->"
ROOT_KEYS = ("model", "review_model")
POLICY_KEYS = {"model": "root_model", "review_model": "review_model"}


class PolicyError(Exception):
    pass


class PolicyDrift(PolicyError):
    pass


def repo_root() -> Path:
    return Path(__file__).resolve().parent.parent


def load_policy(root: Path) -> tuple[dict, str, dict[str, bytes]]:
    try:
        policy = json.loads((root / ".codex" / "model-policy.json").read_text(encoding="utf-8"))
        text = (root / ".codex" / "model-policy.md").read_text(encoding="utf-8")
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise PolicyError(f"cannot read shipped policy: {exc}") from exc
    if not isinstance(policy, dict) or any(not isinstance(policy.get(k), str) or not policy[k] for k in ("root_model", "review_model")):
        raise PolicyError("policy root_model/review_model must be non-empty strings")
    effort = policy.get("reasoning_effort")
    if not isinstance(effort, str) or not effort:
        raise PolicyError("policy reasoning_effort must be a non-empty string")
    roles = policy.get("roles")
    if not isinstance(roles, list) or roles != ["default", "worker", "explorer", "tester", "researcher", "reviewer"]:
        raise PolicyError("policy roles must be the six supported roles in order")
    if START in text or END in text:
        raise PolicyError("shipped policy markdown contains managed markers")
    templates = {}
    for role in roles:
        p = root / ".codex" / "agents" / f"{role}.toml"
        try:
            data = p.read_bytes()
            parsed = tomllib.loads(data.decode("utf-8"))
        except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
            raise PolicyError(f"invalid role template {role}: {exc}") from exc
        expected_model = policy["review_model"] if role == "reviewer" else policy["execution_model"]
        if parsed.get("name") != role or parsed.get("model") != expected_model or parsed.get("model_reasoning_effort") != effort:
            raise PolicyError(f"role template contract mismatch: {role}")
        templates[role] = data
    return policy, text, templates


def home_path(value: str | None) -> Path:
    return Path(value).expanduser() if value else Path(os.environ.get("CODEX_HOME", "~/.codex")).expanduser()


def safe_destination(path: Path, home: Path) -> None:
    home = home.resolve()
    try:
        path.resolve().relative_to(home)
    except ValueError as exc:
        raise PolicyError(f"managed destination escapes Codex home: {path}") from exc
    if path.exists() and path.is_symlink():
        raise PolicyError(f"managed destination is a symlink: {path}")


def parse_config(path: Path) -> dict:
    try:
        return tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise PolicyError(f"invalid config: {exc}") from exc


def parse_config_text(data: bytes) -> dict:
    try:
        return tomllib.loads(data.decode("utf-8"))
    except (UnicodeError, tomllib.TOMLDecodeError) as exc:
        raise PolicyError(f"generated config is invalid: {exc}") from exc


def root_scalar(config_text: str, key: str) -> str | None:
    # Root assignments must precede the first table. Dotted/table ambiguity is
    # rejected rather than risking a semantic change.
    before = config_text.split("[", 1)[0]
    matches = list(re.finditer(rf"(?m)^\s*{re.escape(key)}\s*=\s*([^#\r\n]+)", before))
    if len(matches) > 1:
        raise PolicyError(f"ambiguous root key: {key}")
    return matches[0].group(1).strip() if matches else None


def set_root_keys(text: str, policy: dict) -> str:
    first_table = re.search(r"(?m)^[ \t]*\[", text)
    cut = first_table.start() if first_table else len(text)
    head, tail = text[:cut], text[cut:]
    for key in ROOT_KEYS:
        if re.search(rf"(?m)^\s*{re.escape(key)}\.", head):
            raise PolicyError(f"complex dotted root key: {key}")
        matches = list(re.finditer(rf"(?m)^\s*{re.escape(key)}\s*=.*$", head))
        if len(matches) > 1:
            raise PolicyError(f"ambiguous root key: {key}")
        line = f'{key} = "{policy[POLICY_KEYS[key]]}"'
        if matches:
            a, b = matches[0].span()
            head = head[:a] + line + head[b:]
        else:
            prefix = head.rstrip("\r\n")
            head = (prefix + "\n" if prefix else "") + line + "\n"
    return (head + tail).rstrip("\r\n") + "\n"


def merge_agents(text: str, policy: dict, home: Path) -> str:
    roles = policy["roles"]
    # Reject arrays, dotted agent keys, and duplicate role tables.
    if re.search(r"^\s*\[\[agents\.", text, re.M) or re.search(r"^\s*agents\.[A-Za-z0-9_-]+\s*=", text, re.M):
        raise PolicyError("complex agents TOML cannot be safely merged")
    found: dict[str, tuple[int, int]] = {}
    tables = list(re.finditer(r"(?m)^[ \t]*\[([^\]]+)\][ \t]*$", text))
    for i, match in enumerate(tables):
        name = match.group(1).strip()
        if name.startswith("agents."):
            role = name[7:]
            if role in roles and role in found:
                raise PolicyError(f"unsupported or duplicate agents table: {name}")
            if role in roles:
                end = tables[i + 1].start() if i + 1 < len(tables) else len(text)
                section = text[match.end():end]
                try:
                    section_data = tomllib.loads(section)
                except tomllib.TOMLDecodeError as exc:
                    raise PolicyError(f"invalid agents.{role} section: {exc}") from exc
                if set(section_data) - {"config_file", "description"}:
                    raise PolicyError(f"managed agents.{role} contains unrelated settings")
                expected_path = (home / "agents" / f"{role}.toml").resolve()
                if "config_file" in section_data:
                    configured = Path(section_data["config_file"])
                    configured = (home / configured).resolve() if not configured.is_absolute() else configured.resolve()
                    if configured != expected_path:
                        raise PolicyError(f"managed agents.{role} has an existing custom config_file")
                found[role] = (match.start(), end)
    chunks = [(a, b, role) for role, (a, b) in found.items()]
    for a, b, role in sorted(chunks, reverse=True):
        path = (home / "agents" / f"{role}.toml").resolve()
        replacement = f"[agents.{role}]\nconfig_file = {json.dumps(str(path))}\ndescription = {json.dumps('Managed Chwezi Codex ' + role + ' role')}\n\n"
        text = text[:a] + replacement + text[b:]
    missing = [r for r in roles if r not in found]
    if missing:
        suffix = "\n" if text and not text.endswith("\n") else ""
        for role in missing:
            path = (home / "agents" / f"{role}.toml").resolve()
            suffix += f"\n[agents.{role}]\nconfig_file = {json.dumps(str(path))}\ndescription = {json.dumps('Managed Chwezi Codex ' + role + ' role')}\n"
        text += suffix
    return text


def merge_agents_doc(existing: str, policy_text: str) -> str:
    if START in existing and END in existing and existing.index(END) < existing.index(START):
        raise PolicyError("managed AGENTS markers are out of order")
    if existing.count(START) != existing.count(END) or existing.count(START) > 1:
        raise PolicyError("ambiguous managed AGENTS markers")
    block = f"{START}\n{policy_text.rstrip()}\n{END}"
    if START in existing:
        pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.S)
        return pattern.sub(block, existing)
    return existing.rstrip() + "\n\n" + block + "\n"


def expected(home: Path, policy: dict, policy_text: str, templates: dict[str, bytes]) -> dict[Path, bytes]:
    config = home / "config.toml"
    agents_doc = home / "AGENTS.md"
    current = config.read_text(encoding="utf-8") if config.exists() else ""
    merged = set_root_keys(current, policy)
    for _ in range(3):
        merged = merge_agents(merged, policy, home)
    out = {config: merged.encode("utf-8"), agents_doc: merge_agents_doc(agents_doc.read_text(encoding="utf-8") if agents_doc.exists() else "", policy_text).encode("utf-8")}
    for role, data in templates.items():
        role_path = home / "agents" / f"{role}.toml"
        if role_path.exists() and role_path.read_bytes() != data:
            try:
                existing = tomllib.loads(role_path.read_text(encoding="utf-8"))
                shipped = tomllib.loads(data.decode("utf-8"))
            except (OSError, UnicodeError, tomllib.TOMLDecodeError) as exc:
                raise PolicyError(f"invalid existing role file {role}: {exc}") from exc
            if set(existing) - set(shipped) or ("developer_instructions" in existing and existing.get("developer_instructions") != shipped.get("developer_instructions")):
                raise PolicyError(f"existing role file {role} contains user restrictions; adoption required")
        out[role_path] = data
    return out


def assert_semantic(before: dict, after: dict, policy: dict) -> None:
    def projection(value: dict) -> dict:
        result = dict(value)
        result.pop("model", None)
        result.pop("review_model", None)
        agents = dict(result.get("agents", {}))
        for role in policy["roles"]:
            agents.pop(role, None)
        if agents:
            result["agents"] = agents
        else:
            result.pop("agents", None)
        return result
    if projection(before) != projection(after):
        raise PolicyError("config semantic preservation assertion failed")


def check(home: Path, root: Path) -> None:
    policy, policy_text, templates = load_policy(root)
    config_path = home / "config.toml"
    if not config_path.exists():
        raise PolicyDrift("Codex config.toml is missing")
    parsed = parse_config(config_path)
    if parsed.get("model") != policy["root_model"] or parsed.get("review_model") != policy["review_model"]:
        raise PolicyDrift("root model policy drift")
    expected_files = expected(home, policy, policy_text, templates)
    safe_destination(config_path, home)
    safe_destination(home / "AGENTS.md", home)
    if config_path.read_bytes() != expected_files[config_path]:
        raise PolicyDrift("config model/role policy drift")
    for role in policy["roles"]:
        role_path = home / "agents" / f"{role}.toml"
        safe_destination(role_path, home)
        if not role_path.exists() or role_path.read_bytes() != templates[role]:
            raise PolicyDrift(f"role template drift: {role}")
    doc = home / "AGENTS.md"
    if not doc.exists() or merge_agents_doc(doc.read_text(encoding="utf-8"), policy_text).encode() != doc.read_bytes():
        raise PolicyDrift("managed AGENTS.md policy drift")


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def apply(home: Path, root: Path) -> None:
    policy, policy_text, templates = load_policy(root)
    if home.exists() and home.is_symlink():
        raise PolicyError("Codex home is a symlink")
    home.mkdir(parents=True, exist_ok=True)
    if (home / "config.toml").exists():
        before_parsed = parse_config(home / "config.toml")
    else:
        before_parsed = {}
    files = expected(home, policy, policy_text, templates)
    assert_semantic(before_parsed, parse_config_text(files[home / "config.toml"]), policy)
    for path in files:
        safe_destination(path, home)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup = home / "backups" / stamp
    counter = 0
    while backup.exists():
        counter += 1
        backup = home / "backups" / f"{stamp}-{counter}"
    safe_destination(backup, home)
    existing = {p: p.read_bytes() for p in files if p.exists()}
    changed = [p for p, data in files.items() if not p.exists() or p.read_bytes() != data]
    if not changed:
        return
    try:
        backup.mkdir(parents=True, mode=0o700)
        for path, data in existing.items():
            rel = path.relative_to(home)
            (backup / rel).parent.mkdir(parents=True, exist_ok=True)
            backup_file = backup / rel
            backup_file.write_bytes(data)
            try:
                os.chmod(backup_file, stat.S_IMODE(path.stat().st_mode))
            except OSError:
                pass
        written = []
        for path in changed:
            atomic_write(path, files[path])
            written.append(path)
    except Exception:
        for path in written if 'written' in locals() else []:
            if path in existing:
                atomic_write(path, existing[path])
            elif path.exists():
                path.unlink()
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="verify policy (default)")
    mode.add_argument("--apply", action="store_true")
    parser.add_argument("--codex-home", type=Path)
    parser.add_argument("--runtime", required=True, choices=("codex", "claude"))
    args = parser.parse_args(argv)
    if args.runtime == "claude":
        print("NOT_APPLICABLE: Codex model policy is not used by Claude")
        return 0
    try:
        home = home_path(str(args.codex_home) if args.codex_home else None)
        root = repo_root()
        if args.apply:
            apply(home, root)
        check(home, root)
        print("PASS: Codex model policy is correct")
        return 0
    except PolicyDrift as exc:
        print(f"DRIFT: {exc}", file=sys.stderr)
        return 1
    except PolicyError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:
        print(f"ERROR: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
