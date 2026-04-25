# Risk Management Plan — Template & Guide

**Back to:** [SDLC Planning Skill](../SKILL.md)

## Purpose

Defines how to **identify, assess, mitigate, and monitor project risks** throughout the SDLC. Includes a pre-populated risk register with common SaaS-specific risks.

## Audience

Project managers, stakeholders, development leads, technical leads.

## When to Create

After the Vision & Scope is approved. Update continuously throughout the project lifecycle.

---

## Template

```markdown
# [Project Name] — Risk Management Plan

**Version:** 1.0
**Date:** YYYY-MM-DD
**Author:** [Name]
**Status:** Draft | Under Review | Approved
**Review Cadence:** Bi-weekly during development, monthly post-launch
**References:** [Link to Vision & Scope], [Link to SDP], [Link to QA Plan]

---

## 1. Risk Management Approach

### 1.1 Objectives
- Proactively identify risks before they become problems
- Assess probability and impact using a standardized matrix
- Define mitigation strategies with assigned owners
- Monitor risks at regular intervals and escalate when thresholds are exceeded

### 1.2 Risk Tolerance
| Category | Tolerance Level | Rationale |
|----------|----------------|-----------|
| Security | Zero tolerance for data breaches | Multi-tenant data isolation is non-negotiable |
| Financial | < 15% budget overrun acceptable | Contingency buffer included |
| Schedule | < 3-week delay on non-critical path | Buffer in phase planning |
| Quality | No S1/S2 defects at launch | Release-blocking quality gates |

## 2. Risk Identification Methods

| Method | Frequency | Participants |
|--------|-----------|-------------|
| Brainstorming sessions | Phase start | Full team |
| Sprint retrospectives | Bi-weekly | Dev team |
| Code review findings | Per PR | Reviewers |
| Security audits | Per release | Security + QA |
| Stakeholder interviews | Quarterly | PM + stakeholders |
| Industry monitoring | Ongoing | Tech Lead |
| Incident post-mortems | After each incident | Affected team members |

## 3. Risk Categories

| Category | Abbreviation | Scope |
|----------|-------------|-------|
| Technical | TECH | Architecture, technology, performance, scalability |
| Security | SEC | Auth, data protection, multi-tenant isolation |
| Business | BIZ | Market, funding, requirements, stakeholder |
| Operational | OPS | Deployment, infrastructure, team, process |
| External | EXT | Third-party services, regulations, market forces |

## 4. Risk Assessment Matrix

### 4.1 Probability Scale

| Level | Score | Description |
|-------|-------|-------------|
| Rare | 1 | < 10% chance of occurring |
| Unlikely | 2 | 10-30% chance |
| Possible | 3 | 30-50% chance |
| Likely | 4 | 50-70% chance |
| Almost Certain | 5 | > 70% chance |

### 4.2 Impact Scale

| Level | Score | Schedule | Budget | Quality | Security |
|-------|-------|----------|--------|---------|----------|
| Negligible | 1 | < 1 day delay | < 2% overrun | Cosmetic defects | No data exposure |
| Minor | 2 | 1-3 days | 2-5% overrun | Minor feature degraded | Low-sensitivity data |
| Moderate | 3 | 1-2 weeks | 5-10% overrun | Major feature degraded | Internal data exposed |
| Major | 4 | 2-4 weeks | 10-20% overrun | Feature unusable | PII data exposed |
| Critical | 5 | > 4 weeks | > 20% overrun | System failure | Cross-tenant data breach |

### 4.3 Risk Score Matrix (Probability x Impact)

|  | Negligible(1) | Minor(2) | Moderate(3) | Major(4) | Critical(5) |
|--|:---:|:---:|:---:|:---:|:---:|
| **Almost Certain(5)** | 5 | 10 | 15 | 20 | **25** |
| **Likely(4)** | 4 | 8 | 12 | **16** | **20** |
| **Possible(3)** | 3 | 6 | 9 | 12 | **15** |
| **Unlikely(2)** | 2 | 4 | 6 | 8 | 10 |
| **Rare(1)** | 1 | 2 | 3 | 4 | 5 |

**Score interpretation:** 1-5 = Low (accept), 6-10 = Medium (monitor), 11-15 = High (mitigate), 16-25 = Critical (immediate action).

## 5. Risk Register

### 5.1 Pre-Populated SaaS Risks

| ID | Category | Risk Description | P | I | Score | Mitigation Strategy | Owner | Status |
|----|----------|-----------------|---|---|-------|-------------------|-------|--------|
| R-SEC-001 | SEC | Multi-tenant data leakage: queries missing franchise_id filter expose Tenant A data to Tenant B | 3 | 5 | 15 | Mandatory franchise_id in all queries; automated tenant isolation tests; code review checklist; database views scoped by tenant | Tech Lead | Open |
| R-SEC-002 | SEC | JWT token theft or replay: compromised tokens allow unauthorized access | 3 | 4 | 12 | Short-lived access tokens (1h); refresh token rotation with breach detection; EncryptedSharedPreferences for storage; token revocation on logout | Backend Dev | Open |
| R-TECH-001 | TECH | API breaking changes: backend API changes break existing Android clients | 4 | 4 | 16 | API versioning (v1/v2); backward compatibility policy; minimum 2-week deprecation notice; feature flags for gradual rollout | Tech Lead | Open |
| R-TECH-002 | TECH | Database migration failure on production: migration script corrupts data or fails mid-execution | 2 | 5 | 10 | Idempotent migrations; full backup before migration; staging validation; migration rollback scripts; migration_log table | DevOps | Open |
| R-EXT-001 | EXT | Third-party service outage: payment gateway (M-Pesa), SMS provider, or email service goes down | 3 | 3 | 9 | Graceful degradation; retry with exponential backoff; fallback providers; manual processing capability; SLA monitoring | Backend Dev | Open |
| R-OPS-001 | OPS | Cross-platform deployment issues: code works on Windows WAMP but fails on Linux production | 3 | 3 | 9 | Staging env mirrors production (Ubuntu); case-sensitive file testing; forward-slash paths; CI/CD pipeline tests on Linux | DevOps | Open |
| R-EXT-002 | EXT | Play Store rejection: Android app fails Google review (policy violation, performance, privacy) | 2 | 4 | 8 | Follow Google Play policies; privacy policy page; performance testing; pre-launch report; reference google-play-store-review skill | Android Dev | Open |
| R-SEC-003 | SEC | Security breach / unauthorized access: exploitation of OWASP Top 10 vulnerabilities | 2 | 5 | 10 | OWASP checklist per release; prepared statements only; input validation; RBAC enforcement; security audit; reference vibe-security-skill | Tech Lead | Open |
| R-TECH-003 | TECH | Scaling issues under tenant growth: database queries slow as tenant count and data volume increase | 3 | 3 | 9 | Query optimization; proper indexing; database partitioning plan; caching strategy; performance baseline and monitoring | Backend Dev | Open |
| R-BIZ-001 | BIZ | Requirements change mid-development: stakeholder discovers new needs, scope expands | 4 | 3 | 12 | Phase-gated delivery; change control process; scope freeze during sprints; backlog management; stakeholder sign-off at gates | PM | Open |
| R-OPS-002 | OPS | Key team member unavailable: developer illness, departure, or unavailability | 2 | 4 | 8 | Documentation culture; code reviews (knowledge sharing); cross-training; no single point of failure for critical knowledge | PM | Open |
| R-TECH-004 | TECH | Samsung Knox crash on EncryptedSharedPreferences init: device-specific crash on Samsung devices | 3 | 3 | 9 | Try-catch wrapper on ESP initialization; fallback to regular SharedPreferences if ESP fails; log and monitor crash rates | Android Dev | Open |

### 5.2 Project-Specific Risks
[Add risks specific to your project here using the same table format.]

| ID | Category | Risk Description | P | I | Score | Mitigation Strategy | Owner | Status |
|----|----------|-----------------|---|---|-------|-------------------|-------|--------|
| R-XXX-001 | | | | | | | | Open |

## 6. Mitigation Strategy Categories

| Strategy | When to Use | Example |
|----------|------------|---------|
| **Avoid** | Eliminate the risk entirely | Choose a different technology, remove risky feature |
| **Mitigate** | Reduce probability or impact | Add validation, implement monitoring, create backups |
| **Transfer** | Shift risk to third party | Insurance, SLAs with vendors, managed services |
| **Accept** | Risk is low or unavoidable | Document acceptance, set contingency trigger |

## 7. Contingency Plans

### 7.1 Production System Down (R-SEC-003, R-OPS-001)
1. Alert via monitoring system (immediate)
2. Assess scope and severity (< 15 min)
3. Activate hotfix branch from `main`
4. If data integrity issue: stop writes, assess damage
5. Deploy fix to staging, verify (< 1 hour)
6. Deploy to production
7. Post-incident review within 48 hours

### 7.2 Data Breach Suspected (R-SEC-001)
1. Isolate affected system immediately
2. Assess what data was exposed and which tenants affected
3. Notify affected tenants per data protection requirements
4. Identify and fix the vulnerability
5. Conduct security audit of related code
6. Update risk register and security procedures

### 7.3 Third-Party Service Outage (R-EXT-001)
1. Activate fallback mechanism (if available)
2. Enable manual processing mode
3. Queue failed operations for retry
4. Notify affected users of degraded service
5. Monitor service status, resume when available
6. Process queued operations

## 8. Risk Monitoring & Review

### 8.1 Review Cadence

| Phase | Frequency | Focus |
|-------|-----------|-------|
| Planning | Once | Initial risk identification |
| Development | Bi-weekly (sprint boundary) | New risks, updated scores, mitigation progress |
| Testing | Weekly | Quality risks, defect trends |
| Deployment | Per deployment | Deployment-specific risks |
| Post-Launch | Monthly | Operational risks, incident trends |

### 8.2 Risk Dashboard Metrics
- Total open risks by category
- Risk score trend over time
- Overdue mitigation actions
- Risks closed vs new risks identified
- Top 5 risks by score

## 9. Escalation Procedures

| Risk Score | Escalation Level | Action Required |
|-----------|-----------------|-----------------|
| 1-5 (Low) | Team level | Monitor, no escalation |
| 6-10 (Medium) | Tech Lead | Review mitigation, assign owner |
| 11-15 (High) | PM + Tech Lead | Active mitigation, weekly review |
| 16-25 (Critical) | PM + Sponsor | Immediate action, daily review, may pause project |
```

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Ignoring risks ("it'll be fine") | Risks become surprises that derail the project | Proactive identification, document everything |
| No mitigation owners | Nobody is accountable, mitigations never happen | Every risk must have a named owner |
| Stale risk register | Does not reflect current reality | Review bi-weekly, update at every sprint boundary |
| All risks are "High" priority | Prioritization fails, analysis paralysis | Use the 5x5 matrix, let the math decide |
| No contingency plans | When risks materialize, team scrambles | Pre-plan responses for top 5 risks |
| Risk register as checkbox exercise | Document exists but nobody uses it | Integrate into sprint reviews and phase gates |
| Missing security risks | Security breaches are catastrophic | Pre-populate with SaaS security risks (see above) |
| Not updating after incidents | Same risks repeat | Post-incident review updates risk register |

## Quality Checklist

- [ ] Risk management approach and tolerance levels defined
- [ ] Risk identification methods documented with frequency
- [ ] 5x5 assessment matrix included with score interpretation
- [ ] Risk register has at least 8 pre-populated SaaS-specific risks
- [ ] Every risk has: ID, category, description, probability, impact, score, mitigation, owner, status
- [ ] Multi-tenant data leakage risk included (R-SEC-001)
- [ ] API breaking changes risk included (R-TECH-001)
- [ ] Database migration failure risk included (R-TECH-002)
- [ ] Third-party service outage risk included (R-EXT-001)
- [ ] Cross-platform deployment risk included (R-OPS-001)
- [ ] Play Store rejection risk included (R-EXT-002)
- [ ] Contingency plans defined for top risks
- [ ] Review cadence defined for each project phase
- [ ] Escalation procedures defined by risk score threshold
- [ ] Risk register includes space for project-specific risks
- [ ] Document stays under 500 lines

---

**Back to:** [SDLC Planning Skill](../SKILL.md)
**Previous:** [Quality Assurance Plan](quality-assurance-plan.md)
**Next:** [Software Requirements Specification](software-requirements-spec.md)
