# CRDs and Operators — When to Reach for One

Operators encode operational knowledge as code. They are powerful, and they are also a long-term commitment.

## Build vs install vs avoid

```text
Need declarative lifecycle for a stateful system you operate
(Postgres, Kafka, Redis, ElasticSearch)                       -> install a vetted operator
Repeated multi-step ops you do by hand on Tuesdays            -> consider an operator
A controller that just watches a ConfigMap and restarts Pods  -> a Job + CronJob is enough
A workflow only run by humans, infrequently                   -> a runbook + script
A SaaS tenant lifecycle (create namespace, quota, secrets)    -> GitOps + ApplicationSet first; operator only if dynamic
```

Rule: install before you build. Building an operator is a multi-quarter commitment (controller-runtime, reconciliation, status subresource, finalizers, upgrades, RBAC, conversion webhooks).

## Operators we install (battle-tested)

| Domain | Operator |
|---|---|
| Postgres | CloudNativePG, Zalando Postgres Operator |
| Kafka | Strimzi |
| Redis | Redis Enterprise, OT-CONTAINER-KIT/redis-operator |
| ElasticSearch | ECK (Elastic Cloud on Kubernetes) |
| Prometheus stack | Prometheus Operator (kube-prometheus-stack) |
| Cert management | cert-manager |
| Secrets | external-secrets, Sealed Secrets |
| GitOps | Argo CD, Flux |
| Service mesh | Istio, Linkerd |
| Cost | OpenCost, Kubecost |

Pin the operator version. Read its upgrade matrix. Test upgrades in staging.

## CRD hygiene

- `spec.preserveUnknownFields: false` (default in v1).
- Provide an OpenAPI schema with validation. Default values land here, not in the controller.
- Use `status` subresource so `kubectl edit` of `spec` doesn't fight the controller.
- Conversion webhooks for v1alpha1 -> v1beta1 -> v1 — do not break consumers.
- Finalizers for resources with external state. Always implement deletion correctly.

## Reconciliation patterns

- Idempotent: reconciling 10 times produces the same end state as reconciling once.
- Level-triggered, not edge-triggered. Compute desired state from `spec`; do not react to events.
- Backoff on errors. `requeue: true` with exponential delay.
- Watch only what you own. Set ownerReferences so GC cascades on delete.
- Status reflects observable reality (`observedGeneration`, conditions: `Ready`, `Progressing`, `Degraded`).

## When NOT to write an operator

- The "operator" only renders templates. Use Helm or Kustomize.
- The "operator" only runs a job on cron. Use CronJob.
- The "operator" only mirrors data between namespaces. Use Reflector / external-secrets.
- The team has no ongoing capacity to maintain a Go controller.

## CRD upgrade traps

- Helm chart upgrades skip CRDs by design. Apply CRD changes explicitly: `kubectl apply -f crds/`.
- Removing a field requires a conversion webhook + storage migration. You cannot just delete it from the schema.
- ApiServer caches CRD schemas; new fields can take a moment to validate.

## Security

- Operator ServiceAccount is high privilege. Limit cluster-wide permissions. Scope to namespaces where possible.
- Validate all webhook traffic with TLS; rotate certs (cert-manager handles this).
- Run the operator with `restricted` Pod Security Standard unless it genuinely needs more.

## Anti-patterns

- A custom operator for a workload that has a vetted community operator.
- An operator that mutates other tenants' resources.
- Leaking secrets into CRD `status` (status is world-readable to anyone with `get` on the CR).
- Long-running synchronous work inside reconcile — break it into steps recorded on status.
