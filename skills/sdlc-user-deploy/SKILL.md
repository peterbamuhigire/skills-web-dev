---
name: sdlc-user-deploy
description: Generate User & Deployment documentation for SDLC projects. Covers Software
  User Manual (SUM), Operations/Deployment Manual, Training Materials, Release Notes,
  Maintenance Manual, and README File. Use when preparing software for end-users,
  system...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

## Platform Notes

- Optional helper plugins may help in some environments, but they must not be treated as required for this skill.

# SDLC User & Deployment Skill
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Generate User & Deployment documentation for SDLC projects. Covers Software User Manual (SUM), Operations/Deployment Manual, Training Materials, Release Notes, Maintenance Manual, and README File. Use when preparing software for end-users, system...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `sdlc-user-deploy` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve; load `templates` only as needed.
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
| Release evidence | User and Deployment documentation | Markdown docs covering Software User Manual (SUM) and Operations/Deployment Manual | `docs/sdlc/user-deploy-2026-04-16.md` |

## References

- Use the `templates/` directory when the task needs a structured deliverable.
<!-- dual-compat-end -->
Generate a complete **User & Deployment** documentation suite for software development projects. This skill produces 6 documents that guide end-users, system administrators, and operations teams through using, deploying, and maintaining the software.

## Load Order

1. Load `world-class-engineering`.
2. Load `deployment-release-engineering` and `observability-monitoring`.
3. Load this skill to turn a tested system into a deployable and operable product.

## Executable Delivery Standard

Delivery documents must define:

- rollout and rollback procedure
- release evidence and post-deploy watch list
- operator ownership and runbook entry points
- user-facing changes, known limitations, and recovery guidance

## When to Use

- Preparing a SaaS product for **production deployment** and user onboarding
- Creating **end-user documentation** for franchise owners, staff, and members
- Writing **deployment and operations guides** for system administrators
- Developing **training programs** for new user onboarding
- Documenting **release notes** for version management and stakeholder communication
- Establishing **maintenance procedures** for ongoing system health
- Creating a **project README** for developer onboarding and project discovery

## When NOT to Use

- **Gathering raw requirements** -- use `project-requirements` skill
- **Project-level planning** (SDP, QA Plan, Risk Plan) -- use `sdlc-planning` skill
- **Designing architecture** (SDD, database design, API docs) -- use `sdlc-design` skill
- **Writing test plans and test cases** -- use `sdlc-testing` skill
- **Writing ERP module-specific manuals** with in-app PHP delivery -- use `manual-guide` skill
- **Planning a single feature** -- use `feature-planning` skill
- **Bootstrapping a new SaaS project** -- use `saas-seeder` skill
- **Updating project docs** (CLAUDE.md, README) after code changes -- use `update-claude-documentation`

## Document Inventory

| # | Document | File | Purpose | Audience | Phase |
|---|----------|------|---------|----------|-------|
| 1 | Software User Manual | `templates/software-user-manual.md` | End-user guide for using the software | End users, staff, franchise owners | Pre-launch |
| 2 | Operations / Deployment Manual | `templates/operations-deployment-manual.md` | Deploy, configure, and manage in production | SysAdmins, DevOps, IT ops | Pre-launch |
| 3 | Training Materials | `templates/training-materials.md` | Onboarding, tutorials, assessments | New users, trainers, HR | Pre-launch |
| 4 | Release Notes | `templates/release-notes.md` | Communicate changes per version | All stakeholders | Each release |
| 5 | Maintenance Manual | `templates/maintenance-manual.md` | Ongoing maintenance and troubleshooting | Support engineers, on-call, DevOps | Post-launch |
| 6 | README File | `templates/readme-file.md` | Project introduction for developers | Developers, contributors, evaluators | Project start |

## Audience Segmentation

| Audience | Role Examples | Documents |
|----------|---------------|-----------|
| End Users | Franchise owners, staff, members, customers | User Manual, Training Materials |
| System Administrators | DevOps, IT ops, hosting team | Operations Manual, Maintenance Manual |
| Developers / Technical Team | Backend devs, mobile devs, contributors | README, Release Notes |
| Stakeholders / Management | Investors, product owners, project managers | Release Notes (simplified view) |

## Generation Workflow

Generate documents in this order. Each builds on the previous.

```
Prerequisite: SRS (sdlc-planning) + SDD (sdlc-design) + Test Reports (sdlc-testing)
    |
Step 1: README File (project baseline, developer onboarding)
    |
Step 2: Operations / Deployment Manual (how to set up and run)
    |
Step 3: Software User Manual (how to use the software)
    |
Step 4: Training Materials (how to teach users)
    |
Step 5: Maintenance Manual (how to keep it running)
    |
Step 6: Release Notes (per-version communication — ongoing)
```

**Rationale:** README establishes the project context. Operations manual documents deployment before users arrive. User manual describes the working system. Training materials build on the user manual. Maintenance manual handles post-launch operations. Release notes are ongoing with each version.

### Prerequisites

| Input | Source | Required? |
|-------|--------|-----------|
| Software Requirements Spec (SRS) | `sdlc-planning` output | Yes |
| System Design Document (SDD) | `sdlc-design` output | Recommended |
| Validation Test Report | `sdlc-testing` output | Recommended |
| Working software (deployed to staging) | Development team | Yes (for user manual) |
| Deployment environment details | Infrastructure team | Yes (for ops manual) |
| Module/feature inventory | SRS or SDD | Yes |

## Cross-References to Existing Skills

### Upstream Skills (use BEFORE this skill)

| Skill | Relationship |
|-------|-------------|
| `sdlc-planning` | Provides SRS (feature inventory, user roles), Vision & Scope (project context). |
| `sdlc-design` | Provides SDD (architecture for ops manual), API docs (for README), database design. |
| `sdlc-testing` | Provides test reports (release readiness), test results (known issues for release notes). |
| `project-requirements` | Raw requirements and user workflows inform user manual content. |

### Parallel Skills (use ALONGSIDE this skill)

| Skill | Relationship |
|-------|-------------|
| `manual-guide` | ERP module-specific manuals with in-app PHP delivery. This skill provides the SDLC-standard structure; `manual-guide` provides the interactive web-based manual system. |
| `google-play-store-review` | Play Store compliance. Reference in operations manual for Android deployment. |
| `report-print-pdf` | PDF/print export patterns. Reference in user manual for report features. |
| `vibe-security-skill` | Security baseline. Reference in operations and maintenance manuals. |

### Downstream Skills (use AFTER this skill)

| Skill | Relationship |
|-------|-------------|
| `update-claude-documentation` | Keeps project docs (README, CLAUDE.md) updated after changes. |
| `saas-seeder` | Uses operations manual patterns when bootstrapping new SaaS instances. |

### Sibling SDLC Skills

| Skill | Phase | Status |
|-------|-------|--------|
| `sdlc-planning` | Planning & Management | Available |
| `sdlc-design` | Design & Architecture | Available |
| `sdlc-testing` | Testing & Quality | Available |
| `sdlc-user-deploy` | Delivery & Deployment | **This Skill** |

## Writing Style Guidelines

### Audience Classification (Apply to Every Document)

Tag every document with its primary audience: `End User`, `Administrator`, or `Developer`. This governs vocabulary, sentence complexity, assumed knowledge, and formatting choices.

### Three-Emphasis Rule (Universal)

Apply consistently across all documents:
- `**Bold**` — UI element names and field labels: "Click **Save**."
- `*Italic*` — critical warnings and normative emphasis: "*You must back up before running this command.*"
- `` `Monospace` `` — file paths, terminal commands, environment variable names, code: run `./deploy.sh`.
- Always use asterisks (`**bold**`, `*italic*`), never underscores.

### End-User Documents (User Manual, Training Materials)

