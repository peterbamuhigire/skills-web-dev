# Java production-readiness review

Use `PASS`, `PARTIAL`, `FAIL`, `NOT ASSESSED`, or `NOT APPLICABLE`. Every status
must link to evidence or state the missing check, owner, and due date.

| Area | Required evidence | Status | Evidence/gap |
|---|---|---|---|
| Runtime | Supported JDK/distribution, language/bytecode target, JVM/container memory budget, GC rationale | | |
| Application | Validated config, bounded resources, startup/shutdown, error and health semantics | | |
| Security | Threat model, auth/authz, TLS/secrets, dependency/config/code scans | | |
| Data | Migrations, indexes, transaction/isolation/locking/idempotency tests, backup/restore linkage | | |
| Reliability | Timeouts, retry/bulkhead/load-shed behaviour, duplicate/partial-failure tests | | |
| Observability | Release identity, safe logs, metrics, traces, JVM evidence capture, alerts | | |
| Performance | Defined workload, p50/p95/p99, throughput/errors/resources, profile evidence | | |
| Deployment | Immutable artefact, SBOM/provenance, probes, termination, rollout and rollback/forward | | |
| Operations | Owner, dashboards, alerts, incident and recovery runbooks, escalation | | |
| Lifecycle | Support matrix, compatibility risks, upgrade trigger and review date | | |

## Verdict

- Release decision and owner:
- Blocking failures:
- Accepted residual risks:
- `NOT ASSESSED` items that prevent a production-ready claim:

