[Back to Java Enterprise Development](../SKILL.md)

# Java architecture, framework, and project-structure selection

Use this reference when selecting a Java system shape, framework family,
request-concurrency model, packaging mode, or source layout. It records the
decision boundary and evidence required for a project; it does not replace the
architecture, API, database, security, cloud, reliability, or delivery skills.

## Currentness and evidence boundary

Accessed 2026-09-05. Framework and packaging claims are anchored to official
Spring, Jakarta, Quarkus, Micronaut, Helidon, and GraalVM documentation linked
at the point of claim. The current page for Jakarta EE distinguishes platform,
web, and core profiles and links specifications, Javadocs, TCKs, and compatible
implementations. [Jakarta EE specifications](https://jakarta.ee/specifications/)

Do not infer support, compatibility, lifecycle, licensing, performance, or
feature maturity from a framework name. Inspect the project's pinned JDK,
framework BOM, build plugins, drivers, deployment image, and support contract.
Preview or under-development features are `NOT_ASSESSED` until the target build
proves them. Proposed review date: 2026-10-05 (inference).

## Decision inputs and stop conditions

Require these inputs before a costly choice:

- critical actor and flow, invariant, failure consequence, data ownership,
  transaction boundary, API/event contract, and rollback boundary;
- deployment unit, independent scaling need, trust boundary, team ownership,
  release cadence, operational hours, and recovery capability;
- workload class, concurrency, latency distribution, payload/data size,
  downstream limits, streaming/backpressure need, and startup/density budget;
- exact JDK/runtime, framework modules, persistence and messaging clients,
  reflection/proxy/serialisation use, Native Image requirement, and tests;
- support, security, licensing, migration, exit, and observability evidence.

Stop the selection and record `NOT_ASSESSED` when the choice depends on a
benchmark, lifecycle statement, compatibility promise, or platform capability
that has not been verified against the pinned project.

## System shape: modular monolith or microservices

The following recommendation is engineering policy derived from the Java
runtime, framework, and operational evidence boundary (synthesis and
inference). A modular monolith is the default starting shape when independent
deployment or scaling is not yet a demonstrated requirement.

| Question | Modular monolith | Microservices |
|---|---|---|
| Domain boundary | Capability modules with explicit dependencies and owned contracts | Service boundary with owned API, data, runtime, and on-call responsibility |
| Transaction need | Local transaction can protect an invariant | Local transactions plus idempotent workflow, outbox, reconciliation, or compensation |
| Scaling | Scale the process unless a module can be isolated later | Scale independently only where demand or isolation requires it |
| Failure model | In-process failure containment, process-wide blast radius | Network, timeout, duplicate, partial-write, schema, and discovery failures are first-class |
| Delivery | One release unit with module-level tests and dependency checks | Independent release evidence, contract compatibility, telemetry, rollout, and rollback per service |
| Choose when | Shared data and a cohesive change stream dominate; team needs a clear path to learn the domain | Independent ownership, security, scaling, or release is real and the organisation can operate the distributed failure modes |
| Reject when | Modules are only folders with unrestricted imports and hidden shared state | The split is only to look cloud-native, or no owner can carry its operational and data boundary |

Do not split a monolith by technical layer alone. Split by capability, then
enforce allowed dependencies in the build or architecture tests. Extract only
after a module has a stable contract, a named owner, observable workload,
independent failure handling, and a migration/rollback path (inference).

## Project structure and module boundaries

The structure and dependency rules below are engineering policy (inference),
not proof that a folder name alone enforces a boundary.

| Decision | Default | Evidence needed to depart |
|---|---|---|
| Source layout | Group by bounded capability, then by API, application, domain, and infrastructure concerns | Existing repository convention, collision risk, or generated-code constraint |
| Domain code | Plain Java types and ports with framework-free invariants | A measured framework feature that changes the boundary without hiding rules |
| Inbound adapters | REST, messaging, batch, CLI, or scheduler adapters translate into commands | Transport-specific behaviour that is itself the business rule |
| Outbound adapters | Database, HTTP, broker, filesystem, and model clients sit behind ports | A capability is intentionally owned by a shared platform module |
| Cross-module calls | Published interfaces or events with dependency direction recorded | Shared immutable value types with a stable compatibility owner |
| Tests | Unit tests at invariants; integration tests at adapters; flow tests at contracts | A narrower test would prove the same failure boundary with stronger evidence |
| JPMS | Add named modules where exports, services, or runtime image closure are enforceable | Reflection-heavy framework configuration or an unresolved class-path migration |

A capability-oriented shape can be expressed without a prescribed package name:

```text
orders/
  api/
  application/
  domain/
  infrastructure/
  test/
```

The structure is useful only if the dependency direction is enforced. `api`
must not reach into persistence internals; `domain` must not depend on HTTP,
ORM, or framework lifecycle; `infrastructure` must not own domain policy. This
is a project rule, not a claim that a folder tree proves architecture.

When JPMS is selected, record `exports`, `opens`, `uses`, `provides`, module
path/class path, test access, reflection configuration, and service-loader
evidence. The Java specification and module API define named and unnamed
modules, but they do not make a framework's reflective configuration correct
for you. [Java modules](https://docs.oracle.com/javase/specs/jls/se25/html/jls-7.html) [Module API](https://docs.oracle.com/en/java/javase/26/docs/api/java.base/java/lang/Module.html)

## Framework family selection

The row descriptions state what the cited projects document. The recommended
use is a project decision (inference), not a framework ranking.

| Candidate | Select when the evidence shows | Main risk to test | Do not choose on |
|---|---|---|---|
| Spring | The team and existing estate already use Spring, and its servlet or reactive web module matches the flow. Spring documents MVC as Servlet-based and WebFlux as a separate reactive stack. [Spring MVC](https://docs.spring.io/spring/reference/web/webmvc.html) [Spring WebFlux](https://docs.spring.io/spring/reference/web/webflux.html) | Auto-configuration, proxy boundaries, blocking clients, transaction scope, thread model, and native/reflection metadata | Starter count, annotations, or a benchmark from a different BOM and JDK |
| Jakarta EE | Portability across standard APIs, an application-server estate, or a standards-led contract matters. Jakarta publishes specifications, Javadocs, TCKs, and compatible implementations. [Jakarta specifications](https://jakarta.ee/specifications/) | Profile support, server/JDK matrix, class loading, CDI scope, transaction/resource adapters, and deployment topology | The word "enterprise" without a support or portability requirement |
| Quarkus | The team needs its documented REST execution model, build-time/native path, or virtual-thread integration and will test the selected extensions. Quarkus documents `@RunOnVirtualThread` and a Native Image build path for compatible runtimes. [Quarkus virtual threads](https://quarkus.io/guides/virtual-threads/) | Extension support, blocking annotations, reflection/resource metadata, build/runtime parity, and native executable behaviour | Startup folklore or a native target without a compatibility inventory |
| Micronaut | Compile-time dependency injection and reduced runtime reflection fit the codebase and Native Image plan. Micronaut documents compile-time data for injection and a runtime-reflection-last approach. [Micronaut Core](https://docs.micronaut.io/snapshot/guide/index.html) | Annotation processing, generated code, framework conventions, proxy/serialization edges, and team familiarity | A claim that reflection is impossible or that memory/startup benefits are guaranteed |
| Helidon | A standalone runtime is wanted, with either explicit SE control or a MicroProfile/Jakarta-oriented MP model. Helidon documents SE and MP as different programming models and describes MP as using MicroProfile and Jakarta APIs. [Helidon MP introduction](https://helidon.io/docs/v4/mp/introduction) [Helidon documentation](https://helidon.io/docs/v4/) | SE/MP choice, client and persistence integration, observability, virtual-thread behaviour, native-image support, and operational ownership | A generic "microservice" label without a flow or runtime test |

For a migration, prefer the existing supported framework and team competence
unless a comparative ADR proves that the new framework reduces a named risk or
cost. Keep the domain/application modules independent enough that a framework
change does not rewrite business invariants (inference).

## Spring MVC with virtual threads or reactive execution

The table is a synthesis of the cited framework descriptions and the runtime
constraints in the companion concurrency reference; each choice remains an
inference until the project's flow and evidence support it.

| Requirement | Prefer | Evidence and boundary |
|---|---|---|
| Blocking JDBC/HTTP/filesystem libraries, sequential business flow, ordinary thread-local diagnostics | MVC/Servlet style with virtual threads where the full path supports it | Spring documents a virtual-thread switch and warns that pool properties no longer govern the virtual-thread scheduler; verify runtime, driver, pinning, connection limits, and shutdown. [Spring virtual threads](https://docs.spring.io/spring-boot/reference/features/spring-application.html) |
| End-to-end non-blocking I/O, streaming, backpressure, and reactive clients | WebFlux or another reactive stack | Spring documents WebFlux as non-blocking and supporting Reactive Streams backpressure. Verify every adapter, operator, context propagation, cancellation and error path. [Spring WebFlux](https://docs.spring.io/spring/reference/web/webflux.html) |
| MVC application with a reactive downstream client | MVC plus a narrowly bounded reactive client may be valid | Spring documents that the modules can coexist, but the team must define the blocking boundary and observe both execution models. [Spring WebFlux](https://docs.spring.io/spring/reference/web/webflux.html) |
| Mixed code with blocking calls hidden inside event-loop work | Neither until the boundary is redesigned | Detect blocking calls, queue growth, carrier/event-loop starvation, downstream saturation, and cancellation loss. |

Virtual threads do not remove database, broker, HTTP, rate-limit, or memory
capacity limits. Bound those resources independently and measure the request
path under normal, slow, rejected, cancelled, and dependency-failure cases
(synthesis). Use the runtime evidence workflow in
`java-language-runtime-concurrency.md` before changing the model.

## JVM or Native Image

The default and acceptance rules below are engineering policy (inference)
derived from the cited Native Image constraints and the project's operational
requirements.

| Requirement | JVM | Native Image |
|---|---|---|
| Default choice | Broad Java SE and library compatibility, dynamic loading, familiar diagnostics, and measured steady-state throughput | Choose only when startup, density, packaging, or platform constraints are a demonstrated requirement |
| Reflection/proxies/resources | Usually available at runtime, subject to module and security rules | Inventory and register dynamic features; test the produced executable |
| Build and release | Compile/package with the pinned JDK and run the same artefact through environments | Add native toolchain, longer build feedback, target-architecture evidence, reproducible metadata, and rollback |
| Diagnostics | JVM tools, JFR, heap/thread/native-memory evidence as supported by the runtime | Verify equivalent diagnostics, symbol/debug process, crash evidence, and operational runbook |
| Acceptance gate | Functional, load, memory, startup, shutdown, observability, and recovery evidence | The same gates plus metadata coverage, native build repeatability, startup/RSS/throughput comparison, and compatibility failures |

Native Image performs static reachability analysis under a closed-world
assumption and documents that reflection, JNI, dynamic proxies, resources, and
other dynamic features may need metadata. [Native Image reference](https://www.graalvm.org/latest/reference-manual/native-image/) [Reachability metadata](https://www.graalvm.org/latest/reference-manual/native-image/metadata/)

Do not claim a native benefit from image size or a local startup sample. Compare
the same flow, input shape, concurrency, readiness semantics, logging, memory
budget, and failure cases on the JVM and native artefacts. If a comparable
workload or packaged test is unavailable, the result is `NOT_ASSESSED`.

## ADR and evidence workflow

Write the architecture decision in the repository template and include:

1. Context, actor, critical flow, invariant, failure consequence, and explicit
   non-goals.
2. Options considered, including the current platform and the lowest-cost
   reversible option.
3. Decision matrix with workload, ownership, data, support, security,
   operability, cost, exit, and evidence columns.
4. Dependency and reflection/native inventory, project structure, API/event
   compatibility, and failure-mode list.
5. Normal and failure tests, load evidence, packaged smoke, telemetry,
   termination, rollback, owner, review date, and unresolved gaps.

Do not convert a clean compile into a framework or architecture pass. A choice
passes only when its failure path and operating owner are evidenced (inference).

## AI-agent inspection and degraded evidence

An AI agent selecting a Java architecture must inspect the repository before
recommending a framework. Require this handoff:

| Inspection result | Minimum content |
|---|---|
| Platform card | JDK distribution/build, bytecode target, wrapper, BOM, framework modules, server/runtime, packaging, and support evidence |
| Boundary map | Actor to transport, authentication, module, transaction, data store, side effect, telemetry, and recovery |
| Shape comparison | Modular monolith and service split with owner, data, deployment, scaling, failure, and rollback consequences |
| Framework comparison | Only official source-backed capabilities; pinned dependency proof; migration and exit cost |
| Concurrency comparison | MVC/virtual and reactive paths with blocking inventory, pools, backpressure, cancellation, and pinning evidence |
| Native comparison | Dynamic-feature inventory, metadata, produced-artifact tests, and JVM/native measurements |
| Claim ledger | Source, scope, access date, freshness, support state, uncertainty, and review trigger |

If the agent cannot read build files, run the wrapper, inspect the packaged
artefact, access official sources, run a load test, or observe production, it
must narrow its output. Report the exact unavailable evidence and mark the
affected decision `NOT_ASSESSED`; never fill it with framework reputation,
remembered versions, invented benchmarks, or assumed support.

## Anti-patterns

- Microservices introduced before a service has an owner, data boundary,
  contract, telemetry, and recovery path. Fix: modularise first or record the
  distributed-systems evidence that justifies extraction.
- Framework chosen from a starter generator or popularity claim. Fix: compare
  the pinned dependency graph, flow, support, exit cost, and failure evidence.
- Global `controllers/services/repositories` tree hides capability ownership.
  Fix: group by capability and enforce dependency direction.
- MVC and reactive models mixed without a blocking boundary. Fix: inventory
  adapters, isolate blocking work, and test cancellation/backpressure.
- Native Image selected before reflection, resources, proxies, serialisation,
  JNI, and generated-code inventory. Fix: prove metadata and packaged tests.
- A local startup or throughput figure is treated as a production result. Fix:
  use a controlled workload, same flow, release identity, and residual-risk
  record.
- AI-generated framework configuration copied without compilation and runtime
  evidence. Fix: verify every API and configuration key against the pinned
  build and official documentation.

## Evidence record

The cited framework and packaging pages are primary project/vendor sources,
accessed 2026-09-05. Their scope is limited to the capabilities stated beside
each citation. Support, licence, compatibility, performance, load, production,
archive-snapshot, and reviewer evidence is context-bound to the implementing
project; absent artefacts remain `NOT_ASSESSED`.

| Source family | Scope | Publication/version date | Freshness and support | Review and uncertainty |
|---|---|---|---|---|
| Jakarta EE specifications | Standard profiles, specifications, Javadocs, TCKs, and compatible implementations | Page lists release status; page date `NOT_ASSESSED` | Official specification catalogue; target profile/server support remains context-bound | Review 2026-10-05; application-server matrix `NOT_ASSESSED` |
| Spring Framework and Spring Boot docs | MVC, WebFlux, virtual-thread configuration, and documented execution boundaries | Page date `NOT_ASSESSED` | Official project documentation; pinned BOM and runtime decide support | Review with each dependency change; load and driver evidence `NOT_ASSESSED` |
| Quarkus, Micronaut, and Helidon docs | Virtual-thread integration, compile-time/runtime model, SE/MP choice, and native path | Page date `NOT_ASSESSED` | Official project documentation; extension and release compatibility remain context-bound | Review with the pinned build; native and production evidence `NOT_ASSESSED` |
| GraalVM Native Image docs | Closed-world analysis, dynamic-feature metadata, and native acceptance risks | Page date `NOT_ASSESSED` | Official project documentation; target architecture and toolchain remain context-bound | Review with every Native Image toolchain change; measurements `NOT_ASSESSED` |
