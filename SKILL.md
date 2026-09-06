---
name: skills-web-dev
description: Top-level router for the Chwezi Core Systems web-development and software-engineering skills engine. Use for AI systems, SaaS, architecture, APIs, databases, security, frontend engineering, mobile, DevOps, reliability, product engineering, SDLC documentation, catalog maintenance, delivery evidence packs, routing fixtures, and world-class engineering quality gates.
---

# Skills Web Dev Router

This is the entrypoint for the `skills-web-dev` engine. It routes engineering work to the smallest accurate active skill, applies quality gates, and records evidence so outputs can be reviewed by a team that did not write them.

Standard implemented: Skills Web Dev July 2026 upgrade baseline. Last verified: 2026-07-08.

## Non-negotiable foundation

Always apply these before domain work:

1. `skills/sdlc-meta/anti-ai-slop/SKILL.md` while producing any artifact.
2. `skills/sdlc-meta/ai-slop-audit/SKILL.md` after each major iteration and at release.
3. `templates/delivery-dod/evidence-pack.md` for implementation, architecture, security, data, DevOps, AI, SaaS, mobile, or documentation deliverables.
4. `docs/source-registers/ai-platforms.md` when work depends on current AI, Apple, cloud, security, or framework facts.

5. `skills/sdlc-meta/kaizen-improvement-system/SKILL.md` for every engine audit, product audit,
   book-driven improvement, and post-iteration learning cycle. Published audits are capped at
   65/100; improvement plans target 95/100 and require evidence.

When a task requires external research, use the Digital Research Engine at `C:\wamp64\www\digital-research-engine`, beginning with its `source-evaluation` and `source-verification` skills.

## Route by intent

| Intent | Primary skill family |
|---|---|
| AI application, model gateway, RAG, evaluations, agent runtime, HITL, AI cost or security | `skills/ai/*` |
| API contract, system architecture, distributed systems, microservices, validation contracts | `skills/architecture/*` |
| Database schema, SQL, MySQL, PostgreSQL, reliability, persistence | `skills/backend-databases/*` |
| CI/CD, cloud, containers, Kubernetes, release engineering, observability, reliability | `skills/devops-cloud/*` |
| React, Next.js, Tailwind implementation, frontend performance, image compression, content UX | `skills/frontend-ux/*` |
| Android, iOS, Kotlin Multiplatform, PWA, mobile operations | `skills/android/*`, `skills/ios/*`, `skills/mobile-cross/*` |
| TypeScript, JavaScript, Python, PHP, C#/.NET, Java/JVM, Spring, Jakarta EE, Hibernate, Maven, Gradle, WebLogic, Quarkus, Micronaut, Helidon, GraalVM | `skills/languages/*` |
| SaaS tenancy, pricing, billing, entitlements, SSO/SCIM, portability, admin tooling | `skills/saas/*` |
| Security audit, code safety, DPIA, Linux hardening, network security | `skills/security/*` |
| Product discovery, business metrics, documents, spreadsheets, proposal readiness, delivery control | `skills/product-business/*` |
| SDLC documentation, skill writing, catalog guardrails, world-class engineering gates | `skills/sdlc-meta/*` and `00-meta-initialization/*` |
| Finance/accounting rules, statutory values, IFRS, close, audit, payroll, tax | External `chwezi-accounting-doctrine`; local finance skills only orchestrate implementation |
| Visual design, typography, UI/UX appearance, documents, slides, spreadsheets, PDF visual polish | External `design-system-skills` |

## Running example

Use `docs/world-class-exemplars/running-example.md`: a Chwezi Core Systems multi-tenant field-service SaaS called **FieldOps Ledger**. The same example threads through architecture, API, database, identity, security, reliability, deployment, and evidence-pack artifacts.

## Release workflow

1. Read the selected domain `SKILL.md`.
2. Load only the domain references, templates, and examples that the skill points to.
3. If current facts are needed, check the appropriate source register and invoke Digital Research Skills Engine verification.
4. Produce the artifact and evidence pack together.
5. Run `python -X utf8 scripts\skill_catalog_guardrails.py --report-only` after routing or catalog changes.
6. Run `python -X utf8 scripts\routing_smoke_test.py --report-only` after routing fixtures or frontmatter changes.
7. Ship only when the evidence pack, anti-slop gate, and relevant domain validation pass.

## Stop conditions

Stop and ask or research further when the request lacks a decision/audience, requires current platform/legal/statutory facts that have not been verified, asks for fabricated evidence, changes active-skill count without a routing reason, or would delete/move skill directories contrary to `AGENTS.md`.

## See also

- `README.md`
- `docs/skill-routing-index.md`
- `docs/skill-aliases.yml`
- `docs/catalog-cleanup/empty-directory-disposition.md`
- `templates/delivery-dod/evidence-pack.md`
- `examples/full-stack-saas-reference/README.md`
