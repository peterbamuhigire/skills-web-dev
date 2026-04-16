---
name: sdlc-post-deployment
description: Generate a Post-Deployment Evaluation Report (PDER) to assess software
  health after production deployment. Grounded in ISO/IEC/IEEE 14764:2022 Clause 6
  mandatory outcomes and Grubb & Takang's operational metrics. Covers system availability...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

## Platform Notes

- Optional helper plugins may help in some environments, but they must not be treated as required for this skill.

# SDLC Post-Deployment Skill

<!-- dual-compat-start -->
## Use When

- Generate a Post-Deployment Evaluation Report (PDER) to assess software health after production deployment. Grounded in ISO/IEC/IEEE 14764:2022 Clause 6 mandatory outcomes and Grubb & Takang's operational metrics. Covers system availability...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `sdlc-post-deployment` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve.
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
| Release evidence | Post-Deployment Evaluation Report | Markdown doc covering deploy outcome, KPIs, and remediation actions | `docs/releases/pder-2026-04-16.md` |
| Release evidence | Post-deploy verification log | Markdown doc or CI artifact listing checks run and results | `docs/releases/verify-2026-04-16.md` |

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
Generate a **Post-Deployment Evaluation Report (PDER)** that assesses software health after a production release. This skill produces 1 primary document grounded in ISO/IEC/IEEE 14764:2022 mandatory process outcomes and Grubb & Takang (2003) first-year operational metrics.

## Load Order

1. Load `world-class-engineering`.
2. Load `observability-monitoring`, `reliability-engineering`, and `deployment-release-engineering`.
3. Load this skill to convert post-release data into decisions and maintenance actions.

## Executable Post-Deployment Standard

The PDER must connect:

- what was released
- what telemetry observed
- what failed, degraded, or surprised the team
- what maintenance, architecture, or delivery-system changes follow

## When to Use

- **30–90 days after a major release** — the primary evaluation window per Grubb & Takang (2003)
- After **each subsequent major release** to track health trends across the system lifecycle
- When stakeholders request **evidence that the deployment met its objectives**
- To **seed the Software Maintenance Plan** with real cost, defect, and MTTR data

## When NOT to Use

- **Pre-release quality gates** — use `sdlc-testing` skill (Test Completion Report covers this)
- **Deployment procedures and release notes** — use `sdlc-user-deploy` skill
- **Ongoing maintenance planning** — use `sdlc-maintenance` skill (PDER feeds into it; it does not replace it)
- **Architecture or design reviews** — use `sdlc-design` skill

## Document Inventory

| # | Document | Purpose | Audience | Phase |
|---|----------|---------|----------|-------|
| 1 | **Post-Deployment Evaluation Report (PDER)** | Evidence-based assessment of system health: operational metrics, maintenance type mix, lessons learned, recommended actions | PM, stakeholders, CCB, maintenance team | 30–90 days post-release |

## Standards Basis

The PDER satisfies the five mandatory outcomes of **ISO/IEC/IEEE 14764:2022 §6.4.13.2** (maintenance process outcomes). These outcomes are non-optional: a deployment that cannot produce evidence for all five has an incomplete maintenance process.

**Relationship to Osborne's Model:** Grubb & Takang (2003) describe Osborne's post-installation review as the formal process gate that triggers PDER creation. The review is scheduled at the end of the initial operational period (30–90 days) and produces structured findings that transition the system from the delivery phase into the formal maintenance phase.

## Five Mandatory Outcomes (ISO 14764:2022 §6.4.13.2)

The PDER must provide evidence for each outcome. Flag `[OUTCOME-UNMET]` for any outcome where evidence cannot be gathered.

| Outcome | Description | PDER Section That Addresses It |
|---------|------------|-------------------------------|
| **a)** | Maintenance constraints identified | Operational Health Metrics + Documentation Currency |
| **b)** | Enabling systems and services available | Deployment Summary + Environment Status |
| **c)** | Replacement, repaired, or revised elements available | Maintenance Type Mix Actuals |
| **d)** | Need for corrective, perfective, and adaptive changes reported | Change Request Analysis + Recommended Actions |
| **e)** | Failure and lifetime data (including costs) determined | MTTR Breakdown + Cost Data |

## PDER Required Sections

### 1. System Identification

Document identifier, system name, version under review, deployment date, reporting period (start and end dates), and the name of the evaluator or evaluation team.

### 2. Deployment Summary

