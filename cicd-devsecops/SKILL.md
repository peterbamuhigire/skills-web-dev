---
name: cicd-devsecops
description: Use when hardening CI/CD pipelines with security gates, secrets management,
  scan policy, exception handling, CI server hardening, and evidence retention for
  self-managed or cloud-hosted delivery systems.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# CI/CD DevSecOps

<!-- dual-compat-start -->
## Use When

- Use when hardening CI/CD pipelines with security gates, secrets management, scan policy, exception handling, CI server hardening, and evidence retention for self-managed or cloud-hosted delivery systems.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `cicd-devsecops` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve; load `references` only as needed.
- Confirm the desired deliverable: design, code, review, migration plan, audit, or documentation.

## Workflow

- Read this `SKILL.md` first, then load only the referenced deep-dive files that are necessary for the task.
- Apply the ordered guidance, checklists, and decision rules in this skill instead of cherry-picking isolated snippets.
- Produce the deliverable with assumptions, risks, and follow-up work made explicit when they matter.

## Quality Standards

- Keep outputs execution-oriented, concise, and aligned with the repository's baseline engineering standards.
- Preserve compatibility with existing project conventions unless the skill explicitly requires a stronger standard.
- Prefer deterministic, reviewable steps over vague advice or tool-specific magic.

## Anti-Patterns

- Treating examples as copy-paste truth without checking fit, constraints, or failure modes.
- Loading every reference file by default instead of using progressive disclosure.

## Outputs

- A concrete result that fits the task: implementation guidance, review findings, architecture decisions, templates, or generated artifacts.
- Clear assumptions, tradeoffs, or unresolved gaps when the task cannot be completed from available context alone.
- References used, companion skills, or follow-up actions when they materially improve execution.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Security | Pipeline security gate configuration | YAML or JSON defining SAST/DAST/dependency/secret scan steps | `.github/workflows/security.yml` |
| Security | Scan-exception register | Markdown doc listing accepted findings, owner, and expiry | `docs/security/scan-exceptions.md` |
| Release evidence | Signed build and provenance record | SBOM plus signature or attestation output | `artifacts/sbom-2026-04-16.spdx.json` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
Use this skill when pipeline security must be systematic, reviewable, and auditable. The goal is not to bolt scanners onto a build. The goal is to manage secrets, trust boundaries, evidence, and exceptions so risky changes do not move silently to production.

## Load Order

1. Load `world-class-engineering`.
2. Load `cicd-pipeline-design` to define the pipeline shape.
3. Load this skill to define security gates, secrets handling, and exception policy.
4. Pair it with `vibe-security-skill`, `deployment-release-engineering`, and `observability-monitoring`.

## Executable Outputs

For meaningful DevSecOps work, produce:

- security gate map by pipeline stage
- secret, identity, and credential flow
- exception and suppression policy
- evidence retention and audit trail plan
- incident and rollback triggers for security gate failures

## DevSecOps Workflow

### 1. Map the Trust Boundaries

Capture:

- source repositories and branch protections
- CI runners, agents, and build nodes
- artifact repositories and signing points
- secret stores and credential consumers
- deployment credentials and target environments
- security evidence that must be retained

### 2. Place Security Gates Deliberately

Typical gates include:

- static analysis and secure-code checks
- dependency and SBOM or package-risk checks
- container or artifact scanning
- dynamic or integration-time security checks
- policy or compliance checks for deployment-critical systems

Choose block, warn, or ticket behavior explicitly for each gate.

### 3. Secure Secrets and Identities

- Keep secrets out of source control and pipeline definitions.
- Prefer a dedicated secret manager with access control and audit trail.
- Use short-lived credentials where supported.
- Define rotation, revocation, and emergency disable procedures for every critical credential path.

### 4. Govern Exceptions and Suppressions

- Every suppression or waiver needs a reason, owner, and review date.
- Keep exceptions visible so teams know the current security posture is degraded.
- Separate false-positive suppression from accepted-risk exception handling.
- Do not let temporary waivers become permanent invisible policy.

### 5. Harden the Delivery Infrastructure

