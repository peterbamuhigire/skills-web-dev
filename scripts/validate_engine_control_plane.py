#!/usr/bin/env python3
"""Validate the shared twelve-engine control-plane registry."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs" / "engine-control-plane.json"
EXPECTED_ENGINES = {"srs", "business-plan", "website", "social-media", "linux", "proposal", "accounting", "design", "digital-research", "skills-web-dev", "windows-admin", "political"}
REQUIRED_KEYS = {"id", "domain", "router", "adoption_doc", "agents", "commands", "hooks", "evidence"}
ALLOWED_HOOKS = {"preflight", "context", "before_write", "after_write", "release", "stop"}
ENGINE_DIRS = {
    "srs": "srs-skills",
    "business-plan": "business-plan-skills",
    "website": "website-skills",
    "social-media": "social-media-skills",
    "linux": "linux-skills",
    "proposal": "proposal-skills",
    "accounting": "chwezi-accounting-doctrine",
    "design": "design-system-skills",
    "digital-research": "digital-research-skills",
    "skills-web-dev": "skills-web-dev",
    "windows-admin": "windows-admin-engine-skills",
    "political": "political-essay-skills",
}


def engine_candidates(workspace_root: Path, engine_id: str) -> list[Path]:
    """Resolve an explicit override or the documented local layout.

    An override is authoritative: falling back from an invalid override could
    silently validate a different checkout. The supplied workspace contains
    the authoritative checkouts; unrelated home-directory copies are excluded.
    """
    if engine_id not in ENGINE_DIRS:
        return []
    env_name = f"SKILL_ENGINE_ROOT_{engine_id.upper().replace('-', '_')}"
    candidates: list[Path] = []
    override = os.environ.get(env_name)
    if override:
        return [Path(override).expanduser()]

    candidates.append(workspace_root / ENGINE_DIRS[engine_id])

    if engine_id == "political":
        candidates.append(Path("D:/political-skills"))

    unique: list[Path] = []
    for candidate in candidates:
        resolved = candidate.expanduser()
        if resolved not in unique:
            unique.append(resolved)
    return unique


def resolve_engine_dir(workspace_root: Path, engine_id: str, router: str, adoption_doc: str) -> Path | None:
    for candidate in engine_candidates(workspace_root, engine_id):
        try:
            if candidate.is_dir():
                # Follow an explicitly selected checkout link, but contracts
                # themselves must remain inside that checkout after resolution.
                checkout = candidate.resolve(strict=True)
                for relative in (router, adoption_doc):
                    target = (checkout / relative).resolve(strict=True)
                    if not target.is_relative_to(checkout) or not target.is_file():
                        return None
                return candidate
        except (OSError, RuntimeError):
            # Missing, inaccessible or looping links fail this selected scope.
            return None
    return None


def safe_relative_path(value: object) -> bool:
    """Reject absolute and parent-traversal paths on every supported OS."""
    if not isinstance(value, str) or not value.strip():
        return False
    normalised = value.replace("\\", "/")
    return not (
        normalised.startswith("/")
        or ":" in normalised
        or ".." in normalised.split("/")
    )


def validate_registry(workspace_root: Path | None = None, engine_ids: set[str] | None = None) -> list[str]:
    errors: list[str] = []
    if engine_ids is not None and (not engine_ids or not engine_ids <= EXPECTED_ENGINES):
        return ["selected engine IDs must be a non-empty subset of the registry"]
    try:
        payload = json.loads(REGISTRY.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot read registry: {exc}"]
    if not isinstance(payload, dict):
        return ["registry must be an object"]
    if type(payload.get("schema_version")) is not int or payload["schema_version"] != 1:
        errors.append("schema_version must be 1")
    engines = payload.get("engines")
    if not isinstance(engines, list):
        return ["engines must be a list"]
    ids = [engine["id"] for engine in engines if isinstance(engine, dict) and isinstance(engine.get("id"), str)]
    if set(ids) != EXPECTED_ENGINES:
        errors.append(f"engine IDs must be exactly {sorted(EXPECTED_ENGINES)}; found {sorted(set(ids))}")
    if len(ids) != len(set(ids)):
        errors.append("engine IDs must be unique")
    for engine in engines:
        if not isinstance(engine, dict):
            errors.append("each engine entry must be an object")
            continue
        engine_id = engine.get("id")
        if not isinstance(engine_id, str) or engine_id not in EXPECTED_ENGINES:
            errors.append("engine id must be a recognised string")
            continue
        for key in sorted(REQUIRED_KEYS - set(engine)):
            errors.append(f"{engine_id}: missing {key}")
        for key in ("agents", "commands", "hooks", "evidence"):
            values = engine.get(key)
            if not isinstance(values, list) or not values or any(not isinstance(item, str) or not item.strip() for item in values):
                errors.append(f"{engine_id}: {key} must be a non-empty list of strings")
        paths_valid = True
        for key in ("router", "adoption_doc"):
            if not safe_relative_path(engine.get(key)):
                errors.append(f"{engine_id}: {key} must be a non-empty relative path without parent traversal")
                paths_valid = False
        hooks = engine.get("hooks", [])
        if isinstance(hooks, list):
            unknown = {hook for hook in hooks if isinstance(hook, str)} - ALLOWED_HOOKS
            if unknown:
                errors.append(f"{engine_id}: unsupported hooks {sorted(unknown)}")
        if workspace_root is not None and paths_valid and (engine_ids is None or engine_id in engine_ids):
            engine_dir = resolve_engine_dir(
                workspace_root,
                engine_id,
                engine["router"],
                engine["adoption_doc"],
            )
            if engine_dir is None:
                candidates = ", ".join(str(path) for path in engine_candidates(workspace_root, engine_id))
                errors.append(f"{engine_id}: no candidate contains router and adoption document ({candidates})")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace-root", type=Path, help="Optional parent containing the local engine directories")
    parser.add_argument("--engine", action="append", choices=sorted(EXPECTED_ENGINES), help="Limit installed-checkout checks to these IDs; registry shape is always checked in full")
    args = parser.parse_args()
    if args.engine and args.workspace_root is None:
        parser.error("--engine requires --workspace-root")
    selected = set(args.engine) if args.engine else None
    errors = validate_registry(args.workspace_root.resolve() if args.workspace_root else None, selected)
    print("engine-control-plane-validator:")
    print(f"- registry: {REGISTRY}")
    print(f"- engines: {len(EXPECTED_ENGINES)}")
    print(f"- installed checkout scope: {', '.join(sorted(selected or EXPECTED_ENGINES)) if args.workspace_root else 'NOT ASSESSED (registry-only check)'}")
    print(f"- findings: {len(errors)}")
    for error in errors:
        print(f"[FAIL] {error}")
    if not errors:
        print("PASS: control-plane registry is valid")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
