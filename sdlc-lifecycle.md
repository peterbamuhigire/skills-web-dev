# SDLC Lifecycle Overview

Master reference that ties together all 4 SDLC documentation phases and their supporting skills. Use this as a navigation guide to understand the complete documentation pipeline.

## The Complete SDLC Pipeline

```
PHASE 0: REQUIREMENTS GATHERING
    project-requirements -> requirements.md, business-rules.md,
                            user-types.md, workflows.md

PHASE 1: PLANNING & MANAGEMENT (7 Documents)
    sdlc-planning -> Feasibility Study, Vision & Scope, SRS,
                     SDP, SCMP, QA Plan, Risk Plan

PHASE 2: DESIGN & ARCHITECTURE (6 Documents)
    sdlc-design -> SDD, Tech Spec, Database Design,
                   ICD, API Documentation, Code Standards

PHASE 3: IMPLEMENTATION
    feature-planning / spec-architect -> Per-feature specs
                                         + implementation plans

PHASE 4: TESTING & QUALITY (5 Documents)
    sdlc-testing -> Test Plan, Test Cases, V&V Plan,
                    Test Report, Peer Reviews

PHASE 5: DELIVERY & DEPLOYMENT (6 Documents)
    sdlc-user-deploy -> User Manual, Ops Guide, Training,
                        Release Notes, Maintenance, README
```

**Total: 24 SDLC documents + 4 requirements files = 28 project documents**

## Phase Gate Checklist

Use this to verify readiness before moving to the next phase.

### Gate 0 to 1: Requirements to Planning

- [ ] All 4 requirements files exist and are reviewed
- [ ] Core feature list is prioritized (P0/P1/P2)
- [ ] User types and permissions are defined
- [ ] Key workflows are documented step-by-step

### Gate 1 to 2: Planning to Design

- [ ] Feasibility Study recommends Go
- [ ] Vision & Scope approved by stakeholders
- [ ] SRS has numbered requirement IDs (FR-xxx, NFR-xxx)
- [ ] SDP defines tech stack, phases, and team structure
- [ ] Risk Register populated with 8+ SaaS-specific risks

### Gate 2 to 3: Design to Implementation

- [ ] SDD establishes architecture with ASCII diagrams
- [ ] Database Design is complete with franchise_id strategy
- [ ] API Documentation covers all P0 endpoints
- [ ] Tech Spec provides implementation-level detail
- [ ] Code Standards are agreed upon by team

### Gate 3 to 4: Implementation to Testing

- [ ] Feature specs approved and implemented
- [ ] Code passes php -l syntax checks
- [ ] Unit tests written alongside implementation (TDD)
- [ ] Integration points verified

### Gate 4 to 5: Testing to Delivery

- [ ] Test Plan executed, results documented
- [ ] V&V Report shows acceptable pass rates
- [ ] Peer Reviews completed for critical modules
- [ ] Test Report includes Go/No-Go recommendation

## Skill Selection Guide

### Which skill do I use?

| I need to... | Use this skill |
|-------------|---------------|
| Interview stakeholders for requirements | project-requirements |
| Generate project-level planning docs (SRS, SDP, Feasibility) | sdlc-planning |
| Generate architecture and design docs (SDD, DB Design, API) | sdlc-design |
| Generate test documentation (Test Plan, Test Cases, V&V) | sdlc-testing |
| Generate user and deployment docs (Manual, Ops Guide, Training) | sdlc-user-deploy |
| Plan a single feature (spec + implementation) | feature-planning |
| Quick feature spec only (no implementation plan) | spec-architect |
| Plan an Android companion app (PRD, SDS, API Contract) | android-saas-planning |
| Generate AI guidance docs (AGENTS.md) | doc-architect |
| Write in-app PHP user manuals | manual-guide |
| Update project docs (README, CLAUDE.md) after changes | update-claude-documentation |

## Document Traceability Matrix

Shows how documents reference each other across phases.

| Document | Feeds Into | Traces Back To |
|----------|-----------|---------------|
| requirements.md | SRS, Vision & Scope | Stakeholder interviews |
| business-rules.md | SRS, Tech Spec, Test Cases | Domain expertise |
| Feasibility Study | Go/No-Go decision | All planning inputs |
| Vision & Scope | SDP, SDD, User Manual | Requirements |
| SRS | SDD, Test Plan, User Manual | Requirements |
| SDP | All downstream phases | Vision & Scope, SRS |
| SDD | Tech Spec, Test Cases | SRS, SDP |
| Database Design | Tech Spec, API Docs | SRS, SDD |
| API Documentation | Test Cases, ICD | SDD, Database Design |
| Test Plan | Test Cases, V&V Plan | SRS, SDD |
| Test Cases | Test Report | SRS requirement IDs |
| Test Report | Release decision | Test execution |
| User Manual | Training Materials | SRS, working software |
| Ops Guide | Maintenance Manual | SDD, SDP |
| Release Notes | Stakeholder communication | Test Report, changelog |

## Output Directory Map

```
docs/
  project-requirements/        # Phase 0: project-requirements
    requirements.md
    business-rules.md
    user-types.md
    workflows.md
  planning/                    # Phase 1: sdlc-planning
    01-feasibility-study.md
    02-project-vision-scope.md
    03-software-requirements-spec.md
    04-software-development-plan.md
    05-configuration-management-plan.md
    06-quality-assurance-plan.md
    07-risk-management-plan.md
  design/                      # Phase 2: sdlc-design
    01-system-design-document.md
    02-database-design-document.md
    03-technical-specification.md
    04-interface-control-document.md
    05-api-documentation.md
    06-code-documentation-standards.md
  testing/                     # Phase 4: sdlc-testing
    01-software-test-plan.md
    02-test-case-specifications.md
    03-validation-verification-plan.md
    04-validation-test-report.md
    05-peer-review-report.md
  user-deploy/                 # Phase 5: sdlc-user-deploy
    01-readme.md
    02-operations-deployment-manual.md
    03-software-user-manual.md
    04-training-materials.md
    05-maintenance-manual.md
    06-release-notes/
  plans/                       # Phase 3: feature-planning
    AGENTS.md
    INDEX.md
    specs/
```

## Android SaaS Projects: Extended Pipeline

For projects with an Android companion app, add these after Phase 1:

```
Phase 1 (sdlc-planning)
  |
Phase 1.5: Android Planning (android-saas-planning)
  - PRD, SRS, SDS, API Contract
  - User Journeys, Testing Strategy, Release Plan
  - Phase 1 Bootstrap: Login + Dashboard + Tabs
  |
Phase 2 (sdlc-design) -- includes mobile API design
```

## Supporting Skills (Always Active)

These skills provide cross-cutting standards referenced by all phases:

| Skill | Provides |
|-------|---------|
| vibe-security-skill | Security baseline for all web/API work |
| mysql-best-practices | Database standards for all DB-related docs |
| multi-tenant-saas-architecture | Tenant isolation patterns |
| dual-auth-rbac | Auth and permission model |
| php-modern-standards | PHP coding standards |
| orchestration-best-practices | Multi-step workflow patterns |
| doc-standards.md | 500-line limit, two-tier structure |

---

**Back to:** [Skills Repository](CLAUDE.md)
**Related:** sdlc-planning | sdlc-design | sdlc-testing | sdlc-user-deploy
**Last Updated:** 2026-02-20