- **Plain language** -- no jargon, no acronyms without definition
- **Active voice, present tense** -- "Click Save" not "The Save button should be clicked"
- **Ordered lists mandatory for procedures** -- every sequential task must be a numbered list (`1.`, `2.`, `3.`), never prose paragraphs
- **BFD Framework** — every user-facing document must answer in order: (1) What is this and who needs it? (2) How does it fit into the user's environment? (3) Where and how is it obtained/installed? (4) What does a minimal end-to-end task look like (quick start)? (5) Where is the full feature reference?
- **Screenshot placeholders** -- format: `[Screenshot: {description} -- {screen-name}.png]`
- **Bold for UI elements** -- **Save**, **Dashboard**, **Reports** tab
- **Task-oriented** -- organize by what users want to do, not by features

### Admin Documents (Operations Manual, Maintenance Manual)

- **Technical but clear** -- assume Linux/server knowledge, explain project-specific details
- **Command examples** -- every command in a fenced code block with language identifier (` ```bash `, ` ```yaml `, ` ```sql `); include expected output
- **Ordered lists mandatory** -- deployment steps, installation steps, rollback procedures must all be numbered lists
- **Troubleshooting trees** -- symptom to cause to solution
- **Checklists** -- pre-deployment, post-deployment, routine maintenance
- **Runbook-first for SaaS** -- internal operations runbooks are a prerequisite for production deployment; do not deploy without them

### Developer Documents (README, Release Notes)

- **Concise** -- developers scan, they do not read prose
- **Code-focused** -- commands, configuration snippets, architecture diagrams
- **Architecture-aware** -- explain the "why" behind design decisions
- **Copy-pasteable** -- every command should work when pasted
- **Release notes: factual, never marketing** -- state what changed, what was added, what was removed, and what breaks backward compatibility. Never use "powerful," "seamless," "intuitive," or editorial language.

### Documentation as Definition of Done

A feature is not complete until its documentation is published. Documentation deliverables must be included in every sprint's acceptance criteria. Technical writers should participate from sprint planning, not after feature complete.

## Multi-Tenant Considerations

- User manuals may need **tenant-specific branding** (logo, product name, colors)
- Training materials should use **generic tenant examples** (Tenant A, Tenant B)
- Operations manual must cover **tenant creation, suspension, and data isolation**
- Release notes go to **all tenants** -- avoid tenant-specific references
- Maintenance manual must include **cross-tenant data leakage** as a P1 incident

## Localization Considerations

- **Primary language:** English
- **Secondary languages:** Swahili (East Africa), French (West Africa)
- Use **simple sentence structures** that translate well
- Avoid idioms, cultural references, and humor
- Use **ISO date format** (YYYY-MM-DD) throughout
- Number formatting: consider local conventions (1,000.00 vs 1.000,00)
- **Screenshot text:** plan for screenshots in each language or use annotated callouts

## Output Structure

When generating documents for a project, create this structure:

```
docs/user-deploy/
├── 01-readme.md
├── 02-operations-deployment-manual.md
├── 02-operations/
│   ├── installation-guide.md
│   ├── configuration-reference.md
│   └── backup-recovery.md
├── 03-software-user-manual.md
├── 03-user-manual/
│   ├── getting-started.md
│   ├── module-guides.md
│   └── troubleshooting.md
├── 04-training-materials.md
├── 04-training/
│   ├── quick-start-guides.md
│   ├── tutorial-modules.md
│   └── assessments.md
├── 05-maintenance-manual.md
├── 05-maintenance/
│   ├── troubleshooting-guide.md
│   ├── runbooks.md
│   └── incident-management.md
└── 06-release-notes/
    ├── v1.0.0.md
    ├── v1.1.0.md
    └── changelog.md
```

Each file must stay under 500 lines. Split into subdirectories as needed.

## Quality Checklist

- [ ] All 6 documents generated (or justified why one was skipped)
- [ ] Each document stays under 500 lines (split if needed)
- [ ] User Manual answers the BFD five questions in order (What → How fits environment → Where obtained → Quick start → Full reference)
- [ ] User Manual covers all modules listed in SRS with step-by-step workflows in ordered lists
- [ ] Three-emphasis rule applied: bold for UI elements, italic for warnings, monospace for commands/paths
- [ ] Operations Manual covers all 3 environments (Windows dev, Ubuntu staging, Debian prod)
- [ ] All commands in admin docs use fenced code blocks with language identifiers
- [ ] Operations runbooks complete before any production deployment (runbook-first for SaaS)
- [ ] Training Materials include role-specific quick starts and hands-on exercises
- [ ] Release Notes follow semantic versioning; no marketing language; factual only
- [ ] Maintenance Manual includes runbooks for top 10 operational tasks
- [ ] README includes working installation steps and project structure
- [ ] Screenshot placeholders use consistent format throughout user-facing docs
- [ ] Multi-tenant operations documented (tenant creation, isolation, suspension)
- [ ] Android deployment covered (Play Store, staged rollout, in-app updates)
- [ ] Cross-references to other skills are accurate and bidirectional
- [ ] No jargon in end-user docs; no vague language in admin docs
- [ ] All commands are copy-pasteable with expected output documented
- [ ] Documents cross-reference each other and upstream SRS/SDD
- [ ] Documentation deliverables included in sprint Definition of Done
- [ ] Release notes and operations docs identify rollback trigger points and observation owners

## Anti-Patterns (What NOT to Do)

| Anti-Pattern | Why It Fails | Do This Instead |
|-------------|-------------|-----------------|
| Skip user manual, ship anyway | Users flood support with basic questions | Write user manual before launch |
| No deployment documentation | Only one person knows how to deploy | Document every deployment step |
| Training = reading the manual | Adults learn by doing, not reading | Include hands-on exercises and labs |
| Vague release notes ("various fixes") | Users do not know what changed or why | State exactly what changed, added, removed, and any migration steps |
| Marketing language in release notes | Readers must parse sales pitch to find facts | Never use "powerful," "seamless," "intuitive" — write factually |
| No maintenance runbooks | Tribal knowledge; outages last longer | Write step-by-step runbooks |
| README with no setup instructions | New developers cannot get started | Include complete dev setup guide |
| One-size-fits-all training | Admins and end-users have different needs | Role-specific training paths |
| Outdated screenshots in manual | Users lose trust in documentation | Update screenshots with each release |
| No rollback procedures | Failed deployments become crises | Document rollback for every deployment |
| Docs written after feature complete | Documentation quality suffers; docs launch late | Include docs in sprint DoD; write alongside development |
| Procedures not QA-tested | Steps may not actually work as written | Have a QA engineer or unfamiliar person execute each procedure from scratch before publishing |

## Template Files

Each template provides the complete structure, section-by-section guidance, example excerpts, anti-patterns, and a quality checklist.

1. [Software User Manual](templates/software-user-manual.md)
2. [Operations / Deployment Manual](templates/operations-deployment-manual.md)
3. [Training Materials](templates/training-materials.md)
4. [Release Notes](templates/release-notes.md)
5. [Maintenance Manual](templates/maintenance-manual.md)
6. [README File](templates/readme-file.md)

## References

- [../sdlc-lifecycle.md](../sdlc-lifecycle.md): Shared SDLC execution model and lifecycle gates.

---

**Back to:** [Skills Repository](../CLAUDE.md)
**Related:** [sdlc-planning](../sdlc-planning/SKILL.md) | [sdlc-design](../sdlc-design/SKILL.md) | [sdlc-testing](../sdlc-testing/SKILL.md) | [manual-guide](../manual-guide/SKILL.md) | [google-play-store-review](../google-play-store-review/SKILL.md)
**Last Updated:** 2026-03-15 (strengthened per Etter 2016, Cone 2023, Splunk Product is Docs)