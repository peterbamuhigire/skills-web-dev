# Ingress Controllers

An Ingress object without a controller is inert. Pick one controller per cluster and know its quirks. For new work, Gateway API is the direction of travel.

## Controller comparison

| Controller | Strength | Weakness | Pick when |
|---|---|---|---|
| `ingress-nginx` (Kubernetes-maintained) | Broad adoption, rich annotations, mature. | Config reloads on change; not free under high traffic. | Default pick if no strong constraints. |
| Traefik | Good UX, dashboard, automatic Let's Encrypt, strong Gateway API support. | Smaller ecosystem of ready-made recipes. | Small teams, self-managed clusters, mixed workloads. |
| AWS Load Balancer Controller | Provisions ALB or NLB directly; native IRSA, target-type ip; integrates with WAF. | AWS-only; Ingress semantics differ slightly. | EKS. |
| GCE Ingress (GKE default) | Managed Google Cloud LB, CDN integration. | Limited annotations compared to nginx. | GKE when global HTTPS LB is required. |
| Azure Application Gateway Ingress | Managed Azure App Gateway, WAF, autoscale. | Azure-only, slower to update. | AKS with App Gateway standardised. |
| Contour / Envoy | HTTP/2, gRPC, modern proxy, xDS-based. | Steeper learning curve. | gRPC-heavy services, service mesh adjacency. |
| HAProxy Ingress | Hot reload, low latency, tuneable. | Smaller community. | Latency-sensitive TCP/HTTP mixed ingress. |
| Cilium Ingress / Gateway | Uses eBPF directly, no sidecar proxy. | Requires Cilium CNI. | Cilium shops. |

Rule: run a single controller class per cluster for production-facing traffic. Additional controllers are legitimate for internal traffic (`ingressClassName: nginx-internal`).

## Installing ingress-nginx on a managed cluster

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

helm upgrade --install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx --create-namespace \
  --set controller.replicaCount=2 \
  --set controller.service.type=LoadBalancer \
  --set controller.metrics.enabled=true \
  --set controller.podAnnotations."prometheus\.io/scrape"=true \
  --set controller.config.use-forwarded-headers=true \
  --set controller.config.enable-real-ip=true
```

## Minimal Ingress with TLS via cert-manager

```bash
helm repo add jetstack https://charts.jetstack.io
helm upgrade --install cert-manager jetstack/cert-manager \
  -n cert-manager --create-namespace --set crds.enabled=true
```

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata: { name: letsencrypt }
spec:
  acme:
    email: ops@example.com
    server: https://acme-v02.api.letsencrypt.org/directory
    privateKeySecretRef: { name: letsencrypt-key }
    solvers:
      - http01: { ingress: { class: nginx } }
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api
  namespace: production
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
    - hosts: [api.example.com]
      secretName: api-example-com-tls
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend: { service: { name: api, port: { number: 80 } } }
```

cert-manager creates a `Certificate` resource. Diagnose stalled issuance with:

```bash
kubectl describe certificate api-example-com-tls
kubectl describe challenge -A
```

## Rate limiting on ingress-nginx

```yaml
metadata:
  annotations:
    nginx.ingress.kubernetes.io/limit-rps: "20"
    nginx.ingress.kubernetes.io/limit-connections: "50"
    nginx.ingress.kubernetes.io/limit-burst-multiplier: "3"
```

Rate limits at the Ingress are coarse; put per-user quotas at the application layer. See `network-security` and `vibe-security-skill`.

## Canary rollout on ingress-nginx

Two Ingresses, same host, one marked canary:

```yaml
# canary.yaml
metadata:
  name: api-canary
  annotations:
    nginx.ingress.kubernetes.io/canary: "true"
    nginx.ingress.kubernetes.io/canary-weight: "10"
    # or header-based:
    # nginx.ingress.kubernetes.io/canary-by-header: "x-canary"
spec:
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend: { service: { name: api-canary, port: { number: 80 } } }
```

For a proper progressive delivery pipeline (automated analysis, abort criteria), use Argo Rollouts or Flagger — see `kubernetes-saas-delivery`.

## AWS Load Balancer Controller (EKS)

Install via Helm with IRSA; pick ALB for HTTP(S), NLB for TCP/UDP.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api
  namespace: production
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip           # route directly to Pod IPs
    alb.ingress.kubernetes.io/listen-ports: '[{"HTTP":80},{"HTTPS":443}]'
    alb.ingress.kubernetes.io/ssl-redirect: "443"
    alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:eu-west-1:123:certificate/abc
spec:
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend: { service: { name: api, port: { number: 80 } } }
```

- `target-type: ip` gives faster rollouts and skips kube-proxy hop.
- Group multiple Ingresses on one ALB via `alb.ingress.kubernetes.io/group.name`; saves money.

## GCE Ingress on GKE

GKE ships an Ingress controller out of the box that provisions a Google Cloud LB.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api
  namespace: production
  annotations:
    kubernetes.io/ingress.class: gce
    networking.gke.io/managed-certificates: api-cert
spec:
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /*
            pathType: ImplementationSpecific
            backend: { service: { name: api, port: { number: 80 } } }
```

Use `ManagedCertificate` for Google-managed TLS without cert-manager.

## Gateway API

Gateway API is the standard-track successor: separates cluster-operator concerns (GatewayClass, Gateway) from app-team concerns (HTTPRoute).

```yaml
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata: { name: external, namespace: ingress }
spec:
  gatewayClassName: nginx
  listeners:
    - name: https
      port: 443
      protocol: HTTPS
      tls:
        mode: Terminate
        certificateRefs: [{ name: wildcard-tls }]
      allowedRoutes: { namespaces: { from: All } }
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata: { name: api, namespace: production }
spec:
  parentRefs: [{ name: external, namespace: ingress }]
  hostnames: [api.example.com]
  rules:
    - matches: [{ path: { type: PathPrefix, value: / } }]
      backendRefs: [{ name: api, port: 80 }]
```

Controllers with good Gateway API support: ingress-nginx (GA), Traefik, Contour, Istio, Cilium, Kong. AWS LBC supports it for ALB.

## Common ingress pitfalls

- Forgetting `ingressClassName` — Ingress exists but nothing routes.
- Multiple controllers fighting for the same class — pick one.
- TLS secret in the wrong namespace — `Secret` must live in the same namespace as the Ingress.
- `cert-manager` HTTP-01 blocked because `force-ssl-redirect` rewrites the `/.well-known/acme-challenge/` path — add an exclusion or use DNS-01.
- Long-running WebSocket connections killed at 60s — tune `nginx.ingress.kubernetes.io/proxy-read-timeout` and ALB idle timeout.
- Session-affinity assumed but not set — use `nginx.ingress.kubernetes.io/affinity: cookie` if you really need sticky sessions (you rarely should).
- Mixing `type: LoadBalancer` Services and Ingress per app — expensive. Prefer one Ingress with host/path rules.
