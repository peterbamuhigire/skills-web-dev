# Spring Production Reference

Parent skill: [Java Enterprise Development](../SKILL.md)

This reference is a production decision aid for Spring Framework and Spring Boot
systems. It treats annotations, proxies, transactions, configuration, health,
metrics, messaging, and shutdown as runtime contracts. The rules below are
authored synthesis from the cited official documentation, not a substitute for
the pinned build, a threat model, a load test, or a release record.

## Decision stance

Choose the smallest Spring shape that makes the required failure semantics
visible. Start from one flow: request, event, or job; name its invariant,
resource boundaries, side effects, telemetry, recovery action, and operator.
Do not choose WebFlux, Kafka, Modulith, Spring Cloud, or Spring AI because the
name sounds current. Record the requirement and the evidence that the choice
meets it (synthesis).

Keep business rules in plain domain and application code. Use Spring at the
edges for composition, transport, persistence, scheduling, messaging, and
instrumentation. Spring's container manages beans and their dependencies;
constructor injection keeps the dependency graph visible
([Spring IoC reference](https://docs.spring.io/spring-framework/reference/core/beans.html)).

## Select by operating need

| Need | Default decision | Choose another shape only when | Evidence required |
| --- | --- | --- | --- |
| Core container and configuration | Spring Framework with explicit configuration and constructor injection | Boot conventions remove material setup work without hiding a required boundary | Context startup, bean graph, configuration failure, and packaged smoke |
| Application packaging | Spring Boot when its executable or container shape matches deployment | A managed servlet container, shared platform service, or existing WAR contract is a real constraint | Exact packaged artefact, runtime bindings, probes, and shutdown test |
| HTTP request handling | Spring MVC for ordinary servlet request/response work | WebFlux is required by measured concurrency, streaming, or end-to-end non-blocking I/O | Workload, blocking-call inventory, cancellation/backpressure test, and error mapping |
| Reactive HTTP | Spring WebFlux only across a deliberately non-blocking path | The path depends on blocking JDBC, blocking SDKs, or a team that cannot diagnose reactive context and cancellation | Blocking detection, bounded schedulers, backpressure, timeout, and client disconnect tests |
| Data access | Spring Data repository abstractions for store-backed aggregates and queries | SQL shape, vendor features, bulk work, or a measured hot path needs explicit SQL or a different data model | Query plan, transaction boundary, result-set bound, migration, and duplicate-write test |
| Authentication and authorisation | Spring Security at the transport and method boundaries | A platform identity service or another security stack owns authentication | Threat model, authn/authz matrix, negative tests, and specialist review |
| Batch processing | Spring Batch for restartable, recorded job and step flows | A small idempotent task has no job repository or restart requirement | Restart, skip/retry policy, chunk or partition bounds, and operator replay evidence |
| Enterprise integration | Spring Integration when channels, adapters, routing, and error flows are the domain | A direct client or a single broker consumer is easier to reason about | Message contract, channel type, error route, backpressure, and replay test |
| Kafka | Spring for Apache Kafka when listener lifecycle and transaction wiring are useful | The native client or another stream runtime gives required control and is owned by the team | Consumer lag, rebalance, duplicate, poison-record, offset, and transaction evidence |
| Modular monolith | Spring Modulith when functional module boundaries and event publication need enforcement | Independent deployment or security ownership is proven, not merely desired | Module verification, dependency graph, event contract, and extraction seam |
| Cloud platform concerns | Spring's runtime integration only at the Java boundary | Deployment, service topology, secrets, network policy, or cluster policy is the real decision | Use `cloud-architecture`, `kubernetes-platform`, and `observability-monitoring` |
| AI integration | Spring AI only as an adapter around an owned application use case | Model risk, data policy, evaluation, or agent permissions are the material decision | Use `ai-llm-integration`, `ai-security`, `ai-evaluation`, and `ai-app-architecture` |

Spring MVC and WebFlux are separate optional web modules; WebFlux is designed
for non-blocking processing and Reactive Streams backpressure, while MVC is the
Servlet-based stack ([Spring WebFlux](https://docs.spring.io/spring-framework/reference/web/webflux.html)).
The choice is therefore an end-to-end execution-model decision, not a
controller annotation choice (synthesis).

Spring Data reduces data-access boilerplate, but repository defaults do not
define the transaction boundary for every application query. Spring Data JPA
documents inherited repository transaction settings and the need to make
declared query methods transactional when that is required
([Spring Data repositories](https://docs.spring.io/spring-data/commons/reference/repositories.html),
[Spring Data JPA transactions](https://docs.spring.io/spring-data/jpa/reference/jpa/transactions.html)) (synthesis).

## Proxy, transaction, and annotation discipline

### Keep annotations at a boundary

Use an annotation when it declares a boundary that a reviewer can name:

- composition: bean registration and configuration;
- transport: HTTP, messaging, or scheduled entry point;
- cross-cutting policy: transaction, security, retry, or observation; or
- lifecycle: startup, readiness, drain, or close.

Do not stack unrelated cross-cutting annotations on a domain method. Split the
entry point from the application service, keep policy in one visible place, and
make the call graph testable. A class that is simultaneously a controller,
transaction owner, message listener, scheduler, retry policy, and repository is
a boundary failure, not a productivity win (synthesis).

Spring's default declarative transaction mode uses proxies. Only calls entering
through the proxy are intercepted; a self-invocation within the target does not
start the declared transaction ([Spring transaction annotations](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html)).
Treat this as a testable runtime fact:

- place transaction ownership on an application service called from another
  bean, or use explicit programmatic transaction control when the flow needs it;
- do not rely on a private helper or a same-class call to change propagation;
- test the proxy type and context in which the transaction advisor is registered;
- document advice ordering when security, retry, caching, or transaction
  behaviour crosses the same method (synthesis).

Spring's default declarative rule rolls back for unchecked runtime exceptions
and errors, but not checked exceptions. Set rollback rules to the business
failure contract rather than assuming an exception name implies rollback
([Spring rollback reference](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/rolling-back.html)).
Keep network calls, broker waits, and long file operations outside a database
transaction unless the resource and timeout evidence justify holding the
transaction open (synthesis).

For each transactional flow, record:

- owner and entry boundary;
- resource manager and transaction manager;
- propagation, isolation, timeout, and rollback policy;
- read-only intent and what the database actually enforces;
- duplicate, deadlock, timeout, and partial-side-effect behaviour; and
- reconciliation or outbox action when a second system is involved.

## Configuration, health, metrics, and shutdown

### Configuration

Bind related settings to typed configuration objects. Validate required values
at startup. Distinguish an optional integration from a missing value that makes
the service unsafe to run. Spring Boot supports external properties, YAML,
environment variables, command-line arguments, profile-specific files, and
configuration trees; later sources can override earlier ones
([Spring Boot external configuration](https://docs.spring.io/spring-boot/reference/features/external-config.html)).

Write down the effective source and precedence for every operationally material
setting. Never expose credentials through configuration diagnostics, logs, or
an unrestricted management endpoint. Secret storage and cloud configuration
belong to the security and cloud owners; this reference only requires the
application to fail safely when the binding is absent or malformed (synthesis).

### Health and metrics

Separate process liveness, readiness to receive traffic, dependency health, and
business checks. A dependency outage should remove readiness or degrade the
affected capability according to the service contract; it should not make every
diagnostic endpoint useless. Do not put a remote call with an unbounded timeout
in a liveness check (synthesis).

Actuator endpoints are both an exposure and an access decision; the `health`
endpoint is a built-in example, and the `shutdown` endpoint is disabled by
default in the documented endpoint model
([Spring Boot Actuator endpoints](https://docs.spring.io/spring-boot/reference/actuator/endpoints.html)).
Expose only the management surface required by the platform. Keep management
traffic on a separately controlled path when the deployment permits it (synthesis).

Boot uses Micrometer for application metrics and can configure a composite
meter registry from the registries on the classpath
([Spring Boot metrics](https://docs.spring.io/spring-boot/reference/actuator/metrics.html)).
Define metric names, stable low-cardinality tags, trace correlation, and an
owner before adding a meter. A metric that cannot trigger diagnosis or action
is not production evidence (synthesis).

### Shutdown

Spring Boot performs graceful shutdown while the application context closes for
the documented embedded servlet and reactive servers; a timeout gives existing
requests time to finish and new requests are rejected according to the server
implementation ([Spring Boot graceful shutdown](https://docs.spring.io/spring-boot/reference/web/graceful-shutdown.html)).
Test the whole drain order: stop ingress, stop accepting work, finish or cancel
in-flight work, commit or abandon offsets safely, close pools and clients, then
exit. Treat the platform termination budget as a constraint and record what
happens when the budget expires (synthesis).

## Failure semantics by flow

| Flow | Make explicit | Failure evidence |
| --- | --- | --- |
| HTTP request | validation, timeout, cancellation, response contract, correlation | client disconnect, dependency timeout, malformed input, and safe error response |
| Transactional command | transaction owner, rollback rule, isolation, idempotency | duplicate command, deadlock, checked exception, and commit failure |
| WebFlux pipeline | scheduler boundary, backpressure, cancellation, blocking prohibition | blocked event loop, slow subscriber, cancelled client, and bounded queue |
| Integration message | channel type, error channel, retry, dead letter, and replay owner | handler failure, missing subscriber, poison message, and message loss check |
| Kafka listener | acknowledgement point, offset transaction, retry, pause, and rebalance | duplicate delivery, poison record, rebalance, broker outage, and shutdown |
| Batch job | identity, restart point, item transaction, skip policy, and operator action | partial chunk, restart, duplicate input, permanent failure, and manual stop |
| Configuration | required versus optional, source precedence, secret reference | missing file, invalid value, conflicting profile, and redacted diagnostics |
| Shutdown | drain order, timeout, forced termination, and replay boundary | termination signal during request, listener, batch step, and database commit |

Spring Integration makes the channel a first-class boundary for synchronous or
asynchronous dispatch, and documents error-channel handling for message flows
([Spring Integration channels](https://docs.spring.io/spring-integration/reference/channel.html),
[Spring Integration error handling](https://docs.spring.io/spring-integration/reference/error-handling.html)).
Do not infer asynchronous behaviour from a wire tap or endpoint name; inspect
the channel and executor configuration (synthesis).

Spring Kafka documents transaction participation for listener processing and
offset handling, but this does not remove the need to define duplicate and
poison-record recovery in the application ([Spring Kafka exactly-once](https://docs.spring.io/spring-kafka/reference/kafka/exactly-once.html)).
Use the narrowest claim that the broker, container, database, and test evidence
supports (synthesis).

## Production evidence gate

Before release, retain this cross-source production evidence bundle (synthesis):

- dependency and BOM alignment, build reproducibility, and packaged artefact;
- configuration validation with safe diagnostics;
- normal and failed request, transaction, message, Kafka, or batch paths;
- health, metrics, traces, correlation, and alert ownership;
- graceful termination and forced-termination recovery;
- migration, rollback or roll-forward, and replay procedure; and
- an ADR when MVC/WebFlux, transaction mode, Kafka delivery, Modulith, native
  compilation, or a Spring Cloud integration changes the operating model.

Missing load, failover, restore, security, or production-runtime evidence is
`NOT ASSESSED`, not a pass. Route generic security, cloud, and AI review to the
existing specialist owners named above.

## Source and currentness record

Access date for this research wave: 2026-09-05. The cited pages are official
project or specification sources. Their current page content supports the
capability statements above; exact compatibility with a consuming repository's
pinned dependency set remains `NOT ASSESSED` until its build metadata is read.
Publication or revision dates are not stated on every current reference page;
that is a gap, so re-check these links when a build, runtime, or deployment
target changes. Freshness is stable for the conceptual API boundaries and
context-bound for release compatibility (synthesis).

| Source ID | Source scope | Publication or version date | Access date | Freshness and review date | Support status | Confidence and uncertainty | Owner |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S-SPRING-CORE | Spring Framework container, web, and transaction references linked below | Not stated on every current page (gap) | 2026-09-05 | Stable concepts; review 2026-09-05 and before a framework or build change | Verified for the documented capability | High for page scope; local proxy and compatibility behaviour `NOT ASSESSED` | Java capability owner |
| S-SPRING-BOOT | Spring Boot configuration, Actuator, metrics, and shutdown references linked below | Not stated on every current page (gap) | 2026-09-05 | Context-bound; review 2026-09-05 and before a Boot or deployment change | Verified for the documented capability | High for page scope; local management exposure and platform termination behaviour `NOT ASSESSED` | Java capability owner |
| S-SPRING-DATA | Spring Data repository and JPA transaction references linked below | Not stated on every current page (gap) | 2026-09-05 | Context-bound; review 2026-09-05 and before a data-stack change | Verified for the documented capability | High for page scope; local provider and query behaviour `NOT ASSESSED` | Java capability owner |
| S-SPRING-MSG | Spring Security, Batch, Integration, Kafka, Modulith, and AI references linked below | Not stated on every current page (gap) | 2026-09-05 | Context-bound; review 2026-09-05 and before an integration change | Verified for the documented capability | High for page scope; local broker, job, module, security, and model behaviour `NOT ASSESSED` | Java capability owner |

- [Spring IoC container](https://docs.spring.io/spring-framework/reference/core/beans.html)
- [Spring transaction management](https://docs.spring.io/spring-framework/reference/data-access/transaction.html)
- [Spring transaction annotations](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html)
- [Spring MVC](https://docs.spring.io/spring-framework/reference/web/webmvc.html)
- [Spring WebFlux](https://docs.spring.io/spring-framework/reference/web/webflux.html)
- [Spring Boot external configuration](https://docs.spring.io/spring-boot/reference/features/external-config.html)
- [Spring Boot Actuator endpoints](https://docs.spring.io/spring-boot/reference/actuator/endpoints.html)
- [Spring Boot metrics](https://docs.spring.io/spring-boot/reference/actuator/metrics.html)
- [Spring Boot graceful shutdown](https://docs.spring.io/spring-boot/reference/web/graceful-shutdown.html)
- [Spring Data repositories](https://docs.spring.io/spring-data/commons/reference/repositories.html)
- [Spring Data JPA transactions](https://docs.spring.io/spring-data/jpa/reference/jpa/transactions.html)
- [Spring Security](https://docs.spring.io/spring-security/reference/)
- [Spring Batch](https://docs.spring.io/spring-batch/reference/)
- [Spring Integration](https://docs.spring.io/spring-integration/reference/)
- [Spring Kafka](https://docs.spring.io/spring-kafka/reference/)
- [Spring Modulith](https://docs.spring.io/spring-modulith/reference/)
- [Spring AI](https://docs.spring.io/spring-ai/reference/)
