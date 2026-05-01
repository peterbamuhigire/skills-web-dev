# Project Vision & Scope Document — Template & Guide

**Back to:** [SDLC Planning Skill](../SKILL.md)

## Purpose

Establishes the **"why"** and **"what"** of the project at a high level. This is the foundational document that aligns all stakeholders on the project's direction before any development begins.

## Audience

Stakeholders, executives, investors, project sponsors, product owners.

## When to Create

- During the **proposal or initiation phase**, before any development begins
- When seeking **funding approval** or investor buy-in
- When a new **SaaS product** is being conceptualized
- After the `project-requirements` skill has gathered raw requirements

## Typical Length

15-30 pages (split into multiple files if exceeding 500 lines).

---

## Template

```markdown
# [Project Name] — Project Vision & Scope Document

**Version:** 1.0
**Date:** YYYY-MM-DD
**Author:** [Name]
**Status:** Draft | Under Review | Approved
**Approved By:** [Name, Title]

---

## 1. Executive Summary

[2-3 paragraphs summarizing the project: what it is, who it serves, why it matters,
and the expected business impact. Write this LAST after completing all other sections.]

## 2. Business Problem / Opportunity Statement

### 2.1 Current State
[Describe the current situation, pain points, and inefficiencies.]

### 2.2 Problem Statement
[One clear, concise statement of the problem being solved.]

### 2.3 Opportunity
[What business opportunity does solving this problem create?
Include market size, growth trends, and competitive gaps.]

## 3. Product Vision Statement

[Elevator pitch format — 2-3 sentences max.]

**Template:**
For [target audience] who [need/pain point], [Product Name] is a [product category]
that [key benefit]. Unlike [competitors/current alternatives], our product
[key differentiator].

## 4. Target Audience & User Personas

### Persona 1: [Name — Role]
| Attribute | Details |
|-----------|---------|
| Role | [e.g., School Administrator] |
| Demographics | [Age range, tech comfort, location] |
| Goals | [What they want to achieve] |
| Pain Points | [Current frustrations] |
| Usage Pattern | [Daily/weekly, device, time of day] |
| Success Criteria | [How they measure value] |

### Persona 2: [Name — Role]
[Same table format]

### Persona 3: [Name — Role]
[Same table format]

[Include 3-5 personas. Each represents a distinct user type.]

## 5. Key Features & Capabilities

### Priority Definitions
- **P0 (Must Have):** Core features required for MVP launch
- **P1 (Should Have):** High-value features for first major release
- **P2 (Nice to Have):** Future enhancements and differentiators

### Feature Inventory

| ID | Feature | Priority | Description | User Personas |
|----|---------|----------|-------------|---------------|
| F-001 | [Feature name] | P0 | [Brief description] | Persona 1, 2 |
| F-002 | [Feature name] | P0 | [Brief description] | Persona 1 |
| F-003 | [Feature name] | P1 | [Brief description] | Persona 2, 3 |
| F-004 | [Feature name] | P2 | [Brief description] | All |

## 6. Scope Boundaries

### 6.1 In-Scope
- [Specific capability 1]
- [Specific capability 2]
- [Specific platform: Web + Android]
- [Specific market: East African SaaS companies]

### 6.2 Out-of-Scope
- [Explicitly excluded capability 1 — and WHY]
- [Explicitly excluded platform — and WHY]
- [Explicitly excluded integration — and WHY]

### 6.3 Future Scope (Deferred)
- [Capability planned for future releases]
- [Integration planned for Phase 2+]

## 7. Success Metrics & KPIs

| Metric | Target | Measurement Method | Timeline |
|--------|--------|-------------------|----------|
| [e.g., Monthly Active Users] | [e.g., 500 MAU] | [Analytics dashboard] | [6 months post-launch] |
| [e.g., Tenant Onboarding Rate] | [e.g., 10 new tenants/month] | [Admin dashboard] | [3 months post-launch] |
| [e.g., System Uptime] | [e.g., 99.5%] | [Monitoring tool] | [Ongoing] |
| [e.g., Customer Retention] | [e.g., 85% annual] | [Subscription data] | [12 months] |
| [e.g., Average Response Time] | [e.g., < 500ms API] | [APM tool] | [Ongoing] |

## 8. Assumptions & Constraints

### 8.1 Assumptions
- [e.g., Users have smartphone access with intermittent internet]
- [e.g., Backend PHP 8+ with MySQL 8.x is the chosen stack]
- [e.g., Multi-tenant row-level isolation via franchise_id]

### 8.2 Constraints
- [e.g., Budget: $XX,XXX for Phase 1]
- [e.g., Timeline: MVP in 12 weeks]
- [e.g., Team: 2 developers, 1 QA]
- [e.g., Deployment: Windows dev, Ubuntu staging, Debian production]

## 9. Dependencies & Integrations

| Dependency | Type | Impact if Unavailable | Mitigation |
|-----------|------|----------------------|------------|
| [e.g., Payment gateway (M-Pesa)] | External API | Cannot process payments | Manual payment recording |
| [e.g., SMS provider] | External Service | No OTP or notifications | Email fallback |
| [e.g., Existing ERP database] | Data Migration | No historical data | Phased migration |

## 10. High-Level Timeline & Milestones

| Phase | Milestone | Target Date | Key Deliverables |
|-------|-----------|-------------|-----------------|
| Phase 0 | Planning Complete | Week 2 | All SDLC planning documents |
| Phase 1 | MVP Backend | Week 8 | Core API, auth, 3 modules |
| Phase 2 | MVP Frontend | Week 12 | Web UI for P0 features |
| Phase 3 | Android App | Week 18 | Mobile companion (Phase 1 bootstrap) |
| Phase 4 | Beta Launch | Week 20 | 5 pilot tenants onboarded |
| Phase 5 | Production Launch | Week 24 | Public launch |

## 11. Budget Overview

| Category | Estimated Cost | Notes |
|----------|---------------|-------|
| Development | $XX,XXX | [X developers × Y months] |
| Infrastructure | $X,XXX | [VPS, domain, SSL, backups] |
| Third-Party Services | $X,XXX | [SMS, payment gateway, email] |
| Testing & QA | $X,XXX | [Manual + automated testing] |
| Contingency (15%) | $X,XXX | [Buffer for unknowns] |
| **Total** | **$XX,XXX** | |

## 12. Glossary

| Term | Definition |
|------|-----------|
| Franchise | A tenant in the multi-tenant system |
| franchise_id | Row-level tenant isolation identifier |
| [Domain term] | [Definition] |
```

