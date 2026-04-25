# Container Runtime Security

Image scanning catches known CVEs at build. Runtime security catches what image scans miss: misconfiguration, privilege escalation, and anomalous behaviour on running containers.

Covers distroless base images, OPA/Gatekeeper admission policies, Falco runtime detection, and secure pod specs.

## Defence in Depth

| Layer | Tool | What it catches |
|-------|------|-----------------|
| Build | Trivy, Grype, Snyk | Known CVEs in OS packages, app dependencies |
| Pre-deploy | Cosign, Notary v2 | Unsigned or tampered images |
| Admission | OPA/Gatekeeper, Kyverno | Policy violations (privileged pods, `:latest` tags, missing limits) |
| Runtime | Falco, Tetragon | Suspicious syscalls, shells in no-shell containers, unexpected network |
| Supply chain | SBOM attestation, SLSA | Provenance tampering |

No single layer is enough. Image scan alone does not stop a pod running as root with `hostPath` mounted.

## Distroless and Slim Base Images

Distroless images contain only the application and its direct runtime — no shell, no package manager, no curl, no libc debug tools. An attacker who gets RCE on a distroless container has very little to pivot with.

### Common Distroless Images

| Runtime | Image |
|---------|-------|
| Node.js | `gcr.io/distroless/nodejs22-debian12` |
| Python | `gcr.io/distroless/python3-debian12` |
| Java | `gcr.io/distroless/java21-debian12` |
| Static binary (Go, Rust) | `gcr.io/distroless/static-debian12` |

Tag with `:nonroot` to get UID 65532 built in:

```dockerfile
FROM gcr.io/distroless/nodejs22-debian12:nonroot
```

### When Slim Is Enough

If you need `curl` for health checks or `tini` for signal handling, use a slim base (`node:22-slim`, `python:3.12-slim`) rather than the full variant. Never ship with `:latest` or the full build-chain variant.

## Admission Control — OPA/Gatekeeper

Cluster policy enforces what can be deployed. Below are the rules every production cluster must have.

### Block `:latest` Tags

```yaml
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8simagerequired
spec:
  crd:
    spec:
      names:
        kind: K8sImageRequired
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8simagerequired
        violation[{"msg": msg}] {
          container := input.review.object.spec.containers[_]
          endswith(container.image, ":latest")
          msg := sprintf("container <%v> uses :latest tag", [container.name])
        }
        violation[{"msg": msg}] {
          container := input.review.object.spec.containers[_]
          not contains(container.image, ":")
          msg := sprintf("container <%v> has no tag", [container.name])
        }
```

### Require Resource Limits

```yaml
violation[{"msg": msg}] {
  container := input.review.object.spec.containers[_]
  not container.resources.limits.memory
  msg := sprintf("container <%v> missing memory limit", [container.name])
}
violation[{"msg": msg}] {
  container := input.review.object.spec.containers[_]
  not container.resources.limits.cpu
  msg := sprintf("container <%v> missing cpu limit", [container.name])
}
```

### Block Privileged Containers

```yaml
violation[{"msg": msg}] {
  container := input.review.object.spec.containers[_]
  container.securityContext.privileged == true
  msg := sprintf("container <%v> is privileged", [container.name])
}
```

### Block hostPath Volumes

```yaml
violation[{"msg": msg}] {
  volume := input.review.object.spec.volumes[_]
  volume.hostPath
  msg := sprintf("volume <%v> uses hostPath", [volume.name])
}
```

## Secure Pod Spec

The baseline pod template every service starts from:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  template:
    spec:
      automountServiceAccountToken: false
      securityContext:
        runAsNonRoot: true
        runAsUser: 65532
        fsGroup: 65532
        seccompProfile:
          type: RuntimeDefault
      containers:
        - name: web
          image: registry.example.com/web@sha256:abc123...
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop: ["ALL"]
          resources:
            limits:
              cpu: "500m"
              memory: "512Mi"
            requests:
              cpu: "100m"
              memory: "128Mi"
          ports:
            - containerPort: 3000
              protocol: TCP
          livenessProbe:
            httpGet:
              path: /healthz
              port: 3000
            initialDelaySeconds: 10
            periodSeconds: 15
          volumeMounts:
            - name: tmp
              mountPath: /tmp
      volumes:
        - name: tmp
          emptyDir: {}
