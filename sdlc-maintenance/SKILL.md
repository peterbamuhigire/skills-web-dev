---
name: sdlc-maintenance
description: Generate a Software Maintenance Plan (SMP) and supporting maintenance documentation for SDLC projects. Compliant with ISO/IEC/IEEE 14764:2022. Covers Maintenance Strategy, MR/PR handling workflow, CCB process, maintenance cost estimation, and all...
---

## Required Plugins

**Superpowers plugin:** MUST be active for all work using this skill. Use throughout the entire build pipeline — design decisions, documentation generation, quality checks, and any task where it offers enhanced capabilities.

# SDLC Maintenance Skill

Generate a complete **Software Maintenance Plan (SMP)** and supporting maintenance documentation for software projects. This skill produces 3 documents that establish the maintenance baseline, define the change request workflow, and track ongoing maintenance metrics.

## When to Use

- Transitioning a **delivered system into the maintenance phase**
- Planning maintenance for a **live production system**
- Establishing a **Change Control Board (CCB)** and formal MR/PR workflow
- Documenting **maintenance cost estimates** for budget planning
- Complying with **ISO/IEC/IEEE 14764:2022** maintenance process requirements
- Preparing a **maintenance strategy** for a SaaS platform post-launch

## When NOT to Use

- **Planning development activities before delivery** — use `sdlc-planning` skill
- **Documenting test plans or quality gates** — use `sdlc-testing` skill
- **Creating deployment or release procedures** — use `sdlc-user-deploy` skill
- **Post-deployment health assessment** — use `sdlc-post-deployment` skill (run that first; SMP follows)

## Document Inventory

| # | Document | Purpose | Audience | Phase |
|---|----------|---------|----------|-------|
| 1 | **Software Maintenance Plan (SMP)** | Primary governance document: scope, org, process model, CCB, cost, training, records | Maintenance team, PM, stakeholders | Maintenance phase |
| 2 | **Change Request / Problem Report Form** | MR/PR intake template: identification, classification, impact, approval, resolution | Developers, CCB, end users | Ongoing |
| 3 | **Maintenance Metrics Report** | Periodic measurement: defect rates, MTTR, maintenance type mix, cost actuals vs. estimates | PM, stakeholders, CCB | Periodic (monthly/quarterly) |

## Standards Basis

The SMP structure is governed by **ISO/IEC/IEEE 14764:2022** (Software Engineering — Software Life Cycle Processes — Maintenance), specifically **Clause 9** (Software Maintenance Plan), which mandates 13 numbered subsections. This standard is a process standard within the **ISO/IEC/IEEE 12207:2017** framework; Clause 6.4.13 of 12207 defines the maintenance process outcomes that the SMP must satisfy.

**Relationship to ISO 12207:** 14764 is the dedicated maintenance elaboration of 12207. When a project is governed by 12207, the SMP produced under 14764 Clause 9 fulfills the 12207 §6.4.13 process documentation requirement.

## Five Maintenance Types

ISO/IEC/IEEE 14764:2022 defines five maintenance types. Every SMP must declare which types are in scope.

| Type | Definition | Trigger |
|------|-----------|---------|
| **Corrective** | Reactive modification to fix discovered faults | Bug report, system failure |
| **Adaptive** | Modification to keep the software usable in a changed environment | OS upgrade, API deprecation, regulatory change |
| **Perfective** | Modification to improve performance or maintainability | Performance complaint, code quality initiative |
| **Preventive** | Modification to detect and correct latent faults before they manifest | Code audit findings, proactive refactoring |
| **Additive** | Addition of new functionality or features after delivery *(new in 2022)* | Feature request from stakeholders |

**Empirical Distribution (Lientz & Swanson baseline):** Corrective 20% / Adaptive 25% / Perfective 50% / Preventive 5%. Use this as the planning benchmark when no project-specific history exists. Track actual mix in the Maintenance Metrics Report and adjust future estimates accordingly.

## SMP Required Sections (ISO 14764 Clause 9)

The SMP must include all 13 subsections below. Flag `[CONTEXT-GAP]` for any section where project context is absent.

**9.1.2 — Identification and control of the plan**
Document identifier, version, date, approval authority, and revision history. Links to the parent SDP and SRS.

**9.1.3 — Scope of maintenance**
Name the five maintenance types covered. State the system being maintained (name, version, deployment environment). Define the maintenance window (hours of operation, response SLAs).

**9.1.4 — Designation of maintenance organization**
Define roles: Maintenance Manager, Maintenance Engineers, Change Control Board (CCB) members, Configuration Manager, Customer Representative. Specify CCB quorum rules and escalation path.

