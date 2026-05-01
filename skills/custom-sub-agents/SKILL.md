---
name: custom-sub-agents
description: Guidance for creating and organizing custom sub-agents in local repositories,
  including folder conventions, per-agent structure, and AGENTS.md indexing. Use when
  asked where to store sub-agents or how to document them.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

## Platform Notes

- Optional helper plugins may help in some environments, but they must not be treated as required for this skill.

# Custom Sub-Agents
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Guidance for creating and organizing custom sub-agents in local repositories, including folder conventions, per-agent structure, and AGENTS.md indexing. Use when asked where to store sub-agents or how to document them.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `custom-sub-agents` or would be better handled by a more specific companion skill.
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

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Release evidence | Custom sub-agent register | Markdown doc cataloguing per-project agents, their folder layout, and per-agent strengths | `docs/agents/sub-agent-register.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
## Overview

Use this skill to define sub-agents as portable repository assets instead of editor-specific features. The goal is to make agent structure, ownership, and discovery clear enough that both Claude Code and Codex can work with the same project layout.

## Recommended Layout

Store sub-agents in a project-owned directory such as:

```text
agents/
|-- agent-name/
|   |-- README.md
|   |-- agent.js | agent.py | agent.ts | agent.php
|   `-- supporting files
`-- AGENTS.md
```

If a project already uses a different top-level directory, keep that convention and document it in the nearest `AGENTS.md`.

## Required Structure

1. One folder per sub-agent, named in kebab-case.
2. A `README.md` that explains purpose, scope, inputs, outputs, and usage examples.
3. A clear entrypoint file for the implementation language used by that project.
4. Registration in a local index document when the project has multiple agents.
5. A short note on testing or validation strategy.

## Portable Rules

- Do not require editor-specific settings, marketplace plugins, or hidden discovery behavior.
- Do not assume any single assistant runtime provides exclusive features that the others must emulate.
- Prefer plain files and explicit documentation over hidden auto-loading behavior.
- Keep agent instructions repo-relative. Do not assume an extra nested skill-catalog directory inside this repository.

## Decision Rule: Skill vs Sub-Agent

Use a skill when the work is mostly reusable guidance, checklists, or deterministic patterns.

Use a sub-agent when the project benefits from a durable, specialized worker with clear ownership, such as:

- a migration planner
- a code review helper
- a UI generation worker
- an API contract assistant

If the logic is simple enough to explain in one short section of documentation, prefer a skill over another agent.

## Agent Definition Template

For each agent, document:

- Purpose: what the agent is responsible for.
- Scope: which directories, services, or workflows it owns.
- Inputs: what context or files it requires.
- Outputs: what artifacts it produces.
- Guardrails: safety, review, and escalation rules.
- Validation: how to test or review its work.

## Discovery and Indexing

When a repository has more than a few sub-agents, add an `AGENTS.md` index near the agent root with:

- the list of agents
- a one-line purpose for each
- the folder path
- ownership or routing notes when relevant

## Companion Guidance

- Use [references/CUSTOM_SUB_AGENTS_GUIDE.md](references/CUSTOM_SUB_AGENTS_GUIDE.md) for a compact decision framework and indexing checklist.
- Load architecture and workflow skills when the agent design affects repository structure, deployment, or production operations.