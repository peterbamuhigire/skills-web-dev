---
name: java-enterprise-development
description: Use when building, reviewing, diagnosing, or modernising Java/JVM systems with Spring Boot/Batch/Security OIDC, Jakarta EE, Hibernate query performance, jOOQ, Maven/Gradle, modular Java ERP, Quarkus, GraalVM, WebLogic, Oracle JDBC, Kubernetes, JFR, or javax.persistence-to-jakarta.persistence migration; pair with cross-cutting specialists.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Java Enterprise Development

Use this skill as the Java- and JVM-specific judgement layer for long-lived
enterprise systems. It turns cross-cutting architecture, security, data,
delivery, and operations contracts into version-aware Java decisions and
evidence without replacing their owning skills.

<!-- dual-compat-start -->
## Prerequisites

Load `world-class-engineering`, `anti-ai-slop`, and the delivery evidence pack.
For current versions, lifecycle, licensing, compatibility, or support claims,
consult `docs/source-registers/java-enterprise.md` and run the Digital Research
source-evaluation and source-verification gates. Load the finance engine in
addition when implementing money, ledger, tax, payroll, close, or accounting
rules.

## Use When

- Building or reviewing Java services, APIs, workers, batch systems, libraries,
  modular monoliths, distributed systems, or application-server deployments.
- Working with the JVM, Spring, Jakarta EE, Hibernate, jOOQ, JDBC, Maven,
  Gradle, Quarkus, Micronaut, Helidon, GraalVM, WebLogic, or Oracle integration.
- Diagnosing Java CPU, memory, garbage collection, thread, connection-pool,
  startup, latency, or messaging incidents.
- Planning staged upgrades from older Java, Java EE, Spring Boot, Hibernate,
  build-tool, or application-server generations.

## Do Not Use When

- The task is generic system decomposition, API design, database design,
  security, Kubernetes, cloud, SaaS, AI, or accounting with no Java-specific
  decision. Use that specialist first and return here for implementation.
- The task is Android/Kotlin application work; use the Android or Kotlin
  Multiplatform route unless a separate Java backend is also in scope.
- A current product or licensing claim lacks a verified source. Research it;
  do not fill the gap from memory or this skill.

## Inputs

| Artefact or fact | Required? | If absent |
|---|---|---|
| Repository, affected flow, acceptance criteria, and failure consequence | yes | Inspect or frame before changing code |
| JDK distribution/version and Java language/toolchain level | yes | Detect from build, CI, image, and runtime; mark unresolved fields `NOT ASSESSED` |
| Framework, persistence, build-tool, database, runtime, and deployment versions | conditional | Read manifests, lock/BOM data, server config, and release metadata |
| Architecture boundaries, API/data contracts, security model, and scale/SLOs | conditional | Obtain from owning specialist or state the missing decision |
| Tests, logs, metrics, traces, profiles, dumps, migrations, and release evidence | conditional | Narrow diagnosis or readiness verdict; never invent evidence |

## Workflow

1. **Frame one vertical slice.** Name actor, business invariant, normal path,
   failure path, side effects, telemetry, rollback boundary, and consequence of
   error.
2. **Identify the actual platform.** Inspect Maven/Gradle files, wrappers,
   toolchains, BOMs, CI, container image, framework metadata, database driver,
   application server, deployment descriptors, and runtime output. Record the
   version-awareness card below.
3. **Verify lifecycle facts.** Compare detected versions with the current source
   register. Re-open official sources when the review date or target differs.
4. **Trace boundaries before code.** Follow the request/event/job through
   transport, authentication, application rule, transaction, persistence,
   side effect, telemetry, and recovery. Preserve working local conventions.
5. **Load only relevant depth.** Select the Java reference for the decision and
   pair it with the owning cross-cutting skill.
6. **Choose explicitly.** Record an ADR for costly framework, architecture,
   persistence, concurrency, native-image, application-server, or vendor
   choices. Use measured requirements, team capability, support, and exit cost.
7. **Make the smallest coherent change.** Keep domain invariants visible,
   configuration validated, transactions explicit, concurrency bounded, and
   external calls failure-aware.
8. **Exercise normal and failure behaviour.** Run only commands supported by
   the repository: wrapper-based compile/test/verify tasks, static/security
   checks, migration checks, and a realistic smoke test. Inspect the outputs.