```

Key points:

- `runAsNonRoot: true` + `runAsUser` — never root.
- `readOnlyRootFilesystem: true` — writes go to named volumes only.
- `capabilities: drop: [ALL]` — no NET_ADMIN, SYS_PTRACE, or similar.
- `seccompProfile: RuntimeDefault` — kernel syscall filter on.
- `automountServiceAccountToken: false` unless the workload actually calls the API server.
- Image pinned by digest, not tag.

## Runtime Detection — Falco

Falco watches kernel syscalls via eBPF and fires on rules you define. Start with the default ruleset and add your own.

### Example Custom Rules

```yaml
- rule: Shell spawned in distroless container
  desc: A shell was launched inside a container whose image should contain no shell.
  condition: >
    spawned_process and container and
    (proc.name in (bash, sh, ash, dash, zsh, ksh)) and
    container.image.repository contains "distroless"
  output: >
    Shell spawned in distroless container
    (user=%user.name command=%proc.cmdline container=%container.name image=%container.image.repository)
  priority: CRITICAL
  tags: [container, runtime]

- rule: Read sensitive file
  desc: Process read a sensitive file.
  condition: >
    open_read and
    fd.name in (/etc/shadow, /etc/gshadow, /root/.ssh/id_rsa) and
    not proc.name in (sshd, systemd, cron)
  output: >
    Sensitive file read (user=%user.name file=%fd.name command=%proc.cmdline)
  priority: WARNING
```

### Routing Alerts

- Falco → `falcosidekick` → Slack + PagerDuty + SIEM.
- Sev-Critical = page oncall. Sev-Warning = ticket for triage.
- Every rule has an owner and a runbook link in the output template.

## Image Supply Chain

Every production image should be:

1. Built from a `Dockerfile` in a Git repo at a signed commit.
2. Signed with Cosign keyless (OIDC) at push time.
3. Accompanied by an SBOM attestation (`cosign attest --predicate sbom.json`).
4. Verified at admission with a Cosign verification constraint.

```bash
cosign sign --identity-token "$(gh auth token)" registry.example.com/web@sha256:abc...
cosign attest --predicate sbom.json --type cyclonedx registry.example.com/web@sha256:abc...
cosign verify --certificate-identity "..." --certificate-oidc-issuer https://token.actions.githubusercontent.com registry.example.com/web@sha256:abc...
```

## Network Policy

Default-deny ingress and egress; allow only expected flows.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: web-default-deny
spec:
  podSelector:
    matchLabels: { app: web }
  policyTypes: [Ingress, Egress]
  ingress:
    - from:
        - namespaceSelector:
            matchLabels: { name: ingress }
      ports:
        - port: 3000
          protocol: TCP
  egress:
    - to:
        - namespaceSelector:
            matchLabels: { name: db }
      ports:
        - port: 5432
          protocol: TCP
    - to:
        - namespaceSelector:
            matchLabels: { name: kube-system }
      ports:
        - port: 53
          protocol: UDP
```

## Review Checklist

- [ ] All production images are distroless or explicitly justified slim bases.
- [ ] OPA/Gatekeeper blocks `:latest`, privileged, hostPath, and missing limits.
- [ ] Pod specs enforce non-root, read-only rootfs, dropped capabilities, seccomp.
- [ ] Falco runs on every node with a tuned ruleset and routed alerts.
- [ ] Images are signed with Cosign and verified at admission.
- [ ] Network policies default-deny and explicitly allow required flows.
- [ ] Runbooks exist for every Falco rule that can page oncall.
