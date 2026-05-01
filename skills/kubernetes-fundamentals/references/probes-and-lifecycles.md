# Probes and Pod Lifecycle

Probes decide whether traffic reaches a Pod and whether kubelet restarts it. Lifecycle hooks and init containers decide how a Pod starts and stops. Get these wrong and you produce outages that look like application bugs.

## The three probes

| Probe | Question | Effect of failure | Where it matters |
|---|---|---|---|
| `readinessProbe` | Can this Pod serve traffic right now? | Removed from Service endpoints; no restart. | Every workload behind a Service. |
| `livenessProbe` | Is this Pod stuck and unrecoverable? | Container restarted by kubelet. | Only where you can actually detect a deadlock. |
| `startupProbe` | Has the app finished its slow start? | Liveness is disabled until startup succeeds. | Slow-starting apps (JVM, large caches). |

## Canonical configuration

```yaml
containers:
  - name: api
    image: registry.example.com/api:v1.4.2
    ports: [{ containerPort: 3000, name: http }]
    startupProbe:
      httpGet: { path: /startup, port: http }
      failureThreshold: 30       # 30 * 10s = 5 min budget
      periodSeconds: 10
    readinessProbe:
      httpGet: { path: /ready, port: http }
      initialDelaySeconds: 0
      periodSeconds: 5
      timeoutSeconds: 2
      failureThreshold: 3        # out of rotation after ~15s
    livenessProbe:
      httpGet: { path: /live, port: http }
      periodSeconds: 10
      timeoutSeconds: 2
      failureThreshold: 6        # restart after ~1 min of solid failure
```

Endpoint rules:

- `/live` — returns 200 if the process is alive enough to be worth keeping. No I/O; no downstream calls.
- `/ready` — returns 200 only when dependencies the Pod needs are reachable: open DB pool, warm cache, feature flags loaded. Can fail during maintenance to drain traffic.
- `/startup` — returns 200 once the app has completed initial warm-up.

Anti-pattern: using `/health` for both liveness and readiness. They answer different questions.

## Probe types

- `httpGet` — the default for HTTP services.
- `tcpSocket` — useful for non-HTTP services (databases, brokers).
- `exec` — runs a command in the container. Slow; prefer HTTP where possible.
- `grpc` — for gRPC servers that implement the standard health service.

```yaml
readinessProbe:
  tcpSocket: { port: 5432 }
  periodSeconds: 5

livenessProbe:
  exec:
    command: ["sh", "-c", "pg_isready -U postgres"]
  periodSeconds: 20
```

## Common anti-patterns

**Liveness probe calls the database.**
Database blip -> every Pod fails liveness -> kubelet restarts them all -> thundering herd reconnects -> cascading outage. Keep liveness local to the process.

**Readiness and liveness share the same endpoint.**
The Pod either never gets traffic or gets killed unnecessarily during a transient dependency failure. Split them.

**`initialDelaySeconds` used as a substitute for startupProbe.**
A big initial delay penalises healthy cases and is imprecise. Use `startupProbe` for slow starts.

**Readiness probe that returns 200 too early.**
App starts accepting traffic before DB pool is ready -> first 100 requests fail. Gate `/ready` on actual readiness signals.

**No probe at all.**
Service routes to Pods that are still booting. Always set a readiness probe for any Pod behind a Service.

**Liveness with aggressive failureThreshold.**
`failureThreshold: 1` on a 2-second timeout will restart a healthy Pod during a GC pause. Give liveness a full minute of grace.

## Init containers

Run to completion before the main containers start. Good for: schema migrations you want tied to rollout, file downloads, permissions fixing, config generation.

```yaml
spec:
  initContainers:
    - name: migrate
      image: registry.example.com/api:v1.4.2
      command: ["npm", "run", "migrate"]
      envFrom: [{ secretRef: { name: api-secrets } }]
  containers:
    - name: api
      image: registry.example.com/api:v1.4.2
      ports: [{ containerPort: 3000 }]
```

Rules:

- Init containers run sequentially, not in parallel.
- If one fails, the Pod restarts them all by default. Make them idempotent.
- Heavy migrations as init containers run on every Pod start; use a one-off Job for large migrations instead.

## Lifecycle hooks

```yaml
lifecycle:
  postStart:
    exec: { command: ["sh", "-c", "echo started > /tmp/ready"] }
  preStop:
    exec: { command: ["sh", "-c", "sleep 10; /app/shutdown.sh"] }
```

`postStart` runs immediately after the container starts; the container is not Ready yet. Avoid; use an init container or an entrypoint script instead.

`preStop` runs before `SIGTERM` is sent. The usual pattern:

```yaml
preStop:
  exec:
    command:
      - sh
      - -c
      - |
        # Flip readiness to false so Service drains traffic.
        touch /tmp/draining
        # Wait for the load balancer to notice.
        sleep 10
        # Then let the app handle its own graceful shutdown.
        kill -TERM 1
terminationGracePeriodSeconds: 60
```

## Graceful shutdown

The pipeline when a Pod is terminated:

1. Pod marked `Terminating`. Endpoints controller removes Pod IP from Service endpoints.
2. `preStop` hook runs (if present).
3. `SIGTERM` delivered to PID 1 in each container.
4. App has `terminationGracePeriodSeconds` (default 30s) to exit.
5. `SIGKILL` delivered.

Sharp edges:

- The endpoints removal and SIGTERM happen roughly at the same time. If your app exits too fast, the load balancer still sends requests for a few seconds. Use `preStop: sleep 5-15` so traffic drains first.
- PID 1 in many containers is the shell. It does not forward SIGTERM. Use `exec` in your entrypoint or `tini` so signals reach the app.
- Long-running requests need time to complete; set `terminationGracePeriodSeconds` to the worst-case request time plus drain buffer.

## Reference values

| Workload type | readiness period | liveness period | gracePeriod |
|---|---|---|---|
| Stateless HTTP API | 5s | 10s | 30-45s |
| Worker consuming a queue | n/a (headless) | 30s | >= longest job time |
| JVM app with warmup | startup 10s x 30 | 15s | 60s |
| Database/stateful | 10s tcpSocket | 30s exec | 120s+ |

## Checklist before shipping a workload

- Readiness probe exists and only returns OK when traffic should route.
- Liveness probe only detects stuck processes, never dependencies.
- `terminationGracePeriodSeconds` is at least `(preStop sleep) + (worst request time)`.
- preStop drains traffic before the app exits.
- PID 1 forwards SIGTERM (use `exec` or `tini`).
- HPA target (CPU or custom metric) corresponds to real saturation, not wishful thinking.
