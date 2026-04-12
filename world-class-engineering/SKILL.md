---
name: world-class-engineering
description: Use when designing, building, reviewing, or upgrading production software systems that must be secure, performant, maintainable, scalable, and user-centered. Apply before writing specs, code, architecture, APIs, databases, mobile apps, SaaS platforms, or ERP systems.
---

# World-Class Engineering

Use this skill as the baseline operating system for all serious implementation skills in this repository. It defines what world-class software development, engineering, and management look like when the goal is not just to ship code, but to build software that is valuable, trusted, maintainable, fast to evolve, and worth paying for.

## Output Contract

Every output must satisfy all of these:

- Solve a real user and business problem with explicit constraints, not just a technical prompt.
- Improve one or more of: user value, revenue leverage, trust, speed, reliability, or maintainability.
- Choose an architecture that supports change, not just initial delivery.
- Make security, observability, performance, and failure handling first-class concerns.
- Prefer boring, reliable defaults over clever but fragile abstractions.
- Leave the codebase, workflow, and operating posture better than before.

For meaningful work, produce these artifacts explicitly:

- problem frame and success criteria
- architecture or module shape
- data, API, and failure assumptions
- validation and release evidence
- operational and ownership notes

## Delivery Workflow

### 1. Frame the Product and Business

Before architecture, define:

- target users, operators, buyers, and internal stakeholders
- top jobs to be done and why they matter
- current pain, cost, delay, risk, or revenue friction
- what users should love about the experience if the work succeeds
- success metrics: adoption, conversion, retention, reliability, latency, support burden, margin, engineering speed

If value is unclear, the design is premature.

### 2. Create Shared Understanding

Before proposing code or architecture, define:

- Primary user journeys and failure-sensitive flows.
- Required behaviors, non-goals, edge cases, and unresolved questions.
- Scale assumptions: users, requests, data growth, concurrency, latency, offline needs.
- Trust boundaries: client, edge, API, worker, database, third parties, admin surfaces.
- Quality attributes ranked in order: correctness, security, latency, throughput, cost, operability.
- Hard constraints: platform, staffing, deadlines, compliance, legacy dependencies.

Use shared language and explicit examples. Requirements are not complete until engineering, product, design, and operations would interpret the system the same way.

### 3. Design the Shape

Choose system boundaries deliberately:

- Separate product capability boundaries from technical layers.
- Design around domain concepts, workflows, policies, and invariants.
- Keep domain rules independent from transport, UI, and storage frameworks.
- Define ownership of modules, APIs, schemas, events, and shared contracts.
- Use ADR-style reasoning for important choices: context, options, tradeoffs, decision, fallout.
- Prefer explicit seams for auth, billing, feature flags, audit logs, jobs, and integrations.

### 4. Engineer for Change and Throughput

Build for future modifications:

- Small modules with high cohesion and low coupling.
- Stable interfaces around volatile dependencies.
- Backward-compatible contracts by default.
- Expand-contract data changes for live systems.
- Idempotent writes, retry-safe jobs, and deterministic side effects.
- Optimize for iteration speed where it does not compromise safety: fast tests, reversible releases, small changes, low-friction environments.
- Record decisions and assumptions so future engineers do not need to rediscover them.

### 5. Engineer for Failure and Operations

Assume the happy path is incomplete:

- Enumerate validation, dependency, timeout, concurrency, and partial-failure modes.
- Define user-visible fallback behavior for each critical path.
- Add logging, metrics, tracing, and audit events where diagnosis matters.
- Make recovery paths explicit: retry, replay, reconcile, compensate, roll back.
- Reduce operational burden with automation for repeatable mechanics before trying to automate judgment.
- Design ownership for alerts, incidents, follow-up fixes, and stale complexity removal.

### 6. Manage Delivery as a System

World-class engineering management means:

- prioritize by expected impact, risk reduction, and learning value
- split work into reviewable, testable increments
- validate early with prototypes, experiments, staging checks, or rollout slices
- preserve team health and clarity with transparent decisions, direct communication, and explicit ownership
- build a culture where knowledge is shared, review is normal, and hidden work is discouraged

Good management increases both throughput and quality. It does not trade one for the other by default.

### 7. Ship with Gates

Do not call an output production-ready unless it passes:

- Product-value gate
- Architecture gate
- Security gate
- Performance gate
- Reliability gate
- UX/content gate
- Testability gate
- Operability gate

Use the release gates in [references/world-class-gates.md](references/world-class-gates.md).

## Non-Negotiable Standards

### Product and Commercial Quality

- Solve an expensive problem, remove meaningful friction, or create a clearly superior experience.
- Make the core workflow easy to understand, easy to trust, and hard to misuse.
- Reduce time-to-value for first use, repeated use, and recovery from mistakes.
- Treat product quality, writing, and system behavior as one user experience.

### Engineering

- Use explicit module boundaries and predictable dependencies.
- Keep business logic out of controllers, routes, views, and UI components.
- Name things by domain meaning, not implementation detail.
- Prefer composition over inheritance unless hierarchy is truly stable.
- Document the invariants that must never be violated.
- Compare viable options before committing to a costly shape.
- Favor simple designs with known tradeoffs over fashionable architectures.

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

### Reliability and Operability

- Design retries, timeouts, backpressure, and degradation deliberately.
- Assume duplicate delivery, partial writes, stale reads, and dependency slowness will happen.
- Every critical workflow needs diagnosis signals, recovery steps, and ownership.
- Make incident response easier through correlation IDs, safe defaults, and documented runbooks.

### UX and Product Writing

- Reduce cognitive load before adding new features.
- Use conventions unless deviation clearly improves outcomes.
- Write microcopy that explains action, consequence, and recovery.
- Treat loading, empty, error, and success states as first-class design work.
- Design for accessibility, translation expansion, and interruption recovery.

### Management and Team Execution

- Prioritize work by leverage, not visibility.
- Invest in learning, documentation, and reusable systems that compound over time.
- Keep decision-making transparent enough that other engineers can contribute early.
- Delegate ownership, not just tasks.
- Build psychological safety for review, correction, and escalation.

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
- What evidence shows users and the business actually benefit from this work?
- What part of the workflow will become a tax on the team six months from now?
- What evidence proves this is ready beyond "it works on my machine"?

## Companion Skills

- Load `system-architecture-design` for decomposition, ADRs, and tradeoff analysis.
- Load `database-design-engineering` for schemas, queries, migrations, and data lifecycle choices.
- Load `git-collaboration-workflow` for branch, review, and release discipline.
- Load `saas-erp-system-design` for configurable business systems, auditability, and domain boundaries.
- Load `observability-monitoring` for telemetry, SLOs, alerts, and diagnosis-first dashboards.
- Load `reliability-engineering` for fault tolerance, incident readiness, and recovery-aware design.
- Load `advanced-testing-strategy` for risk-based validation and release evidence.
- Load `deployment-release-engineering` for rollout, rollback, migration-safe shipping, and post-deploy verification.
- Load `distributed-systems-patterns` when crossing service, queue, or consistency boundaries.
- Load `engineering-management-system` for delivery operating rhythm, delegation, communication, and team scaling.
- Load platform and security skills relevant to the stack after this baseline is established.

## References

- [references/source-patterns.md](references/source-patterns.md): Book-to-practice workflows derived from the supplied PDFs.
- [references/world-class-gates.md](references/world-class-gates.md): Release gates for engineering, security, performance, UX, and operations.
