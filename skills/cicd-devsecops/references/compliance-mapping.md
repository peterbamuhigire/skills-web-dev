# Compliance Mapping for Debian/Ubuntu SaaS

Purpose: Map the technical security controls implemented across the DevSecOps stack to common compliance frameworks.
Covers ISO 27001, SOC 2, PCI-DSS v4, NIST CSF, continuous evidence collection, and common audit findings.

## Frameworks covered

| Framework | Scope | When you need it |
|---|---|---|
| **ISO 27001** | Information security management system (ISMS) | Enterprise customers, procurement requirements |
| **SOC 2** | Trust Services Criteria for service organisations | US enterprise B2B SaaS customers |
| **PCI-DSS v4** | Cardholder data protection | Processing, storing, or transmitting card data |
| **NIST CSF** | Cybersecurity framework (Identify, Protect, Detect, Respond, Recover) | US federal work, generic baseline |
| **Uganda DPPA 2019** | Personal data protection | Any SaaS processing Ugandan personal data |

## How to use this reference

1. Pick the framework your customer or regulator requires.
2. For each control, identify the technical evidence you already produce.
3. Where evidence is missing, add it to the Ansible nightly audit playbook.
4. Centralise all evidence into a compliance bucket with time-stamped immutable snapshots.
5. When the auditor arrives, you hand them read-only access, not a frantic week of collection.

The goal is **continuous compliance** — the work is already done by the time the audit starts.

## ISO 27001 Annex A control mapping (abbreviated)

| Annex A clause | Control area | Your technical evidence |
|---|---|---|
| A.5 | Information security policies | Policies documented in repo; signed by management |
| A.6 | Organisation of security | RACI matrix; incident response roles; security officer designated |
| A.7 | Human resource security | Onboarding/offboarding Ansible playbooks; signed NDAs; background checks |
| A.8 | Asset management | CMDB inventory; SBOM per build artifact; data classification tags |
| A.9 | Access control | RBAC (see `dual-auth-rbac`); MFA on admin; least-privilege sudoers |
| A.10 | Cryptography | TLS 1.3 everywhere; Vault for keys; Argon2id for passwords |
| A.11 | Physical security | Inherited from cloud/VPS provider; provider SOC 2 report on file |
| A.12 | Operations security | Ansible patch playbook; daily backups; auditd; ClamAV; OSSEC/Wazuh |
| A.13 | Communications security | nftables/UFW; network segmentation; TLS internal |
| A.14 | System acquisition, development, maintenance | SDLC docs (see `sdlc-*` skills); code review; SAST/DAST in pipeline |
| A.15 | Supplier relationships | Vendor review checklist; DPAs with sub-processors |
| A.16 | Information security incident management | Incident runbook; on-call rotation; post-mortem template |
| A.17 | Business continuity | BCP; DR runbook; quarterly DR drill; RPO/RTO documented |
| A.18 | Compliance | Audit trail (auditd + app log + Vault audit); legal register |

### Example: mapping A.12.1.2 (change management)

- **Evidence 1**: Git commit history for all infrastructure changes
- **Evidence 2**: Jenkins pipeline logs showing peer review + approval before deployment
- **Evidence 3**: Ansible run log with timestamp, user, playbook, target hosts
- **Evidence 4**: Change advisory board (CAB) ticket linking business request to git commit

## PCI-DSS v4 requirement mapping (abbreviated)

| Req | Title | Technical implementation |
|---|---|---|
| R1 | Network security controls | nftables stateful firewall; VPC segmentation; no direct internet to DB |
| R2 | Secure configurations | Ansible baseline hardening; CIS benchmark Lynis reports |
| R3 | Protect stored account data | Tokenization (PAN never stored); Vault Transit for any retained data; strong crypto |
| R4 | Protect data in transit | TLS 1.3; HSTS; strong cipher suites; certificate pinning for mobile |
| R5 | Protect against malware | ClamAV scheduled scans; auditd file-integrity monitoring; immutable base images |
| R6 | Develop secure systems | SAST (Semgrep/SonarQube); DAST (OWASP ZAP); dependency scanning (OWASP DC); peer review |
| R7 | Restrict access by need-to-know | RBAC (see `dual-auth-rbac`); row-level security for multi-tenant isolation |
| R8 | Identify and authenticate users | Argon2id passwords; MFA on all admin; session management; account lockout |
| R9 | Restrict physical access | Inherited from cloud/VPS provider; compensating controls documented |
| R10 | Log and monitor access | auditd + Vault audit + app logs shipped to SigNoz/SIEM; daily log review |
| R11 | Regularly test security | Quarterly external pen test; weekly vuln scans; annual red team |
| R12 | Information security policy | Security policy; acceptable use; incident response; reviewed annually |