- Restrict access to CI servers, runners, and deployment endpoints.
- Use role-based access control for approval and production deployment actions.
- Protect signing keys, deploy credentials, and artifact repositories as high-trust systems.
- Keep security updates, backups, and audit logs current on CI infrastructure.

### 6. Retain Evidence and Respond

- Keep scan results long enough for incident review and audit.
- Link security findings to the release, artifact, or commit they affect.
- Define which findings block merge, block production, or open tracked follow-up work.
- Escalate rapidly when secrets, signing, or deployment credentials may be compromised.

## Standards

### Gate Policy

- Block on findings that create active release risk on the changed path.
- Warn or ticket on lower-risk findings when immediate stop-the-line action is not justified.
- Make policy severity understandable to engineers and operators.

### Secret Hygiene

- Secrets should be centrally managed, rotated, and auditable.
- Shared long-lived production credentials are a risk to remove, not a stable default.
- Secret access should follow least privilege and environment scoping.

### Exception Governance

- Exceptions are time-bounded unless explicitly renewed.
- Exception records must be reviewable by security and delivery owners.
- Exception policy should not hide whether the release carries unresolved risk.

## Secrets Lifecycle

Secrets must be centrally managed with auth, rotation, revocation, and audit. Vault is the reference implementation for this repository.

- **AppRole auth** for applications: `role_id` baked into deploy config, `secret_id` fetched at runtime from a wrapping token. TTL short (5–15 minutes). Revocation instant via `vault write auth/approle/role/<name>/secret-id-accessor/destroy`.
- **Dynamic database credentials** — Vault mints a unique `db-reader-<uuid>` account per session with a 1-hour TTL. No shared DB password in code, logs, or config.
- **PKI engine** — Vault CA issues short-lived TLS certs (≤ 24h) for service-to-service mTLS. Private keys never leave the pod or instance that requested them.
- **Rotation runbook** — every critical credential has a documented rotation job: quarterly for static keys, monthly for signing keys, on-event for compromise. Rotation is scripted and idempotent.
- **Emergency revocation** — `vault lease revoke -prefix` cancels every dynamic credential under a path; documented as an incident-response step.

Deep runbook: [references/vault-operations.md](references/vault-operations.md). Installation and HA/DR: [references/vault-secrets-lifecycle.md](references/vault-secrets-lifecycle.md).

## Compliance Controls

Technical controls have to map to frameworks or they are not auditable. Map once, collect evidence continuously, hand auditors read-only access.

- **ISO 27001 Annex A** — A.9 (access control), A.10 (cryptography), A.12 (operations), A.14 (SDLC), A.16 (incident), A.18 (compliance) are the pipeline-adjacent clauses.
- **PCI-DSS v4** — requirements 6 (secure development), 8 (identification), 10 (logging), 11 (testing), 12 (policy) are where CI/CD evidence lives.
- **SOC 2 CC series** — CC6 (logical access), CC7 (system operations), CC8 (change management), CC9 (risk mitigation) map directly to pipeline gates and deployment records.
- **Audit evidence checklist** — artefact digest, SBOM, signed deployment record, access logs, scan output, approvers, dated waivers. Retain for the longer of 3 years or the framework requirement.

Per-framework control mapping: [references/compliance-controls.md](references/compliance-controls.md). Broader framework coverage: [references/compliance-mapping.md](references/compliance-mapping.md).

## Container Runtime Security

Image scans catch known CVEs. Runtime policy catches what the image cannot — policy violations at deploy time and behaviour anomalies in production.

- **Distroless or slim base images** — no shell, no package manager, no debug tools in the running container. Build tools live in the `builder` stage only.
- **Admission control** — OPA/Gatekeeper or Kyverno enforces cluster policy at admission: no `:latest` tags, no privileged containers, no hostPath, resource limits required, ingress from expected namespaces only.
- **Runtime detection** — Falco (or equivalent eBPF-based sensor) watches syscalls and flags suspicious behaviour: shell spawned in a container that should have no shell, reads of `/etc/shadow`, outbound connections to unknown IPs.
- **Least-privilege pod spec** — `runAsNonRoot: true`, `readOnlyRootFilesystem: true`, dropped capabilities, `seccompProfile: RuntimeDefault`, network policies that default-deny and explicitly allow required flows.

