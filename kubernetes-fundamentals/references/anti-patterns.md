# Kubernetes Anti-Patterns

Twenty-two frequent mistakes. Each is an observed failure mode, not theory. Fix the underlying habit, not just the manifest.

## 1. `image: myapp:latest`

- **Why it bites:** You cannot reproduce a deploy. Rolling a fix requires a new tag because `latest` is cached and the ImagePullPolicy defaults change its meaning.
- **Fix:** Always tag with an immutable identifier — `:v1.2.3` or a short git SHA `:a1b2c3d`. Set `imagePullPolicy: IfNotPresent`.
- **Exception:** None in production. `latest` belongs in quickstart docs, not manifests.

## 2. No resource requests and limits

- **Why it bites:** Scheduler has no idea how to place Pods; noisy neighbours throttle or OOM quiet ones; HPA cannot compute utilisation.
- **Fix:** Set `resources.requests` from real observation (load test p95) and `resources.limits` at 1.5x-2x requests for CPU, equal to requests for memory.
- Use `VerticalPodAutoscaler` in recommender mode to validate numbers.

```yaml
resources:
  requests: { cpu: 100m, memory: 256Mi }
  limits:   { cpu: 500m, memory: 256Mi }
```

## 3. Liveness probe hitting a dependency

- **Why it bites:** DB blip -> every Pod fails liveness -> kubelet restarts them all -> cascading outage, often worse than the original blip.
- **Fix:** Liveness checks only local, in-process signals (deadlock detection, event-loop stall). Dependency health belongs in readiness.

## 4. Readiness and liveness on the same path

- **Why it bites:** You either never get traffic (readiness treats transient failure as dead) or get killed unnecessarily.
- **Fix:** Two endpoints, `/ready` and `/live`, answering different questions. See `references/probes-and-lifecycles.md`.

## 5. Secrets committed to Git as `kind: Secret`

- **Why it bites:** Base64 is not encryption. Anyone with repo read has production credentials.
- **Fix:** One of: external-secrets-operator pulling from AWS Secrets Manager / GCP Secret Manager / Vault; sealed-secrets; SOPS with age or KMS. Rotate anything that leaked.

## 6. `hostPath` volumes

- **Why it bites:** Breaks portability across nodes; any Pod with hostPath can escalate onto the node filesystem; rescheduling loses data.
- **Fix:** PersistentVolumeClaim with a real StorageClass. For temporary per-Pod scratch, use `emptyDir`. hostPath is only legitimate for node-local agents (DaemonSets intentionally tied to the node).

## 7. Privileged containers or unrestricted capabilities

- **Why it bites:** A compromise becomes a node compromise. Privileged equals root on the host.
- **Fix:** `securityContext.runAsNonRoot: true`, `readOnlyRootFilesystem: true`, `allowPrivilegeEscalation: false`, drop `ALL` capabilities and add only what is needed. Enforce with PodSecurity admission `restricted`.

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 10001
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  capabilities: { drop: ["ALL"] }
```

## 8. Default ServiceAccount mounted everywhere

- **Why it bites:** Every Pod gets a token that, by default, can list things it has no business seeing. Supply-chain attacks lift that token.
- **Fix:** Create a dedicated ServiceAccount per workload with minimum RBAC. Set `automountServiceAccountToken: false` on Pods that do not talk to the API.

## 9. One giant namespace for everything

- **Why it bites:** No blast radius, no per-team RBAC, no per-tenant quotas, no clean NetworkPolicy.
- **Fix:** One namespace per (application, environment) or per tenant. Apply `ResourceQuota`, `LimitRange`, and default-deny `NetworkPolicy` per namespace.

## 10. No NetworkPolicy

- **Why it bites:** Any Pod can reach any Pod, including databases, metadata services, and the API server.
- **Fix:** Default deny ingress and egress per namespace, then allow-list specific flows.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: default-deny, namespace: production }
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
```

## 11. `kubectl edit` or `kubectl patch` in production

- **Why it bites:** Cluster state drifts from Git. Next `kubectl apply` wipes your hotfix. No audit trail of why.
- **Fix:** All changes through Git and CI. If you must patch live, open a PR that encodes the change afterward and rotate the on-call.