Brief description of what was deployed: features delivered, known issues at go-live, deviations from the release plan, and the environment the system is running in (OS, database version, hosting platform). Cross-reference the Deployment Guide and Release Notes from `sdlc-user-deploy`.

### 3. Operational Health Metrics

These metrics are the quantitative core of the PDER. All metrics must be populated from actual operational data — no estimates.

**Change Requests per KLOC (first year)**
The primary quality indicator per Grubb & Takang (2003). Measures the rate at which defects and change requests are filed against the delivered code base.

$$CR_{rate} = \frac{\text{Total MRs/PRs filed}}{\text{KLOC delivered}}$$

Flag if $CR_{rate}$ exceeds the project's planned threshold. If no project threshold exists, use the Grubb & Takang industry median as a reference benchmark.

**Post-Operational Fault Count**
Total defects identified during the reporting period. Weight by severity:

$$Weighted\_Faults = \sum (Severity\_Weight_i \times Fault\_Count_i)$$

where $Severity\_Weight$ is defined in the project's STP (e.g., Critical=4, High=3, Medium=2, Low=1).

**MTTR Breakdown**
Mean Time to Repair, decomposed into the six administrative phases. Each phase must be measured separately to identify process bottlenecks.

| Phase | Description |
|-------|------------|
| Recognition | Time from fault occurrence to detection/reporting |
| Administrative | Time to assign, triage, and enter the MR/PR system |
| Tools | Time waiting for environment access, build, or deploy tools |
| Analysis | Time to diagnose root cause |
| Specification | Time to design and specify the fix |
| Change | Time to implement, test, and release the fix |

$$MTTR_{total} = T_{recognition} + T_{admin} + T_{tools} + T_{analysis} + T_{spec} + T_{change}$$

**System Availability**

$$Availability = \frac{Total\_Hours - Downtime\_Hours}{Total\_Hours} \times 100\%$$

Compare against the NFR-AVAIL target from the SRS.

**Schedule Variance**

$$SV = \frac{Planned\_Hours - Actual\_Hours}{Planned\_Hours} \times 100\%$$

A negative SV indicates overrun. Document root cause for any SV beyond ±10%.

### 4. Maintenance Type Mix — Actual vs. Planned

Record the count and percentage of MRs/PRs by maintenance type for the reporting period. Compare to the planned distribution from the SMP (or the Lientz/Swanson baseline if no SMP exists).

| Type | Planned % | Actual Count | Actual % | Variance |
|------|-----------|-------------|---------|---------|
| Corrective | 20% | — | — | — |
| Adaptive | 25% | — | — | — |
| Perfective | 50% | — | — | — |
| Preventive | 5% | — | — | — |
| Additive | 0% | — | — | — |

Significant variance from the planned mix (>10 percentage points for any type) must be explained and fed back into the next SMP revision.

### 5. User Satisfaction Assessment

Summarize user satisfaction data gathered from surveys, support tickets, or feedback sessions. **Caveat (mandatory):** User satisfaction is an insufficient quality indicator on its own. Users adapt to poor software over time (Grubb & Takang, 2003). Pair satisfaction data with the structural metrics in Section 3 before drawing conclusions. High satisfaction combined with high $CR_{rate}$ or poor MTTR indicates a quality risk, not a clean bill of health.

### 6. Documentation Currency Status

List each project document and its currency status: current, needs update, or out of date.

| Document | Status | Last Updated | Action Required |
|----------|--------|-------------|----------------|
| Software Requirements Specification | — | — | — |
| Software Design Document | — | — | — |
| Software Test Plan | — | — | — |
| Deployment Guide | — | — | — |
| User Manual | — | — | — |
| Software Maintenance Plan | — | — | — |

Documents marked "out of date" must be updated before the SMP maintenance cycle begins.

### 7. Lessons Learned

Structured findings from the deployment and first operational period. Each lesson must state: what happened, why it happened (root cause), and what should change. Lessons feed directly into SMP §9.1.8 (process improvements) and future project planning.

### 8. Recommended Actions for Next Period

Prioritized action list: immediate corrective actions, adaptive changes required (e.g., upcoming OS upgrade), perfective improvements requested, and preventive measures identified. Each action must have an owner and a target date.

### 9. Recommended Maintenance Type Budget for Next Period

Based on the actual type mix observed and the lessons learned, recommend the maintenance effort distribution for the next period. Express as person-months per type. This recommendation feeds directly into SMP §9.1.10 (maintenance cost estimates).

## Osborne's Post-Installation Review Gate