Implementation detail: [references/container-runtime-security.md](references/container-runtime-security.md).

## Review Checklist

- [ ] Trust boundaries and credential paths are explicit.
- [ ] Security gates are mapped to concrete pipeline stages.
- [ ] Gate behavior distinguishes blockers from advisory findings.
- [ ] Secret rotation, revocation, and ownership are defined.
- [ ] Suppressions and waivers are tracked with owners and review dates.
- [ ] CI and deployment infrastructure are hardened and access-controlled.
- [ ] Security evidence is retained and linked to artifacts or releases.
- [ ] Vault AppRole, dynamic DB creds, and PKI engine are documented with rotation runbooks.
- [ ] Compliance control mapping is current and evidence collection is continuous.
- [ ] Container runtime policy (admission + detection) is enforced, not just image scanning.

## Advanced Security Operations

### HashiCorp Vault

Secret engines cover the common credential types; choose the engine that matches the credential lifecycle.

- KV v2 for static app secrets with versioning:

```bash
vault secrets enable -path=secret -version=2 kv
vault kv put secret/myapp/db username=app password=s3cret!
vault kv get -version=3 secret/myapp/db
```

- Database engine for dynamic PostgreSQL credentials (unique user per lease, auto-revoked at TTL):

```bash
vault secrets enable database
vault write database/config/app-postgres \
  plugin_name=postgresql-database-plugin \
  allowed_roles="app-ro" \
  connection_url="postgresql://{{username}}:{{password}}@db:5432/app?sslmode=require" \
  username="vault" password="$VAULT_DB_PASSWORD"

vault write database/roles/app-ro \
  db_name=app-postgres \
  creation_statements="CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'; GRANT SELECT ON ALL TABLES IN SCHEMA public TO \"{{name}}\";" \
  default_ttl="1h" max_ttl="24h"

vault read database/creds/app-ro
```

- AWS engine for dynamic IAM credentials scoped to a policy:

```bash
vault secrets enable aws
vault write aws/config/root access_key=$AWS_ACCESS_KEY secret_key=$AWS_SECRET_KEY region=eu-west-1
vault write aws/roles/s3-readonly credential_type=iam_user policy_document=@s3-readonly.json
vault read aws/creds/s3-readonly
```

- Transit engine for encryption-as-a-service (the app never holds the key):

```bash
vault secrets enable transit
vault write -f transit/keys/orders
vault write transit/encrypt/orders plaintext=$(base64 <<< "card-tok-42")
vault write transit/decrypt/orders ciphertext="vault:v1:..."
```

PKI infrastructure issues short-lived leaf certificates from a root plus intermediate CA.

```bash
# Root CA (offline after setup)
vault secrets enable -path=pki_root pki
vault secrets tune -max-lease-ttl=87600h pki_root
vault write -field=certificate pki_root/root/generate/internal \
  common_name="example-root" ttl=87600h > root_ca.crt

# Intermediate CA (online issuer)
vault secrets enable -path=pki_int pki
vault secrets tune -max-lease-ttl=43800h pki_int
vault write -format=json pki_int/intermediate/generate/internal \
  common_name="example-intermediate" | jq -r '.data.csr' > pki_int.csr
vault write -format=json pki_root/root/sign-intermediate csr=@pki_int.csr \
  format=pem_bundle ttl=43800h | jq -r '.data.certificate' > pki_int.crt
vault write pki_int/intermediate/set-signed certificate=@pki_int.crt

# Role + issue leaf cert
vault write pki_int/roles/my-role allowed_domains="example.com" \
  allow_subdomains=true max_ttl="72h"
vault write pki_int/issue/my-role common_name="api.example.com" ttl="24h"
```

Kubernetes auth method binds Vault to ServiceAccounts so pods fetch secrets without static tokens.

```bash
vault auth enable kubernetes
vault write auth/kubernetes/config \
  kubernetes_host="https://kubernetes.default.svc" \
  token_reviewer_jwt="$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)" \
  kubernetes_ca_cert=@/var/run/secrets/kubernetes.io/serviceaccount/ca.crt

vault write auth/kubernetes/role/app \
  bound_service_account_names=app-sa \
  bound_service_account_namespaces=prod \
  policies=app-read ttl=1h
```

