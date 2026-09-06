[Back to Java Enterprise Development](../SKILL.md)

# Performance, observability, and production operations

Use this reference to investigate a Java system from evidence. Pair it with
`observability-monitoring` and `reliability-engineering` for SLOs, alerts,
incident process, capacity, and recovery ownership.

## Start with the service objective

Define the critical flow, workload, latency distribution, throughput, error
rate, concurrency, data size, resource budget, and acceptable recovery. A
single average, local microbenchmark, or profiler screenshot cannot establish
production performance.

| Question | Primary evidence |
|---|---|
| Did demand change? | Request/message/job rate, payload/data size, tenant mix |
| Where is time spent? | Distributed traces, server timing, database/broker/downstream telemetry |
| Is the process saturated? | CPU/throttling, runnable/blocked threads, allocation/GC, heap/RSS/native memory, pools/queues |
| Did a release/config/schema change coincide? | Release marker, diff, migration and runtime identity |
| Can the observation be reproduced? | Controlled workload and before/after experiment |

## Telemetry contract

### Logs

Emit structured events with timestamp, level, service, environment, release,
operation, outcome, duration where meaningful, correlation and trace IDs, and
safe domain identifiers. Log once at the handling boundary. Keep secrets,
credentials, tokens, health records, payment data, and unnecessary PII out of
messages, MDC, exceptions, and dump paths.

Application logs explain behaviour. Audit records establish accountable actor,
action, object, result, time, source/correlation, reason, and protected
integrity/retention. Do not use mutable application logs as the sole audit trail.

### Metrics

Use request rate, errors, and duration for services; utilisation, saturation,
and errors for resources. Add JVM allocation/GC/heap/non-heap/thread/class data,
database/HTTP connection pools, executor/queue depth, cache behaviour,
consumer lag, batch progress, and business-invariant indicators only when an
owner can act on them. Avoid unbounded labels such as user, request, or raw URL.

### Traces

Propagate trace context across supported HTTP, messaging, and job boundaries.
Create spans around owned operations and material dependencies; record status
and bounded diagnostic attributes. Use baggage sparingly because it propagates
widely. Sampling policy must retain enough failures and tail behaviour without
claiming complete traces when sampling is active.

Spring Actuator/Micrometer or runtime-specific integrations can expose health
and telemetry; OpenTelemetry can provide vendor-neutral signals. Verify the
actual framework generation and avoid duplicate agents/instrumentation that
double-counts spans or metrics.

## Evidence-driven diagnosis

### Latency spike

```text
release/traffic marker
-> trace latency by service and dependency
-> CPU/throttling, GC/allocation, thread and pool saturation
-> database query/lock/pool and broker/downstream evidence
-> compare healthy interval
-> discriminating reproduction or safe production test
```

Do not change GC, heap, thread count, pool size, retries, or cache until the
bottleneck hypothesis predicts an observable result.

### High CPU

Confirm container/host CPU and throttling; capture a time-aligned JFR or trusted
sampling profile; inspect hot methods, allocation/GC, runnable threads, regex,
serialisation, loops, encryption/compression, and query/message demand. A thread
dump alone is a state snapshot, not a CPU profile.

### Memory failure

Distinguish Java heap exhaustion, metaspace, direct/native buffers, thread
stacks, native/JNI/agent allocation, and platform OOM kill. Preserve container
events and process RSS. Capture heap or Native Memory Tracking evidence only
under approved storage/privacy controls. Fix retention/ownership or capacity;
do not merely increase memory.

### Long GC pauses

Correlate GC logs/JFR with allocation rate, live-set growth, promotion,
humongous/large objects, heap headroom, CPU, pause distribution, and request
latency. First remove pathological allocation or retention. Change collector or
supported JVM control only in a repeatable experiment.

### Thread deadlock or exhaustion

Collect multiple timestamped thread dumps plus pool/executor/request evidence.
For deadlock, identify lock ownership and cycle; for exhaustion, distinguish
blocked downstream I/O, lock contention, undersized admission, leaked tasks,
unbounded concurrency, and slow transactions. Add a regression test or lock
ordering/ownership rule after repair.

### Connection-pool exhaustion

Measure active/idle/pending, checkout duration, request concurrency, database
sessions/waits, query and transaction duration, leaks, timeouts, and database
capacity. Increasing the pool can move failure to the database. Bound
transactions, close resources, fix slow work, and size end to end.

### Kafka consumer lag

Correlate incoming rate, processing throughput, partition assignment/rebalance,
handler latency/failures, retry/DLQ behaviour, downstream pools, batch size, and
commit/ack semantics. Scale only when partitions and downstream capacity permit;
verify replay, duplicates, ordering, and business idempotency.

## Performance method

1. Use an end-to-end load test for user objectives, a component benchmark for a
   suspected subsystem, and JMH only for carefully isolated JVM code.
2. Record environment, JDK/JVM, warm-up, workload, data/cache state, duration,
   sample/error counts, p50/p95/p99, throughput, CPU, memory/allocation/GC, and
   database/downstream load in `templates/performance-evidence.md`.
3. Profile before modifying. Change one causal factor when possible; repeat
   enough to expose run-to-run variance and compare the same workload.
4. Verify the full application after a micro-optimisation. A faster method can
   increase end-to-end latency, memory, contention, or maintenance cost.

## JVM tuning rule

Identify the exact supported runtime and ergonomics, establish a measured
baseline, collect evidence, select one supported change, repeat the workload,
compare all relevant quality attributes, and retain or revert. Keep the option,
rationale, source/review date, result, and owner. Remove obsolete inherited
flags during upgrades only after compatibility and rollback checks.

## Reliability and recovery checks

- Timeouts form a decreasing budget across call layers; retries are bounded,
  jittered where appropriate, and limited to safe/idempotent operations.
- Admission control, queues, pools, bulkheads, rate limits, and load shedding
  protect a defined resource and expose saturation telemetry.
- Startup, health, graceful shutdown, dependency outage, partial failure,
  retry exhaustion, duplicate delivery, and recovery are exercised.
- Backups are not application recovery evidence until restore, schema/version
  compatibility, secret/key access, reconciliation, and RTO/RPO are tested by
  their owning teams.

## Anti-patterns

- Random JVM flags after a symptom. Collect discriminating evidence first.
- Reporting average latency without tails, errors, load, or environment. Use a
  complete workload record.
- Adding high-cardinality telemetry labels. Keep dimensions bounded and link to
  traces/logs for detail.
- Treating a health endpoint response as business correctness or availability.
  Add critical-flow and SLO evidence.
- Capturing heap/JFR/thread evidence without access, retention, disk-space, or
  privacy controls. Make diagnostics operable and safe before the incident.

