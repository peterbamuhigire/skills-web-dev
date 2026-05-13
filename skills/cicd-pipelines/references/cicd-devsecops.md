# Absorbed Skill: cicd-devsecops

Original entrypoint: `skills/cicd-devsecops/SKILL.md`
Active parent skill: `skills/cicd-pipelines/SKILL.md`
Status: Absorbed as reference material; this file preserves the old skill content for progressive disclosure.

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
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

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

## Vault Cluster Architecture

Production-grade single-region Vault topology on Debian/Ubuntu:

- 3 or 5 Vault nodes with the integrated Raft storage backend; odd node count for quorum.
- Auto-unseal via cloud KMS or HSM. Manual unseal is operator toil and unsafe in production.
- TLS on the listener; mTLS between Raft peers; storage traffic on a private subnet.
- Audit devices configured before any secret is written. File plus syslog at minimum. Loss of all audit devices halts Vault by design, so always run two.
- Namespaces (Vault Enterprise) for tenant isolation when the cluster is multi-tenant; verify edition before relying on this.

Reference Debian/Ubuntu install snippet:

```bash
curl -fsSL https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | \
  sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install -y vault
sudo systemctl enable --now vault
vault audit enable file file_path=/var/log/vault_audit.log
vault audit enable syslog tag="vault" facility="AUTH"
```

Policies are HCL documents binding paths to capabilities (`create`, `read`, `update`, `delete`, `list`, `sudo`) under default-deny. Every request is recorded by audit devices in append-only form. Encryption at rest is supplied by the KMS-backed seal or by disk encryption — they are not interchangeable substitutes; document which one the cluster relies on.

Key rotation:

- `vault operator rotate` rotates the encryption key for storage.
- `vault operator rekey` rotates root and recovery keys; requires a quorum of unseal-key holders.
- Transit keys rotate with `vault write -f transit/keys/<name>/rotate`; old versions remain available for decryption until explicitly trimmed.

Deeper deployment, HA, DR, and engine reference: [references/vault-secrets-lifecycle.md](references/vault-secrets-lifecycle.md). AppRole, dynamic credentials, and rotation runbooks: [references/vault-operations.md](references/vault-operations.md).

## PKI Lifecycle

Two-tier CA with Vault PKI:

- Root CA generated once, then taken offline. Long lifetime (10+ years). Root key material exported to an HSM or air-gapped store after issuing the intermediate.
- Intermediate CA online inside the Vault PKI engine. Lifetime 1 to 5 years. This is the only issuer pods and services see.
- Leaf certificates short-lived (24h to a few weeks for service-to-service mTLS). Issuance and renewal are automated through Vault Agent or cert-manager.

Rotation cadence:

- root: planned re-issuance well before expiry, with overlap; the new root is distributed to trust stores months ahead of cutover.
- intermediate: rotate annually or when staff with key access depart; signed by the offline root, then `set-signed` on the engine.
- leaf: rotate every TTL window; set `max_ttl` on the role so misconfigured clients cannot keep a cert alive indefinitely.

Revocation:

- `vault write pki_int/revoke serial_number=<sn>` revokes a leaf and updates the CRL.
- Publish the CRL through `pki_int/crl/pem` and serve it from a stable URL referenced by the issued certs (`crl_distribution_points`).
- Run an OCSP responder when client libraries require it; otherwise CRL plus short TTLs is the lower-toil option.

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

- AWS engine — dynamic IAM users scoped to a policy document.
- Transit engine — encryption-as-a-service so the app never holds the key.
- PKI engine — short-lived leaf certs from a two-tier CA (root offline, intermediate online).

Auth methods to know:

- AppRole — `role_id` plus short-lived `secret_id`; suits static workloads with secure secret_id delivery.
- Kubernetes — pods authenticate via the projected ServiceAccount token; Vault validates against the K8s API. No static tokens in the pod.
- JWT/OIDC — federates GitHub Actions, GitLab CI, or any OIDC provider; eliminates long-lived CI credentials.

Auto-rotation on a database role uses `default_ttl` (lease TTL) plus `rotation_period` (root-credential rotation). The Vault Agent Injector renders dynamic credentials into pods via annotations without code changes in the app.

Working examples for AWS, Transit, the two-tier PKI bootstrap, the Kubernetes auth method, the JWT/OIDC auth method (with the GitHub Actions consumer step), and the Vault Agent Injector annotation pattern are in [references/vault-operations.md](references/vault-operations.md).

### ISO 27001 Controls Mapping

Annex A controls most relevant to a SaaS pipeline with their 2022 IDs:

- A.5.15 Access control — RBAC across Git, CI, artifact registry, K8s, cloud accounts.
- A.5.23 Cloud services — documented shared-responsibility boundary, vendor assurance records.
- A.8.2 Privileged access rights — break-glass procedures, MFA for admins, approval workflow.
- A.8.16 Monitoring activities — centralised logs, alerting on privileged actions, audit retention.
- A.8.24 Cryptography — TLS 1.2+, KMS-managed keys, approved cipher suites, rotation schedule.
- A.8.25 Secure development lifecycle — threat modelling, peer review, gated merges, tracked design decisions.
- A.8.28 Secure coding — SAST in CI, dependency scanning, secure coding training records.

