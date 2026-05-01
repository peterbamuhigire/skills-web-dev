# Workflow Automation Engines — Deep Reference

Companion to `microservices-communication/SKILL.md` §Workflow Automation. Covers
n8n, Temporal, and Apache Airflow in depth — deployment, determinism rules,
retry semantics, child workflows, signals, queries, XCom, scheduler pitfalls,
and operational concerns (HA, observability, backup, upgrades).

For generic async theory (outbox, sagas, idempotency) see
`event-driven-architecture` and `distributed-systems-patterns`. For real-time
push channels (WebSocket, SSE) see `realtime-systems`. This file does not
duplicate that material.

---

## 1. When To Reach For A Workflow Engine

Three signals that synchronous request/response is not enough:

1. The unit of work spans minutes to days (saga compensation, video transcoding,
   onboarding with manual approval steps).
2. The unit of work needs durable retry across process crashes and deploys.
3. The unit of work has dependency structure — a DAG, or a saga with
   compensations.

Each engine answers a different version of "async":

- n8n — connect SaaS APIs and internal endpoints with low-code; webhook- or
  schedule-triggered.
- Temporal — author durable, long-running application workflows in real code
  with exactly-once-effect semantics on activities.
- Airflow — schedule data pipelines (ETL/ELT) where DAG structure is fixed and
  runs are time-boxed.

---

## 2. n8n Self-Hosted

### 2.1 Concepts (per docs.n8n.io/workflows)

- Workflow — automated process built by connecting nodes; supports manual
  execution, scheduling, error handling.
- Nodes — building blocks. Categories: core nodes (Code, HTTP Request, Filter,
  Set, IF), action nodes (third-party SaaS integrations), trigger nodes.
- Connections — wires that pass JSON items from one node's output to the next
  node's input.
- Sticky Notes — in-canvas annotations.
- Triggers — Webhook Triggers ("Event-driven activation through HTTP requests")
  and Schedule Trigger ("Time-based automation").
- Credentials — encrypted at rest using `N8N_ENCRYPTION_KEY`; referenced by
  node configuration so secrets never appear in workflow JSON.
- Executions — every run is logged with per-node input/output and is retriable
  from the UI.

### 2.2 Self-Host Topology (Debian/Ubuntu)

- Container: `n8nio/n8n:latest` on Docker.
- Reverse proxy: Nginx or Traefik terminates HTTPS in front of port 5678.
- Backing store: PostgreSQL (do not run with the default SQLite past prototyping).
- Queue mode for HA: enable `EXECUTIONS_MODE=queue`, add Redis, run multiple
  worker processes (`n8n worker`); main process handles UI and webhooks.
- Backup: `pg_dump` of the n8n database plus the encrypted credentials file
  on the n8n volume. Both are required to restore — credentials are useless
  without the matching encryption key.

### 2.3 When n8n Fits

- Webhook-to-SaaS integration glue (Stripe to Slack, Airtable to email, etc.).
- Internal automations the ops team owns and edits in the UI.
- Scheduled report exports and notifications.

### 2.4 When n8n Does Not Fit

- Long-running customer-facing transactional workflows with strict
  exactly-once-effect semantics — pick Temporal.
- Hourly batch ETL with complex DAG structure, backfill, and data-team
  ownership — pick Airflow.

---

## 3. Temporal

### 3.1 Definitions (per docs.temporal.io)

- Workflow Definition — code that defines a sequence of steps; running it
  produces a Workflow Execution.
- Activity — a normal function that performs a single, well-defined action,
  short or long running, such as calling another service, transcoding media,
  or sending email.
- Workflow vs Activity — workflow code orchestrates activity execution and
  persists results; activities can be non-deterministic, workflows cannot.

### 3.2 Determinism Rule (mandatory)

Workflow code is replayed from event history on worker restart. Every replay
must produce the same decisions as the original execution. Therefore workflow
code must not call:

- `time.Now()` / `Date.now()` directly — use `workflow.Now()` instead.
- `rand.Int()` / `Math.random()` — use `workflow.SideEffect` or push into an
  activity.