**9.1.5 — References**
List all governing documents: SRS, SDD, STP, deployment guide, and this SMP. Include standard references: ISO/IEC/IEEE 14764:2022, ISO/IEC/IEEE 12207:2017.

**9.1.6 — Definitions**
Define all maintenance-specific terms used in the plan: MR (Modification Request), PR (Problem Report), CCB, MTTR, baseline, corrective/adaptive/perfective/preventive/additive maintenance.

**9.1.7 — Processes (maintenance process model selection)**
Select and justify one of three process models:
- **Quick-Fix Model:** Fast turnaround; fix applied directly to operational code then back-ported to design docs. Risk: documentation drift. Use only for critical production fixes.
- **Iterative Enhancement Model:** Changes are analyzed, designed, implemented, and tested in mini-cycles before release. Preferred for planned maintenance.
- **Osborne's Model:** Post-delivery fixes integrated into a formal release pipeline with explicit review gates. Use when the CCB requires formal approval before any change.

**9.1.8 — Organization and maintenance activities**
Define the MR/PR 10-step workflow (see below). Assign responsible role to each step.

**9.1.9 — Resources**
List tools (version control, issue tracker, CI/CD pipeline, test environments), infrastructure, and third-party dependencies required to execute maintenance.

**9.1.10 — Estimate of maintenance costs**
Apply one or more estimation methods:
- **COCOMO II** (post-architecture model): $Effort = A \times Size^{E} \times \prod EM_i$ where effort multipliers reflect maintenance context
- **Historical data ratio:** Maintenance effort typically 40–80% of original development cost per year (Grubb & Takang, 2003)
- **Person-month estimates per maintenance type:** State assumptions explicitly; flag estimates as `[ESTIMATE-UNVERIFIED]` until actual data replaces them

**9.1.11 — Training**
Identify training required for maintenance engineers: system domain knowledge, tool proficiency, standards compliance. State who is responsible for training delivery.

**9.1.12 — Software maintenance control requirements**
Define CCB authority levels (who can approve corrective fixes vs. perfective enhancements), configuration management (CM) procedures under the SCMP, and the baseline lock/unlock protocol.

**9.1.13 — Maintenance records and reports**
Specify which records are kept: all MRs/PRs (open and closed), CCB meeting minutes, cost actuals, Maintenance Metrics Reports. State retention period and storage location.

**9.2.2 — Personnel resources**
Headcount plan: number of maintenance engineers required per maintenance type, skill profiles, and ramp-up time for new team members.

**9.2.3 — Environment resources**
Maintenance environment specification: hardware, OS, database versions, network access. Must match the production environment documented in the Deployment Guide.

**9.2.4 — Financial resources**
Annual maintenance budget broken down by maintenance type. Include contingency reserve (recommend 15–20% of total estimate).

## MR/PR 10-Step Process (ISO 14764 Clause 6.2)

Every modification — regardless of type — must follow this sequence. No step may be skipped without documented CCB waiver.

| Step | Name | Description | Owner |
|------|------|-------------|-------|
| 1 | **Problem/modification identification** | MR or PR submitted with system ID, version, environment, and symptom description | Requestor |
| 2 | **Analysis** | Impact assessment: affected modules, risk level, effort estimate, classification (corrective/adaptive/perfective/preventive/additive) | Maintenance Engineer |
| 3 | **CCB review** | CCB evaluates analysis, approves, defers, or rejects the change | CCB |
| 4 | **Design** | Technical solution designed; existing design documents updated | Maintenance Engineer |
| 5 | **Implementation** | Code change developed against approved design | Developer |
| 6 | **Unit testing** | Verify the change in isolation per STP criteria | Developer |
| 7 | **Integration/regression testing** | Verify no regression; run full test suite | QA |
| 8 | **Acceptance testing** | Requestor or designated user confirms the change resolves the original MR/PR | Requestor / QA |
| 9 | **Delivery** | Change released to production via CM-controlled deployment procedure | Ops / DevOps |
| 10 | **Closure** | MR/PR record updated to Closed; lessons learned captured; documentation updated | Maintenance Manager |

## Lehman's Laws

Two of Lehman's eight laws are directly relevant to maintenance planning and serve as the theoretical justification for why an SMP is mandatory, not optional.

**Law I — Continuing Change (1974):** A program that is used must be continually adapted or it becomes progressively less satisfactory in use.

**Law VII — Declining Quality (1996):** The quality of an evolving system will appear to be declining unless it is rigorously maintained and adapted to operational environment changes.

**Implication for the SMP:** These laws establish that software entropy is not accidental — it is a predictable consequence of failing to maintain. The SMP is the engineering control that counteracts both laws. An organization that delivers software without an SMP is accepting Law I and Law VII as inevitable outcomes rather than engineering risks to be managed.

