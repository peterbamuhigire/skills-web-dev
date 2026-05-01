# kubectl Workflow

The day-to-day commands that 80% of K8s work is done with, plus the debugging sequence to follow when a Pod is unhealthy.

## Context and kubeconfig

kubeconfig lives at `~/.kube/config` on Linux/macOS or `%USERPROFILE%\.kube\config` on Windows. It can list many clusters, users, and contexts.

```bash
# Inspect
kubectl config view --minify
kubectl config get-contexts
kubectl config current-context

# Switch cluster or namespace
kubectl config use-context prod-eks
kubectl config set-context --current --namespace=production

# Merge another kubeconfig temporarily
export KUBECONFIG=~/.kube/config:~/.kube/client-a
kubectl config view --flatten > ~/.kube/merged && export KUBECONFIG=~/.kube/merged
```

Rule: never work in a shared kubeconfig in your shell history. Use `kubectx` and `kubens` (below) or direnv to set `KUBECONFIG` per project.

## Daily commands

```bash
# List things
kubectl get pods
kubectl get pods -o wide                    # adds node, IP
kubectl get pods -l app=api                 # label selector
kubectl get pods -A                         # all namespaces
kubectl get deploy,svc,ingress              # multiple kinds at once

# Detail and events
kubectl describe pod api-7c9b
kubectl get events --sort-by=.lastTimestamp

# Apply and delete
kubectl apply -f manifests/
kubectl apply -k overlays/production        # Kustomize
kubectl delete -f manifests/api.yaml
kubectl diff -f manifests/                  # dry-run diff against cluster

# Exec and logs
kubectl logs deploy/api --tail=200 -f
kubectl logs pod/api-7c9b -c sidecar        # container in multi-container Pod
kubectl logs pod/api-7c9b --previous         # logs from last crashed container
kubectl exec -it deploy/api -- sh

# Port-forward for local testing
kubectl port-forward svc/api 8080:80

# Scale
kubectl scale deploy/api --replicas=5
```

## Debugging triage

When a Pod is broken, work this order. Do not skip steps; you lose time guessing.

1. `kubectl get pods` — what is the state? `CrashLoopBackOff`, `ImagePullBackOff`, `Pending`, `Error`?
2. `kubectl describe pod <name>` — scroll to **Events** at the bottom. 80% of problems are explained there.
3. `kubectl logs <pod> [-c <container>]` — the app's own error. Add `--previous` if it is crash-looping.
4. `kubectl logs <pod> --previous` — the last container's final words.
5. `kubectl exec -it <pod> -- sh` — shell in if the container is running. Use `nicolaka/netshoot` as a debug sidecar if the image is distroless.
6. `kubectl get events -n <ns> --sort-by=.lastTimestamp` — node-level and scheduling events.
7. `kubectl top pods` and `kubectl top nodes` — live resource pressure.

Symptom-to-step map:

| Symptom | Where the answer usually is |
|---|---|
| `Pending` forever | `describe pod` Events: insufficient CPU/memory, PVC unbound, taints. |
| `ImagePullBackOff` | `describe pod` Events: bad tag, bad registry, missing imagePullSecret. |
| `CrashLoopBackOff` | `kubectl logs --previous`: app exited non-zero. |
| `OOMKilled` | `describe pod`: Last State Reason. Raise memory limit or fix leak. |
| 502 through Ingress | Check readiness probe, Service selector, endpoint slices: `kubectl get endpoints <svc>`. |
| DNS failures | From inside a Pod: `nslookup svc-name.namespace.svc.cluster.local`. Check CoreDNS Pods. |

## Rollouts

```bash
# Check the rollout progress of a Deployment
kubectl rollout status deploy/api

# History and rollback
kubectl rollout history deploy/api
kubectl rollout history deploy/api --revision=3
kubectl rollout undo deploy/api               # back to previous
kubectl rollout undo deploy/api --to-revision=2

# Pause and resume to batch changes
kubectl rollout pause deploy/api
kubectl set image deploy/api api=registry.example.com/api:v1.4.3
kubectl set env  deploy/api FEATURE_FLAG=on
kubectl rollout resume deploy/api
```

Include `kubernetes.io/change-cause` annotation on every change so `history` is meaningful.

## JSONPath and custom output

`-o jsonpath` is the cleanest way to extract fields for scripts.

```bash
# Every Pod's image
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].image}{"\n"}{end}'

# Node names
kubectl get nodes -o jsonpath='{.items[*].metadata.name}'

# Pod IPs for a label
kubectl get pods -l app=api -o jsonpath='{.items[*].status.podIP}'

# Custom columns
kubectl get pods -o custom-columns='NAME:.metadata.name,NODE:.spec.nodeName,STATUS:.status.phase'
```

For richer queries use `jq`:

```bash
kubectl get pods -o json | jq '.items[] | select(.status.phase != "Running") | .metadata.name'
```

## Useful plugins

Install via [krew](https://krew.sigs.k8s.io/):

```bash
kubectl krew install ctx ns tree neat stern who-can
```

- `kubectx` / `kubens` — fast context and namespace switching (`kubectx prod-eks`, `kubens payments`).
- `stern` — tail logs across many Pods matching a regex: `stern 'api-.*' -n production --since 10m`.
- `k9s` — terminal UI; fastest cluster exploration tool for fundamentals-level work.
- `kubectl tree` — shows the object ownership tree (Deployment -> ReplicaSet -> Pod).
- `kubectl neat` — strips managedFields and defaults from `get -o yaml`; indispensable for clean diffs.
- `kubectl who-can` — "who can create pods in this namespace?" for RBAC questions.
- `kubectl-rolesum` — summarise a ServiceAccount's effective RBAC.

## Quick aliases worth adopting

```bash
alias k=kubectl
alias kgp='kubectl get pods'
alias kgd='kubectl get deploy'
alias kd='kubectl describe'
alias kl='kubectl logs -f --tail=200'
alias kex='kubectl exec -it'
complete -F __start_kubectl k
```

## Safe-edit patterns

- Never run `kubectl edit` on production. It bypasses the git source of truth and is invisible to review.
- Use `kubectl diff -f` before `apply -f` to preview changes.
- Use `--server-side --field-manager=<tool>` for apply when multiple controllers own parts of the same resource.
- Wrap destructive ops in a dry-run first: `kubectl delete -f foo.yaml --dry-run=client`.

## Debug ephemeral containers

`kubectl debug` lets you attach a debug container to a running Pod without restarting it. Essential for distroless images.

```bash
kubectl debug -it pod/api-7c9b --image=nicolaka/netshoot --target=api
```

For node-level debugging:

```bash
kubectl debug node/ip-10-0-1-23 -it --image=ubuntu
```

## Troubleshooting reference card

- Endpoints empty but Pods running -> Service selector does not match Pod labels.
- Ingress 404 -> `ingressClassName` missing or wrong host rule.
- TLS errors -> cert-manager Certificate not Ready; `kubectl describe certificate`.
- `FailedScheduling` with `didn't match node selector` -> taint/toleration or nodeSelector mismatch.
- HPA says `<unknown>` -> metrics-server not installed or not reachable.
- CronJob not firing -> check `concurrencyPolicy` and `startingDeadlineSeconds`; check `kubectl get cronjob` for `LAST SCHEDULE`.