ISO/IEC 27001:2022 reorganised Annex A into four control themes. Use this mapping pattern instead of paraphrasing clause numbers from secondary sources — quote clause IDs only from the official catalogue.

| Annex A theme | Engine artefacts that supply evidence |
|---------------|----------------------------------------|
| Organizational | `CODEOWNERS`, `SECURITY.md`, on-call rota, supplier register, ISMS scope statement |
| People | Onboarding/offboarding runbook, access-review log, training records, NDA register |
| Physical | Cloud or co-lo provider attestations, data-centre access reports, asset disposal records |
| Technological | Vault audit log, GitHub Actions logs, Falco alerts, Trivy/Grype scan reports, Kubernetes audit log, signed artefacts and SBOMs |

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

For the canonical list of the 12 PCI-DSS v4.0 requirement categories, download the official "PCI DSS v4.0 At A Glance" PDF from the PCI Security Standards Council document library and paste the categories verbatim into your engagement's compliance dossier — do not paraphrase clause titles.

Scope-reduction patterns:

- Tokenisation through Stripe, Adyen, or another PCI-validated payment gateway with hosted fields. Cardholder data never enters engine systems, so most of the 12 categories drop out and the assessment moves toward SAQ A or SAQ A-EP.
- Network segmentation: keep any cardholder-data environment (CDE) on a dedicated VLAN or VPC with explicit, tested firewall rules. Out-of-CDE systems do not need to satisfy CDE-only controls.
- Choose the lightest applicable SAQ based on integration model; document the eligibility argument so an assessor can validate it without re-deriving the integration.

SAQ A scope reduction explanation: Stripe-hosted Checkout loads the card form inside an iframe served from Stripe's domain. Card data never enters your DOM, your servers, or your logs. That limits you to SAQ A (around 22 controls) instead of SAQ D (~329 controls). What still applies: TLS on your redirect page, MFA for staff, logging, vulnerability scans of any page that redirects to Stripe, written policies, and vendor management of Stripe itself.

### Falco Runtime Threat Detection

Falco supports three driver types: the modern eBPF probe (default on supported kernels), the legacy eBPF probe (deprecated), and a kernel module. Verify the driver default for the version you pin before deploying. Alerts can be sent to stdout, files, syslog, HTTP endpoints, or spawned programs; route through Falcosidekick to fan out to Slack, PagerDuty, and Loki.

Rule-tuning workflow:

1. Start with the upstream `falco_rules.yaml` defaults; never edit that file in place.
2. Run for one to two weeks and capture every alert to a triage queue.
3. Allow-list legitimate noise in `falco_rules.local.yaml` with a justification comment per exception.
4. Add custom rules for engine-specific concerns (for example, flag execution of the `vault` binary outside the Vault namespace, or any process writing to `/etc/cron.d` inside an app container).

Install on Kubernetes via the `falcosecurity/falco` Helm chart with `driver.kind=ebpf` and `falcosidekick.enabled=true`. Route alerts through Falcosidekick to Slack (warning+), PagerDuty (critical only), and Loki (informational+) so high-signal events page on-call while low-priority events stay queryable.

A custom rule pack should at minimum cover: shell spawned in a container that should have none, reads of `/etc/shadow`, writes to `/etc/cron.d`, execution of the `vault` binary outside the Vault namespace, and outbound connections to IPs not on the egress allow-list.

Install commands, the shell-in-container rule, and the Falcosidekick routing config: [references/container-runtime-security.md](references/container-runtime-security.md).

### OPA/Gatekeeper Admission Policies

Gatekeeper is a validating and mutating admission webhook that enforces CRD-based policies executed by Open Policy Agent. Its primitives:

- Constraint Templates — CRDs that extend the policy library with new Rego logic.
- Constraints — CRDs that instantiate a template against specific resources and namespaces.
- Audit — periodically examines existing resources and reports violations without blocking.
- Mutation — modifies resources during admission (for example, injecting `securityContext` defaults).

Ship at least three concrete Gatekeeper constraints in any production cluster: required image registry (only `registry.example.com/*` allowed), required CPU and memory resource limits on every container, and disallowed `hostPath` volumes outside an explicit allow-list of operator namespaces. Enable API-server audit logging with `--audit-policy-file` capturing `RequestResponse` on `admissionregistration.k8s.io` resources so denials are reviewable.

Install manifest, a `runAsNonRoot` ConstraintTemplate, and a deploy-time Constraint example: [references/container-runtime-security.md](references/container-runtime-security.md).

### Trivy and Grype Container Scanning

CVE threshold policy for the engine:

- block pipeline on `CRITICAL` or `HIGH` with a known upstream fix available
- allow known-unfixable findings only via `.trivyignore` (or Grype equivalent) with a mandatory `exp:YYYY-MM-DD` annotation, an owner, and a review date
- fail the nightly scan when any ignore entry expires; CI rejects unannotated entries on commit

Pick Trivy or Grype as the primary build-time gate to keep results deterministic; both produce CVE reports against OS packages and language ecosystems and can be paired with `cosign attest` to bind a CycloneDX SBOM to the image digest.

Trivy GitHub Action with SARIF upload, SBOM attestation command, and the `.trivyignore` template are in [references/container-runtime-security.md](references/container-runtime-security.md).

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
