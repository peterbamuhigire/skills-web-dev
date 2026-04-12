---
name: world-class-engineering
description: Use when designing, building, reviewing, or upgrading production software systems that must be secure, performant, maintainable, scalable, and user-centered. Apply before writing specs, code, architecture, APIs, databases, mobile apps, SaaS platforms, or ERP systems.
---

# World-Class Engineering

Use this skill as the baseline quality contract for all implementation skills in this repository. It defines the minimum bar for outputs that should resemble disciplined top-tier engineering rather than fast prototypes.

## Output Contract

Every output must satisfy all of these:

- Solve a real user and business problem with explicit constraints.
- Choose an architecture that supports change, not just initial delivery.
- Make security, observability, performance, and failure handling first-class concerns.
- Prefer boring, reliable defaults over clever but fragile abstractions.
- Leave the codebase easier to operate, test, and extend than before.

## Delivery Workflow

### 1. Frame the System

Before proposing code or architecture, define:

- Primary user journeys and failure-sensitive flows.
- Scale assumptions: users, requests, data growth, concurrency, latency, offline needs.
- Trust boundaries: client, edge, API, worker, database, third parties, admin surfaces.
- Quality attributes ranked in order: correctness, security, latency, throughput, cost, operability.
- Hard constraints: platform, staffing, deadlines, compliance, legacy dependencies.

If any of these are missing, state the gap and choose conservative defaults.

### 2. Design the Shape

Choose system boundaries deliberately:

- Separate product capability boundaries from technical layers.
- Keep domain rules independent from transport, UI, and storage frameworks.
- Define ownership of modules, APIs, schemas, events, and shared contracts.
- Use ADR-style reasoning for important choices: context, options, tradeoffs, decision, fallout.
- Prefer explicit seams for auth, billing, feature flags, audit logs, jobs, and integrations.

### 3. Engineer for Change

Build for future modifications:

- Small modules with high cohesion and low coupling.
- Stable interfaces around volatile dependencies.
- Backward-compatible contracts by default.
- Expand-contract data changes for live systems.
- Idempotent writes, retry-safe jobs, and deterministic side effects.

### 4. Engineer for Failure

Assume the happy path is incomplete:

- Enumerate validation, dependency, timeout, concurrency, and partial-failure modes.
- Define user-visible fallback behavior for each critical path.
- Add logging, metrics, tracing, and audit events where diagnosis matters.
- Make recovery paths explicit: retry, replay, reconcile, compensate, roll back.

### 5. Ship with Gates

Do not call an output production-ready unless it passes:

- Architecture gate
- Security gate
- Performance gate
- UX/content gate
- Testability gate
- Operability gate

Use the release gates in [references/world-class-gates.md](references/world-class-gates.md).

## Non-Negotiable Standards

### Engineering

- Use explicit module boundaries and predictable dependencies.
- Keep business logic out of controllers, routes, views, and UI components.
- Name things by domain meaning, not implementation detail.
- Prefer composition over inheritance unless hierarchy is truly stable.
- Document the invariants that must never be violated.

### Performance

- Define latency and throughput budgets before optimizing.
- Measure on realistic devices, networks, data volumes, and concurrency.
- Eliminate unbounded work on request paths.
- Budget memory, bundle size, query cost, background work, and third-party dependencies.
- Optimize the highest-impact user path first.

### Security

- Model abuse cases before implementation, not after.
- Deny by default.
- Scope every data access by actor, tenant, and permission.
- Validate input at every boundary and encode output for its destination.
- Protect secrets, tokens, keys, sessions, webhooks, and admin operations with dedicated controls.

### UX and Product Writing

- Reduce cognitive load before adding new features.
- Use conventions unless deviation clearly improves outcomes.
- Write microcopy that explains action, consequence, and recovery.
- Treat loading, empty, error, and success states as first-class design work.
- Design for accessibility, translation expansion, and interruption recovery.

### Developer Workflow

- Keep branches short-lived and commits reviewable.
- Make CI prove correctness, safety, and packaging readiness.
- Use code review to catch risk, not style trivia.
- Preserve deployability on main.
- Make rollback and release verification routine, not heroic.

## Review Prompts

Use these prompts while working:

- What must stay true even under load, retries, and partial failure?
- What becomes expensive or unsafe at 10x current scale?
- Which decisions are hard to reverse later?
- What will the next engineer misunderstand here?
- What evidence proves this is ready beyond "it works on my machine"?

## Companion Skills

- Load `system-architecture-design` for decomposition, ADRs, and tradeoff analysis.
- Load `database-design-engineering` for schemas, queries, migrations, and data lifecycle choices.
- Load `git-collaboration-workflow` for branch, review, and release discipline.
- Load `saas-erp-system-design` for configurable business systems, auditability, and domain boundaries.
- Load platform and security skills relevant to the stack after this baseline is established.

## References

- [references/source-patterns.md](references/source-patterns.md): Book-to-practice workflows derived from the supplied PDFs.
- [references/world-class-gates.md](references/world-class-gates.md): Release gates for engineering, security, performance, UX, and operations.