## 12. Long-running workloads as Deployments when they should be Jobs

- **Why it bites:** Migrations, backfills, imports re-run forever when their Pod restarts. Jobs have retry semantics built in.
- **Fix:** `kind: Job` with a `backoffLimit` and `ttlSecondsAfterFinished`. Use `Deployment` only for services.

## 13. Missing PodDisruptionBudget

- **Why it bites:** Cluster upgrade drains nodes. Without a PDB, all replicas can be evicted at once. A stateful workload loses quorum.
- **Fix:** Define PDB for anything with more than one replica or state.

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata: { name: api }
spec:
  minAvailable: 2
  selector: { matchLabels: { app: api } }
```

## 14. Single-replica Deployments behind Services

- **Why it bites:** Any Pod churn (node drain, image pull, OOM) is downtime.
- **Fix:** `replicas: 2+` with topology-spread to avoid co-locating replicas on the same node or zone.

```yaml
topologySpreadConstraints:
  - maxSkew: 1
    topologyKey: topology.kubernetes.io/zone
    whenUnsatisfiable: ScheduleAnyway
    labelSelector: { matchLabels: { app: api } }
```

## 15. `emptyDir` used for durable state

- **Why it bites:** `emptyDir` dies with the Pod. Writing your primary data there guarantees loss.
- **Fix:** PVC. Only use `emptyDir` for scratch that you can lose.

## 16. CronJobs without `concurrencyPolicy`

- **Why it bites:** A slow 01:00 run overlaps with 01:05 and the job fights itself. Duplicates appear.
- **Fix:** `concurrencyPolicy: Forbid` for any CronJob that cannot tolerate overlap. Set `startingDeadlineSeconds` so missed schedules do not pile up.

## 17. Not passing `SIGTERM` to the app

- **Why it bites:** Shell wrappers swallow the signal. The process hard-kills at grace period end, drops in-flight requests, corrupts state.
- **Fix:** Use `exec` in entrypoints, or `tini` as PID 1. Verify by sending SIGTERM in local Docker.

## 18. Cluster-admin RBAC for CI

- **Why it bites:** One stolen CI token deletes the cluster. Supply-chain compromise is catastrophic.
- **Fix:** Dedicated ServiceAccount per pipeline, scoped to a namespace and to the verbs it needs. Audit with `kubectl-who-can`.

## 19. Autoscaling without a saturation metric

- **Why it bites:** HPA on CPU when the app is I/O-bound does nothing. Pods pile up memory until OOM.
- **Fix:** Pick the metric that reflects actual saturation: request latency, queue depth, RPS per Pod. Use a custom metrics adapter if CPU is not enough.

## 20. No graceful drain on shutdown

- **Why it bites:** SIGTERM arrives, Pod stops accepting connections, load balancer still sends requests for a few seconds -> 502s.
- **Fix:** `preStop` hook that flips readiness to false and sleeps for the LB deregister interval (10-15 s) before the app exits; tune `terminationGracePeriodSeconds` above the worst request time.

## 21. Using `nodePort` services as a primary ingress

- **Why it bites:** Exposes high ports directly on every node, bypasses TLS termination, fragile DNS story.
- **Fix:** Ingress controller with TLS from cert-manager, or Gateway API. `nodePort` is a debugging tool, not a production front door.

## 22. One cluster per service per environment

- **Why it bites:** Dozens of clusters to upgrade and monitor. Control-plane fees add up fast. Drift between them is inevitable.
- **Fix:** One cluster per environment; use namespaces, RBAC, and quotas for isolation. Only split clusters for a real blast-radius or compliance reason.

## Bonus: signs you have drifted

- You have more than one place that defines the same secret value.
- `kubectl get events -A | head` is never empty of warnings.
- Your runbook starts with "first, ssh to the node".
- Two engineers disagree about which cluster is production.
- Upgrading K8s involves a three-week project instead of an afternoon.

If three or more apply, stop adding features and spend a sprint flattening drift. See `kubernetes-production` and `kubernetes-saas-delivery` for the next level up.
