# NetworkPolicies — Default Deny and Explicit Allow

Kubernetes is open by default — any Pod can reach any other Pod. NetworkPolicies are the Kubernetes-native firewall at L3/L4; Cilium adds L7. Default-deny + explicit allow is the only defensible posture.

## CNI support

NetworkPolicy is a spec; enforcement needs a CNI that implements it:

| CNI | NetworkPolicy | Extensions |
|---|---|---|
| Calico | Yes | Global policies, DNS policy, eBPF dataplane |
| Cilium | Yes | L7 (HTTP/gRPC/Kafka), FQDN, identity-based |
| Azure CNI (overlay) | Yes | Calico under the hood |
| AWS VPC CNI | Yes (requires `amazon-vpc-cni-k8s` with NetworkPolicy flag enabled) | ipamd-based |
| GKE Dataplane v2 | Yes (Cilium) | Cilium features |
| Flannel | **No** | Install Calico for policy only |

Verify enforcement:

```bash
# Deploy a test deny, try to reach the Pod from a busybox, expect timeout.
kubectl run tester --rm -it --image=busybox -- wget -qO- --timeout=3 http://api.production.svc/
```

## Default-deny in every namespace

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: default-deny-all, namespace: production }
spec:
  podSelector: {}                  # all Pods
  policyTypes: [Ingress, Egress]
  # no ingress or egress rules -> deny both directions
```

Ship this to every application namespace first, then layer explicit allows.

## Allow DNS (always needed)

Egress-only allow for kube-dns:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: allow-dns, namespace: production }
spec:
  podSelector: {}
  policyTypes: [Egress]
  egress:
    - to:
        - namespaceSelector:
            matchLabels: { kubernetes.io/metadata.name: kube-system }
          podSelector:
            matchLabels: { k8s-app: kube-dns }
      ports:
        - { port: 53, protocol: UDP }
        - { port: 53, protocol: TCP }
```

## Three-tier web app — typical allow set

```yaml
# web accepts ingress from ingress controller only
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: web-ingress, namespace: production }
spec:
  podSelector: { matchLabels: { app: web } }
  policyTypes: [Ingress]
  ingress:
    - from:
        - namespaceSelector: { matchLabels: { kubernetes.io/metadata.name: ingress-nginx } }
          podSelector:       { matchLabels: { app.kubernetes.io/name: ingress-nginx } }
      ports: [{ port: 8080, protocol: TCP }]
---
# web can call api, DNS, and external HTTPS
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: web-egress, namespace: production }
spec:
  podSelector: { matchLabels: { app: web } }
  policyTypes: [Egress]
  egress:
    - to:
        - podSelector: { matchLabels: { app: api } }
      ports: [{ port: 8080, protocol: TCP }]
    - to:
        - namespaceSelector: { matchLabels: { kubernetes.io/metadata.name: kube-system } }
          podSelector:       { matchLabels: { k8s-app: kube-dns } }
      ports: [{ port: 53, protocol: UDP }]
    - to:                                               # external HTTPS
        - ipBlock:
            cidr: 0.0.0.0/0
            except: [10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16]
      ports: [{ port: 443, protocol: TCP }]
---
# api accepts ingress from web, calls db + external
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: api-policy, namespace: production }
spec:
  podSelector: { matchLabels: { app: api } }
  policyTypes: [Ingress, Egress]
  ingress:
    - from:
        - podSelector: { matchLabels: { app: web } }
      ports: [{ port: 8080, protocol: TCP }]
  egress:
    - to:
        - podSelector: { matchLabels: { app: db } }
      ports: [{ port: 5432, protocol: TCP }]
    - to:
        - namespaceSelector: { matchLabels: { kubernetes.io/metadata.name: kube-system } }
          podSelector:       { matchLabels: { k8s-app: kube-dns } }
      ports: [{ port: 53, protocol: UDP }]
---
# db accepts only from api, no egress
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: db-policy, namespace: production }
spec:
  podSelector: { matchLabels: { app: db } }
  policyTypes: [Ingress, Egress]
  ingress:
    - from:
        - podSelector: { matchLabels: { app: api } }
      ports: [{ port: 5432, protocol: TCP }]
  egress: []                                  # lock down entirely; add DNS only if needed
```

## Cross-namespace allow

Use `namespaceSelector` (requires target namespaces to carry a label you match on). Best practice: use `kubernetes.io/metadata.name` (auto-added to every namespace since K8s 1.22).

