# Claude Code Guide - Skills Repository

Quick reference hub for working in this repository.

## Repository Context

- Purpose: shared Claude Code skills library
- Type: reference and execution-logic repository
- Usage pattern: skills are authored here and loaded into Claude Code sessions in other projects
- Dual-compatibility note: the same `skills/<skill-name>/SKILL.md` directories are also consumable by Codex through root `AGENTS.md`

## Mandatory Documentation Rules

All markdown files in this repository must follow these rules:

- keep `SKILL.md` entrypoints and top-level repository guidance under 500 lines; split deep references when they are refreshed
- use a high-level document plus focused deep-dive references when needed
- keep related content grouped logically

See `doc-standards.md` for the full rules.

## Baseline Skill Order

For substantial implementation, architecture, or repository-upgrade work, load skills in this order:

1. `world-class-engineering`
2. `system-architecture-design`, `database-design-engineering`, `saas-erp-system-design`, or `git-collaboration-workflow` as appropriate
3. platform or framework skill
4. security, UX, performance, observability, testing, and release companion skills
5. reliability, distributed-systems, and management skills when the problem includes scale, multi-service coordination, or team execution risk

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

### Email Baseline

Whenever an app needs to send HTML email (transactional or marketing), load `tabler-email-templates`. It ships 80 production HTML templates (welcome, confirm-email, magic-link, OTP, password reset, invoice, order, shipped, subscription, newsletter, promotions, security alert, deployment-failed, invitations, surveys, etc.) with light + dark variants and cross-client tested markup. Do not hand-roll responsive email HTML when a template in this skill matches the intent.

### When Adding New Skills

If asked to create a new skill:

1. review existing skills first
2. avoid duplication unless the new skill clearly raises the quality bar
3. use validator-safe frontmatter and repository conventions
4. update `README.md` and `PROJECT_BRIEF.md` if the new skill materially changes repository capability
5. preserve Codex compatibility by keeping the skill portable through `SKILL.md` frontmatter and the portable execution sections
6. align new engineering skills with `world-class-engineering` unless there is a clear reason not to

See `skills/skill-writing/SKILL.md` and `claude-guides/skill-creation-workflow.md`.

### When Modifying Existing Skills

If improving a skill:

1. read the current skill completely
2. preserve working scope unless a change is intentionally broader
3. raise weak sections toward clearer decision rules, release gates, and real-world constraints
4. keep documentation in sync with the actual repository capability
5. validate the updated skill

## Key Baseline Skills

- `world-class-engineering` - shared production bar and release gates
- `skill-composition-standards` - house-style template, cross-skill I/O contracts, 14 canonical artifact templates
- `validation-contract` - seven evidence categories, Release Evidence Bundle, and ship-readiness gate for specialist skills
- `capability-matrix` - per-domain Foundation → Implementation → Validation → Companions skill stacks; load when starting any new project or feature
- `system-architecture-design` - decomposition, contracts, ADRs, failure design
- `database-design-engineering` - schema shape, tenancy, indexing, migrations, retention
- `saas-erp-system-design` - configurable workflow systems, approvals, controls, auditability
- `git-collaboration-workflow` - branch, review, conflict, merge, and release discipline
- `observability-monitoring` - logs, metrics, traces, alerts, SLOs, and diagnosis-first telemetry
- `reliability-engineering` - retries, timeouts, degradation, incident readiness, and recovery-aware design
- `advanced-testing-strategy` - risk-based test depth and release evidence
- `deployment-release-engineering` - rollout, rollback, migration-safe deployment, post-deploy verification
- `distributed-systems-patterns` - consistency, messaging, idempotency, sagas, and cross-service tradeoffs
- `engineering-management-system` - prioritization, delegation, operating rhythm, coaching, and team scaling
- `engineering-strategy` - strategy diagnosis, altitude, guiding policy, operating mechanisms, review loops, written strategy briefs
- `saas-architecture-strategy` - tenancy/consumption model selection, deployment mapping, scaling, blast radius, architecture-to-capability map
- `experience-mapping` - hypothesis-driven discovery, impact mapping, journey mapping, outcome-to-feature traceability
- `service-design-blueprinting` - service blueprints, frontstage/backstage alignment, failure/recovery design, CX/EX alignment
- `ux-content-strategy` - voice charts, content-first design, UI text patterns, form completion gates, content measurement, decision communication, narrative arcs
- `premium-client-sales` - discovery, ethical persuasion, objection handling, premium pricing discipline, buyer proof
- `customer-service-excellence` - recovery loop, service language, difficult interactions, service quality measurement, CX/EX
- `continuous-improvement-system` - operating cadence, evidence-driven retros, outcome traceability, earn-or-learn milestones

