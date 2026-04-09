# Infrastructure & Platform Engineering — Skills Gap Analysis

**Date:** 2026-04-10
**Context:** Mapping the skills repository against the Head of Infrastructure & Platform Engineering
role requirements at NSANO. Goal is to identify what skills already cover the role, what needs
enhancing, and what genuinely new skills must be created — while keeping the repository lean.

**Stack alignment note:** All new skills and enhancements must fit the existing repo stack:
PHP + JavaScript (frontend), MySQL/PostgreSQL, Node.js, Android (Kotlin/Compose), iOS (Swift/SwiftUI),
Next.js, and the DevOps toolchain already represented (Jenkins, Docker, Debian/Ubuntu Linux).

---

## Principle

> Enhance existing skills first. Only create a new skill when the domain is genuinely absent.
> We build skills from books — get the books first, build the skills after.

---

## Role Responsibilities Summary

The role covers 9 domains:

1. Infrastructure strategy & architecture
2. Multi-cloud & systems engineering
3. Kubernetes & container platforms
4. DevOps & automation (CI/CD)
5. Performance profiling & cost optimisation
6. Open-source platform ops (reverse proxies, API gateways, workflow engines)
7. Observability & reliability (SLOs/SLAs, monitoring, alerting)
8. Security & compliance (ISO 27001, PCI-DSS)
9. Team leadership & mentorship

---

## Existing Skills — Coverage Map

| Domain | Covering Skill(s) | Coverage |
|---|---|---|
| CI/CD pipelines & automation | `cicd-pipeline-design`, `cicd-jenkins-debian` | Strong |
| DevSecOps, container hardening, secrets basics | `cicd-devsecops` | Strong |
| API gateway & service discovery | `microservices-architecture-models` | Good |
| Resilience (circuit breaker, health, load balancing) | `microservices-resilience` | Good |
| Inter-service auth & API contracts | `microservices-communication` | Good |
| 12-Factor App, bounded contexts, decomposition | `microservices-fundamentals` | Good |
| Database SLOs, runbooks, backup/restore | `database-reliability` | Good |
| MySQL HA, replication, zero-downtime migrations | `mysql-administration` | Good |
| PostgreSQL replication, WAL/PITR, monitoring | `postgresql-administration` | Good |
| Web app security audit (8-layer) | `web-app-security-audit`, `vibe-security-skill` | Good |
| Auth & RBAC | `dual-auth-rbac` | Good |
| Realtime systems (WebSockets, SSE) | `realtime-systems` | Partial |

---

## Gap Analysis

### Skills to Enhance (Not Create New)

| Gap Area | Target Skill | What to Add |
|---|---|---|
| Secrets lifecycle — Vault deep-dive, PKI, key rotation, encryption-at-rest | `cicd-devsecops` | Full Vault operations section |
| Compliance — ISO 27001 controls, PCI-DSS requirements, audit evidence | `cicd-devsecops` | Compliance mapping section |
| Container runtime security — Falco, OPA, admission controllers | `cicd-devsecops` | Runtime threat detection & policy section |
| Network security — firewall rules, WAF, zero-trust, VPN | `web-app-security-audit` | Network-layer security section |
| Reverse proxy ops — Nginx/HAProxy config, reload, health, rate limiting | `microservices-architecture-models` | Ops runbook section |
| API gateway ops — Kong/Traefik routing, plugins, auth | `microservices-architecture-models` | Gateway ops section |
| Workflow automation engines — n8n, Temporal, Airflow async patterns | `microservices-communication` | Async orchestration section |
| SRE practices — SLO/SLI/error budgets, blameless postmortems, escalation | `database-reliability` | Platform SRE section (expand scope beyond DB) |
| FinOps / cost governance — resource quotas, utilisation targets, budgets | `cicd-pipeline-design` | Cost governance section |
| Linux hardening & performance tuning — sysctl, cgroups, auditd | `cicd-jenkins-debian` | Linux systems hardening section |

### New Skills to Create (Genuinely Absent Domains)

Only 3 domains have zero coverage in the repository:

| New Skill | Why It Cannot Be An Enhancement | Source Books |
|---|---|---|
| `kubernetes-platform` | Nothing in the repo touches K8s — cluster management, Helm, RBAC, resource governance, pod security, workload scaling is a full standalone domain | *Kubernetes in Action* (Luksa); *Production Kubernetes* (Rosso et al.) |
| `infrastructure-as-code` | No IaC coverage anywhere — Terraform, Ansible, state management, modules, GitOps (ArgoCD/Flux) is a full standalone domain | *Terraform: Up & Running* (Brikman); *Infrastructure as Code* (Morris) |
| `observability-platform` | No monitoring stack skill exists — Prometheus, Grafana, OpenTelemetry, distributed tracing, SigNoz, alert routing is a full standalone domain | *Observability Engineering* (Majors et al.); *SRE Book* (Google, free online) |

**Result: 3 new skills, 10 existing skills enhanced. Repository stays lean.**

---

## Stack Alignment Guidelines

When building these skills, all patterns and examples must align with the existing stack:

**Runtime environments:** Debian/Ubuntu Linux (primary), Docker containers, Jenkins agents
**Languages in examples:** PHP, JavaScript/Node.js, Python (tooling scripts only)
**Databases referenced:** MySQL 8.x, PostgreSQL 15+
**CI/CD toolchain:** Jenkins (primary), GitLab CI (advantageous per JD)
**Existing security baseline:** `vibe-security-skill` + `cicd-devsecops` — new skills must not contradict these
**IaC target:** Terraform for cloud resources, Ansible for server configuration (Debian/Ubuntu)
**K8s context:** Self-managed clusters on VPS/bare-metal first (NSANO VPS-first model), cloud-managed second
**Observability stack:** SigNoz preferred per JD (open-source, self-hosted) over commercial tools

---

## Recommended Book List (Get Before Building Skills)

### Critical (for the 3 new skills)

1. *Kubernetes in Action* — Marko Luksa
2. *Production Kubernetes* — Josh Rosso, Rich Lander, Alex Brand, John Harris
3. *Terraform: Up & Running* — Yevgeniy Brikman (3rd ed.)
4. *Infrastructure as Code* — Kief Morris (O'Reilly, 2nd ed.)
5. *Observability Engineering* — Charity Majors, Liz Fong-Jones, George Miranda
6. *Site Reliability Engineering* — Google (free at sre.google/books/)

### For Enhancements

7. *The Practice of Cloud System Administration* — Limoncelli et al. (SRE + Linux ops)
8. *Linux System Administration Handbook* — Nemeth et al. (Linux hardening section)
9. *HashiCorp Vault: The Definitive Guide* (secrets management in cicd-devsecops)
10. *PCI DSS: A Practical Guide* (compliance section in cicd-devsecops)

---

## Build Order (When Ready)

### Phase 1 — High-impact enhancements (builds on strongest existing skills)

1. Enhance `cicd-devsecops` — secrets lifecycle + compliance + container runtime security
2. Enhance `database-reliability` — add platform SRE section (SLO/SLI, error budgets, postmortems)
3. Enhance `microservices-architecture-models` — reverse proxy ops + API gateway ops

### Phase 2 — New skills (once books are read)

4. Create `kubernetes-platform`
5. Create `infrastructure-as-code`
6. Create `observability-platform`

### Phase 3 — Remaining enhancements

7. Enhance `web-app-security-audit` — network security layer
8. Enhance `cicd-pipeline-design` — FinOps / cost governance section
9. Enhance `cicd-jenkins-debian` — Linux hardening & performance tuning
10. Enhance `microservices-communication` — workflow automation (n8n, Temporal)

---

## Success Criteria

- [ ] All 3 new skills created and under 500 lines each
- [ ] All 10 existing skills enhanced without exceeding 500-line limit
- [ ] Every code example uses the existing stack (PHP/JS/Node, MySQL/PG, Debian/Ubuntu)
- [ ] K8s skill targets self-managed VPS-first deployment model
- [ ] Observability skill references SigNoz as primary (open-source, self-hosted)
- [ ] Compliance section maps ISO 27001 and PCI-DSS controls to existing toolchain
- [ ] No duplicate domains — enhancements do not create content that belongs in another skill

---

**Total skills touched:** 13 (3 new + 10 enhanced)
**Maintained by:** Peter Bamuhigire
**Line count:** ~160 lines
