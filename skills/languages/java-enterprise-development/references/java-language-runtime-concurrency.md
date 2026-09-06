[Back to Java Enterprise Development](../SKILL.md)

# Java language, runtime, and concurrency doctrine

Use this reference for Java language and JVM decisions that affect correctness,
resource ownership, observability, or failure behaviour. It is a decision aid,
not a syntax tutorial. Route generic testing, security, database, API, and
distributed-systems doctrine to the owning skills.

## Currentness and evidence boundary

Accessed 2026-09-05. The Java claims below are anchored to the Oracle Java
Language and Virtual Machine specifications and Java SE API documentation. The
JVM specification used for runtime structure identifies itself as the Java SE
25 edition and is dated 2025-07-29. [JVM specification](https://docs.oracle.com/javase/specs/jvms/se25/html/index.html)

Treat the repository's pinned toolchain, compiler flags, framework adapters,
and production runtime as authoritative for a project. A preview API,
under-development specification, or feature absent from the pinned build is
`NOT_ASSESSED`, not a capability. Review this reference when the target JDK,
framework, build plugins, deployment image, or support policy changes. Proposed
review date: 2026-10-05 (inference).

## Inspect before choosing

Record the following before changing a Java system:

- JDK distribution, runtime build, language level, bytecode target, preview
  flags, module path/class path, and default locale/time zone;
- entrypoint, process model, shutdown hooks, signals, child processes,
  standard streams, health endpoint, and release identity;
- request, message, batch, and scheduled-task flow through domain rules,
  transactions, external calls, resource pools, cancellation, and telemetry;
- collection ownership, value invariants, serialisation boundaries, reflection
  use, generated code, proxies, service loading, and Native Image metadata;
- concurrency budgets for CPU, blocking I/O, database connections, queues,
  retries, timeouts, result sets, request bodies, and task lifetime.

If a fact cannot be observed in the repository, build, runtime, or an
authoritative source, write `NOT_ASSESSED` beside it and name the missing
evidence.

## Value modelling and types

The modelling defaults below are engineering policy (inference) grounded in
the cited Java type contracts and the failure modes of enterprise boundaries.

| Domain need | Preferred model | Failure to prevent |
|---|---|---|
| Immutable data crossing a boundary | Record with constructor validation and explicit wire mapping | Accidental mutable DTO or leaked persistence state |
| Entity with identity and lifecycle | Class with named transitions and invariant-preserving methods | Equality or mutation that changes business identity |
| Closed family of alternatives | Sealed interface/class with exhaustive handling | Silent fall-through when a new alternative is added |
| Open extension point | Interface or non-sealed base type with compatibility rules | Pretending an extension point is closed |
| Money or measured decimal | `BigDecimal` plus currency, scale, rounding policy, and persistence mapping | Binary rounding or inconsistent totals |
| Date without a time zone | `LocalDate` | Accidental midnight conversion |
| Moment on a timeline | `Instant`, with a zone only at presentation or business-zone boundaries | Machine-local time drift |
| User-facing text or number | Explicit `Locale` and formatter at the edge | Host-locale output in APIs, logs, or tests |
| Identifier with domain meaning | Small value type or validated record | Mixing unrelated strings or numeric IDs |

Records are shallowly immutable carriers for a fixed set of components, not a
promise that every referenced object is immutable. Validate invariants in the
canonical constructor, use defensive copies for mutable components, and keep
transport-specific names out of the domain model. [Record API](https://docs.oracle.com/en/java/javase/26/docs/api/java.base/java/lang/Record.html)

Use generics to express ownership and substitution at compile time. Reject raw
types and unchecked casts at the boundary. Return the narrowest useful
interface, choose variance deliberately (`? extends` for producers and `?
super` for consumers), and make nullability explicit in the contract. Do not
use a generic type parameter to disguise two values with different invariants.

## Collections and streams

The ownership and selection rules in this section are engineering policy
(inference); the cited API pages establish the platform contracts.

Select a collection by its contract: ordering, duplicate policy, key equality,
null policy, mutation ownership, access pattern, and expected size. Copy incoming
collections before retaining them when the caller can mutate them; expose an
unmodifiable view or immutable copy when the owner must retain control. The
collections API marks some operations as optional, so do not infer support from
the interface alone. [Collection API](https://docs.oracle.com/en/java/javase/26/docs/api/java.base/java/util/Collection.html)

A stream is a source, intermediate operations, and a terminal operation. Use a
stream for a readable finite transformation or reduction; use a loop when
early exit, checked failure, mutation, or resource lifetime is clearer. Keep
side effects at the terminal boundary, do not reuse a consumed stream, and make
ordering and duplicate semantics visible. The Stream API describes streams as
pipelines rather than collection replacements. [Stream API](https://docs.oracle.com/en/java/javase/26/docs/api/java.base/java/util/stream/Stream.html)

Do not use `parallelStream()` as a server-side capacity control. It has no
relationship to a database pool, downstream quota, or request cancellation.
Adopt parallel data processing only after a controlled workload shows a benefit,
the executor/resource budgets are understood, and the failure path is tested.

## Records, sealed types, and patterns

The design guidance below is an inference from the cited language contracts and
the need to make domain variants and null handling explicit.

Use sealed types where the domain really is closed at the boundary being
modelled. Pair them with an exhaustive `switch` that makes an unrecognised
variant fail at compile time where possible. Add an explicit `null` policy;
`null` does not match a record pattern. [Record patterns](https://docs.oracle.com/en/java/javase/25/language/record-patterns.html)

Use pattern matching to keep type tests and extracted values together, but keep
business decisions in named methods when the `switch` becomes a policy table.
Order guarded and broad patterns deliberately because a preceding pattern can
dominate a later label. [Pattern matching with `switch`](https://docs.oracle.com/en/java/javase/25/language/pattern-matching-switch.html)

Do not enable a preview pattern merely because an example compiles on a local
JDK. Confirm compiler and runtime flags, CI reproducibility, packaging, support,
and rollback in the pinned toolchain. The Oracle language guide warns that a
preview feature may change or disappear, so preview use is a recorded ADR,
not a default style. [Preview feature note](https://docs.oracle.com/en/java/javase/25/language/pattern-matching-switch.html)

## Modules, reflection, and serialisation

The boundary rules below are engineering policy (inference); the cited
specifications describe the runtime mechanisms, not a complete architecture.

Use JPMS modules when they enforce a real dependency boundary, service-provider
contract, or runtime image constraint. Keep `exports`, `opens`, `uses`, and
`provides` intentional. Start with a package-level dependency map and add
`module-info.java` when the team can keep the module path, test path, reflection
and framework configuration coherent. A named module and an unnamed module
have different runtime identity and readability rules. [Module API](https://docs.oracle.com/en/java/javase/26/docs/api/java.base/java/lang/Module.html)

Treat reflection as an integration seam. Record the class, member, access mode,
caller, module opening, generated proxy, service loader, and test that proves it.
Reflection exposes runtime JVM structures and can therefore diverge from the
source-level design. [Reflection package](https://docs.oracle.com/en/java/javase/26/docs/api/java.base/java/lang/reflect/package-summary.html)

Do not use Java native serialisation for untrusted input or a public wire
contract. If legacy serialisation is unavoidable, define the allowed classes
and graph limits, install an `ObjectInputFilter`, test rejection, and document
compatibility ownership. Oracle's API documentation states that untrusted
deserialisation is dangerous and describes filtering by class and resource
limits. [ObjectInputFilter API](https://docs.oracle.com/en/java/javase/26/docs/api/java.base/java/io/ObjectInputFilter.html)

For serialisable classes that must survive evolution, make the compatibility
policy explicit and review the `serialVersionUID`; the API documentation warns
that relying on computed identifiers is sensitive to class details.
[Serializable API](https://docs.oracle.com/en/java/javase/26/docs/api/java.base/java/io/Serializable.html)

Native Image uses static reachability analysis. Reflection, dynamic proxies,
JNI, resources, serialisation, and resource bundles may require reachability
metadata and tests against the produced executable. [Native Image dynamic features](https://www.graalvm.org/latest/reference-manual/native-image/dynamic-features/)

## Date-time, numeric, and internationalisation rules

The mapping rules below are engineering policy (inference) based on the cited
type semantics and common boundary failures; verify the business contract.

The `java.time` types are immutable and thread-safe. Use `Instant` for an
absolute event, `LocalDate` for a date without time, `LocalTime` for a wall-clock
time without a date, `LocalDateTime` only when the missing zone is intentional,
and `ZonedDateTime` when a named zone is part of the business rule. Persist the
chosen meaning, not merely the Java type, and test daylight-saving transitions
where the chosen zone matters. [java.time package](https://docs.oracle.com/en/java/javase/26/docs/api/java.base/java/time/package-summary.html)

Use `BigDecimal` for decimal arithmetic where scale and rounding matter. Its
documented model is an arbitrary-precision decimal with an explicit scale.
Construct it from a decimal representation, define rounding at each business
boundary, and test equality versus numerical comparison deliberately.
[BigDecimal API](https://docs.oracle.com/en/java/javase/26/docs/api/java.base/java/math/BigDecimal.html)

Pass `Locale` to parsing and formatting rather than relying on the host default.
Keep user-facing messages in `ResourceBundle` families with a deliberate base
bundle and fallback policy. Do not localise protocol tokens, database keys, or
machine-readable error codes. [Locale API](https://docs.oracle.com/en/java/javase/26/docs/api/java.base/java/util/Locale.html) [ResourceBundle API](https://docs.oracle.com/en/java/javase/26/docs/api/java.base/java/util/ResourceBundle.html)

## Exceptions and resource ownership

The handling policy below is an inference from the language's resource and
interruption semantics plus the owning boundary's recovery responsibility.

Use checked exceptions for a recoverable boundary whose caller can act; use
unchecked exceptions for violated invariants or failures that the current layer
cannot recover from. Translate once at the boundary that owns the response,
preserve the cause and correlation data, and avoid logging the same failure at
every layer. Never expose stack traces or provider details to a caller.

Use try-with-resources for every closeable resource. The language specification
preserves the primary failure and attaches close failures as suppressed
exceptions, so incident logging must retain suppressed causes.
[Try-with-resources specification](https://docs.oracle.com/javase/specs/jls/se25/jls25.pdf)

On interruption, restore the interrupt status or propagate the interruption;
do not convert cancellation into a successful result. Make ownership visible:
the method that acquires a socket, stream, lock, permit, database connection,
or task scope must define who closes, releases, cancels, or compensates it.

## JVM and process model

The operational rules below are engineering policy (inference) applied to the
runtime mechanisms described by the cited specifications and APIs.

The JVM dynamically loads, links, and initialises classes. Initialisation is
synchronised and can fail, so static initialisers must not perform network calls,
unbounded work, or irreversible registration without an explicit failure plan.
[Loading, linking, and initialising](https://docs.oracle.com/javase/specs/jvms/se25/html/jvms-5.html)

Budget the whole process rather than equating heap with memory limit. Include
heap, metaspace, code cache, thread stacks, direct buffers, garbage collector
and JIT memory, agents, JNI/native libraries, mapped files, and framework
overhead. Collect the process command line, JDK identity, release marker, GC/JFR
data, thread evidence, heap/RSS, and native-memory evidence before tuning.

For child processes, capture standard output and error, define timeout and
termination behaviour, and inspect liveness through `ProcessHandle` rather than
assuming a process identifier remains unique. The API documents that process
state changes asynchronously and that races exist between checking and acting.
[ProcessHandle API](https://docs.oracle.com/en/java/javase/26/docs/api/java.base/java/lang/ProcessHandle.html)

## Threads and bounded concurrency

The workload choices below are a synthesis of the cited thread, executor, and
semaphore contracts with enterprise resource-boundary requirements.

| Workload | Default | Required proof before changing it |
|---|---|---|
| CPU-bound calculation | Platform executor sized to measured CPU and downstream limits | Controlled workload, CPU profile, cancellation, and queue behaviour |
| Blocking request or I/O task | Virtual thread per task where the JDK, framework, driver, and libraries support it | Blocking-path test, connection/permit budget, pinning evidence, graceful shutdown |
| Long-lived scheduler or process supervisor | Named platform thread or managed scheduler | Liveness, daemon status, shutdown, missed-run and duplicate-run behaviour |
| Bulk data transformation | Sequential stream or bounded platform parallelism | Data size, ordering, memory, failure and backpressure evidence |
| External resource with a hard capacity | Any suitable thread model plus semaphore, bounded pool, or admission gate | Permit count, timeout, cancellation, rejection and recovery evidence |

Virtual threads are scheduled by the Java runtime, are intended for tasks that
spend much of their time blocked, and are not intended to make CPU work run
faster. They should not be pooled merely to limit a resource; use a resource
bound such as a semaphore instead. [Thread API](https://docs.oracle.com/en/java/javase/26/docs/api/java.base/java/lang/Thread.html) [Virtual threads guidance](https://openjdk.org/jeps/444) [Semaphore API](https://docs.oracle.com/en/java/javase/26/docs/api/java.base/java/util/concurrent/Semaphore.html)

For every executor or task scope, specify admission, maximum useful
concurrency, queue or permit behaviour, task timeout, cancellation propagation,
interruption policy, rejection/degradation, shutdown, and telemetry. A fixed
pool can bound thread and task resources; an unbounded queue can still turn
arrival pressure into memory growth. [ThreadPoolExecutor API](https://docs.oracle.com/en/java/javase/26/docs/api/java.base/java/util/concurrent/ThreadPoolExecutor.html)

Structured concurrency is useful when related subtasks must share a lifetime,
join point, cancellation policy, and error result. The current Oracle API page
marks `StructuredTaskScope` as a preview API, so inspect the exact target build
before using it. If preview use is not acceptable, retain an explicit owner
around `ExecutorService` tasks and close/cancel them in a `finally` block.
[StructuredTaskScope API](https://docs.oracle.com/en/java/javase/26/docs/api/java.base/java/util/concurrent/StructuredTaskScope.html)

## Blocking, pinning, and evidence

Do not label a call "blocking" from its method name alone. Classify the wait as
CPU, monitor/lock, parking, socket/file I/O, native/foreign call, database pool,
broker, rate limit, queue, or downstream response, then measure the resource
that is actually scarce.

For virtual-thread adoption, collect:

- JFR events for `jdk.VirtualThreadPinned`, task submission failures, socket
  reads, waits, and long pauses;
- `jcmd <pid> Thread.print` for mounted virtual threads and carriers;
- `jcmd <pid> Thread.dump_to_file -format=json <file>` for a tool-readable view
  of virtual and platform threads, noting that it is not a consistent pause;
- `jcmd <pid> Thread.vthread_scheduler` and poller evidence where available;
- carrier utilisation, runnable count, database/HTTP pool saturation, semaphore
  permits, queue depth, timeout/cancellation counts, and request traces.

Oracle's virtual-thread guide documents JFR pinning events and the `jcmd`
diagnostic commands; use the configured event threshold and tool support of the
target runtime rather than copying a default into an SLO. [Virtual-thread diagnostics](https://docs.oracle.com/en/java/javase/26/core/virtual-threads.html)

Stop a virtual-thread rollout when a blocking path pins carriers, the database
or downstream resource is unbounded, cancellation is lost, thread-local state
is unsafe, or the packaged runtime differs from the test runtime. Fall back to
a bounded platform executor for the affected integration while retaining the
evidence and an owner for remediation (inference).

## AI-agent inspection and degraded evidence

An AI agent may inspect, but must not infer, the platform. Require it to return:

| Agent output | Acceptance test |
|---|---|
| Version-awareness card | Values copied from wrapper, build, CI, image, or runtime output; unknown fields are `NOT_ASSESSED` |
| Runtime flow | Entrypoint, resource owner, cancellation edge, telemetry, and recovery path are named |
| Dynamic-feature inventory | Reflection, proxies, service loading, serialisation, resources, JNI, and Native Image metadata are located or marked absent only after search |
| Concurrency map | Each executor, queue, permit, pool, timeout, and shutdown owner has a source location |
| Claim ledger | Each current claim has source, scope, access date, support state, uncertainty, and review trigger |

If source, build, runtime, load, JFR, thread dump, or production evidence is
unavailable, return the narrowest qualified recommendation and list the exact
command or artefact needed. Do not report a benchmark, absence of pinning,
successful cancellation, or support status without its output. Missing evidence
is `NOT_ASSESSED`.

## Anti-patterns

- Raw `String`, `double`, or unvalidated map used for a domain invariant. Fix:
  introduce a value type and test construction, equality, serialisation, and
  persistence boundaries.
- Record used as a mutable aggregate or public persistence entity. Fix: keep
  identity/lifecycle in a class and map records at the boundary.
- Reflection or native serialisation added without an allowlist and runtime
  test. Fix: record the seam, filter input, and exercise the packaged shape.
- `parallelStream()` or an unbounded executor used to hide a slow dependency.
  Fix: measure the wait, bound the resource, and propagate cancellation.
- Virtual threads pooled, or virtual threads assumed to improve CPU latency.
  Fix: create per task and bound the scarce downstream resource.
- Interrupted work catches `InterruptedException` and continues. Fix: restore
  status or propagate it, then release owned resources.
- Static initialiser performs external I/O or registers global state. Fix: use
  explicit startup with validation, timeout, observability, and rollback.
- Preview or framework behaviour copied from an AI answer. Fix: inspect the
  pinned compiler/runtime and official source; otherwise mark `NOT_ASSESSED`.

## Evidence record

The cited pages are primary vendor/specification sources, accessed 2026-09-05.
Source scope is limited to the Java APIs/specifications and runtime diagnostics
described beside each claim. Framework-specific thread scheduling, driver
support, Native Image compatibility, and lifecycle remain context-bound to the
project's pinned dependency graph. Archive snapshot status, local build output,
load test, production profile, and reviewer sign-off are `NOT_ASSESSED` in this
reference and must be supplied by the implementing project.

| Source family | Scope | Publication/version date | Freshness and support | Review and uncertainty |
|---|---|---|---|---|
| Oracle JLS/JVMS and Java SE API pages | Language, JVM, collections, types, processes, time, serialisation, and concurrency contracts | Specification date is recorded above; individual API page date `NOT_ASSESSED` | Current at access for the cited page; official contract, not a project compatibility proof | Review 2026-10-05; target JDK and vendor build remain context-bound |
| OpenJDK virtual-thread proposal | Virtual-thread intent and adoption constraints | Page date `NOT_ASSESSED` | Official design record; implementation details remain target-runtime dependent | Review with the target JDK; performance and pinning outcome `NOT_ASSESSED` without runtime evidence |
| Oracle runtime diagnostic guide | Thread dumps, JFR pinning evidence, and scheduler diagnostics | Page date `NOT_ASSESSED` | Current at access for the cited page; command availability is runtime-bound | Review with each runtime change; local permissions and production overhead `NOT_ASSESSED` |
