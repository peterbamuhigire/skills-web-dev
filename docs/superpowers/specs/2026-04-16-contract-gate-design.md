# contract_gate.py — Design Spec

- **Date:** 2026-04-16
- **Author:** Peter Bamuhigire (with Claude Opus 4.6)
- **Status:** Approved for implementation
- **Companion to:** `validation-contract`, `skill-composition-standards`, `quick_validate.py`

## 1. Purpose

The repository now codifies three contracts (house style, Inputs/Outputs, Evidence Produced) but enforces only the first. `quick_validate.py` checks frontmatter, required sections, dual-compat markers, and line limits — it does not look at the `## Evidence Produced` table introduced by `validation-contract`.

`contract_gate.py` adds mechanical enforcement on top:

1. Every specialist skill carries a well-formed `## Evidence Produced` section.
2. Every Release Evidence Bundle (when present) is complete: no empty cells, no unjustified `N/A`.

The script is normative-but-graduated: today it warns on missing Evidence Produced sections (so the ~150 unnormalised specialists don't break the build); after item 1 (normalisation rollout) lands, default behaviour can be bumped to error in a one-line follow-up.

## 2. Non-goals

- Not a replacement for `quick_validate.py`. The two run side-by-side. `quick_validate.py` checks the house-style frontmatter and required sections; `contract_gate.py` checks the contracts on top.
- Not a parser of `## Inputs Contract` / `## Outputs Contract` declarations. Those declarative tables are not yet defined in `skill-composition-standards`. When they are, this script gains a third checker.
- Not a CI hook itself. The script is a CLI; wiring it into Git pre-commit or GitHub Actions is a separate concern done in the consuming repo's CI config.

## 3. Three checkers

### 3.1 Evidence Produced check (default)

For every skill in the repository (one directory per skill at the repo root, containing a `SKILL.md`), unless the skill is in the EXEMPT set:

- The `## Evidence Produced` section MUST exist.
- The section MUST sit between `<!-- dual-compat-start -->` and `<!-- dual-compat-end -->` (so Codex consumers see it).
- The section MUST contain a markdown table with header `| Category | Artifact | Format | Example |`.
- Each data row MUST have exactly 4 cells.
- The first column (Category) MUST be one of the seven canonical names (case-sensitive): `Correctness`, `Security`, `Data safety`, `Performance`, `Operability`, `UX quality`, `Release evidence`.
- The Format and Example columns MUST be non-empty.

### 3.2 Release Evidence Bundle check

Given a path to a bundle file (e.g. a project's `docs/releases/2026-XX-XX-evidence.md`):

- All seven `## N. <category>` sections MUST be present.
- Every bullet line of the form `- <Label>: <value>` MUST have a non-empty `<value>`.
- A value of `N/A` MUST be followed by ` — ` and a reason (em-dash + space + non-empty reason).
- Placeholder template tokens like `<link>` or `<...>` are reported as warnings (the canonical template intentionally has them; consuming projects fill them in).

### 3.3 Inputs/Outputs check (deferred)

A stub function `check_inputs_outputs(path)` exists with a docstring marker. When `skill-composition-standards` defines a parseable `## Inputs Contract` / `## Outputs Contract` table, the body of this function gets written in a follow-up. For now: no-op, returns no findings.

## 4. EXEMPT set

Skills excluded from the Evidence Produced check (baseline + process + index skills):

```python
EXEMPT_SKILLS = {
    "world-class-engineering",
    "skill-composition-standards",
    "validation-contract",
    "capability-matrix",
    "system-architecture-design",
    "engineering-management-system",
    "git-collaboration-workflow",
    "feature-planning",
    "spec-architect",
    "skill-writing",
}
```

Tested by directory name match. The list is conservative — if a skill straddles the line, it is NOT in the exempt list (default is to require declaration). This list lives at the top of `contract_gate.py` and is the single source of truth for "who is exempt".

## 5. CLI

```
python -X utf8 contract_gate.py [options]

Options:
  --evidence              Run Evidence Produced check across all specialist skills
  --bundle <PATH>         Run Release Evidence Bundle check on the given file
  --skill <NAME>          Limit Evidence check to one skill
  --strict                Treat warnings as errors (exit 1 instead of 0)
  --all                   Run --evidence on the whole repo (default)
  -h, --help              Show help
```

Default behaviour with no flags: same as `--all`.

`--strict` and `--evidence` / `--bundle` compose. `--skill <name>` is a filter on `--evidence`.

## 6. Output

- Exit 0 = clean (or only warnings without `--strict`).
- Exit 1 = errors found, OR warnings found AND `--strict`.
- Findings written to stderr; summary line to stdout.

Format per finding:
```
[ERROR]   <skill>/SKILL.md:<line>: <message>
[WARNING] <skill>/SKILL.md:<line>: <message>
```

Summary line format:
```
contract-gate: scanned <N> skills | <E> errors | <W> warnings | <X> exempt
```

## 7. Strictness today vs after item 1

- **Today:** missing Evidence Produced section = warning (so the ~150 unnormalised specialists don't break the script). Malformed sections, invalid categories, empty cells in a present section = error (because they indicate user mistakes that need fixing).
- **After item 1 (normalisation rollout):** the missing-section warning gets promoted to error. Single-line change to a constant in `contract_gate.py`.

## 8. Implementation shape

```python
# contract_gate.py — single file, ~300 lines

REPO_ROOT = Path(__file__).resolve().parents[2]
EXEMPT_SKILLS = {...}
CANONICAL_CATEGORIES = ("Correctness", "Security", "Data safety", "Performance",
                       "Operability", "UX quality", "Release evidence")
MISSING_SECTION_SEVERITY = "warning"  # change to "error" after item 1

# parsing helpers
def read_skill_md(path: Path) -> str: ...
def find_section(body: str, heading: str) -> tuple[int, str] | None: ...
def parse_evidence_table(section_body: str) -> list[Row]: ...
def find_dual_compat_block(body: str) -> tuple[int, int] | None: ...

# checkers
def check_evidence_produced(skill_dir: Path) -> list[Finding]: ...
def check_bundle(bundle_path: Path) -> list[Finding]: ...
def check_inputs_outputs(skill_dir: Path) -> list[Finding]: ...  # stub

# main
def main() -> int: ...  # argparse, dispatch, summary, exit code

if __name__ == "__main__":
    sys.exit(main())
```

No external dependencies beyond the stdlib (matches `quick_validate.py`).

## 9. Acceptance criteria

1. File exists at `skill-writing/scripts/contract_gate.py`.
2. `python -X utf8 skill-writing/scripts/contract_gate.py --help` prints the help text without error.
3. `python -X utf8 skill-writing/scripts/contract_gate.py --all` exits 0, reports the count of specialist skills missing Evidence Produced as warnings (~150), and the 16 declared specialists pass clean.
4. `python -X utf8 skill-writing/scripts/contract_gate.py --skill validation-contract --strict` exits 0 (exempt skill, nothing to check).
5. `python -X utf8 skill-writing/scripts/contract_gate.py --skill vibe-security-skill --strict` exits 0 (declared, valid).
6. `python -X utf8 skill-writing/scripts/contract_gate.py --bundle validation-contract/references/release-evidence-bundle-template.md` runs without error; reports placeholder tokens as warnings.
7. Adding a malformed Evidence row (e.g., `Securty` typo) to a specialist skill makes `--strict` exit 1.
8. README or `skill-writing/SKILL.md` mentions the new script alongside `quick_validate.py`.

## 10. Out of scope

- **CI integration.** No GitHub Actions workflow change. Consumers wire it into their pipeline themselves.
- **Inputs/Outputs Contract checking.** Deferred until skill-composition-standards defines the table form.
- **Auto-fix mode.** The script reports findings; it does not modify files.
- **Test suite for the script itself.** Following the repo pattern (`quick_validate.py` has no tests), the script is small enough that errors will surface on first use. If complex regressions appear, tests get added.
