---
name: skill-writing
description: Use when creating or upgrading reusable skills, specialist-role instructions, or vendor adapters. Covers agent-versus-skill boundaries, model-neutral canonical sources, triggers, capability and output contracts, progressive disclosure, validation, and repository quality gates.
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

- Use when creating or upgrading reusable skills, specialist-role instructions, or vendor adapters. Covers agent-versus-skill boundaries, model-neutral canonical sources, triggers, capability and output contracts, progressive disclosure, validation, and repository quality gates.

## Do Not Use When

- A narrower neighbouring skill owns the task or this workflow would not change the result.

## Required Inputs

- Use the task-specific inputs declared in the core workflow below; identify missing required inputs before acting.

## Workflow

- Follow the ordered core workflow below and load only the references needed for the current branch.

## Quality Standards

- Apply the domain gates, evidence requirements, and acceptance criteria defined below.

## Anti-Patterns

- Do not replace the domain-specific rules below with generic advice or load unrelated references.

## Outputs

- Produce the named artefacts and evidence specified by the core output contract below.

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
- Use the `scripts/` directory for repository-native automation before inventing new tooling.
<!-- dual-compat-end -->
Use this skill for repository-native skill authoring. A Markdown file is an instruction artefact, not an autonomous agent: it becomes part of an agent only when a runner loads it into a model context, grants capabilities, and executes work. Encode reusable operational knowledge independently from any one runner, then add thin vendor adapters only where needed.

## Core Model

| Concept | Meaning | Canonical content |
|---|---|---|
| Agent | A specialised worker instantiated by a runner with context, tools, permissions, and an execution lifecycle | Role, responsibility boundary, capability policy, handoff contract |
| Skill | A reusable procedure or standard an agent can apply | Trigger, workflow, decision rules, checks, output contract |
| Tool | Equipment exposed by the runner | Capability requirements and safety constraints, not vendor command syntax |
| Workflow | An assignment that sequences one or more agents and skills | Routing, dependencies, reconciliation, stop conditions |

Do not label every role Markdown file an agent. State whether the artefact is a role definition, skill, project instruction file, workflow, standard, or vendor adapter.

## Repository Rules

- Keep `SKILL.md` under 500 lines. Keep deeper markdown references lean and split them when they become hard to load or maintain.
- Use only validator-approved frontmatter keys: `name`, `description`, `license`, `allowed-tools`, `metadata`.
- Make `description` the trigger: what the skill does and when to use it.
- Keep the discovery description concise: at most 350 characters under this repository's catalogue policy, with only the user goal, trigger conditions, and a neighbour boundary.
- Put deep detail in `references/`; keep `SKILL.md` focused on execution logic.
- Do not add meta-docs inside skills such as `README.md` or `CHANGELOG.md`.
- Keep shared expertise in one canonical, model-neutral source. Adapters may point to it but must not copy its full content.
- Keep project-wide instruction files short: project rules, routing, safety, and links belong there; specialist bodies do not.