- Direct network or filesystem I/O — wrap in an activity.
- `os.Getenv()` for values that may change — read at activity time.
- Goroutines / threads / native promises — use the SDK's workflow concurrency
  primitives.

Violating this rule corrupts replay and the workflow will fail with a
non-deterministic-history error on the next worker restart.

### 3.3 Retry Policy Parameters

Per `docs.temporal.io/encyclopedia/retry-policies`:

| Parameter | Definition | Default |
|-----------|------------|---------|
| Initial Interval | Amount of time that must elapse before the first retry occurs. | 1 second |
| Backoff Coefficient | The value dictates how much the retry interval increases. | 2.0 |
| Maximum Interval | Specifies the maximum interval between retries. | 100 x Initial Interval |
| Maximum Attempts | Specifies the maximum number of execution attempts that can be made in the presence of failures. | unlimited |
| Non-Retryable Errors | Non-Retryable Errors specify errors that shouldn't be retried. | none |

Tune Initial Interval high (e.g. 30s) for downstream APIs with strict rate
limits, and set Maximum Attempts to bound noisy failure modes that should
escalate to a human rather than retry forever.

### 3.4 Timeouts

- `startToCloseTimeout` — bounds a single activity attempt.
- `scheduleToCloseTimeout` — bounds the activity including all retries.
- `heartbeatTimeout` — long activities must call `Activity.heartbeat()` inside
  this interval; missing a heartbeat marks the attempt failed and triggers
  retry.

### 3.5 Signals, Queries, Child Workflows

- Signals — asynchronous external messages delivered into a running workflow
  (e.g. `workflow.signal('approved', payload)`). Use for human approval steps,
  cancellation, payload updates.
- Queries — synchronous, read-only inspection of workflow state without
  mutating it (`workflow.query('getStatus')`). Use for status endpoints.
- Child Workflows — decompose long workflows into composable sub-workflows;
  the parent receives the child's result or failure as if it were an activity.
- Continue-As-New — when event history grows large (thousands of events),
  end the current execution and start a fresh one with the same workflow ID
  and a carry-over input.

### 3.6 SDK Languages

Temporal publishes SDKs for Go, TypeScript, Java, Python, .NET, and PHP. Tier
of support varies — confirm against the current SDK landing page before
committing to a language.

### 3.7 Self-Host Topology

Temporal cluster services:

- Frontend — gRPC/HTTP API, terminates SDK traffic.
- History — owns event histories; the persistence DB IS the workflow state.
- Matching — hands tasks to workers via task queues.
- Worker — internal system worker for cluster housekeeping (not user
  workflows; user code runs in your own worker processes).

Persistence stores: Cassandra, PostgreSQL, or MySQL. PostgreSQL is the
sweet spot for small/medium clusters.

---

## 4. Apache Airflow

### 4.1 Definitions (per airflow.apache.org docs)

- DAG — "a model that encapsulates everything needed to execute a workflow",
  including schedule, tasks, dependencies, callbacks. Name comes from
  "directed acyclic graph".
- Tasks — "discrete units of work that are run on workers".
- Task forms — "Operators, Sensors or TaskFlow".
- XCom — cross-task communication via the metadata DB; small values only.

### 4.2 Pitfalls

- Scheduler latency — tasks can sit in `scheduled` state for seconds to
  minutes. Airflow is not a sub-second orchestrator.
- DAG-as-code complexity — dynamic DAG generation evaluated at parse time
  hammers the scheduler; prefer TaskFlow or dynamic task mapping for fan-out.
- XCom is not a queue — it persists in the metadata DB; do not push large
  payloads. Store the blob in S3/MinIO and pass a pointer in XCom.
- Time-zone confusion — DAG `start_date` and `schedule` interpretation in
  UTC vs local time bites teams new to Airflow.
- Backfill semantics — `catchup=True` with a far-back `start_date` will
  spawn a flood of runs; default to `catchup=False` for new DAGs.

### 4.3 Executors And HA

- LocalExecutor — single-host, parallel via subprocess. Fine for small estates.
- CeleryExecutor — workers across many hosts via Redis/RabbitMQ. Standard HA
  choice for self-hosted Airflow.
