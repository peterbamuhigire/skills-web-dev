# Claude Code Guide - Skills Repository

Quick reference hub for working in this repository.

## Repository Context

- Purpose: shared Claude Code skills library
- Type: reference and execution-logic repository
- Usage pattern: skills are authored here and loaded into Claude Code sessions in other projects

## Mandatory Documentation Rules

All markdown files in this repository must follow these rules:

- maximum 500 lines per file
- use a high-level document plus focused deep-dive references when needed
- keep related content grouped logically

See `doc-standards.md` for the full rules.

## Baseline Skill Order

For substantial implementation, architecture, or repository-upgrade work, load skills in this order:

1. `world-class-engineering`
2. `system-architecture-design`, `database-design-engineering`, `saas-erp-system-design`, or `git-collaboration-workflow` as appropriate
3. platform or framework skill
4. security, UX, performance, observability, testing, and release companion skills

This prevents stack-specific work from skipping architecture, quality gates, or delivery discipline.

## How Claude Should Work With This Repository

### When Asked To Use Skills

If a user wants to use a skill from this collection:

1. determine the project context
2. identify the right baseline and specialist skills
3. explain how the skill should be invoked or combined
4. apply the skill patterns consistently

Alias: if a user says `seeder-script`, treat it as the `saas-seeder` skill.

### Security Baseline

For web applications, APIs, and web-connected systems, always pair the main implementation skill with the relevant security skill. `vibe-security-skill` is the default web security baseline.

### When Adding New Skills

If asked to create a new skill:

1. review existing skills first
2. avoid duplication unless the new skill clearly raises the quality bar
3. use validator-safe frontmatter and repository conventions
4. update `README.md` and `PROJECT_BRIEF.md` if the new skill materially changes repository capability
5. align new engineering skills with `world-class-engineering` unless there is a clear reason not to

See `skill-writing/SKILL.md` and `claude-guides/skill-creation-workflow.md`.

### When Modifying Existing Skills

If improving a skill:

1. read the current skill completely
2. preserve working scope unless a change is intentionally broader
3. raise weak sections toward clearer decision rules, release gates, and real-world constraints
4. keep documentation in sync with the actual repository capability
5. validate the updated skill

## Key Baseline Skills

- `world-class-engineering` - shared production bar and release gates
- `system-architecture-design` - decomposition, contracts, ADRs, failure design
- `database-design-engineering` - schema shape, tenancy, indexing, migrations, retention
- `saas-erp-system-design` - configurable workflow systems, approvals, controls, auditability
- `git-collaboration-workflow` - branch, review, conflict, merge, and release discipline
- `observability-monitoring` - logs, metrics, traces, alerts, SLOs, and diagnosis-first telemetry
- `advanced-testing-strategy` - risk-based test depth and release evidence
- `deployment-release-engineering` - rollout, rollback, migration-safe deployment, post-deploy verification

## Repository Structure

Representative layout:

```text
skills/
|-- world-class-engineering/
|-- system-architecture-design/
|-- database-design-engineering/
|-- saas-erp-system-design/
|-- git-collaboration-workflow/
|-- observability-monitoring/
|-- advanced-testing-strategy/
|-- deployment-release-engineering/
|-- android-development/
|-- ios-development/
|-- api-design-first/
|-- modular-saas-architecture/
|-- multi-tenant-saas-architecture/
|-- skill-writing/
|-- README.md
|-- PROJECT_BRIEF.md
`-- CLAUDE.md
```

## Critical Rules

### World-Class Baseline

When the request involves architecture, production implementation, or repository-wide skill upgrades:

- start from `world-class-engineering`
- add the relevant architecture, data, workflow, or business-system baseline skill
- then add stack-specific skills

Do not jump straight to framework-level implementation when architecture or data-shape decisions are still open.

### Database Standards

All database-related work should reference the relevant database skills and follow safe migration discipline. Use `database-design-engineering` for modeling and `mysql-best-practices` or the PostgreSQL skills for engine-specific execution.

### Skill Quality Standards

Every skill should:

- have a clear scope
- contain concrete decision rules
- define anti-patterns or failure risks
- stay concise in `SKILL.md`
- move depth into `references/`
- be useful in real implementation work, not just explanatory reading

## Working With Skill Files

### SKILL.md Format

Each skill should begin with:

```yaml
---
name: skill-name
description: Use when ...
---
```

Use only repository-accepted frontmatter keys. Keep the trigger description specific.

### Validation

Use the repository validator after editing skills:

```text
python -X utf8 skill-writing/scripts/quick_validate.py <skill-directory>
```

### Reading Strategy

When applying a skill:

1. read the frontmatter and full `SKILL.md`
2. load only the referenced deep-dive files that matter
3. apply the workflow as a whole, not as isolated snippets

## Quick Reference

- `README.md` - public-facing repository overview
- `PROJECT_BRIEF.md` - concise repository mission and direction
- `skill-writing/SKILL.md` - repository-native skill authoring rules
- `doc-standards.md` - markdown limits and formatting rules
- `claude-guides/` - deeper workflow guides

## Summary

This repository exists to make Claude Code more consistent and more capable across production engineering work. Use the baseline skills first, keep documentation concise, and make every skill encode real execution logic rather than generic advice.

Maintained by Peter Bamuhigire.
