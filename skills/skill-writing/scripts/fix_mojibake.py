#!/usr/bin/env python3
"""
Repair common UTF-8/Latin-1 mojibake in repository text files.
"""

from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
TARGET_SUFFIXES = {".md", ".skill"}
SUSPICIOUS = ("â", "Ã", "Â", "ðŸ", "\ufffd")
TOKEN_RE = re.compile(r"\S+")


def badness(text: str) -> int:
    return sum(text.count(marker) for marker in SUSPICIOUS)


def repair_token(token: str) -> str:
    candidate = token
    for _ in range(3):
        if not any(marker in candidate for marker in ("â", "Ã", "Â", "ð")):
            break
        improved = candidate
        for encoding in ("latin1", "cp1252"):
            try:
                decoded = candidate.encode(encoding).decode("utf-8")
            except (UnicodeEncodeError, UnicodeDecodeError):
                continue
            if badness(decoded) < badness(improved):
                improved = decoded
        if improved == candidate:
            break
        candidate = improved
    return candidate


def repair_text(text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        token = match.group(0)
        return repair_token(token)

    return TOKEN_RE.sub(replace, text)


def main() -> None:
    changed = []
    for path in REPO_ROOT.rglob("*"):
        if path.suffix not in TARGET_SUFFIXES or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if not any(marker in text for marker in SUSPICIOUS):
            continue
        repaired = repair_text(text)
        if badness(repaired) < badness(text):
            path.write_text(repaired, encoding="utf-8", newline="\n")
            changed.append(path.relative_to(REPO_ROOT))

    print(f"Repaired {len(changed)} files.")
    for rel in changed[:200]:
        print(rel)


if __name__ == "__main__":
    main()