### Per-domain stacks

For domain-specific Foundation → Implementation → Validation → Companions skill stacks, load `capability-matrix`. It covers 17 technology domains (Web/SaaS, Multi-tenant SaaS, iOS, Android, KMP, API, Database, Frontend, AI Feature, LLM Integration, Python Service, TypeScript Stack, Kubernetes, GIS, ERP, CI/CD, SRE) with explicit row entries per column, plus vertical addenda for Healthcare, POS, Payments, Auth, East-African compliance, and reporting.

## Repository Structure

Representative layout:

```text
|-- docs/
|-- skills/
|   |-- world-class-engineering/
|   |-- system-architecture-design/
|   |-- database-design-engineering/
|   |-- saas-erp-system-design/
|   |-- git-collaboration-workflow/
|   |-- observability-monitoring/
|   |-- reliability-engineering/
|   |-- advanced-testing-strategy/
|   |-- deployment-release-engineering/
|   |-- distributed-systems-patterns/
|   |-- engineering-management-system/
|   |-- android-development/
|   |-- ios-development/
|   |-- api-design-first/
|   |-- modular-saas-architecture/
|   |-- multi-tenant-saas-architecture/
|   `-- skill-writing/
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
- add `reliability-engineering` or `distributed-systems-patterns` when cross-service or async consistency risks appear
- add `engineering-management-system` when the request includes delivery process, team scaling, prioritization, or management behavior

Do not jump straight to framework-level implementation when architecture or data-shape decisions are still open.

### Premium Default

For this skills engine, premium is the default. Web, SaaS, product, UX, architecture, proposal-support, and client-facing outputs should be designed for world-class quality and premium positioning unless a narrower technical task explicitly excludes product or buyer experience.

- Use `premium-software-product-execution`, `premium-product-positioning`, and `premium-ui-ux-design` whenever perceived value, trust, buyer quality, pricing power, high-ticket positioning, premium software quality, or executive-facing delivery matters.
- Make premium value visible through packaging, simple usable UX, proof, content/SEO authority, service quality, pricing discipline, and high-value sales assets. Do not rely on premium adjectives without evidence.
- Do not dilute outputs to fit commodity, low-budget, or sub-premium work. If a buyer expects cheap execution without proper discovery, quality gates, or value logic, treat that as a poor-fit engagement and recommend a smaller premium scope or a no-bid/no-build decision.
- Premium means measurable quality, product depth, trust, supportability, proof, polish, and operational excellence; it is not superficial decoration.

### Database Standards

All database-related work should reference the relevant database skills and follow safe migration discipline. Use `database-design-engineering` for modeling and `mysql-best-practices` or the PostgreSQL skills for engine-specific execution.

For web development projects with a live database, include or maintain a root pull-time migration script that reads the app's normal database environment, compares tracked migrations against live migration history, and applies only missing migrations. Seeds, demo data, fixtures, and bootstrap seed bundles must stay on a separate explicit command.

### Skill Quality Standards

Every skill should:

- have a clear scope
- expose the portable sections used by both Claude Code and Codex
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
python -X utf8 skills/skill-writing/scripts/quick_validate.py skills/<skill-directory>
```

### Reading Strategy

When applying a skill:

1. read the frontmatter and full `SKILL.md`
2. load only the referenced deep-dive files that matter
3. apply the workflow as a whole, not as isolated snippets

## Quick Reference

- `README.md` - public-facing repository overview
- `PROJECT_BRIEF.md` - concise repository mission and direction
- `skills/skill-writing/SKILL.md` - repository-native skill authoring rules
- `doc-standards.md` - markdown limits and formatting rules
- `claude-guides/` - deeper workflow guides

## Summary

This repository exists to make Claude Code more consistent and more capable across production engineering work. Use the baseline skills first, keep documentation concise, and make every skill encode real execution logic rather than generic advice.

Maintained by Peter Bamuhigire.