- KubernetesExecutor — each task runs as a pod; good for variable workloads.
- Scheduler — runs as multiple instances active-active in current 2.x
  versions; verify against the version you deploy.
- Web server — stateless; run two behind a load balancer.
- Metadata DB — the critical asset. Postgres with replication and PITR.

---

## 5. Decision Matrix

| Concern | n8n | Temporal | Airflow |
|---------|-----|----------|---------|
| Programming model | Visual / low-code; JS Code nodes for escape hatch | Workflow-as-code (Go / TS / Java / Python) | DAGs in Python |
| Durability across crashes | Yes (DB-persisted execution history) | Yes (Event History is the source of truth) | Yes (metadata DB) |
| Sub-second step latency | Limited | Designed for it | No (scheduler tick) |
| Long-running (days+) | OK for simple cases | Yes — designed for it | Use sensors / external triggers |
| Authoring audience | Ops / non-engineers | Backend engineers | Data engineers |
| Best fit | SaaS integrations, ops glue, low-code | Customer-facing async transactions, sagas, durable retry | Scheduled batch / data pipelines (ETL) |

Picking rule:

- "Glue this webhook to that API and Slack me on failure" → n8n.
- "This onboarding takes 30 days, must survive deploys, and we cannot lose
  state" → Temporal.
- "Refresh six tables every night and backfill last week" → Airflow.

---

## 6. Operational Concerns

### 6.1 Observability

- n8n — built-in execution log per workflow with node-level inputs/outputs;
  filter by status. Ship structured logs to the central log store.
- Temporal — Server and SDKs export Prometheus metrics; full event history is
  visible in the Web UI; integrate with SigNoz via the OTel collector.
- Airflow — scheduler/worker metrics via StatsD or OpenTelemetry; Web UI
  provides per-DAG/per-task views and Gantt for bottleneck analysis.

### 6.2 High Availability

- n8n — queue mode with Redis, multiple worker processes; PostgreSQL HA
  underneath.
- Temporal — Frontend / History / Matching cluster services; persistence DB
  (Cassandra/Postgres/MySQL) is the critical asset.
- Airflow — active-active scheduler in current 2.x; stateless web server;
  metadata DB and executor are the HA story.

### 6.3 Version Upgrades

- All three keep workflow definitions compatible across minor versions but can
  break on majors. Pin versions; rehearse upgrades on a staging DB clone.
- Temporal: workflow versioning APIs (`GetVersion` in Go SDK; equivalents in
  others) let in-flight workflows take a different code path on resume — use
  this when changing workflow logic in ways that would break replay.
- Airflow: pin provider package versions alongside the core; provider bumps
  break operators independently of core upgrades.
- n8n: read the upgrade notes — node schema changes occasionally require
  re-saving workflows.

### 6.4 Backup

- n8n — PostgreSQL dumps plus the encrypted-credentials file. Both are
  required to restore.
- Temporal — back up the persistence DB; the History service IS the workflow
  state. Rehearse restore quarterly.
- Airflow — back up the metadata DB; DAGs themselves live in source control
  and are redeployed from there.

### 6.5 Security

- All three: do not expose admin UIs to the public internet. Front them with
  the API gateway plus SSO/IP allowlist.
- n8n: rotate `N8N_ENCRYPTION_KEY` requires re-saving every credential —
  treat as a sensitive ops procedure.
- Temporal: enable mTLS between SDK clients, workers, and the Frontend
  service in production.
- Airflow: lock down the Web UI with RBAC roles; the default `Admin` role can
  trigger arbitrary DAG runs.

---

## 7. Cross-References

- `event-driven-architecture` — broker selection, outbox pattern, saga
  patterns; complement Temporal sagas with broker-backed events when other
  services need to react.
- `realtime-systems` — push channels (WebSocket, SSE) for status updates back
  to clients while a workflow runs.
- `distributed-systems-patterns` — idempotency keys, exactly-once-effect, and
  cross-service consistency tradeoffs.
- `observability-monitoring` — wiring engine metrics into SigNoz / Prometheus
  / Grafana with diagnosis-first dashboards.
- `database-reliability` — backup and PITR discipline for the persistence
  stores all three engines depend on.
