[Back to Java Enterprise Development](../SKILL.md)

# Containers, Kubernetes, and cloud integration

This reference owns Java runtime behaviour inside a deployment selected by the
cloud, Kubernetes, container, and release specialists. It does not design
clusters, networks, accounts, IAM estates, or disaster recovery by itself.

## Packaging decision

| Requirement | Candidate | Evidence required |
|---|---|---|
| Conventional service with broad library/tool support | JVM image with supported JRE/JDK runtime | Image/runtime compatibility, startup, steady-state, memory and operations |
| Smaller runtime surface under controlled module use | `jlink` runtime image | Module closure, TLS/locale/management functionality, update process |
| Very fast startup or tight density/serverless constraint | Native Image | Compatibility metadata, build/debug cost, startup/RSS/throughput comparison |
| Managed application-server estate | WAR/EAR or server-specific package | Supported server/JDK matrix, classloading, data source/JTA/JMS and rollout evidence |

Use multi-stage builds or controlled buildpacks as project policy permits.
Pin the base by an approved immutable reference, run as a non-root UID, use a
read-only filesystem where the application supports it, keep writable paths
explicit, and scan the final image. Do not place secrets in layers or build
arguments that persist in metadata.

## JVM memory under a container limit

Budget the whole process, not only heap:

```text
container limit
  = Java heap
  + metaspace and code cache
  + thread stacks
  + direct/native buffers
  + GC/JIT/runtime native memory
  + agents/JNI/libraries
  + safety margin
```

Inspect the supported JDK's container detection and actual runtime flags. Use
RSS/container metrics, heap/GC data, thread count/stack sizing, direct-buffer
use, class count, Native Memory Tracking when justified, and pod events to
explain memory. `-Xmx` below the limit does not rule out an OOM kill.

CPU limits can alter effective processor count, common-pool sizing, GC/JIT
behaviour, request pools, and throttling. Measure throttled time and tail
latency; do not size pools from host CPUs or user count.

## Probe semantics

| Probe | Question | Failure risk |
|---|---|---|
| Startup | Has this instance had enough time to initialise? | Killing a slow but progressing start repeatedly |
| Readiness | Can it receive new work without violating correctness? | Sending traffic before migrations/config/dependencies are ready |
| Liveness | Is the process irrecoverably unable to make progress? | Restart storms caused by a transient dependency outage |

Keep liveness local and conservative. Readiness may reflect critical dependency
state, but avoid cascading the failure of a shared database through every pod
unless traffic truly cannot be served safely. Protect health endpoints and keep
their cost bounded.

## Graceful termination

1. Stop new traffic or partition assignment through the platform mechanism.
2. Allow in-flight requests within a measured grace period.
3. Stop accepting scheduled/batch work and coordinate singleton ownership.
4. Commit, roll back, checkpoint, or return message work according to the
   delivery contract; never acknowledge unfinished side effects.
5. Flush bounded telemetry and close HTTP/database/broker pools.
6. Exit before the platform's hard kill; test the sequence during rolling and
   interrupted deployment.

The termination budget must cover load-balancer propagation and application
drain behaviour. A shutdown hook that exists but has never been interrupted is
`NOT ASSESSED`.

## Capacity and autoscaling

- Size request, virtual-thread admission, database/HTTP pools, consumer
  concurrency, and queues as one system. Thousands of application tasks do not
  create thousands of database connections.
- Scale on the constraining signal: latency/saturation, queue lag, throughput,
  CPU, or a safe composite. CPU-only scaling misses blocked I/O and downstream
  exhaustion.
- Define per-instance sustainable throughput and downstream budget before
  autoscaling. Cap scale so replicas cannot overwhelm the database or identity
  provider.
- Use disruption budgets, topology, anti-affinity, and rollout settings only
  after the Kubernetes owner maps availability and capacity requirements.

## Runtime configuration and cloud identity

Separate build-time from runtime settings. Bind configuration into typed,
validated objects; fail startup for missing unsafe production values. Avoid a
combinatorial profile matrix. Retrieve secrets through the platform's managed
identity/secret mechanism, define rotation behaviour, and prevent value leakage
through environment dumps, Actuator/config endpoints, logs, or crash artefacts.

Use workload identity rather than long-lived cloud keys where supported by the
selected provider. The cloud specialist owns account, role, network, secret,
managed database, KMS, and cross-region design; this Java route owns client
initialisation, credential refresh, deadlines, pool lifecycle, telemetry, and
failure handling.

## Kubernetes/Java release checks

- Image architecture, JDK distribution/version, base digest, UID/filesystem,
  CA/time-zone/locale requirements, SBOM and scan disposition.
- Resource request/limit rationale plus heap/native/thread/direct-buffer budget.
- Startup/readiness/liveness normal and failure tests.
- SIGTERM drain, forced termination, pod disruption, rolling compatibility,
  release marker, and connection/message behaviour.
- Heap dump, JFR, thread dump, GC and native-memory capture procedure that
  respects storage, PII, access, and incident controls.
- Load/autoscaling evidence including database/broker saturation and p99.
- Restore/failover evidence from owning platform/database skills, or
  `NOT ASSESSED`.

## Anti-patterns

- Setting `-Xmx` equal to the pod limit. Reserve and measure non-heap/native
  consumers and safety margin.
- Making liveness depend on every downstream system. Use readiness/degradation
  policy and avoid restart storms.
- Assuming more pods fix latency. Find the saturated resource and protect shared
  dependencies first.
- Baking environment configuration or credentials into an image. Promote one
  image and inject validated runtime configuration.
- Using an ultra-minimal image without certificates, time-zone/locale data, or
  diagnostics required by the service. Test the real operational paths.