Osborne's Model (Grubb & Takang, 2003) defines a formal post-installation review as the explicit process gate that transitions a system from the delivery phase into the maintenance phase. The review is mandatory — a system that bypasses this gate has no validated baseline for maintenance planning.

**Trigger:** End of the 30–90 day initial operational period following go-live.
**Participants:** Maintenance Manager, a CCB representative, a user representative, and the project PM.
**Output:** The signed PDER, which formally opens the maintenance phase and authorizes the SMP to become operative.

## Quality Checklist

- [ ] PDER covers all five ISO 14764:2022 §6.4.13.2 mandatory outcomes (a through e)
- [ ] All metrics populated from actual operational data — no estimates or placeholders
- [ ] $CR_{rate}$ calculated and compared against project threshold or Grubb & Takang benchmark
- [ ] MTTR decomposed into all six phases (recognition, admin, tools, analysis, specification, change)
- [ ] System availability compared against NFR-AVAIL target from SRS
- [ ] Schedule variance calculated and root cause provided for any SV beyond ±10%
- [ ] Maintenance type mix table populated with actuals vs. planned
- [ ] Significant type mix variance (>10 pp) explained and flagged for SMP revision
- [ ] User satisfaction explicitly caveated: paired with structural metrics, not used alone
- [ ] Documentation currency status assessed for all six core documents
- [ ] Lessons learned include root cause for each finding (not just what happened)
- [ ] Recommended actions include owner and target date for each item
- [ ] Recommended budget for next period expressed as person-months per maintenance type
- [ ] Osborne's review gate formally triggered: signed PDER authorizes SMP to become operative
- [ ] `[OUTCOME-UNMET]` flags raised for any ISO 14764 outcome lacking evidence
- [ ] Findings map directly to owners, dates, and the next maintenance or delivery action

## Anti-Patterns

| Anti-Pattern | Why It Fails | Do This Instead |
|-------------|-------------|-----------------|
| Running PDER at day 7 post-launch | Insufficient operational data; metrics are noise, not signal | Wait 30–90 days for a statistically meaningful sample |
| Using user satisfaction as the only metric | Users adapt to poor software; satisfaction hides quality debt | Pair satisfaction with $CR_{rate}$, MTTR, and fault count |
| Reporting total MTTR without phase breakdown | Cannot identify whether the bottleneck is in analysis, tools, or process | Decompose MTTR into all six phases; target the dominant phase |
| Skipping Osborne's review gate | No formal transition from delivery to maintenance; SMP has no activation point | Schedule the review at day 30–90; sign the PDER to activate the SMP |
| Treating the PDER as a pass/fail report | Stakeholders receive a summary without actionable detail | Every finding must link to a recommended action with an owner and date |
| Not feeding PDER data back into the SMP | SMP cost estimates remain theoretical; next budget cycle repeats the same errors | Update SMP §9.1.10 using actual person-months from the PDER |

## Cross-References

### Upstream Skills (use BEFORE this skill)

| Skill | Relationship |
|-------|-------------|
| `sdlc-user-deploy` | Deployment Guide and Release Notes provide the deployment context for PDER Section 2. |
| `sdlc-testing` | Test Completion Report provides the pre-release quality baseline against which post-release metrics are compared. |

### Downstream Skills (use AFTER this skill)

| Skill | Relationship |
|-------|-------------|
| `sdlc-maintenance` | PDER is the primary input to the SMP. Cost actuals, type mix, and MTTR data seed SMP §9.1.10 estimates. PDER sign-off activates the SMP. |

### Sibling SDLC Skills

| Skill | Phase | Status |
|-------|-------|--------|
| `sdlc-planning` | Planning & Management | Available |
| `sdlc-design` | Design & Architecture | Available |
| `sdlc-testing` | Testing & Quality | Available |
| `sdlc-user-deploy` | Delivery & Deployment | Available |
| `sdlc-post-deployment` | Post-Deployment Evaluation | **This Skill** |
| `sdlc-maintenance` | Software Maintenance | Available |

---

**Back to:** [Skills Repository](../CLAUDE.md)
**Related:** [sdlc-maintenance](../sdlc-maintenance/SKILL.md) | [sdlc-testing](../sdlc-testing/SKILL.md) | [sdlc-user-deploy](../sdlc-user-deploy/SKILL.md)
**Last Updated:** 2026-03-15 (created per ISO/IEC/IEEE 14764:2022 Clause 6 + Grubb & Takang 2003)

## References

- [../sdlc-lifecycle.md](../sdlc-lifecycle.md): Shared SDLC execution model and lifecycle gates.