Auto-rotation on the database role sets `default_ttl` (lease TTL) and `rotation_period` (root-credential rotation). Reference the Vault Agent Injector through pod annotations:

```yaml
metadata:
  annotations:
    vault.hashicorp.com/agent-inject: "true"
    vault.hashicorp.com/role: "app"
    vault.hashicorp.com/agent-inject-secret-db: "database/creds/app-ro"
    vault.hashicorp.com/agent-inject-template-db: |
      {{- with secret "database/creds/app-ro" -}}
      DB_USER={{ .Data.username }}
      DB_PASS={{ .Data.password }}
      {{- end }}
```

### ISO 27001 Controls Mapping

Annex A controls most relevant to a SaaS pipeline with their 2022 IDs:

- A.5.15 Access control — RBAC across Git, CI, artifact registry, K8s, cloud accounts.
- A.5.23 Cloud services — documented shared-responsibility boundary, vendor assurance records.
- A.8.2 Privileged access rights — break-glass procedures, MFA for admins, approval workflow.
- A.8.16 Monitoring activities — centralised logs, alerting on privileged actions, audit retention.
- A.8.24 Cryptography — TLS 1.2+, KMS-managed keys, approved cipher suites, rotation schedule.
- A.8.25 Secure development lifecycle — threat modelling, peer review, gated merges, tracked design decisions.
- A.8.28 Secure coding — SAST in CI, dependency scanning, secure coding training records.

Evidence collection checklist — CI/CD must automatically capture:

- pipeline run logs (retain 3 years minimum, longer if ISMS demands)
- signed container images plus CycloneDX SBOMs attached to each digest
- access request tickets linked to the change that consumed the access
- pull-request records with reviewer identity, approval timestamp, and change description
- vulnerability-scan artefacts (SAST, DAST, SCA, container) with severity and remediation status

### PCI-DSS v4.0

Requirement snapshot for a SaaS that redirects card capture to Stripe (reduces scope to SAQ A):

- Req 3 Protect stored account data — not applicable when no PAN, CVV, or track data touches your systems (Stripe-hosted Checkout).
- Req 4 Protect transmission with cryptography — TLS 1.2+ on every public endpoint, HSTS, strong cipher suites only.
- Req 6 Develop and maintain secure systems — SAST and DAST in CI, patch management SLA, change-control records.
- Req 8 Identify users and authenticate access — MFA mandatory for any admin, console, or production-deploy role.
- Req 10 Log and monitor access — centralised audit log of admin and data access, retained 12 months minimum.
- Req 11 Regular testing — quarterly external vulnerability scans by an ASV, annual third-party penetration test.

SAQ A scope reduction explanation: Stripe-hosted Checkout loads the card form inside an iframe served from Stripe's domain. Card data never enters your DOM, your servers, or your logs. That limits you to SAQ A (around 22 controls) instead of SAQ D (~329 controls). What still applies: TLS on your redirect page, MFA for staff, logging, vulnerability scans of any page that redirects to Stripe, written policies, and vendor management of Stripe itself.

### Falco Runtime Threat Detection

Install on Kubernetes via Helm with the eBPF driver (no kernel module required):

```bash
helm repo add falcosecurity https://falcosecurity.github.io/charts
helm install falco falcosecurity/falco \
  --namespace falco --create-namespace \
  --set driver.kind=ebpf \
  --set falcosidekick.enabled=true \
  --set falcosidekick.webui.enabled=true
```

Sample rule that detects a shell spawned inside a container:

```yaml
- rule: Shell spawned in container
  desc: A shell was spawned inside a container
  condition: container.id != host and proc.name in (shell_binaries)
  output: "Shell started (user=%user.name container=%container.id command=%proc.cmdline)"
  priority: WARNING
  tags: [container, shell]
```

Alert routing through Falcosidekick forwards detections to Slack, PagerDuty, and Loki simultaneously:

