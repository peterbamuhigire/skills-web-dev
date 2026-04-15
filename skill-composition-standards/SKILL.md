---
name: skill-composition-standards
description: Use when authoring a new skill, normalising an older skill, or reviewing
  a skill PR — defines the repository-wide house style (frontmatter, decision rules,
  anti-patterns, references), the output contracts each baseline-skill type must produce,
  and the input contracts each specialist skill must declare. This is the enforcement
  spine that makes the repository compose as a system, not a library of linked documents.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Skill Composition Standards

<!-- dual-compat-start -->
## Use When

- Use when authoring a new skill, normalising an older skill, or reviewing a skill PR — defines the repository-wide house style (frontmatter, decision rules, anti-patterns, references), the output contracts each baseline-skill type must produce, and the input contracts each specialist skill must declare. This is the enforcement spine that makes the repository compose as a system, not a library of linked documents.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `skill-composition-standards` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve; load `references` only as needed.
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
<!-- dual-compat-end -->
The rules that make every skill in this repository compose cleanly with every other skill. Two concerns in one skill, because they are two faces of the same question: "what does this skill promise, and what is it allowed to expect?"

## When this skill applies

- Creating a new skill — load this before `skill-writing`.
- Normalising an older skill against the current bar.
- Reviewing a skill PR for acceptance.
- Auditing the repository for drift.
- Introducing a new skill category (define its contract here first).

## The two standards this skill codifies

### Standard 1 — The house-style template (normalisation)

Every skill, old or new, must meet this shape. This is what "normalised" means.

### Standard 2 — Input/Output contracts (composition)

Every skill must declare the artifacts it consumes (inputs) and the artifacts it produces (outputs). Downstream skills can then depend on those artifacts being present and well-formed.

---

## Standard 1 — House-Style Template

### Required frontmatter

```yaml
---
name: <skill-slug>
description: Use when <trigger scenarios> — <what this skill covers>, <what it does not cover>. <One-line differentiator against neighbouring skills>.
---
```

Rules for `description`:

- Starts with "Use when" (trigger-phrasing — Claude loads skills on trigger match).
- Names the scenarios that should trigger loading.
- Names the neighbour skills (so the reader knows the difference).
- Single line, fits on screen without wrapping — under ~350 characters.

### Required sections (in order)

A normalised SKILL.md must have these sections; each may be short, but none may be missing:

1. **Title** — `# Skill Name` (human-readable)
2. **Opening paragraph** — one or two sentences stating the purpose
3. **Prerequisites** — "Load X and Y first" when other skills must be loaded before this one
4. **When this skill applies** — bullet list of 3–7 concrete scenarios
5. **Inputs** — what artifacts this skill consumes from upstream (see Standard 2)
6. **Outputs** — what artifacts this skill produces for downstream (see Standard 2)
7. **Non-negotiables** — the hard rules this skill enforces (optional for non-engineering skills)
8. **Decision rules** — at least one explicit decision table / ladder with thresholds
9. **Core content** — the workflow, recipes, or patterns
10. **Anti-patterns** — 5+ concrete "do not do this" items, each with the fix
11. **Read next** — cross-references to adjacent skills
12. **References** — list of `references/*.md` deep-dive files

Rules:

- SKILL.md **≤ 500 lines**. Overflow goes into `references/`.
- Every code snippet has a language tag on the fence.
- No emojis unless the user explicitly requests them.
- British English.
- Imperative voice for rules. Declarative for explanations.

### Required depth structure

- Anything deeper than a single reading pass must be extracted to `references/<topic>.md`.
- Each reference file 150–400 lines.
- Reference files follow the same no-emoji / British-English / language-tagged-fences rules.

### Required cross-linking

- The SKILL.md "Read next" section names adjacent skills.
- Every reference file links back to its parent SKILL.md at the top.
- Every skill declares its neighbour-differentiator in the `description`.

See `references/house-style-checklist.md` for the full 20-point checklist and `references/normalisation-playbook.md` for how to bring a legacy skill up to this bar.

---

## Standard 2 — Input/Output Contracts

### The principle

Every skill declares what it produces (outputs) and what it consumes (inputs). Downstream skills can then depend on those artifacts being present and well-formed. The baseline skills produce the artifact set that specialist skills consume, and specialist skills produce narrower deliverables that platform skills consume.

### Required contract declaration

Every SKILL.md has an **Inputs** and an **Outputs** section with a table:

```markdown
## Inputs

| Artifact | Produced by | Required? | Why |
|---|---|---|---|
| Context map | `system-architecture-design` | required | service/module boundaries |
| Access pattern list | `database-design-engineering` | required | shapes the API contract |
| Threat model | `vibe-security-skill` | optional | informs auth rules |

## Outputs

| Artifact | Consumed by | Template |
|---|---|---|
| OpenAPI 3 spec | frontend, mobile, SDK skills | `skill-composition-standards/references/openapi-contract.md` |
| Error model | frontend, mobile | `skill-composition-standards/references/error-model.md` |
| Idempotency map | `reliability-engineering` | inline |
```

If a skill does not depend on any upstream artifact, its Inputs section says so:

```markdown
## Inputs

None. This skill is a foundational baseline.
```

### Standard artifact types

The repository defines these standard artifacts. Each has a template in `references/`.

