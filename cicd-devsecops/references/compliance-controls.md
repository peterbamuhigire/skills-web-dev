# Compliance Controls — Mapping CI/CD Evidence to ISO 27001, PCI-DSS, SOC 2

Focused control mapping for the pipeline and deployment layer. For broader framework coverage (NIST CSF, Uganda DPPA), see `compliance-mapping.md`.

## Principle

Map each control to a concrete technical artefact your pipeline already produces (or should produce). Collect evidence continuously. Hand auditors a read-only view — not a month of scrambling.

## ISO 27001 — Annex A (pipeline-adjacent clauses)

| Clause | Control | Pipeline Evidence |
|--------|---------|-------------------|
| A.5.1 | Policies | Repo-tracked security policy; signed by management |
| A.5.15 | Access control | SSO + MFA required for all deploy actions; GitHub Environments reviewers enforced |
| A.5.16 | Identity management | Service accounts tracked in a registry with owner; no shared logins |
| A.5.17 | Authentication info | Vault manages all secrets; no secrets in Git history |
| A.8.2 | Privileged access | Separate IAM roles for read vs deploy; break-glass accounts audited monthly |
| A.8.3 | Information access restriction | Per-environment secrets; least-privilege IAM policies |
| A.8.9 | Configuration management | IaC in Git with required review; drift detection runs weekly |
| A.8.15 | Logging | Pipeline audit logs retained ≥ 1 year; deployment records signed |
| A.8.16 | Monitoring | Alerts on failed auth, unusual deploys, secret access spikes |
| A.8.20 | Network security | Security groups documented; default-deny; traffic diagrammed |
| A.8.25 | Secure development lifecycle | SDLC documented; SAST/DAST in pipeline; code review required |
| A.8.28 | Secure coding | Linters, type checks, SAST run on every PR |
| A.8.29 | Security testing | Pen-test annually; results tracked to remediation |
| A.8.30 | Outsourced development | Vendor review checklist; DPAs with each supplier |
| A.8.32 | Change management | Every change moves through PR → staging → prod with approvers logged |

## PCI-DSS v4.0 (selected requirements)

| Requirement | Subtopic | Pipeline Evidence |
|-------------|----------|-------------------|
| 6.2 | Bespoke and custom software developed securely | SDLC doc; peer review required; SAST results retained |
| 6.3.2 | Inventory of bespoke software | SBOM generated per build; retained in registry |
| 6.3.3 | Vulnerability management | Dependency scan blocks Critical; High ticketed within 30 days |
| 6.4.1 | Code changes reviewed | Branch protection; reviewer ≠ author; CODEOWNERS enforced |
| 6.5.1 | Separation of environments | Separate AWS accounts per environment; separate Vault namespaces |
| 6.5.4 | Separation of duties | Deployer role distinct from developer role; prod deploys require reviewer |
| 6.5.5 | Production data not in test | Synthetic fixtures; prod data masking on any copy |
| 6.5.6 | Test data and accounts removed before production | CI step fails build if test fixtures present in release artefact |
| 8.2.1 | Unique IDs for users | No shared logins anywhere — pipeline, Vault, cloud |
| 8.3.6 | Minimum password requirements | Enforced by SSO policy; ≥ 12 chars, MFA mandatory |
| 10.2 | Audit logs for system components | CloudTrail/Audit logs retained ≥ 12 months; immutable storage |
| 10.4 | Audit logs reviewed | Weekly alert review; anomalies ticketed |
| 11.3.1 | Internal vulnerability scans | Quarterly scans; results retained |
| 11.3.2 | External scans (ASV) | Approved Scanning Vendor engaged quarterly |
| 12.10 | Incident response | IR playbook documented; tabletop exercise annually |

## SOC 2 Trust Services Criteria (CC series)

| Criterion | Topic | Pipeline Evidence |
|-----------|-------|-------------------|
| CC1.2 | Management commitment | Security policy approved and reviewed annually |
| CC2.2 | Internal communication | Security notices to engineering; incident comms documented |
| CC3.2 | Risk identification | Threat model per major change; risk register updated quarterly |
| CC6.1 | Logical access | MFA on all privileged systems; access granted via role, not individual ACLs |
| CC6.2 | Access provisioning | Joiner/mover/leaver process scripted; quarterly access review |
| CC6.3 | Access removal | Offboarding completed within 24h of termination; evidence in ticket |
| CC6.6 | Boundary protection | WAF, security groups, mTLS documented |
| CC6.7 | Data transmission | TLS ≥ 1.2 enforced end-to-end; cert inventory current |
| CC6.8 | Malicious code prevention | Container images scanned; registry blocks vulnerable pulls |
| CC7.1 | Detection monitoring | CloudWatch/Datadog alerts defined for security events |
| CC7.2 | System monitoring | SLO dashboards; alert runbooks linked |
| CC7.3 | Incident response | Incidents tracked in ticketing; post-mortems published |
| CC7.4 | Security incident recovery | Disaster recovery tested ≥ annually |
| CC8.1 | Change management | PR template enforces reviewer, tests, rollback plan |
| CC9.1 | Risk mitigation | Vendor review for suppliers; DPAs signed |
| CC9.2 | Vendor management | Vendor list maintained; security review on onboard |

## Audit Evidence Checklist

For every release, retain:

- Signed deployment record (who, what, when, digest, approvers)
- Build log with the exact commit SHA
- SBOM (CycloneDX or SPDX format)
- Image scan output (Trivy, Snyk, or equivalent) with severity counts
- SAST / DAST report summary
- Pull request URL with reviewer approvals
- Link to the test run results (unit, integration, e2e)
- Migration plan and rollback plan
- Post-deploy smoke test output

Retention:

- Deployment records and audit logs: ≥ 3 years (7 years for regulated workloads).
- SBOM and scan outputs: ≥ 1 year minimum.
- Access logs on deploy systems: ≥ 12 months (PCI), longer if legal requires.

Storage:

- Immutable storage (S3 Object Lock in compliance mode, or equivalent).
- Tamper-evident logs — hash every daily batch and store the hash separately.
- Read-only auditor account with scoped access to evidence only.

## Continuous Evidence Collection

Bad pattern: audit scramble once a year.

Good pattern: every pipeline run writes evidence to the durable store; a nightly job verifies completeness and alerts on gaps. When the auditor arrives, they read from the same store the team uses daily.

### Scripted Completeness Check

A simple nightly job that scans the last 24 hours of deployment records and confirms each has: digest, SBOM, scan output, reviewers. Alerts on missing fields so the team fixes the pipeline — not the audit evidence after the fact.

## Common Audit Findings

- **Shared service accounts** — always a finding. Replace with per-service accounts bound to identity.
- **Long-lived access keys** — move to OIDC/STS federation.
- **Unreviewed changes merged** — tighten branch protection; enforce `require_code_owner_reviews`.
- **Incomplete deployment records** — make the record a required step in the pipeline; fail the deploy if the sink is unreachable.
- **No evidence of quarterly access review** — schedule it; ship the output to the evidence store.
- **Missing incident post-mortems** — any Sev-1/Sev-2 without a post-mortem is a finding.