The boolean `metadata.portable` and list-valued `metadata.compatible_with` are
this repository's local authoring contract. They do not establish conformance
to another interchange schema or prove that a host has loaded the skill.
Require unique runtime names including `claude-code` and `codex`; preserve
additional declared runtimes. Before export, inspect the destination schema
and test a representative adapter and task. Report unavailable host checks as
NOT ASSESSED. See the [current audit's metadata finding](../../../docs/audits/2026-09-06-kaizen/06-standards-benchmark.md).

## Five-Part Instruction Contract

Every reusable specialist instruction must define:

1. **Role or procedure** — the specialised responsibility or repeatable job.
2. **Trigger** — positive and negative activation conditions, including neighbouring routes.
3. **Instructions** — ordered workflow, decision rules, failure handling, and stop conditions.
4. **Capabilities and permissions** — what must or may be read, edited, executed, accessed, or delegated.
5. **Output contract** — named artefacts, required sections, evidence, acceptance criteria, and handoff target.

For capability-based wording, write "when repository search is available, inspect the code before answering" rather than naming a vendor command. Put runner-specific tool names, model selection, directories, and delegation syntax only in adapters.

## Authoring Workflow

### 1. Define the Reusable Problem

Create or update a skill only if it captures:

- A repeatable workflow.
- A stable architectural or domain pattern.
- A high-risk area where guardrails materially improve outcomes.

Do not create skills for generic programming knowledge or one-off tasks.

### Runtime metadata budget

Skill names and descriptions are discovery metadata exposed before the model
chooses which full instruction body to load. Treat this metadata as a shared
runtime budget across local engines and plugins:

- Keep each description at or below the repository's 350-character limit; prefer one or two direct sentences. A host's separate runtime budget does not relax this limit.
- Put procedures, output contracts, examples, policy detail, and long trigger lists in the body or `references/`.
- Keep one canonical `SKILL.md` entrypoint per capability. Use `ALIAS.md` and the routing index for absorbed or renamed topics.
- Do not expose ignored, archived, or reference-only trees as runtime skill roots.
- Run the aggregate runtime validator against the exact roots a host exposes; a repository-local pass is not sufficient.

### 2. Choose the Skill Shape

Use one of these structures:

- Workflow skill: step-by-step execution for fragile or sequential work.
- Standards skill: decision rules, checklists, and gates for quality-sensitive domains.
- Domain skill: business concepts, invariants, and recurring implementation patterns.

If the request is primarily for a specialised worker rather than a procedure, create or update a role definition and keep its reusable procedures as separate skills. One role may use several skills; one skill may be used by several roles.

### 2A. Choose the Source and Adapter Boundary

Use the hierarchy appropriate to the target project:

```text
AGENTS.md / CLAUDE.md     project-wide operating and routing rules
.ai/standards/            shared model-neutral standards
.ai/agents/               model-neutral specialist roles
.ai/workflows/            model-neutral multi-step assignments
.ai/procedures/           model-neutral reusable procedures, when used
.claude/agents/           Claude-specific adapters
.agents/<skill>/SKILL.md  Codex/open-agent skill adapters
.github/                  Copilot-specific adapters
```

This repository's active skill-root `SKILL.md` files remain canonical unless a project explicitly adopts `.ai/` as its canonical library. Never create parallel copies without naming which location owns the source of truth.

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

Good skills tell Codex:

- What to prioritize
- What to avoid
- What tradeoffs matter
- What "done" means

Bad skills just restate obvious framework syntax or dump long tutorials.

### 5. Design for Graceful Capability Degradation

- If search or file access exists, require inspection before advice.
- If execution exists, require relevant checks and inspection of their results.
- If editing is unavailable, return a patch or implementation plan.
- If web access is unavailable, identify facts that remain unverified.
- If parallel workers exist, delegate only independent, bounded work and reconcile their findings.
- Never assume a tool, edit, command, or delegated task succeeded without evidence.
- Preserve a read-only default for analysis/review roles; grant write or destructive capabilities only when the task requires them.

### 6. Test the Routing and Contract

Test at least:

- A clear positive trigger.
- A near-neighbour prompt that must route elsewhere.
- An ambiguous prompt that should request or gather context.
- A limited-capability run.
- A failure or stop-condition case.
- The required output shape and evidence fields.

## Quality Standard

Every skill in this repo should help Codex produce outputs that are:

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

If a skill covers multiple subdomains, split references by topic so each file
has a single clear purpose (for example, one file for security gates, one for a
schema checklist, and one for a review template). Name each file after the topic
it owns, keep it loadable on its own, and link it directly from `SKILL.md`.

Do not reinvent common templates. The `skill-composition-standards` skill already
ships a reusable template library under its `references/` directory, including a
`threat-model-template.md` for security gates, an `entity-model-template.md` and
`normalisation-playbook.md` for schema work, and a `test-plan-template.md` for
review and verification. Reuse those before creating a new local reference.

Do not bury important files several levels deep. Link them directly from `SKILL.md`.

Load [universal agent and skill architecture](references/universal-agent-skill-architecture.md) when designing a canonical role library, vendor adapters, capability policies, or multi-agent workflows.

### Book and Source-File Distillation Rule

When the user provides books, EPUBs, PDFs, course notes, long articles, or other
source files while creating or upgrading a skill:

- Load and follow [source distillation and copyright gate](references/source-distillation-and-copyright.md).
- Never commit the source, a whole-work conversion, OCR output, page images, or
  a chapter-sequential substitute. Process raw material only in a temporary
  directory outside the repository and delete temporary conversions after use.

- Treat the source files as temporary inputs. The finished skill must remain
  useful after those files are deleted, moved, or renamed.
- Do not merely link to the source file path. Distill the practical knowledge
  into self-contained `references/*.md` files.
- Preserve operational knowledge: workflows, decision tables, checklists,
  failure modes, examples, quality gates, and output requirements.
- Keep `SKILL.md` concise. Put durable depth in directly linked reference files.
- Avoid copying long passages. Summarize, synthesize, and convert book knowledge
  into reusable execution rules.
- Record bibliographic attribution, not local download paths or piracy-site
  metadata. Lawful access does not imply republication rights.
- Add a short note in the reference file saying it is self-contained and was
  prepared from provided source material, so future agents do not depend on the
  original file.
- If the source material is broad, split the result by practical topic rather
  than by book chapter.
- Validate that every new reference is linked from `SKILL.md` with clear
  conditions for when to load it.

## Upgrade Checklist

When improving an existing skill:

- Remove vague or generic advice.
- Add decision rules and release gates.
- Add real failure cases and anti-patterns.
- If book/source files were provided, make the upgraded skill self-contained and
  do not depend on those files continuing to exist.
- Tighten the activation description.
- Link to other skills only when the dependency is genuinely useful.
- Re-check line counts after editing.
- Separate worker identity from reusable procedure.
- Replace vendor-specific commands in canonical content with capability-based instructions.
- Define permissions, read-only/write boundaries, stop conditions, output schema, and handoff target.
- Ensure adapters reference the canonical source and contain only runner-specific metadata or commands.
- Add positive, negative, collision, limited-capability, and failure-path test prompts.

## Validation

After creating or updating a skill:

1. Run `python -X utf8 skill-writing/scripts/quick_validate.py <skill-dir>` (frontmatter, required sections, dual-compat markers, line limits).
2. Run `python -X utf8 skill-writing/scripts/contract_gate.py --skill <skill-dir>` (Evidence Produced contract from `validation-contract`). Use `--all` to scan the whole repo, `--bundle <path>` to validate a Release Evidence Bundle, and `--strict` to treat warnings as errors.
3. Run `python -X utf8 scripts/skill_catalog_guardrails.py`; any raw-source or
   likely full-text finding blocks release.
4. Run the coordination engine's aggregate runtime metadata validator against
   the assembled local and plugin roots.
5. Fix any frontmatter, structure, contract, source-ingestion, or runtime-budget issues.
6. Sanity-check the skill against a realistic prompt.
7. Ensure the skill still reads cleanly when loaded on its own.

## Anti-Patterns

- Huge `SKILL.md` files that act like textbooks.
- Trigger descriptions that are too broad to be useful.
- Long discovery descriptions that repeat the workflow or claim broad auto-loading. Fix: keep the trigger concise and move detail into references.
- Skills that duplicate existing skills without raising the quality bar.
- Example-heavy files with little operational guidance.
- Raw books, ebook conversions, OCR dumps, or chapter-by-chapter paraphrases in
  a skill repository.
- Instructions that ignore security, performance, testing, or maintainability.
- Calling a Markdown file an autonomous agent without naming the runner, capabilities, and execution lifecycle.
- Copying full specialist instructions into `AGENTS.md`, Claude adapters, Codex adapters, and Copilot files.
- Hard-coding model names without a measured cost, latency, or reasoning requirement.
- Granting broad write, shell, network, or production access to a role that only analyses or reviews.
- Multi-agent workflows that split dependent tasks, omit reconciliation, or allow workers to make conflicting edits.

## Companion Skills

- Load `world-class-engineering` when authoring engineering skills.
- Load `skill-safety-audit` before sharing high-impact or security-sensitive skills.

## Inputs

| Artefact | Required? | Why |
|---|---|---|
| Reusable problem and trigger examples | yes | Establish scope and routing |
| Neighbouring skill descriptions | yes | Prevent collisions |
| Runner capabilities and permission boundary | yes | Define safe execution |

## Decision rules

| Condition | Authoring choice | Failure avoided |
|---|---|---|
| Repeatable procedure used by multiple roles | Create or update a skill | Persona-procedure coupling |
| Specialist identity with distinct permissions and handoff | Create a role definition | Treating Markdown as an autonomous agent |
| Runner-specific metadata or commands only | Create a thin adapter | Canonical-source drift |

## Domain anti-patterns

- Copying canonical expertise into every adapter. Fix: link to one source and keep only runner metadata.
- Giving review roles write access. Fix: default analysis and review to read-only.
- Naming tools in model-neutral instructions. Fix: specify capabilities and put command names in adapters.
- Testing only positive triggers. Fix: add neighbour, collision, degraded-mode, and failure prompts.
- Declaring success without evidence. Fix: inspect tool results, diffs, and contract artefacts.