| Artifact | Template file | Produced by (typical) |
|---|---|---|
| Context map | `references/context-map-template.md` | `system-architecture-design` |
| ADR set | `references/adr-template.md` | any skill making a structural decision |
| Critical-flow table | `references/critical-flow-template.md` | `system-architecture-design` |
| Entity model | `references/entity-model-template.md` | `database-design-engineering` |
| Access-pattern list | `references/access-patterns-template.md` | `database-design-engineering` |
| Migration plan | `references/migration-plan-template.md` | `database-design-engineering`, `deployment-release-engineering` |
| OpenAPI contract | `references/openapi-contract.md` | `api-design-first` |
| Error model | `references/error-model.md` | `api-design-first` |
| Threat model | `references/threat-model-template.md` | `vibe-security-skill` |
| SLOs + alert plan | `references/slo-template.md` | `observability-monitoring` |
| Release plan | `references/release-plan-template.md` | `deployment-release-engineering` |
| Rollback plan | `references/rollback-plan-template.md` | `deployment-release-engineering` |
| Runbook | `references/runbook-template.md` | `reliability-engineering`, `observability-monitoring` |
| Test plan + evidence | `references/test-plan-template.md` | `advanced-testing-strategy` |

A skill that produces one of these artifacts must produce it in the format the template specifies. Downstream skills consume the template-format version.

### Contract gates (for review)

When reviewing a skill PR, verify:

1. Does the skill's Outputs section declare the artifacts it produces?
2. Does the skill's Inputs section declare what it consumes?
3. Are the output artifact templates linked from `skill-composition-standards/references/`?
4. Does the skill produce the artifact in the template format, not a free-form substitute?

If any answer is no, the PR fails the contract gate.

---

## Baseline output contracts (per baseline skill type)

Each baseline skill type has a mandatory output set. These are the contracts specialist skills depend on.

### `world-class-engineering`

Outputs: release gate checklist, production-readiness rubric.

### `system-architecture-design`

Outputs: **context map** + **critical-flow table** + **ADR set** + **dependency diagram notes** + **failure mode list**.

### `database-design-engineering`

Outputs: **entity model** + **access-pattern list** + **index plan** + **migration plan** + **retention + tenancy notes**.

### `api-design-first`

Outputs: **OpenAPI contract** + **auth model** + **error model** + **idempotency keys** + **observability notes**.

### `observability-monitoring`

Outputs: **SLOs** + **alert rules** + **dashboards** + **runbook-per-service**.

### `reliability-engineering`

Outputs: **retry/timeout matrix** + **degradation plan** + **incident playbook** + **postmortem template**.

### `deployment-release-engineering`

Outputs: **release plan** + **rollback plan** + **migration choreography** + **post-deploy verification steps**.

### `advanced-testing-strategy`

Outputs: **test plan** + **test evidence bundle** + **risk-based coverage map**.

### `vibe-security-skill`

Outputs: **threat model** + **abuse case list** + **auth/authz matrix** + **secret handling plan**.

See `references/baseline-contract-register.md` for the full list and full schemas.

---

## Normalisation workflow (bringing older skills up)

When normalising an older skill:

1. **Read the current SKILL.md and all references** in one pass.
2. **Score against the 20-point checklist** (`references/house-style-checklist.md`). Note gaps.
3. **Declare contracts first** — write the Inputs and Outputs sections. If the skill currently produces free-form output, decide what artifact type(s) it should produce and point at the templates.
4. **Restructure the SKILL.md** into the required section order. Keep all existing valuable content; just move it into the right sections.
5. **Extract depth into references** — anything longer than a page of dense content moves to `references/<topic>.md`.
6. **Add decision rules** — if the skill currently describes "what to do" without "when one option wins over another", add a decision table.
7. **Add anti-patterns** — concrete before/after examples for at least 5 mistakes.
8. **Add Read next** — name 3–5 adjacent skills.
9. **Clean prose** — no emojis, British English, language-tagged code fences.
10. **Run validator** — `python -X utf8 skill-writing/scripts/quick_validate.py <skill>`.

See `references/normalisation-playbook.md` for the full procedure with examples.

---

## Enforcement

This skill is **advisory in mechanism, mandatory in convention**. There is no CI bot (yet) that blocks a skill from merging if it fails the contract gate. Enforcement is by:

- Referencing this skill from `world-class-engineering` (repo-wide baseline).
- Referencing this skill from `skill-writing` (skill-authoring guide).
- Using the 20-point checklist in review.
- Running `quick_validate.py` in CI.
- Running the normalisation playbook on one older skill per week until the repository is normalised.

Future work: a CI hook that parses Inputs / Outputs tables and warns when a claimed upstream artifact is not declared by any upstream skill.

## Anti-patterns

- A skill with no Outputs declaration (every skill produces something).
- A skill that claims an input that no upstream skill produces — the input does not actually exist.
- Output described in prose rather than pointing at a template — loses composability.
- "References" section that is just a list of bullet points without the files existing.
- Decision rules written as prose paragraphs instead of tables / ladders.
- Anti-patterns section that lists principles ("avoid tight coupling") rather than concrete before/after examples.
- Neighbour skill not mentioned anywhere, leaving overlap ambiguous.
- Skill over 500 lines with no `references/` directory.

## Read next

- `skill-writing` — authoring process, validator, frontmatter rules.
- `world-class-engineering` — repository-wide quality bar that references this skill.
- `advanced-testing-strategy`, `observability-monitoring`, `reliability-engineering`, `deployment-release-engineering` — the operability baseline skills whose contracts anchor the repository.

## References

- `references/house-style-checklist.md` — 20-point review checklist
- `references/normalisation-playbook.md` — how to upgrade a legacy skill
- `references/baseline-contract-register.md` — full artifact-contract register per baseline skill type
- `references/context-map-template.md`
- `references/adr-template.md`
- `references/critical-flow-template.md`
- `references/openapi-contract.md`
- `references/error-model.md`
- `references/threat-model-template.md`
- `references/slo-template.md`
- `references/release-plan-template.md`
- `references/rollback-plan-template.md`
- `references/runbook-template.md`
- `references/test-plan-template.md`
