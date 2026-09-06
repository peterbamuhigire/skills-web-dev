# Enterprise Java red-team scenarios

Return to [Java Enterprise Development](../SKILL.md).

These are decision probes, not canned solutions. Each response must first
establish the exact runtime, framework, dependency, deployment, and data estate.

| Scenario | Required judgement | Evidence that prevents guessing |
|---|---|---|
| Java 17 service to Java 25 | Stage toolchain, dependency, runtime and rollout changes; use compatibility checkpoints rather than a blind version jump | Current build/tests, dependency graph, removed/deprecated API scan, performance baseline, canary and rollback boundary |
| WebLogic Java EE with `javax.*` | Separate supported WebLogic upgrade, namespace migration, specification changes and business-code modernisation | Estate inventory, server/JDK/database certification, descriptors, shared libraries, integration tests and deployment rehearsal |
| Intermittent 10-second latency | Correlate the deployment change with traces, pools, SQL, JVM pauses, CPU and downstream latency before changing flags | Version markers, p95/p99 timeline, trace exemplars, JFR, GC, pool and database evidence |
| Kubernetes OOMKill below `-Xmx` | Account for metaspace, direct buffers, thread stacks, code cache, agents and other native memory | Pod termination reason, cgroup limit, NMT/JFR, thread count, RSS and heap evidence |
| Hibernate issues 2,000 queries | Identify the access path and required result shape; choose fetch joins, entity graphs, batching, projections or SQL-centric access deliberately | SQL count, query plan, cardinality, transaction boundary and regression test |
| Retried payment must not charge twice | Define an authorised idempotency key and durable request/result state; isolate provider ambiguity and reconciliation | Unique constraint/state machine, concurrent and retry tests, provider contract, audit record and recovery drill |
| Kafka redelivery | Assume at-least-once delivery unless proven otherwise; make the business effect idempotent | Offset/ack policy, deduplication transaction, duplicate and poison-message tests, lag telemetry |
| 50,000-line ERP proposed as 40 services | First expose modules and coupling; distribute only boundaries with independent ownership, release or scaling needs | Dependency map, data ownership, team topology, SLOs and operational-cost estimate |
| "Native is faster" | Compare startup, memory, steady-state throughput, build/debug cost and compatibility for the real workload | Same-workload JVM/native benchmark, reachability tests, profiles and operational rehearsal |
| Oracle RAC service | Use service-based connectivity and decide whether UCP/FAN/FCF, load balancing and Application Continuity are required | Certified driver/JDK matrix, service configuration, transaction replay analysis and controlled failover test |
| Spring OIDC resource server | Delegate identity, validate issuer/audience/algorithms and map claims to least-privilege authorities | Provider metadata, key rotation and negative-token tests, authorization matrix and security-specialist review |
| Fifty-million-row reconciliation | Partition or stream bounded work with restartable checkpoints; keep transactions and memory bounded | Representative data, throughput window, restart/failure tests, database plan and reconciliation totals |
| Intermittent deadlock | Capture multiple thread dumps and JVM evidence before changing synchronization | Deadlock graph, lock owners/waiters, workload reproduction and concurrency regression test |
| Mission-critical Java 8 with no tests | Build a characterization and operational safety net before dependency or runtime migration | Supported-state inventory, production traces, golden cases, data reconciliation and staged rollback |
| WebFlux proposed for 10,000 users | Base the choice on concurrency shape and blocking dependencies, not user count; compare MVC/virtual threads where supported | Arrival rate, concurrent in-flight I/O, blocking inventory, load test and operator capability |
| Complex Oracle reporting SQL | Prefer jOOQ or JDBC when SQL is the core abstraction; keep ORM for workloads it models well | Required SQL features, plans, bind behaviour, result-volume/memory test and database-specialist review |

For every scenario, report `PASS`, `PARTIAL`, `FAIL`, `NOT ASSESSED`, or
`NOT APPLICABLE` per evidence area. A plausible design without execution or
target-environment proof is not production validation.
