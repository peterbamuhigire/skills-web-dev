# Cluster Setup on EKS and GKE

Managed Kubernetes is the right starting point unless compliance forbids it. This file walks through two production-shaped clusters: AWS EKS with eksctl and Karpenter, and GKE (Autopilot and Standard). Paste the commands into a scratch account first — they create billable resources.

## Decision: EKS vs GKE vs AKS

- Pick the one where the rest of your platform lives. Data gravity beats K8s preferences.
- If you have no preference: GKE Autopilot is the fastest path to a good cluster; EKS is the most common with the richest ecosystem; AKS is strongest when you already use Azure Entra ID and Azure DevOps.
- Multi-cloud is rarely worth its cost in day-one posture.

## EKS with eksctl

### Baseline cluster

```bash
cat > cluster.yaml <<'YAML'
apiVersion: eksctl.io/v1alpha5
kind: ClusterConfig
metadata:
  name: platform-prod
  region: eu-west-1
  version: "1.30"

iam:
  withOIDC: true                          # required for IRSA

vpc:
  clusterEndpoints:
    publicAccess: true
    privateAccess: true
  nat: { gateway: Single }                # cheap enough for prod start

managedNodeGroups:
  - name: system
    instanceType: t3.large
    desiredCapacity: 2
    minSize: 2
    maxSize: 4
    volumeSize: 50
    volumeEncrypted: true
    privateNetworking: true
    labels: { role: system }
    taints:
      - key: CriticalAddonsOnly
        value: "true"
        effect: NoSchedule

addons:
  - name: vpc-cni
  - name: kube-proxy
  - name: coredns
  - name: eks-pod-identity-agent
  - name: aws-ebs-csi-driver
YAML

eksctl create cluster -f cluster.yaml
```

The `system` node group runs addons (CoreDNS, controller, metrics-server). Karpenter will own the rest.

### Karpenter for app nodes

Karpenter replaces cluster-autoscaler with fast, bin-packing node provisioning.

```bash
# 1. Install Karpenter (see upstream quickstart for full IRSA setup)
helm repo add karpenter oci://public.ecr.aws/karpenter
helm upgrade --install karpenter karpenter/karpenter \
  --version v1.0.5 -n karpenter --create-namespace \
  --set serviceAccount.annotations."eks\.amazonaws\.com/role-arn"=$KARPENTER_IRSA_ARN \
  --set settings.clusterName=platform-prod
```

```yaml
# 2. Define a NodePool
apiVersion: karpenter.sh/v1
kind: NodePool
metadata: { name: default }
spec:
  template:
    spec:
      requirements:
        - key: kubernetes.io/arch
          operator: In
          values: [amd64]
        - key: karpenter.k8s.aws/instance-category
          operator: In
          values: [m, c, r]
        - key: karpenter.k8s.aws/instance-size
          operator: NotIn
          values: [nano, micro, small]
        - key: karpenter.sh/capacity-type
          operator: In
          values: [spot, on-demand]
      nodeClassRef:
        group: karpenter.k8s.aws
        kind: EC2NodeClass
        name: default
  limits: { cpu: "200", memory: 400Gi }
  disruption:
    consolidationPolicy: WhenEmptyOrUnderutilized
    consolidateAfter: 30s
---
apiVersion: karpenter.k8s.aws/v1
kind: EC2NodeClass
metadata: { name: default }
spec:
  amiFamily: AL2023
  role: KarpenterNodeRole-platform-prod
  subnetSelectorTerms:   [{ tags: { karpenter.sh/discovery: platform-prod } }]
  securityGroupSelectorTerms: [{ tags: { karpenter.sh/discovery: platform-prod } }]
```

Tips:

- Use Spot for stateless; keep a small on-demand slice for critical services.
- `consolidateAfter: 30s` aggressively packs Pods onto fewer nodes; raise if churn is an issue.
- Karpenter reads `requests`, not `limits`, when sizing nodes. Wrong requests cause under- or over-provisioning.

### IRSA (IAM Roles for Service Accounts)

Give a Pod AWS permissions without node-wide creds.

```bash
eksctl create iamserviceaccount \
  --cluster platform-prod --namespace production \
  --name api --role-name api-production-role \
  --attach-policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess \
  --approve
```

Then in the Pod spec:

```yaml
serviceAccountName: api
```

For newer clusters prefer **EKS Pod Identity** (`eksctl create podidentityassociation`) — it avoids the OIDC federation complexity.

## GKE