```yaml
falcosidekick:
  config:
    slack:
      webhookurl: "https://hooks.slack.com/services/XXX/YYY/ZZZ"
      minimumpriority: warning
    pagerduty:
      routingkey: "$PAGERDUTY_ROUTING_KEY"
      minimumpriority: critical
    loki:
      hostport: "http://loki:3100"
      minimumpriority: informational
```

### OPA/Gatekeeper Admission Policies

Install Gatekeeper from the upstream release manifest:

```bash
kubectl apply -f https://raw.githubusercontent.com/open-policy-agent/gatekeeper/release-3.15/deploy/gatekeeper.yaml
```

ConstraintTemplate requiring `runAsNonRoot: true`:

```yaml
apiVersion: templates.gatekeeper.sh/v1
kind: ConstraintTemplate
metadata:
  name: k8srequirednonroot
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredNonRoot
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srequirednonroot
        violation[{"msg": msg}] {
          input.review.object.spec.securityContext.runAsNonRoot == false
          msg := "Containers must runAsNonRoot: true"
        }
```

Constraint manifest applying the template to all pods in production namespaces:

```yaml
apiVersion: constraints.gatekeeper.sh/v1beta1
kind: K8sRequiredNonRoot
metadata:
  name: pods-must-run-as-nonroot
spec:
  enforcementAction: deny
  match:
    kinds:
      - apiGroups: [""]
        kinds: ["Pod"]
    namespaces: ["prod", "prod-eu", "prod-us"]
```

Violation reporting and audit:

```bash
kubectl get constraints
kubectl get k8srequirednonroot pods-must-run-as-nonroot -o yaml
kubectl logs -n gatekeeper-system -l control-plane=audit-controller
```

Enable audit logging on the API server to capture admission denials with `--audit-policy-file` referencing a policy that records `RequestResponse` on `admissionregistration.k8s.io` resources.

### Trivy Container Scanning

GitHub Action snippet that fails the build on unfixed CRITICAL or HIGH findings and uploads SARIF to GitHub Security:

```yaml
- name: Trivy image scan
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ${{ steps.build.outputs.image }}
    severity: CRITICAL,HIGH
    exit-code: 1
    ignore-unfixed: true
    format: sarif
    output: trivy-results.sarif
- uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: trivy-results.sarif
```

SBOM generation in CycloneDX format (attach to the image digest via `cosign attest`):

```bash
trivy image --format cyclonedx --output sbom.json "$IMAGE"
cosign attest --predicate sbom.json --type cyclonedx "$IMAGE"
```

CVE threshold policy:

- block pipeline on CRITICAL or HIGH with a known fix available
- allow known-unfixable findings only through `.trivyignore` with an expiry annotation

Example `.trivyignore`:

```text
# CVE-2024-12345 — no upstream fix as of 2026-03-01
# Owner: platform-sec; Review: 2026-06-01
CVE-2024-12345 exp:2026-06-01
```

CI should reject any `.trivyignore` entry without an `exp:YYYY-MM-DD` annotation and fail the nightly scan when an entry expires.

## References

- [references/security-gate-governance.md](references/security-gate-governance.md): Gate policy, suppression hygiene, and evidence retention.
- [references/vault-operations.md](references/vault-operations.md): AppRole auth, dynamic DB credentials, PKI, and rotation runbooks.
- [references/vault-secrets-lifecycle.md](references/vault-secrets-lifecycle.md): Vault install, unseal, HA, DR, and secrets engine depth.
- [references/compliance-controls.md](references/compliance-controls.md): ISO 27001, PCI-DSS, and SOC 2 control mapping with audit-evidence checklist.
- [references/compliance-mapping.md](references/compliance-mapping.md): Broader cross-framework compliance mapping.
- [references/container-runtime-security.md](references/container-runtime-security.md): Falco rules, OPA/Gatekeeper policies, and distroless base images.
- [references/ansible-security-automation.md](references/ansible-security-automation.md): Hardening automation across the fleet.
- [../cicd-pipeline-design/references/pipeline-governance.md](../cicd-pipeline-design/references/pipeline-governance.md): Pipeline governance and trusted delivery rules.
- [../world-class-engineering/references/source-patterns.md](../world-class-engineering/references/source-patterns.md): DevOps and security-adjacent workflow patterns derived from the supplied books.