### Req 10 detail

PCI R10 is exacting. You need:

- Who accessed what, when, from where
- Successful and failed login attempts
- Privilege escalation events
- Changes to audit logs themselves
- Changes to authentication mechanisms
- Logs preserved for at least 12 months, 3 months immediately accessible
- Daily log review (automated with alerting counts as review)

The stack of auditd + Vault audit log + application audit log + Jenkins audit log, unified in SigNoz or a SIEM, satisfies this.

## SOC 2 Trust Services Criteria mapping

SOC 2 is organised around 5 TSCs. Security (CC) is mandatory; the others are optional based on the report scope.

| TSC | Focus | Key controls |
|---|---|---|
| **CC (Security)** | Core control set across all domains | Change management, access control, vuln mgmt, incident response, risk assessment |
| **A (Availability)** | SLOs, capacity, DR | Uptime monitoring; backup verification; DR drills; capacity planning |
| **PI (Processing Integrity)** | Accurate, complete, timely processing | Input validation; reconciliation; batch error handling; transaction logging |
| **C (Confidentiality)** | Non-public info protection | Data classification; encryption at rest; DLP; retention and disposal |
| **P (Privacy)** | Personal information lifecycle | Consent; notice; choice; access rights; breach notification |

SOC 2 auditors care about **design** (is the control documented?) AND **operating effectiveness** (can you show it worked for 6–12 months?). Continuous evidence collection is therefore mandatory for Type II reports.

## Evidence collection automation

Run a nightly Ansible playbook that collects a machine-readable snapshot per host:

```yaml
- name: Nightly compliance snapshot
  hosts: all
  become: true
  tasks:
    - name: Collect package inventory
      ansible.builtin.shell: dpkg -l | awk '/^ii/ {print $2, $3}'
      register: pkg_list
      changed_when: false

    - name: Collect UFW rules
      ansible.builtin.command: ufw status verbose
      register: ufw_rules
      changed_when: false

    - name: Collect auditd status
      ansible.builtin.command: auditctl -s
      register: auditd_status
      changed_when: false

    - name: Collect cert expiry
      ansible.builtin.shell: |
        for cert in /etc/nginx/tls/*.crt; do
          openssl x509 -in "$cert" -noout -subject -enddate
        done
      register: cert_expiry
      changed_when: false

    - name: Collect user list
      ansible.builtin.shell: getent passwd | awk -F: '$3 >= 1000 {print $1}'
      register: user_list
      changed_when: false

    - name: Write snapshot JSON
      ansible.builtin.copy:
        content: |
          {
            "host": "{{ inventory_hostname }}",
            "timestamp": "{{ ansible_date_time.iso8601 }}",
            "packages": {{ pkg_list.stdout_lines | to_json }},
            "ufw": {{ ufw_rules.stdout_lines | to_json }},
            "auditd": {{ auditd_status.stdout_lines | to_json }},
            "certs": {{ cert_expiry.stdout_lines | to_json }},
            "users": {{ user_list.stdout_lines | to_json }}
          }
        dest: "/var/lib/compliance/snapshot-{{ ansible_date_time.date }}.json"
        mode: "0644"

    - name: Ship to compliance bucket
      ansible.builtin.command: >
        aws s3 cp /var/lib/compliance/snapshot-{{ ansible_date_time.date }}.json
        s3://compliance-evidence/{{ inventory_hostname }}/
```

Snapshots are append-only, time-stamped, and immutable. Auditors get read-only bucket access; they pick any date and verify.

## Continuous compliance monitoring

| Tool | What it gives you |
|---|---|
| **Wazuh** | Host integrity monitoring, CIS benchmark scoring, log collection, rootkit detection |
| **Lynis** | Scheduled hardening audit; produces a hardening index and specific remediation items |
| **Trivy** | Container and filesystem CVE scanning; fail CI builds on high severity |
| **OpenVAS / Greenbone** | Authenticated network vulnerability scans |
| **OSSEC** | Log analysis, file integrity, active response (alternative to Wazuh) |
| **Prometheus + Alertmanager** | Metric-based alerting (failed SSH, auditd queue full, cert near expiry) |