## Quality Checklist

- [ ] All 3 documents generated (or justified why one was skipped)
- [ ] SMP covers all 13 ISO 14764 Clause 9 subsections
- [ ] All five maintenance types declared in scope (or explicitly excluded with rationale)
- [ ] Process model selected (Quick-Fix / Iterative Enhancement / Osborne's) and justified
- [ ] MR/PR 10-step workflow defined with role assigned to each step
- [ ] CCB composition documented with quorum rules and escalation path
- [ ] Maintenance cost estimate uses COCOMO II or historical ratio — no vague estimates
- [ ] All cost estimates flagged `[ESTIMATE-UNVERIFIED]` until actuals replace them
- [ ] Lientz/Swanson empirical distribution (20/25/50/5) used as planning baseline
- [ ] Lehman's Laws I and VII cited as justification for mandatory SMP
- [ ] Maintenance environment matches production environment in Deployment Guide
- [ ] Training plan identifies who delivers training and when
- [ ] Records retention period and storage location specified in 9.1.13
- [ ] Financial resources section includes 15–20% contingency reserve
- [ ] Change Request / Problem Report Form template covers: ID, classification, impact, CCB decision, resolution
- [ ] Maintenance Metrics Report covers: defect rates, MTTR, type mix, cost actuals
- [ ] All documents cross-reference the SRS, SDP, STP, and Deployment Guide
- [ ] No vague language ("fast fixes", "as needed") — all SLAs have numeric targets

## Anti-Patterns

| Anti-Pattern | Why It Fails | Do This Instead |
|-------------|-------------|-----------------|
| No SMP at product launch | Teams improvise; fixes are inconsistent; costs balloon | Draft SMP during final testing phase; activate at go-live |
| Treating all changes as corrective | Perfective and adaptive work goes unplanned and unbudgeted | Classify every MR/PR using the five-type taxonomy at intake |
| Quick-Fix model as the default | Documentation drifts from code; next maintainer inherits technical debt | Default to Iterative Enhancement; Quick-Fix requires documented CCB waiver |
| CCB with no quorum rules | Changes approved by a single person; no audit trail | Define minimum quorum (e.g., 3 of 5 members) in SMP §9.1.4 |
| Ignoring Lehman's Laws | Management treats maintenance as optional spend and cuts budget mid-year | Cite Law I and Law VII in the SMP business case to anchor the budget |
| Vague cost estimates with no method | Budget is arbitrary; overruns are guaranteed | Use COCOMO II or historical ratio; document all assumptions |
| No regression testing gate (Step 7) | Fixes break other features silently | Step 7 is mandatory before acceptance; reference STP for suite scope |
| Closing MRs without documentation updates | System documentation diverges from deployed code over time | Step 10 requires documentation update before closure |

## Cross-References

### Upstream Skills (use BEFORE this skill)

| Skill | Relationship |
|-------|-------------|
| `sdlc-user-deploy` | Deployment Guide documents the production environment that §9.2.3 must match. Release procedures inform the Step 9 delivery process. |
| `sdlc-testing` | STP defines the regression suite scope used in MR/PR Step 7 and acceptance criteria in Step 8. |
| `sdlc-post-deployment` | PDER provides first-90-day metrics (defect rate, MTTR, type mix) that seed the SMP cost estimates in §9.1.10. |

### Parallel Skills (use ALONGSIDE this skill)

| Skill | Relationship |
|-------|-------------|
| `sdlc-planning` | SCMP governs CM procedures referenced in §9.1.12. QA Plan standards apply to maintenance quality gates. |

### Sibling SDLC Skills

| Skill | Phase | Status |
|-------|-------|--------|
| `sdlc-planning` | Planning & Management | Available |
| `sdlc-design` | Design & Architecture | Available |
| `sdlc-testing` | Testing & Quality | Available |
| `sdlc-user-deploy` | Delivery & Deployment | Available |
| `sdlc-post-deployment` | Post-Deployment Evaluation | Available |
| `sdlc-maintenance` | Software Maintenance | **This Skill** |

---

**Back to:** [Skills Repository](../CLAUDE.md)
**Related:** [sdlc-planning](../sdlc-planning/SKILL.md) | [sdlc-testing](../sdlc-testing/SKILL.md) | [sdlc-user-deploy](../sdlc-user-deploy/SKILL.md) | [sdlc-post-deployment](../sdlc-post-deployment/SKILL.md)
**Last Updated:** 2026-03-15 (created per ISO/IEC/IEEE 14764:2022 Clause 9 + Grubb & Takang 2003)
