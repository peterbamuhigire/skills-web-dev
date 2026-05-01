---
name: skill-writing
description: Use when creating or upgrading skills in this repository. Covers repository-specific
  frontmatter rules, progressive disclosure, reference-file strategy, validation,
  and the quality bar required for production-grade engineering skills.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Skill Writing
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Use when creating or upgrading skills in this repository. Covers repository-specific frontmatter rules, progressive disclosure, reference-file strategy, validation, and the quality bar required for production-grade engineering skills.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `skill-writing` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve; load `references, scripts` only as needed.
- Confirm the desired deliverable: design, code, review, migration plan, audit, or documentation.

## Workflow

- Read this `SKILL.md` first, then load only the referenced deep-dive files that are necessary for the task.
- Apply the ordered guidance, checklists, and decision rules in this skill instead of cherry-picking isolated snippets.
- Produce the deliverable with assumptions, risks, and follow-up work made explicit when they matter.

## Quality Standards

- Keep outputs execution-oriented, concise, and aligned with the repository's baseline engineering standards.
- Preserve compatibility with existing project conventions unless the skill explicitly requires a stronger standard.
- Prefer deterministic, reviewable steps over vague advice or tool-specific magic.

## Anti-Patterns

- Treating examples as copy-paste truth without checking fit, constraints, or failure modes.
- Loading every reference file by default instead of using progressive disclosure.

## Outputs

- A concrete result that fits the task: implementation guidance, review findings, architecture decisions, templates, or generated artifacts.
- Clear assumptions, tradeoffs, or unresolved gaps when the task cannot be completed from available context alone.
- References used, companion skills, or follow-up actions when they materially improve execution.

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
- Use the `scripts/` directory for repository-native automation before inventing new tooling.
<!-- dual-compat-end -->
Use this skill for repository-native skill authoring. The goal is not to create generic instructional files; it is to encode reusable, high-signal operational knowledge for Claude Code.

## Repository Rules

- Keep `SKILL.md` under 500 lines. Keep deeper markdown references lean and split them when they become hard to load or maintain.
- Use only validator-approved frontmatter keys: `name`, `description`, `license`, `allowed-tools`, `metadata`.
- Make `description` the trigger: what the skill does and when to use it.
- Put deep detail in `references/`; keep `SKILL.md` focused on execution logic.
- Do not add meta-docs inside skills such as `README.md` or `CHANGELOG.md`.

## Authoring Workflow

### 1. Define the Reusable Problem

Create or update a skill only if it captures:

- A repeatable workflow.
- A stable architectural or domain pattern.
- A high-risk area where guardrails materially improve outcomes.

Do not create skills for generic programming knowledge or one-off tasks.

### 2. Choose the Skill Shape

Use one of these structures:

- Workflow skill: step-by-step execution for fragile or sequential work.
- Standards skill: decision rules, checklists, and gates for quality-sensitive domains.
- Domain skill: business concepts, invariants, and recurring implementation patterns.

### 3. Keep the Core Lean

`SKILL.md` should contain:

- Scope and activation clues.
- Ordered workflow or decision logic.
- Non-negotiable standards.
- Short checklists.
- References to deeper files.

Move these to `references/`:

- Large examples
- Review templates
- Detailed schemas
- Long checklists
- Topic-specific deep dives

### 4. Encode Judgment, Not Boilerplate

Good skills tell Claude Code:

- What to prioritize
- What to avoid
- What tradeoffs matter
- What "done" means

Bad skills just restate obvious framework syntax or dump long tutorials.

## Quality Standard

Every skill in this repo should help Claude Code produce outputs that are:

- Production-ready
- Secure by default
- Performance-conscious
- Testable and maintainable
- User-centered
- Explicit about failure handling and operational risk

Use `world-class-engineering` as the baseline when writing engineering skills.

## Frontmatter Standard

Use this template:

```yaml
---
name: skill-name
description: Use when ...
---
```

Guidelines:

- `name` must match the directory name exactly.
- Keep the description direct and specific.
- Front-load the main trigger phrase.
- Avoid filler and marketing language.

## Reference Strategy

If a skill covers multiple subdomains, split references by topic. For example:

- `references/security-gates.md`
- `references/schema-checklist.md`
- `references/review-template.md`

Do not bury important files several levels deep. Link them directly from `SKILL.md`.

## Upgrade Checklist

When improving an existing skill:

- Remove vague or generic advice.
- Add decision rules and release gates.
- Add real failure cases and anti-patterns.
- Tighten the activation description.
- Link to other skills only when the dependency is genuinely useful.
- Re-check line counts after editing.

## Validation

After creating or updating a skill:

1. Run `python -X utf8 skill-writing/scripts/quick_validate.py <skill-dir>` (frontmatter, required sections, dual-compat markers, line limits).
2. Run `python -X utf8 skill-writing/scripts/contract_gate.py --skill <skill-dir>` (Evidence Produced contract from `validation-contract`). Use `--all` to scan the whole repo, `--bundle <path>` to validate a Release Evidence Bundle, and `--strict` to treat warnings as errors.
3. Fix any frontmatter, structure, or contract issues.
4. Sanity-check the skill against a realistic prompt.
5. Ensure the skill still reads cleanly when loaded on its own.

## Anti-Patterns

- Huge `SKILL.md` files that act like textbooks.
- Trigger descriptions that are too broad to be useful.
- Skills that duplicate existing skills without raising the quality bar.
- Example-heavy files with little operational guidance.
- Instructions that ignore security, performance, testing, or maintainability.

## Companion Skills

- Load `world-class-engineering` when authoring engineering skills.
- Load `skill-safety-audit` before sharing high-impact or security-sensitive skills.