9. **Test production shape.** Where applicable exercise the packaged artefact,
   runtime configuration, database dialect, broker, container limits, probes,
   graceful termination, telemetry, and rollback or roll-forward procedure.
10. **Record an evidence verdict.** Use `PASS`, `PARTIAL`, `FAIL`,
    `NOT ASSESSED`, or `NOT APPLICABLE` per quality area. Never collapse missing
    load, failover, restore, or production evidence into a pass.

### Version-awareness card

```text
JDK distribution/runtime:
Java language and bytecode target:
Framework and modules:
Jakarta/Java EE level:
Persistence provider and database driver:
Build tool and wrapper:
Application server or embedded runtime:
Database and dialect:
Packaging and deployment target:
Support evidence/review date:
```

## Quality Standards

- Correctness and data integrity outrank framework convenience. Define money,
  rounding, time zones, transaction isolation, idempotency, and concurrency
  behaviour at the business boundary.
- Prefer a supported LTS runtime for production when constraints permit, but do
  not upgrade or change distributions without compatibility, licensing,
  operational, and rollback evidence.
- Keep business rules out of controllers, listeners, entities, framework
  callbacks, deployment descriptors, and generated persistence plumbing.
- Treat Spring annotations, Jakarta interceptors, ORM sessions, transactions,
  retries, reactive pipelines, and native-image metadata as mechanisms whose
  boundaries and failure semantics must be understood.
- Require bounded executors, queues, result sets, request bodies, retries,
  timeouts, caches, batch chunks, and concurrency. Propagate cancellation or
  interruption according to the runtime contract.
- Verify dependencies and APIs against the pinned build. Use framework BOMs or
  Gradle platforms, wrappers, convergence/locking controls, and trusted
  repositories; arbitrary dependencies require a recorded benefit and owner.
- Make the shipped unit diagnosable: release identity, structured safe logs,
  metrics, traces, JVM evidence access, health semantics, and an owned runbook.
- Optimise only against a repeatable workload and before/after evidence. Do not
  prescribe JVM flags, reactive programming, caching, Native Image, or a new
  framework as folklore.

## Decision Rules

| Decision | Prefer | Require before choosing the costlier alternative |
|---|---|---|
| New system shape | Modular monolith with explicit modules | Independent deployment/scaling/security ownership plus operational maturity for services |
| Request concurrency | Spring MVC/servlet or Jakarta REST with platform/virtual threads where supported | End-to-end non-blocking stack, measured concurrency need, backpressure design, and reactive operating skill for WebFlux |
| Persistence | JPA/Hibernate for aggregate-centred transactional work | jOOQ for SQL-led queries/vendor features; JDBC for small explicit paths; evidence for mixed models |
| Enterprise platform | Existing supported platform and team competence | Comparative ADR for Spring Boot, Jakarta runtime, Quarkus, Micronaut, or Helidon |
| JVM or Native Image | JVM for broad compatibility and steady-state optimisation | Startup/density requirement, compatibility inventory, build/debug plan, and measured native result |
| Maven or Gradle | Existing wrapper and conventions | Migration benefit exceeding retraining, plugin, cache, and reproducibility cost |
| Local or distributed transaction | Local transaction plus idempotent workflow/outbox | XA/JTA only when atomic resource coordination is required and failure/recovery is exercised |
| Vendor-specific capability | Standard/portable contract with an adapter | Measured benefit, support commitment, isolation boundary, migration cost, and fallback |

## Outputs

| Artefact | Consumer | Template |
|---|---|---|
| Java implementation/review and version-awareness card | Developer and maintainer | Inline and repository-native code |
| Java architecture or technology ADR | `system-architecture-design` and reviewers | `templates/architecture-decision.md` |
| Java production-readiness verdict | Release owner | `templates/production-readiness.md` |
| JVM incident diagnosis | Operators and incident owner | `templates/java-incident-runbook.md` |
| Performance experiment | Performance/reliability owner | `templates/performance-evidence.md` |
| Staged Java/platform migration | `deployment-release-engineering` | `templates/migration-plan.md` |
| Java release gate | CI/CD and release owner | `templates/release-readiness.md` |

## Evidence Produced

