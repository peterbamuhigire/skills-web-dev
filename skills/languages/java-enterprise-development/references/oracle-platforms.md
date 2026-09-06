[Back to Java Enterprise Development](../SKILL.md)

# Oracle Java platforms and enterprise integration

Use this reference for Oracle-specific Java decisions. It does not require
Oracle products where standards or another platform better fit the system.
Consult the current source register before any version, support, licensing, or
compatibility statement, and route legal conclusions to qualified counsel.

## Oracle JDK and distribution choice

Distinguish the Java specification/language level, OpenJDK source project,
binary distribution, update stream, licence, security update channel,
commercial support, operating-system/architecture support, and production
runtime. Oracle JDK, Oracle OpenJDK builds, Temurin, Corretto, Microsoft Build
of OpenJDK, Azul, and other distributions may implement the same Java SE level
while differing operationally and commercially.

Record the exact distribution/build and evidence for:

- supported OS/architecture and container base;
- update cadence, security advisories, support end, and patch ownership;
- licence terms applicable to the organisation and deployment;
- Flight Recorder/management/crypto/provider behaviour used by the application;
- vendor support required by WebLogic, Oracle Database, or another product;
- build/runtime reproducibility and disaster-recovery availability.

Do not infer a licence right from an LTS label or an old book. Use Oracle's
current roadmap/licensing material and qualified review.

## Oracle Database Java-side boundary

Load `persistence-transactions-oracle.md` for SQL and transaction mechanics and
the database specialist for schema, plans, RAC/Data Guard, backup, and database
operations. On the Java side:

1. Pin a supported Oracle JDBC driver compatible with the JDK, database, pool,
   and framework. Test the real combination.
2. Decide between an application-owned pool such as HikariCP, Oracle UCP, or an
   application-server-managed data source from requirements: framework fit,
   Oracle HA/Application Continuity features, observability, validation,
   support, and operational ownership.
3. Set connection, statement/query, socket/network, transaction, and request
   deadlines coherently. A pool checkout timeout is not a database query
   timeout.
4. Reset or avoid session state on pooled connections: schema, NLS/time zone,
   client identifier, application context, temporary objects, transaction and
   package state. Tagging/initialisation must be deterministic and tested.
5. Use bind variables and bounded batching. Verify generated plans and child
   cursor behaviour with database evidence; do not concatenate literals to
   influence a plan.
6. Stream large results/LOBs within explicit resource and transaction lifetime.
   Test materialisation, fetch size, cancellation, retry, and memory under the
   exact driver.
7. Translate Oracle errors by stable SQL state/vendor code where appropriate,
   preserve cause and correlation, and classify retry only with transaction and
   operation semantics. Never retry every `SQLException`.

## Stored procedures and PL/SQL

Stored procedures, functions, packages, cursors, arrays, and database-defined
types are legitimate when the data boundary, performance, existing ownership,
or regulated control justifies them. Define a versioned Java/database contract:
parameter names/order/modes, SQL and Java types, nullability, array/object type
mapping, cursor/result shape, transaction ownership, error mapping, timeout,
privileges, migration order, and compatibility tests.

Use JDBC callable statements, framework adapters, or generated jOOQ bindings
according to project evidence. Close cursors/LOBs/statements/connections in the
correct order. Test package evolution and mixed-version deployment; compilation
success alone does not prove runtime contract compatibility.

## RAC, Data Guard, and continuity concepts

The database/platform owner must define topology, services, role transitions,
connect descriptors, drain/failover events, recovery objectives, and supported
driver/pool features. The application must define:

- which operations are safe to replay and how commit outcome ambiguity is
  resolved;
- transaction/session state that prevents transparent replay;
- connection validation/borrowing during node/service change;
- retry budgets and duplicate-side-effect protection;
- planned maintenance drain and rolling deployment behaviour;
- telemetry identifying database service/instance where safe and useful;
- failover and switchover tests under realistic in-flight work.

RAC awareness does not make an application highly available. Application
Continuity or replay features do not replace idempotency, commit-outcome design,
reconciliation, or business acceptance testing. If the supported topology
cannot be exercised, mark failover `NOT ASSESSED`.

## WebLogic operating model

Inventory domain, administration and managed servers, clusters, machines/node
management, JDK, WebLogic patch/support level, deployment units, libraries,
classloading descriptors, data sources, JTA, JMS, security realms/providers,
work managers, sessions, certificates, logging/diagnostics, startup scripts,
and automated configuration source.

| Concern | Decision evidence |
|---|---|
| WAR/EAR/shared library | Isolation, versioning, server-provided APIs, classloading and redeployment tests |
| JDBC/JTA | Managed resource ownership, transaction timeout/recovery logs, pool/HA configuration |
| JMS | Destination/module/targeting, delivery/idempotency, redelivery/DLQ, migration/recovery |
| Cluster/session | Stateless preference; replication/externalisation need, object compatibility and failover test |
| Deployment | Staging mode, health/readiness, traffic drain, mixed-version compatibility, rollback/forward |
| Diagnostics | Release identity, server/application logs, WLDF/JFR/JMX or supported telemetry, incident access |

Do not edit production domains manually without an owned change method and
recovery path. Separate application defects from domain/server/JDK/database
configuration, and reproduce against the supported matrix before recommending
a migration.

## Helidon, GraalVM, and OCI

Consider Helidon when its current programming model, support, footprint,
standards/API fit, OCI alignment, and team capability meet the requirement; do
not choose it solely because the database or cloud is Oracle. Verify current
major generation and migration model.

For GraalVM/Native Image, inventory reflection, proxies, resources,
serialisation, JNI, agents, dynamic classloading, monitoring, and libraries.
Compare startup, RSS, build time, throughput/tail latency, debugging, patching,
and operations against the JVM using the performance template. Native is a
deployment choice, not an automatic performance upgrade.

OCI architecture remains with `cloud-architecture` and `kubernetes-platform`.
Java implementation must use workload identity/instance principals where
appropriate, managed secret/key retrieval, bounded SDK clients, explicit
regions/endpoints, retries/timeouts, managed database connection behaviour,
telemetry, and graceful scaling. Validate exact SDK/runtime APIs before code.

## Anti-patterns

- "Oracle-grade" translated into mandatory Oracle products. Select by evidence
  and retain portable contracts where practical.
- HikariCP or UCP chosen by slogan. Test required Oracle continuity features,
  framework/server ownership, metrics, and failure behaviour.
- Retrying after a lost connection without resolving commit outcome. Use
  idempotency/reconciliation and supported continuity semantics.
- Migrating a working WebLogic system because application servers are declared
  obsolete. Establish support, cost, coupling, risk, and staged business value.
- Hard-coding connect descriptors, credentials, schema, or NLS assumptions.
  Externalise, validate, secure, and test session state.