Run all of these from a scheduled Ansible playbook or systemd timer; ship results to the same compliance bucket.

## Audit trail requirements

A compliant audit trail has to answer these questions for every event:

- **Who** — user ID, service account, or IP
- **What** — action performed (read/write/delete), resource touched
- **When** — timestamp in UTC with sub-second precision
- **Where** — source IP, hostname, geographic origin
- **How** — was it MFA'd? via which auth method?
- **Result** — success/failure; authorization decision

Sources to unify:

- **auditd** — kernel and syscall events
- **Application audit log** — business actions (user created an invoice, exported a report)
- **Vault audit log** — secret reads
- **Jenkins audit log** — pipeline runs, who triggered, what changed
- **Web server access log** — all HTTP traffic
- **Database audit log** — mysql-audit or PostgreSQL pgaudit

Ship everything to SigNoz, Loki, Elastic, or an external SIEM. Retain per your framework's requirement (PCI: 1 year; SOC 2: typically 1 year; ISO 27001: defined by your retention policy).

## Data residency and sovereignty

- **Uganda DPPA 2019** requires that personal data of Ugandans be processed in-country except under specific legal bases. See `uganda-dppa-compliance` skill.
- Document where data physically resides (which data centre, which region).
- Cross-border transfer requires either adequacy, SCCs, or explicit consent.
- Vault, database, and backup storage must all be in-country if the DPPA applies.

## Incident response for compliance

Compliance frameworks mandate breach notification timelines:

| Framework | Notify whom | Within |
|---|---|---|
| **PCI-DSS** | Card brands, acquirer | Within 24 hours of confirmation |
| **ISO 27001** | As per incident response policy | "Without undue delay" |
| **SOC 2** | Per customer contract | Usually 24–72 hours |
| **Uganda DPPA** | Personal Data Protection Office; data subjects | 72 hours (PDPO); reasonable time (subjects) |
| **GDPR** | Supervisory authority | 72 hours |

Your incident runbook should have a decision tree: "Was personal data affected? → Go to notification playbook within X hours."

## Common audit findings to pre-empt

These are the findings auditors write up most often. Close them before the audit starts.

1. **No access review cadence** — show a quarterly ticket with evidence of who was reviewed and what access was revoked.
2. **Secrets in code** — run git-secrets, gitleaks, or truffleHog on the history; remediate + rotate.
3. **No vuln scan evidence** — retain Trivy/Lynis/OpenVAS reports with timestamps.
4. **Unpatched systems** — nightly unattended-upgrades + Ansible patch playbook + reporting.
5. **No incident response test** — tabletop exercise at least annually, documented.
6. **No backup restore test** — quarterly restore to an isolated environment, documented.
7. **Unclear data classification** — tag data assets; document retention and disposal per class.
8. **No asset inventory** — CMDB or Ansible inventory export reconciled to billing/cloud console.
9. **Expired certs found in production** — cert expiry monitoring with 30/14/7 day alerts.
10. **No proof of employee security training** — annual training with signed completion records.

## Anti-patterns

- **Compliance theatre** — policies that say one thing while the tech does another. Auditors look for this.
- **Last-minute scramble** — collecting evidence the week before the audit. Use continuous collection.
- **No continuous evidence** — taking screenshots on audit day that don't match historical state.
- **Auditing only for audit** — running Lynis once a year to print a report. The tools exist to improve security, not produce paper.
- **One-person audit knowledge** — if only one engineer can answer audit questions, the bus factor is a finding.
- **Ignoring minor findings** — they compound; next year's audit will re-raise them with interest.
- **Undocumented exceptions** — every deviation from policy should have a documented risk acceptance with expiry date and owner.

## Cross-references

- `cicd-devsecops/SKILL.md` — parent skill: DevSecOps CI/CD hardening
- `cicd-devsecops/references/ansible-security-automation.md` — Ansible playbooks for evidence collection
- `cicd-devsecops/references/vault-secrets-lifecycle.md` — Vault audit log
- `linux-security-hardening/SKILL.md` — host-level controls for A.12, R2, R5
- `network-security/SKILL.md` — network controls for A.13, R1
- `dual-auth-rbac/SKILL.md` — access control for A.9, R7, R8
- `uganda-dppa-compliance/SKILL.md` — Uganda-specific data protection
- `sdlc-planning/`, `sdlc-design/`, `sdlc-testing/` — documentation for A.14 and R6
