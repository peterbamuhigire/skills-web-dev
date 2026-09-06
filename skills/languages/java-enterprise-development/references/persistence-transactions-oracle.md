[Back to Java Enterprise Development](../SKILL.md)

# Persistence, transactions, and Oracle JDBC

Use this reference when a Java service must preserve a database invariant while
choosing between JDBC, JPA/Hibernate, Spring Data, jOOQ, stored procedures, or
schema-migration tooling. It is a decision and evidence guide, not a framework
tutorial. Pair it with `database-design-engineering` for schema ownership and
access patterns, `database-reliability` for recovery and database operations,
and `reliability-engineering` for service-level failure policy.

## Evidence boundary and currentness

The parent Java skill names a Java source register. Use the [Java enterprise
currentness register](../../../../docs/source-registers/java-enterprise.md) for
the portfolio evidence record, then pin the JDK, JDBC driver, database release,
ORM/provider, framework, pool, and migration-tool versions from the build and
deployment artefacts before relying on a concrete API or support statement.
This reference deliberately prefers stable concepts and links to the official
documentation listed in the source ledger. Exact method signatures, defaults,
support matrices, and vendor error codes remain `NOT ASSESSED` until checked
against the pinned environment.

| Source | Scope admitted | Currentness record |
|---|---|---|
| [JDBC transaction tutorial](https://docs.oracle.com/javase/tutorial/jdbc/basics/transactions.html) | Auto-commit, commit, rollback, savepoints, isolation discovery, and driver capability checks | Accessed 2026-09-05; stable concept source; exact runtime behaviour remains driver/database-bound |
| [Jakarta Persistence specification](https://jakarta.ee/specifications/persistence/3.2/jakarta-persistence-spec-3.2.html) | Persistence-context transaction requirements, versioning, lock modes, and lock-failure semantics | Final release dated 2024-04-10; accessed 2026-09-05; use the pinned Jakarta level for API compatibility |
| [Spring transaction reference](https://docs.spring.io/spring-framework/reference/data-access/transaction.html) | Resource-local/JTA abstraction, declarative boundaries, propagation, rollback rules, and proxy limits | Accessed 2026-09-05; current documentation is time-sensitive; verify against the pinned Spring line |
| [Hibernate ORM user guide](https://docs.hibernate.org/orm/current/userguide/html_single/) | Session/transaction patterns, locking, batching, and provider behaviour | Accessed 2026-09-05; current guide is time-sensitive; provider-specific details need a pinned version |
| [jOOQ transaction management](https://www.jooq.org/doc/latest/manual/sql-execution/transaction-management/) | Interoperability with JDBC, Spring, and Jakarta transactions | Accessed 2026-09-05; current manual is time-sensitive; generated-code compatibility is `NOT ASSESSED` |
| [Oracle JDBC Developer's Guide](https://docs.oracle.com/en/database/oracle/oracle-database/26/jjdbc/jdbc-developers-guide.pdf) | Oracle types, LOBs, REF CURSORs, batching, result sets, and driver extensions | Published 2026-05-01; accessed 2026-09-05; release-specific driver/database compatibility remains context-bound |
| [Oracle UCP documentation](https://docs.oracle.com/en/database/oracle/oracle-database/26/jjucp/toc.htm) | Pool borrowing, pool configuration, high availability, and diagnostics | Accessed 2026-09-05; release-specific; exact pool defaults are `NOT ASSESSED` |
| [Flyway versioned migrations](https://documentation.red-gate.com/flyway/flyway-concepts/migrations/versioned-migrations) and [repeatable migrations](https://documentation.red-gate.com/flyway/flyway-concepts/migrations/repeatable-migrations) | Versioned/repeatable migration ordering and schema history | Accessed 2026-09-05; product behaviour is time-sensitive; verify the licensed edition and pinned release |
| [Liquibase preconditions](https://docs.liquibase.com/community/user-guide-5-0-4/what-are-preconditions) | Preconditions that gate changeset execution | Page updated 2026-08-21; accessed 2026-09-05; API and edition details remain context-bound |

No direct quotations are used. The rules below are paraphrases or synthesis of
the linked sources; any local recommendation is labelled `(inference)` where it
depends on more than one source or on operational judgement.
Archive snapshots were not captured in this task, so archival proof for the live
links remains `NOT ASSESSED`; run the archive check before publishing a release
evidence packet.

## Select the persistence boundary

Choose the smallest abstraction that exposes the required invariant and query
shape. Do not select a framework because its repository interface hides the
SQL; inspect the generated or executed SQL before accepting the boundary.

| Need | Prefer | Proof before adoption | Failure to expose early |
|---|---|---|---|
| SQL-led read/write path, vendor syntax, or a small explicit unit of work | JDBC | Parameterised SQL review, resource-lifecycle test, query-plan evidence, and driver integration test | Leaked resources, SQL drift, partial batches, and hidden driver behaviour |
| Aggregate-centred object graph with provider-managed unit of work | JPA with Hibernate or another pinned provider | Entity model, flush/SQL trace, lazy-boundary test, lock-conflict test, and migration compatibility | Accidental lazy loads, flush surprises, stale entities, and over-fetching |
| Repository conventions over JPA | Spring Data JPA | Repository transaction map, generated query review, and explicit service-level transaction tests | A repository method appears atomic while its caller's boundary is wrong |
| SQL-led work with generated schema-aware Java types | jOOQ | Generated-code reproducibility, dialect review, SQL assertion, and transaction-manager integration test | Regenerated code drift, dialect assumptions, and accidental transaction ownership |
| Existing database-owned invariant, package, bulk operation, or cursor contract | Stored procedure through JDBC or jOOQ | Package signature, privilege, side-effect, timeout, result-shape, and rollback tests | Hidden writes, deployment coupling, opaque observability, and portability loss |
| Incremental schema change in version control | Flyway or Liquibase | Migration packet, clean-database replay, upgrade-path rehearsal, drift check, and rollback/forward-fix decision | Locking surprises, checksum drift, incompatible application overlap, and unrecoverable data change |

JPA defines transaction requirements for persistence-context operations and
standardises optimistic and pessimistic lock modes; it does not make provider
SQL, database lock scope, or vendor hints portable. See the [Jakarta Persistence
locking sections](https://jakarta.ee/specifications/persistence/3.2/jakarta-persistence-spec-3.2.html#locking_and_concurrency).

## Choose the transaction boundary

| Boundary | Use when | Keep outside | Evidence required |
|---|---|---|---|
| One service method and one local database resource | The invariant is wholly owned by that database | Network calls, user interaction, unbounded loops, and broker acknowledgement | Commit/rollback test, timeout behaviour, lock evidence, and transaction duration telemetry |
| Read-only database transaction | A consistent read is required or the provider needs a transaction for a lock/fetch contract | Large streaming work with no back-pressure | Isolation decision, result-set lifetime test, and replica/currentness decision |
| Resource-local transaction with an outbox row | A database change must publish an event without losing the intent | Direct broker publish inside the database transaction | Same-transaction outbox test, relay duplicate test, and reconciliation evidence |
| JTA/XA or container-coordinated transaction | Multiple resources must commit together and the cost is justified | A default choice for ordinary database plus broker workflows | Recovery-log, heuristic-outcome, timeout, failover, and operator-recovery evidence |
| Saga or compensating workflow | The flow spans independent resources or long-running steps | Pretending the whole flow is atomic | State machine, compensation contract, replay test, and stuck-workflow runbook |

Spring documents a common transaction abstraction across JDBC, JTA, Hibernate,
and JPA, while its declarative annotations are interpreted by runtime
infrastructure and, by default, proxy semantics. A local method call that does
not cross the configured proxy is therefore a transaction-boundary risk
`(inference)`; test the real call path rather than trusting an annotation. See
[Spring declarative transactions](https://docs.spring.io/spring-framework/reference/data-access/transaction/declarative/annotations.html).

## Operate each persistence option

### JDBC

- Borrow a connection for a bounded unit of work and return it in a `finally`-
  equivalent resource scope. Close statements, result sets, streams, and
  callable resources even on a driver error.
- Do not assume a pooled connection has the desired auto-commit, isolation,
  read-only flag, schema, session time zone, current user, or driver state.
  Verify and set the state owned by the application, then prove that the pool
  returns a clean session to the next borrower `(inference)`.
- Disable auto-commit only for an explicit multi-statement unit. Commit once on
  success; roll back the whole unit on an unknown or failed outcome. Use a
  savepoint only when partial rollback is part of the business design, not as a
  substitute for a smaller transaction.
- Bind values. Allowlist identifiers and sort fragments that cannot be bound.
  Treat SQL text, bind order, row counts, warnings, and database error details as
  evidence captured by the data-access test.

JDBC documentation states that auto-commit treats individual completed
statements as transactions and exposes isolation and savepoint operations, but
also warns that driver support for isolation levels varies. Verify support with
the pinned driver and database rather than copying a matrix from memory. See the
[JDBC transaction guidance](https://docs.oracle.com/javase/tutorial/jdbc/basics/transactions.html).

### JPA, Hibernate, and Spring Data

- Put the transaction boundary in an application-service command or query
  whose invariant can be named. Keep controllers, listeners, and repository
  methods thin unless a repository method is itself the deliberate boundary.
- Treat the persistence context as a unit of work, not a cache to carry across
  requests, threads, or messages. Initialise the graph required by the boundary
  or project into a read model before the context closes.
- Add a version field to entities that can be concurrently edited or merged
  from detached state. Handle an optimistic conflict as a business conflict:
  roll back, reload, compare, and ask the caller to merge or retry only when the
  operation remains safe. Jakarta Persistence requires a version check to fail
  with an optimistic-lock exception and mark the current transaction for
  rollback when the check fails. See the [optimistic-locking specification](https://jakarta.ee/specifications/persistence/3.2/jakarta-persistence-spec-3.2.html#optimistic_locking).
- Use pessimistic locks for a short, well-understood contention window. Record
  the rows and ordering that must be locked. Do not assume a portable provider
  hint gives a particular database lock plan; the specification leaves the
  underlying mechanism and possible extra rows provider/database-bound.
- Make flush timing visible in tests. A method can fail at flush or commit even
  when entity mutation appeared successful. Assert the database outcome, not
  only the in-memory object graph.
- For Spring Data, do not let inherited repository transaction settings replace
  a service transaction decision. The official reference describes inherited
  transactional configuration and read-only settings; redeclare deliberately
  when a method needs different semantics. See [Spring Data JPA transactionality](https://docs.spring.io/spring-data/jpa/reference/jpa/transactions.html).

Hibernate's current guide covers physical transactions, contextual sessions,
locking, and JDBC batching. Provider extensions are useful only after the
provider version and generated SQL are pinned; generic doctrine remains owned
by `database-design-engineering` and `reliability-engineering`.

### jOOQ and stored procedures

- Let one transaction owner control the connection. jOOQ can work with an
  existing JDBC, Spring, or Jakarta transaction model; do not nest independent
  connection ownership beneath it. See [jOOQ transaction management](https://www.jooq.org/doc/latest/manual/sql-execution/transaction-management/).
- Generate database-aware types only from a controlled schema snapshot. Review
  generated diffs, rendered SQL, bind values, and the dialect before release.
- Treat a stored procedure as a versioned integration contract: input and output
  types, nullability, privileges, commits/rollbacks, locks, side effects,
  result ordering, timeout, and error translation must be documented and tested.
- Use a portable JDBC `CallableStatement` surface where it is sufficient. Use
  jOOQ generated routines where the project accepts its code-generation and
  dialect boundary. Do not claim that advanced cursor, array, object, or vendor
  types are portable; the jOOQ documentation itself notes that procedure
  features vary across databases. See [jOOQ stored procedures](https://www.jooq.org/doc/latest/manual/sql-execution/stored-procedures/).

### Flyway and Liquibase

| Tool path | Choose when | Control to prove | Failure to exercise |
|---|---|---|---|
| Flyway versioned migrations | The team wants an ordered migration history whose applied scripts and checksums are visible | New migrations are additive or forward-fix-only, applied history is immutable, and schema-history state is checked | An edited applied migration, missing migration, failed deployment, and old/new application overlap |
| Flyway repeatable migrations | A view, routine, or other definition is intentionally reapplied when its checksum changes | The script is safe to apply repeatedly and its dependency order is explicit | A repeatable script that is not repeat-safe or changes in an unsafe order |
| Liquibase changesets with preconditions | The release needs database-state checks before a changeset is allowed to run | Preconditions, failure action, generated SQL, and target database are reviewed | A false precondition, a check error, and a failure action that accidentally marks work complete |

Flyway documents ordered versioned migrations, checksums, schema history, and
the practice of creating a new migration rather than editing an applied one;
its repeatable migrations are reapplied when their checksum changes and must be
safe to run again. See [Flyway versioned migrations](https://documentation.red-gate.com/flyway/flyway-concepts/migrations/versioned-migrations)
and [Flyway repeatable migrations](https://documentation.red-gate.com/flyway/flyway-concepts/migrations/repeatable-migrations).

Liquibase documents preconditions as gates based on database state and exposes
explicit failure/error actions. Select the action as part of the release
contract; never use a permissive action to conceal an unmet invariant. See
[Liquibase preconditions](https://docs.liquibase.com/community/user-guide-5-0-4/what-are-preconditions).

For either tool, keep application startup from becoming an unbounded migration
runner unless ownership, locking, timeout, observability, and rollback or
forward-fix authority are explicit. Produce the repository migration packet
defined by `database-design-engineering`, then run clean-database replay,
upgrade-from-production-shape, checksum/drift, precondition, lock-contention,
and application-overlap tests.

## Oracle JDBC, UCP, and session-bound resources

### Driver and pool selection

Oracle's current developer material describes the Thin driver as a pure-Java
driver and UCP as a pool with Oracle integration for connection management and
high-availability scenarios. The choice still depends on the pinned JDK,
database, driver, pool, network, and support matrix. Record that matrix; do not
copy an `ojdbc` or UCP artefact name from another service. See [Oracle JDBC and UCP downloads](https://www.oracle.com/database/technologies/appdev/jdbc-downloads.html).

### LOBs

- Decide whether the boundary is a stream, locator, byte sequence, character
  sequence, or durable object reference. Never silently materialise a large LOB
  into heap memory.
- Keep the connection/transaction lifetime explicit while reading or writing a
  locator-backed LOB. Close streams and locators on every path, and test commit,
  rollback, connection return, and failover interruption.
- Record character encoding, maximum accepted size, truncation policy,
  redaction rules, and whether the LOB is part of the transaction's invariant.
- Use Oracle-specific LOB interfaces only behind an adapter. The current Oracle
  guide documents both standard and Oracle-specific mappings; the exact mapping
  is driver- and environment-bound. See [Oracle data access and manipulation](https://docs.oracle.com/en/database/oracle/oracle-database/26/jjdbc/data-access-and-manipulation.html).

### REF CURSORs

An Oracle `REF CURSOR` is a cursor reference returned through a callable or
prepared statement and materialised by the Oracle driver as a JDBC result set;
the current guide states that REF CURSOR results are not scrollable. Consume the
result set within the agreed resource scope, map it to an explicit result model,
and close it before returning a pooled connection. Do not expose the driver
cursor object as an API contract. See [Oracle REF CURSOR documentation](https://docs.oracle.com/en/database/oracle/oracle-database/26/jjdbc/jdbc-developers-guide.pdf).

### Batching

Use batching only after measuring the database access path and memory/lock
window. Define the unit of retry, row-count interpretation, partial-failure
policy, generated-key handling, and commit boundary. Hibernate, jOOQ, JDBC, and
Oracle update batching can have different flush and failure behaviour; compare
the executed SQL and driver results, not just the Java call shape. Oracle places
update batching and row prefetch in its performance guidance, while Hibernate
documents JDBC batching and session batching; both are evidence sources, not a
universal batch-size recommendation. See [Oracle performance and scalability](https://docs.oracle.com/en/database/oracle/oracle-database/26/jjdbc/performance-and-scalability.html) and [Hibernate batching](https://docs.hibernate.org/orm/current/userguide/html_single/#batch).

### Session state and failover

- Treat session state as part of the connection contract: schema, NLS/locale,
  time zone, application context, transaction mode, temporary objects, and
  package state need an owner and a reset test `(inference)`.
- On connection validation or failover, distinguish a safe pre-execution
  failure from an outcome that is unknown because the database may have
  committed. Query a durable idempotency key or reconciliation record before
  replaying a write.
- Oracle Application Continuity and related pool/database features can change
  how interrupted work is replayed. Adopt them only with a support matrix,
  replay-safety review, and an exercise that proves session state, side effects,
  and transaction outcome. See [Oracle Application Continuity](https://docs.oracle.com/en/database/oracle/oracle-database/26/jjdbc/application-continuity.html).

## Isolation, locking, deadlocks, and idempotency

| Problem | Default decision | Failure evidence |
|---|---|---|
| Lost update on an editable entity | Versioned optimistic check or an equivalent conditional update | Two concurrent writers; one wins and the other receives a defined conflict |
| Hot row or scarce allocation | Short pessimistic lock with a declared order and lock timeout policy | Contention, timeout, deadlock, rollback, and operator-visible outcome |
| Invariant spans a query and a write | Database constraint first; stronger isolation only when the constraint cannot express the invariant | Concurrent interleaving that would violate the invariant under the selected isolation |
| Retry after an uncertain commit | Durable idempotency key, unique business key, or reconciliation query | Connection loss after server-side work and safe replay proof |
| Deadlock | Consistent lock order, short transactions, no remote call while holding the lock, and bounded retry only after full rollback | Reproducible cycle, database diagnostic, retry count, and final business outcome |

Isolation names have database-specific meaning and availability. JDBC exposes
inspection and request of an isolation level, but the driver may substitute or
reject a requested level. Record the actual level at runtime and hand database
lock semantics to `database-design-engineering` and the vendor database skill.

Never retry an unknown write merely because the exception is transient. A retry
is safe only when the command's effect is idempotent or the service can prove
whether the first attempt committed `(inference)`. Preserve the original
correlation and idempotency key through every retry.

## Failure tests and evidence outputs

| Scenario | Test setup | Evidence to retain |
|---|---|---|
| Rollback after a mid-unit exception | Fail after one invariant-bearing write and before commit | Database state, exception translation, rollback marker, and transaction trace |
| Isolation anomaly | Run competing reads/writes against the pinned database | Actual isolation, observed interleaving, and accepted business result |
| Optimistic conflict | Concurrently update the same versioned entity | Conflict exception, rollback state, caller-visible response, and no lost update |
| Deadlock | Reverse lock acquisition order in two controlled workers | Database diagnostic, abort decision, bounded retry result, and alert signal |
| Pool session leakage | Set session state, return connection, borrow again | Before/after session state and pool validation result |
| Failover with known outcome | Interrupt before execution and after server-side work | Replay decision, idempotency lookup, and reconciliation record |
| LOB interruption | Kill or cancel a stream during read/write | Resource closure, partial-data policy, transaction outcome, and leak check |
| REF CURSOR lifecycle | Close statement/result/connection at each boundary | Row mapping, resource closure, and driver-specific error handling |
| Batch partial failure | Fail one row or a driver batch boundary | Update counts, committed rows, retry unit, and operator action |
| Migration overlap | Run old and new application versions across expand/contract stages | Lock time, compatibility, validation, rollback or forward-fix decision |
| Procedure contract drift | Change package signature or result shape in a test database | Build/runtime failure, migration gate, and compatibility response |

Produce a transaction map, persistence selection matrix, lock/isolation decision,
migration packet, version-awareness card, telemetry map, and failure-test report.
Capture transaction duration, pool wait/exhaustion, active connections, rollback
cause, lock wait/deadlock, batch size and outcome, migration identifier, and
procedure/driver error class without logging secrets or sensitive bind values.

## Handoffs

| Handoff | Send | Receiving owner |
|---|---|---|
| Schema and access design | Entity/lifecycle assumptions, access patterns, constraints, indexes, lock scope, and migration choreography | `database-design-engineering` |
| Database operations | Driver/pool matrix, failover assumptions, session state, backup/restore dependency, and recovery evidence | `database-reliability` and the vendor database skill |
| API contract | Transaction result, conflict mapping, idempotency key, timeout, and error model | `api-design-first` |
| Distributed workflow | Outbox/inbox boundary, event publication point, duplicate/replay behaviour, and compensation need | `distributed-systems-patterns` |
| Service reliability | Retry eligibility, timeout budget, circuit/degradation effect, alerts, and runbook owner | `reliability-engineering` and `observability-monitoring` |

## Anti-patterns

- Put a remote call inside a database transaction. Fix: persist intent, commit,
  and continue through an outbox or compensating workflow.
- Treat `@Transactional` as proof that a method is transactional. Fix: test the
  actual proxy/container call path and assert commit and rollback outcomes.
- Keep a Hibernate session or JDBC connection in a singleton, thread field, or
  message payload. Fix: scope it to the unit of work and close it deterministically.
- Retry a deadlock or timeout without rolling back the full transaction. Fix:
  translate the failure, discard the contaminated context, and retry only an
  idempotent command within a budget.
- Return an Oracle `REF CURSOR`, LOB locator, entity, or JDBC resource from a
  public API. Fix: consume it inside the resource scope and return an explicit
  contract.
- Choose a batch size, isolation level, or pool size from folklore. Fix: pin
  the environment, measure representative load, and retain failure evidence.
- Edit an applied migration or hide a stored-procedure change in application
  startup. Fix: use version-controlled migration history and an explicit release
  gate.

## Read next

- [`database-design-engineering`](../../../backend-databases/database-design-engineering/SKILL.md) for entities, access patterns, constraints, and migrations.
- [`database-reliability`](../../../backend-databases/database-reliability/SKILL.md) for database recovery, availability, and operational evidence.
- [`api-design-first`](../../../architecture/api-design-first/SKILL.md) for API contracts, error models, and idempotency keys.
- [`distributed-systems-patterns`](../../../architecture/distributed-systems-patterns/SKILL.md) for outbox, inbox, saga, ordering, and consistency ownership.
- [`reliability-engineering`](../../../devops-cloud/reliability-engineering/SKILL.md) for timeout, retry, degradation, and incident readiness.
