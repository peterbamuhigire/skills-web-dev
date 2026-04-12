---
name: skill-writing
description: Use when creating or upgrading Claude Code skills in this repository. Covers repository-specific frontmatter rules, progressive disclosure, reference-file strategy, validation, and the quality bar required for production-grade engineering skills.
---

# Skill Writing

Use this skill for repository-native skill authoring. The goal is not to create generic instructional files; it is to encode reusable, high-signal operational knowledge for Claude Code.

## Repository Rules

- Keep `SKILL.md` and every `.md` reference file under 500 lines.
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

1. Run `python -X utf8 skill-writing/scripts/quick_validate.py <skill-dir>`.
2. Fix any frontmatter or structure issues.
3. Sanity-check the skill against a realistic prompt.
4. Ensure the skill still reads cleanly when loaded on its own.

## Anti-Patterns

- Huge `SKILL.md` files that act like textbooks.
- Trigger descriptions that are too broad to be useful.
- Skills that duplicate existing skills without raising the quality bar.
- Example-heavy files with little operational guidance.
- Instructions that ignore security, performance, testing, or maintainability.

## Companion Skills

- Load `world-class-engineering` when authoring engineering skills.
- Load `skill-safety-audit` before sharing high-impact or security-sensitive skills.