```yaml
ingress:
  - from:
      - namespaceSelector:
          matchLabels: { kubernetes.io/metadata.name: ingress-nginx }
        podSelector:
          matchLabels: { app.kubernetes.io/name: ingress-nginx }
```

## Egress to external services — two approaches

### Pure NetworkPolicy (IP-based)

Brittle — if the SaaS has dynamic IPs, breaks on day two:

```yaml
egress:
  - to:
      - ipBlock: { cidr: 52.84.0.0/15 }   # CloudFront, hypothetical
    ports: [{ port: 443, protocol: TCP }]
```

### Cilium FQDN policy (recommended for SaaS egress)

```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata: { name: api-external, namespace: production }
spec:
  endpointSelector: { matchLabels: { app: api } }
  egress:
    - toFQDNs:
        - matchName: api.stripe.com
        - matchPattern: "*.amazonaws.com"
      toPorts:
        - ports: [{ port: "443", protocol: TCP }]
```

Cilium resolves FQDNs and maintains an IP allowlist automatically.

## L7 policy — Cilium only

Filter by HTTP method/path:

```yaml
apiVersion: cilium.io/v2
kind: CiliumNetworkPolicy
metadata: { name: api-readonly, namespace: production }
spec:
  endpointSelector: { matchLabels: { app: api } }
  ingress:
    - fromEndpoints: [{ matchLabels: { app: web } }]
      toPorts:
        - ports: [{ port: "8080", protocol: TCP }]
          rules:
            http:
              - { method: "GET",  path: "/api/v1/.*" }
              - { method: "POST", path: "/api/v1/orders" }
```

## Debugging NetworkPolicy denies

### Is traffic being denied at all?

```bash
# Cilium
cilium hubble observe --pod production/api-7f... --verdict DENIED

# Calico
kubectl logs -n calico-system -l k8s-app=calico-node | grep -i denied
# Or enable Calico flow logs to Elasticsearch/Loki
```

### Test from a debug Pod

```bash
kubectl run dbg --rm -it --image=nicolaka/netshoot -n production -- bash
# inside:
dig api.production.svc.cluster.local
nc -vz api.production.svc 8080
curl -v https://api.stripe.com/
```

### Trace with tcpdump on the node

```bash
# Find Pod's veth interface
kubectl get pod api-7f... -n production -o wide                   # node name + IP
# SSH to node, find veth
ip -o addr | grep <podIP>
tcpdump -i <veth> -nn port 5432
```

## Calico GlobalNetworkPolicy — cluster-wide rules

```yaml
apiVersion: projectcalico.org/v3
kind: GlobalNetworkPolicy
metadata: { name: deny-metadata-service }
spec:
  types: [Egress]
  selector: all()
  egress:
    - action: Deny
      destination:
        nets: [169.254.169.254/32]        # cloud metadata
```

Blocks all Pods from reaching the cloud metadata endpoint — a major attack vector (steals instance credentials). Do this cluster-wide unless a specific workload has IRSA/WIF disabled and legitimately needs IMDS.

## Anti-patterns

- No default-deny. Adding allows without a deny is decoration, not policy.
- Allowing `0.0.0.0/0` on egress without scoping to port 443 and `except` for internal CIDRs.
- Policies with the wrong namespace selector (only apply to own namespace — cross-NS allow requires `namespaceSelector`).
- Using `Flannel` and believing policies work — they do not.
- Forgetting DNS allow — app breaks mysteriously after default-deny applied.
- Copying policies between namespaces without updating selectors.

## Review checklist

- [ ] Default-deny NetworkPolicy in every application namespace
- [ ] Allow-DNS policy in every application namespace
- [ ] Every workload has an explicit ingress policy listing allowed sources
- [ ] Every workload has an explicit egress policy listing allowed destinations
- [ ] No wildcard egress to `0.0.0.0/0` except through an egress gateway with scrutiny
- [ ] Block egress to cloud metadata (`169.254.169.254/32`) cluster-wide
- [ ] Cross-namespace allows use `namespaceSelector` with `kubernetes.io/metadata.name`
- [ ] CNI confirmed to enforce NetworkPolicy (not Flannel alone)
- [ ] Test Pod proves a blocked connection actually blocks
- [ ] External SaaS egress uses FQDN (Cilium) or egress gateway, not brittle IP blocks