| Category | Evidence | Acceptance condition |
|---|---|---|
| Correctness | Compile, test, integration, migration, and business-invariant results | Exact command/task, environment, result, and failures retained |
| Security | Dependency/SAST/configuration findings plus threat-model linkage | Java-specific findings and specialist disposition are traceable |
| Performance | Workload, runtime, profile, before/after measurements | Same controlled workload; no claim from a single unqualified number |
| Operability | Packaged smoke, telemetry, termination, recovery, and ownership evidence | Runtime identity and failure path are exercised or marked `NOT ASSESSED` |
| Release | Artefact/SBOM/provenance, migration, rollout, rollback or roll-forward evidence | Immutable identity and accountable owner are recorded |

## Anti-Patterns

- Adding interfaces, factories, base managers, wrappers, or mapping layers with
  no boundary or substitution need. Fix: keep the direct coherent design.
- Organising a large codebase only as global `controllers/services/repositories`.
  Fix: preserve existing shape or group by bounded capability with enforced
  dependencies.
- Treating `@Transactional`, retries, Kafka delivery, or database constraints
  as magic correctness. Fix: trace proxy/resource boundaries and test duplicate,
  rollback, isolation, deadlock, and partial-failure behaviour.
- Returning persistence entities as public contracts. Fix: use explicit API or
  event models where privacy, compatibility, or boundary ownership matters.
- Selecting microservices, WebFlux, Native Image, event sourcing, CQRS, or cache
  because it sounds modern. Fix: write the requirement and measure the trade-off.
- Catching `Exception` without containment and recovery, swallowing interrupts,
  logging the same failure at every layer, or exposing stack traces. Fix:
  translate once, preserve cause/correlation, and assign logging ownership.
- Creating raw threads, unbounded pools/queues, ad hoc retries, or `parallelStream`
  on server request paths. Fix: use managed, bounded concurrency and load tests.
- Using binary floating point for money or relying on implicit time zones and
  locale. Fix: define decimal scale/rounding, currency, `java.time` type, zone,
  locale, and database mapping.
- Setting heap equal to container memory or copying `-XX` flags from another
  service. Fix: budget heap and native consumers, collect evidence, change one
  supported control, and retain or revert.
- Claiming a build, test, benchmark, failover, or release passed without tool
  output. Fix: mark it `NOT ASSESSED` and name the exact missing check.

## Read Next

- `system-architecture-design`, `distributed-systems-patterns`, and
  `microservices-architecture` for boundaries, ADRs, consistency, and topology.
- `api-design-first`, `database-design-engineering`, and the database-specific
  skill for contracts, access patterns, schema, SQL, and database operations.
- `vibe-security-skill` and `web-app-security-audit` for threat modelling,
  authorisation, supply-chain, and release security.
- `advanced-testing-strategy`, `observability-monitoring`,
  `reliability-engineering`, and `deployment-release-engineering` for evidence,
  SLOs, incidents, rollout, and recovery.
- `kubernetes-platform`, `cloud-architecture`, relevant SaaS skills, and AI
  skills when Java implements those specialist decisions.

## References

- `references/java-language-runtime-concurrency.md`
- `references/architecture-framework-selection.md`
- `references/spring-production.md`
- `references/jakarta-runtimes-cloud-native.md`
- `references/persistence-transactions-oracle.md`
- `references/api-messaging-distributed-systems.md`
- `references/security-testing-quality.md`
- `references/build-supply-chain-release.md`
- `references/performance-observability-operations.md`
- `references/containers-kubernetes-cloud.md`
- `references/oracle-platforms.md`
- `references/legacy-modernisation.md`
- `references/ai-in-enterprise-java.md`
- `references/source-study-notes.md`
- `examples/enterprise-java-reference.md`
- `examples/red-team-scenarios.md`
<!-- dual-compat-end -->

## Capability Contract

Read and search are required. Editing and execution follow the task authority.
Network access is required for stale lifecycle/API claims. Delegation is
optional and limited to independent scopes. Production mutation, deployment,
data change, or irreversible migration requires explicit authority and recovery
proof.

## Degraded Mode

Without source, build, runtime, database, load, security, or production access,
return the narrowest evidence-backed plan or review. List exact commands and
artefacts still needed, and mark each affected quality area `NOT ASSESSED`.