### Autopilot (recommended for starter clusters)

Autopilot manages nodes entirely; you pay per Pod second.

```bash
gcloud container clusters create-auto platform-prod \
  --region=europe-west2 \
  --release-channel=regular \
  --enable-private-nodes \
  --enable-master-authorized-networks \
  --master-authorized-networks="<office-cidr>/32"

gcloud container clusters get-credentials platform-prod --region=europe-west2
```

Autopilot constraints to know:

- No DaemonSets on system nodes; use built-in logging/metrics.
- `hostPath`, `privileged`, and certain capabilities are blocked by default.
- Nodes are Ubuntu-based cos_containerd; GPU requires a supported accelerator class.
- You pay a small per-Pod overhead vs Standard; for many small Pods it can be more expensive.

### Standard cluster

Pick Standard when you need DaemonSets, custom kernel modules, GPU driver control, or large-scale savings with reserved instances.

```bash
gcloud container clusters create platform-prod \
  --region=europe-west2 \
  --release-channel=regular \
  --enable-ip-alias \
  --enable-private-nodes \
  --master-ipv4-cidr=172.16.0.0/28 \
  --network=default \
  --subnetwork=default \
  --workload-pool=$(gcloud config get-value project).svc.id.goog \
  --enable-shielded-nodes \
  --num-nodes=2 \
  --machine-type=e2-standard-4 \
  --enable-autoscaling --min-nodes=2 --max-nodes=10
```

`--workload-pool` enables **Workload Identity** (the GCP equivalent of IRSA).

### Workload Identity

```bash
# 1. Google service account
gcloud iam service-accounts create api-prod

# 2. Bind K8s SA to Google SA
gcloud iam service-accounts add-iam-policy-binding \
  api-prod@$PROJECT.iam.gserviceaccount.com \
  --role=roles/iam.workloadIdentityUser \
  --member="serviceAccount:$PROJECT.svc.id.goog[production/api]"

# 3. Grant actual permissions to the Google SA
gcloud projects add-iam-policy-binding $PROJECT \
  --role=roles/storage.objectViewer \
  --member="serviceAccount:api-prod@$PROJECT.iam.gserviceaccount.com"
```

Annotate the K8s ServiceAccount:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: api
  namespace: production
  annotations:
    iam.gke.io/gcp-service-account: api-prod@$PROJECT.iam.gserviceaccount.com
```

## Network plugin choice

- **EKS** defaults to `amazon-vpc-cni-k8s`: Pod IPs are VPC IPs (great for observability, security groups per Pod). Watch IP exhaustion on small subnets; enable prefix delegation.
- **GKE** uses its own `netd` + dataplane V2 (Cilium-based) on newer clusters. Dataplane V2 is the default; enables Network Policy natively.
- **Self-hosted**: pick Cilium unless you have a reason otherwise. Calico is a solid alternative with rich NetworkPolicy support.

## Post-install baseline

Every new cluster should have, from day one:

1. `metrics-server` — enables `kubectl top` and HPA.
2. An ingress controller (`ingress-nginx` or cloud-native).
3. `cert-manager` for TLS automation.
4. A logging pipeline (CloudWatch/Cloud Logging or Loki).
5. `kube-prometheus-stack` or managed Prometheus.
6. `external-secrets-operator` pointing at AWS Secrets Manager or GCP Secret Manager.
7. RBAC baseline: no ClusterAdmin for humans; SSO with group-based role bindings.
8. NetworkPolicy default-deny in each application namespace.
9. PodSecurity admission set to `restricted` in app namespaces.
10. Cost reporting: kubecost, opencost, or the cloud's native cost-allocation.

## Upgrade discipline

- Managed control planes run an N, N-1, N-2 support window. Plan one minor version upgrade per quarter.
- Node pools upgrade independently; on EKS, cycle Karpenter nodes by draining and letting it replace them with a newer AMI.
- Test upgrades in a non-prod cluster with the same addon set. Addon version drift causes most upgrade failures.
- Keep `kubectl` and helm charts on the same minor as the server.

## Cost guardrails

- One cluster per environment, not per team, unless you have very strong isolation needs.
- Node group quotas: cap `maxSize` in Karpenter and cluster-autoscaler to bound blast radius of a runaway HPA.
- LoadBalancer Services are billed per-LB; funnel through one Ingress.
- Egress to the internet via NAT is the quiet bill-killer; use VPC endpoints / Private Google Access for S3, ECR, GCR, Secrets Manager.
