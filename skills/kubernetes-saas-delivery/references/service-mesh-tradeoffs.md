# Service Mesh — When the Cost Is Worth It

A service mesh adds an L7 proxy (sidecar or ambient/node) on every Pod. It buys you mTLS, traffic shaping, retries, and per-call telemetry. It costs latency, memory per Pod, an entire control plane to operate, and a steeper learning curve.

## The "do you need a mesh?" decision

Yes, install a mesh, when at least two of the following hold:

- You need mTLS between every service for compliance (PCI, HIPAA, SOC2 control).
- You run progressive delivery (canary, traffic shifting) across many services.
- You need per-call retries / timeouts / circuit breaking that you cannot put in client libraries (polyglot stack).
- You need cross-cluster service discovery / failover.
- You need detailed L7 telemetry (latency per route, per caller) without instrumenting apps.

No, skip the mesh, when:

- Single language stack with a good RPC library that already does retries, timeouts, mTLS via SPIFFE/cert-manager.
- Fewer than ~10 services.
- Team has no capacity to operate Envoy + a control plane.
- Ingress + NetworkPolicy + observability already cover your needs.

If you skip: get mTLS via cert-manager + SPIRE, get retries in the client, get telemetry from OpenTelemetry SDKs.

## Picking a mesh

| Mesh | Strength | Watch out for |
|---|---|---|
| Linkerd | Simple, low overhead (Rust microproxy), great UX | Fewer features than Istio (no rich routing for arbitrary L7) |
| Istio (sidecar) | Most features, biggest community, Envoy power | Operational complexity; sidecar memory/CPU per Pod |
| Istio Ambient | No sidecars; ztunnel + waypoint proxies | Newer; verify your features are GA |
| Cilium Service Mesh | No sidecar, eBPF, fits if you already run Cilium CNI | Mesh features still maturing vs Istio |
| Consul | Multi-runtime (VMs + K8s) | Mesh is a small slice of Consul; complexity if you only want mesh |

Default pick for a SaaS that needs a mesh: Linkerd if you want simple; Istio Ambient if you need rich routing without sidecar tax.

## Cost model

- Sidecar mesh: +50-150 MB memory and +0.05-0.5 vCPU per Pod sidecar. Multiply by Pod count.
- Sidecar startup adds 1-3 seconds to Pod readiness.
- Latency: +1-3 ms per hop typical for Envoy/Linkerd; can be more under load.
- Operational: a dedicated person-quarter to learn, install, and integrate with observability.

For a 200-Pod cluster, a sidecar mesh adds ~10-30 GB memory just for proxies. Ambient/eBPF meshes cut that hard.

## Multi-tenant SaaS specifics

- Per-tenant routing rules via VirtualService / HTTPRoute — gives you per-tenant canary and per-tenant rate limits.
- mTLS identity = ServiceAccount; tenant boundaries align with namespaces if you keep one SA per tenant workload.
- AuthorizationPolicy in Istio enforces "service A in tenant X may not call service B in tenant Y."
- Per-tenant SLOs from mesh telemetry (request rate, error rate, p99) without instrumenting apps.

## Failure modes

- Control plane outage often means new Pods cannot start (no sidecar config) — make the control plane HA and isolated from app workload churn.
- Wrong AuthorizationPolicy can deny all traffic. Stage policies in `permissive` mode first.
- Sidecar OOMs because limits were copied from the app. Set sidecar resources explicitly.
- mTLS rotation gaps — verify cert-manager / mesh-managed cert rotation under load.

## Migration guidance

1. Install in observe-only mode (no mTLS enforcement, no policies).
2. Inject sidecars into one non-critical namespace; measure latency and memory.
3. Turn on mTLS in `permissive` mode mesh-wide; verify all clients work.
4. Move to `strict` mTLS namespace by namespace.
5. Add AuthorizationPolicy / traffic-shifting last.

## Anti-patterns

- Installing a mesh because it is fashionable, not because of a need.
- Running two meshes in the same cluster.
- Mesh-as-API-gateway when an ingress controller is the right tool (or vice versa).
- No latency budget set before adoption — surprise +5 ms p99 in production.
- Ignoring upgrade cadence — meshes have strict version skew with the API server.
