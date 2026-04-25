# Custom Sub-Agents Guide

This guide keeps the `custom-sub-agents` skill practical and portable. It gives a small decision framework plus pointers into the deeper reference set in this directory.

## Use This Guide For

- deciding whether a project should use a skill or a sub-agent
- choosing a stable folder layout
- documenting agent ownership and discovery
- finding the right deep-dive reference file without loading everything

## Skill vs Sub-Agent

Use a skill when the answer is mostly static guidance:

- reusable implementation patterns
- checklists
- architecture guardrails
- deterministic workflows

Use a sub-agent when you need a reusable worker with ongoing ownership:

- bounded responsibility in a larger codebase
- repeated tasks with persistent instructions
- coordination across multiple files or modules
- a specialized review or planning role

## Decision Checklist

- If the behavior fits in one short markdown workflow, keep it as a skill.
- If the project needs a named worker that can be routed to repeatedly, create a sub-agent.
- If the work depends on editor-specific discovery or plugins, redesign it to use plain files and explicit docs.
- If multiple agents are introduced, add an `AGENTS.md` index near the agent root.

## Recommended Layout

```text
agents/
|-- AGENTS.md
|-- api-reviewer/
|   |-- README.md
|   `-- agent.py
`-- migration-planner/
    |-- README.md
    `-- agent.ts
```

Alternative roots are acceptable when they match the host repository. The important part is that the structure is documented and discoverable.

## Per-Agent Checklist

- Folder name is kebab-case.
- `README.md` explains purpose, scope, inputs, outputs, and constraints.
- Implementation entrypoint is obvious.
- Ownership boundaries are explicit.
- Validation steps or tests are documented.

## Index Checklist

An agent index should record:

- agent name
- path
- one-line purpose
- ownership or routing notes
- dependencies or handoff rules when they matter

## Deep-Dive References

Use these only when the task needs them:

- [01-agent-folder-structure.md](01-agent-folder-structure.md): folder and file organization
- [02-agent-config-documentation.md](02-agent-config-documentation.md): config and README structure
- [03-entry-points-patterns.md](03-entry-points-patterns.md): entrypoints and implementation patterns
- [04-testing-tools.md](04-testing-tools.md): testing and validation
- [05-advanced-patterns.md](05-advanced-patterns.md): orchestration patterns
- [06-parent-sub-agent.md](06-parent-sub-agent.md): parent/worker coordination
- [07-project-organization.md](07-project-organization.md): registry and large-project organization
- [08-integration-deployment.md](08-integration-deployment.md): integration and deployment concerns

## Portability Rules

- Keep paths repo-relative.
- Do not require VS Code settings or marketplace integrations.
- Do not assume GitHub Copilot, Claude-specific plugins, or Codex-only behaviors.
- Prefer documented conventions over hidden auto-loading.
