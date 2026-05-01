# Cluster-Managed Components

Pairs with `SKILL.md` §9. The minimum platform layer above kubeadm: a CNI plus the three components below.

## Ingress Controller (ingress-nginx)

Install with the upstream Helm chart, pinned by version:

```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update
helm install ingress-nginx ingress-nginx/ingress-nginx \
  -n ingress-nginx --create-namespace \
  --version <pinned> \
  -f values.ingress.yaml
```

`values.ingress.yaml` highlights:

```yaml
controller:
  replicaCount: 2
  service:
    type: LoadBalancer       # or NodePort + external LB on bare metal
  config:
    use-forwarded-headers: "true"
    proxy-body-size: 16m
  ingressClassResource:
    name: nginx
    default: true
  metrics:
    enabled: true
    serviceMonitor: { enabled: true }
  podSecurityContext: { runAsNonRoot: true }
```

For multi-tenant clusters that need separate ingress fleets per tier (public / internal / partner), install one release per IngressClass and label tenant namespaces with the class they may use. Enforce class selection via a validating policy (Kyverno or Gatekeeper).

## cert-manager

```bash
helm repo add jetstack https://charts.jetstack.io
helm repo update
helm install cert-manager jetstack/cert-manager \
  -n cert-manager --create-namespace \
  --version <pinned> \
  --set installCRDs=true
```

Cluster-wide ACME issuer for Let's Encrypt with HTTP-01 solver:

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata: { name: letsencrypt-prod }
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: ops@example.com
    privateKeySecretRef: { name: letsencrypt-prod-account-key }
    solvers:
      - http01:
          ingress: { class: nginx }
```

For wildcard certs, use DNS-01 with the appropriate provider (Cloudflare, Route53, etc.) — HTTP-01 cannot issue wildcards. Restrict the DNS provider credential to the smallest zone the issuer needs.

## metrics-server

```bash
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/
helm repo update
helm install metrics-server metrics-server/metrics-server \
  -n kube-system --version <pinned> \
  --set 'args={--kubelet-insecure-tls=false,--kubelet-preferred-address-types=InternalIP}'
```

On kubeadm clusters where kubelet uses self-signed certs, you may need `--kubelet-insecure-tls`. Prefer to issue proper kubelet serving certs via the kubelet certificate-bootstrap mechanism and keep `--kubelet-insecure-tls=false`.

`kubectl top nodes` and `kubectl top pods` should return data within a minute. HPA and VPA both depend on this.

## Version Pinning Convention

Maintain a single file (e.g. `platform/versions.yaml`) listing the chart name, repo, version, and values file for each platform component. The bootstrap and upgrade scripts read from this file. Bumping a version is a PR; rolling it out is a Helm upgrade.

## Anti-Patterns

- Installing the ingress controller via `kubectl apply` on a one-shot manifest that has no upgrade path.
- Running cert-manager without rate-limit awareness on the Let's Encrypt staging vs prod endpoints — test with staging first.
- Installing two ingress controllers without distinct IngressClasses, leaving routing ambiguous.
- Disabling metrics-server "to save resources" and then wondering why HPA does not scale.