---

## Section-by-Section Guidance

### Executive Summary
Write this **last**. Summarize the entire document in 2-3 paragraphs. A busy executive should understand the project by reading only this section.

### Business Problem
Be specific. Quantify the pain: "Schools in Uganda spend 40+ hours/month on manual grade calculations" is better than "Schools need better software."

### Product Vision
Use the elevator pitch template. If you cannot fill it in one sentence, the vision is too complex. Simplify.

### User Personas
Base personas on real user research or domain knowledge. Each persona should have distinct needs. Avoid generic personas that apply to any software.

### Features & Capabilities
Prioritize ruthlessly. P0 should have no more than 5-8 features. If everything is P0, nothing is P0.

### Scope Boundaries
The Out-of-Scope section is as important as In-Scope. Explicitly listing what you will NOT build prevents scope creep.

### Success Metrics
Every metric must have a **specific numeric target** and a **measurement method**. "Improve user satisfaction" is not measurable. "Achieve NPS score of 40+" is.

### Dependencies
List every external system, API, or service your project depends on. Include the mitigation plan for each.

---

## Example Excerpt — Multi-Tenant School Management ERP

```markdown
## 3. Product Vision Statement

For school administrators in East Africa who struggle with manual student records,
fee tracking, and grade management, EduTrack SaaS is a multi-tenant school ERP
that digitizes all academic and administrative workflows. Unlike existing school
management tools, EduTrack provides offline-capable Android access, M-Pesa fee
integration, and per-school data isolation at an affordable per-student pricing tier.

## 7. Success Metrics & KPIs

| Metric | Target | Method | Timeline |
|--------|--------|--------|----------|
| Schools Onboarded | 50 schools | Admin dashboard | 6 months |
| Monthly Active Users | 2,000 MAU | Analytics | 6 months |
| Fee Collection Rate | 90% digital | Payment reports | 12 months |
| System Uptime | 99.5% | UptimeRobot | Ongoing |
| Android App Rating | 4.0+ stars | Play Store | 6 months |
| API Response Time | < 500ms (p95) | APM monitoring | Ongoing |
```

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Vague vision ("build a great app") | No alignment, no measurable success | Use elevator pitch template with specifics |
| No measurable success criteria | Cannot tell if project succeeded | Define 5-8 KPIs with numeric targets |
| Scope creep from inception (everything is P0) | Project never ships | Limit P0 to 5-8 core features |
| Missing Out-of-Scope section | Stakeholders assume everything is included | Explicitly list what is excluded and why |
| Generic personas ("User A") | No actionable design guidance | Base on real users with specific pain points |
| No budget or timeline | No resource planning, infinite project | Include even rough estimates |
| Writing Executive Summary first | Summary does not match document content | Write it last |

## Quality Checklist

- [ ] Executive Summary written last, accurately reflects all sections
- [ ] Business Problem is specific and quantified
- [ ] Product Vision fits in 2-3 sentences (elevator pitch)
- [ ] 3-5 user personas with distinct roles and pain points
- [ ] Features prioritized as P0/P1/P2 with no more than 8 P0 features
- [ ] Scope Boundaries include explicit Out-of-Scope items with reasons
- [ ] 5-8 Success Metrics with specific numeric targets and measurement methods
- [ ] Assumptions and Constraints are realistic and complete
- [ ] Dependencies list includes mitigation plans
- [ ] Timeline has specific dates (not "TBD") and key deliverables per phase
- [ ] Budget includes contingency (10-20%)
- [ ] Glossary defines all domain-specific terms
- [ ] Document stays under 500 lines (split if needed)
- [ ] Cross-references SRS and SDP where relevant

---

**Back to:** [SDLC Planning Skill](../SKILL.md)
**Next:** [Software Development Plan](software-development-plan.md)
