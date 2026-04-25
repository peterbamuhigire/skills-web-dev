# Debugging Recipes

Symptom-driven runbook. Always start with `kubectl describe pod` — the Events section is where the real cause is, not the logs.

## Triage flow

```text
kubectl get pod <name> -o wide          # node, IP, status, restarts
kubectl describe pod <name>             # Events at the bottom — read these first
kubectl logs <name> -c <ctr> --previous # logs from the crashed container, not the new one
kubectl get events --sort-by=.lastTimestamp -n <ns>
kubectl debug -it <name> --image=busybox --target=<ctr>   # ephemeral debug container, no rebuild
```

## CrashLoopBackOff

CrashLoopBackOff is a status, not a cause. The container exited; kubelet is backing off restarts (10s, 20s, 40s, ... up to 5m).

Order of checks:

1. `kubectl logs <pod> --previous` — what did the app print before exit?
2. Exit code from `kubectl describe pod` -> `Last State: Terminated, Exit Code: N`.
   - 0  - clean exit (likely a CMD that doesn't loop / tail). Wrong entrypoint.
   - 1  - app error. Read previous logs.
   - 137 - SIGKILL, almost always OOMKilled. Bump memory limit or fix leak.
   - 139 - SIGSEGV. Native crash; check libc/arch mismatch.
   - 143 - SIGTERM during shutdown; preStop too long, or readiness flapping.
3. Misconfigured liveness probe restarting a healthy app — disable liveness temporarily and watch.
4. ConfigMap/Secret missing — describe shows `MountVolume.SetUp failed`.

## ImagePullBackOff / ErrImagePull

1. `kubectl describe pod` -> look at `Failed to pull image`.
2. Wrong tag — typo, or tag never pushed. `docker manifest inspect <image>:<tag>`.
3. Private registry — missing `imagePullSecrets`. Check the SA: `kubectl get sa default -o yaml`.
4. Rate-limited (Docker Hub anonymous = 100/6h per IP). Mirror critical images to GHCR/ECR/GAR.
5. Architecture mismatch (arm64 image on amd64 node) — manifest says `no matching manifest`.

## Pending

The scheduler couldn't place the Pod.

```text
kubectl describe pod <name>   # Events -> "0/N nodes are available..."
```

Common causes:

- Insufficient CPU/memory across all nodes — check `kubectl describe nodes | grep -A5 Allocated`.
- No node matches `nodeSelector` / affinity / taints — Pod sits forever.
- PVC is Pending — no matching StorageClass or volume binding mode is `WaitForFirstConsumer`.
- ResourceQuota in the namespace exhausted.

Fix: scale the cluster, relax affinity, add a toleration, or fix the PVC.

## OOMKilled (137)

```text
kubectl describe pod <name>
# Last State: Terminated, Reason: OOMKilled, Exit Code: 137
```

- Memory limit too low for working set. JVM/Node.js/Python often need limit = working set + 30 percent.
- Real leak — restarts get faster over time. Take a heap dump before raising limits.
- Burst on init (DB load, cache warm) — add a startup probe and raise initial limit.
- Node OOM killer (different from cgroup OOM): `dmesg | grep -i kill`. Means requests are too low across the board, not just this Pod.

## Pods Evicted

Node ran out of resources; kubelet evicted Pods by QoS class:

```text
BestEffort  -> evicted first  (no requests/limits at all)
Burstable   -> next           (requests < limits)
Guaranteed  -> last           (requests == limits)
```

Set `requests == limits` on tier-1 workloads to put them in the Guaranteed class.

## Service has no endpoints

```text
kubectl get endpoints <svc>     # empty?
kubectl get pods -l <selector>  # do labels match?
```

- Selector typo or label drift between Service and Pod template.
- Pods are running but readiness probe failing — only Ready Pods are added to endpoints.
- Wrong `targetPort` (named vs numeric).

## DNS failures inside Pods

```text
kubectl run -it --rm dnstest --image=busybox -- nslookup kubernetes.default
```

- CoreDNS Pods crashed or scaled to zero.
- NetworkPolicy denies egress to `kube-system` :53 — always allow egress to CoreDNS.
- `ndots:5` in `/etc/resolv.conf` causes 5 lookups per FQDN — use FQDN with trailing dot for hot paths.

## Slow rollout / stuck rollout

```text
kubectl rollout status deployment/<name>
kubectl rollout history deployment/<name>
kubectl describe deployment <name>   # check ProgressDeadlineSeconds, conditions
```

- New ReplicaSet Pods never become Ready — readiness probe is wrong or app is slow to start. Add startupProbe.
- `maxUnavailable` too aggressive on a small deployment.
- PDB blocks eviction of old Pods.

Roll back fast: `kubectl rollout undo deployment/<name>`.

## Node NotReady

```text
kubectl describe node <name>   # Conditions: MemoryPressure, DiskPressure, PIDPressure, NetworkUnavailable
journalctl -u kubelet -n 200   # on the node
```

- DiskPressure -> image GC kicks in, Pods get evicted. Free disk or raise the threshold.
- Container runtime down (`systemctl status containerd`).
- kubelet cert expired (self-managed clusters; happens at 1 year).

## Useful one-liners

```bash
# Top memory consumers in a namespace
kubectl top pod -n <ns> --sort-by=memory

# Pods not in Running state
kubectl get pods -A --field-selector=status.phase!=Running

# Recent events cluster-wide
kubectl get events -A --sort-by=.lastTimestamp | tail -30

# Force-delete a stuck Pod (only after you understand why)
kubectl delete pod <name> --grace-period=0 --force
```

## Anti-patterns

- Reading logs of the new restart instead of `--previous`.
- Fixing CrashLoopBackOff by raising restart backoff or `restartPolicy: Never` instead of finding the cause.
- `kubectl delete pod --force` as a default reflex — masks real bugs and can corrupt StatefulSet state.
- Disabling probes to "make it green" — now Service routes traffic to a broken Pod.
