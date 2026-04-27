---
name: "new-project"
description: "Use when the task matches skill: new project scaffold and this skill's local workflow."
metadata:
  use_when: "Use when the task matches skill: new project scaffold and this skill's local workflow."
  do_not_use_when: "Do not use when a more specific upstream or downstream skill owns the task, or when the required project context has not been prepared."
  required_inputs: "Provide the target project or document, the relevant context files, scope constraints, and any domain or standards inputs referenced here."
  workflow: "Follow the ordered steps, review gates, and local generation logic in this file before consulting deeper support files as needed."
  quality_standards: "Keep outputs grounded in source context, traceable to stated standards, and specific enough to review or verify."
  anti_patterns: "Do not fabricate missing requirements, skip human review gates, or substitute vague prose for verifiable documentation."
  outputs: "Produce or update the document, scaffold, analysis, or phase artifact that this skill defines."
  references: "Use sibling files in this directory when deeper detail is needed."
---

# Skill: New Project Scaffold

## Trigger
User says any of: "start a new project", "create a new project",
"scaffold a project", "new client project", "initialize project"

## MANDATORY FIRST STEP
Before anything else, invoke `superpowers:brainstorming` to explore the project
intent, requirements, and design. Do NOT skip this step. Do NOT ask clarifying
questions before invoking brainstorming.

---

## How to Use the SRS-Skills Engine (PRIME Workflow)

Every skill in this engine follows the **PRIME methodology** (Kodukula & Vinueza, 2024):

| Step | What the Consultant Does | SRS-Skills Equivalent |
|------|--------------------------|----------------------|
| **P — Prepare** | Gather all project data before prompting | Populate `_context/` files with real stakeholder data, not placeholders |
| **R — Relay** | Submit the prompt with precise instructions | Invoke the SKILL.md (tell Claude: "Run the [skill name] skill") |
| **I — Inspect** | Critically evaluate AI output against objectives | Read the generated document; check it against `_context/` source files |
| **M — Modify** | Refine if output diverges from expectations | Edit the output or update `_context/` and re-invoke the skill |
| **E — Execute** | Approve and build the final artifact | Run `build-doc.sh` to produce the `.docx` |

> **Quality rule:** Never execute (build the `.docx`) without completing Inspect and Modify. The first AI output is a draft, not a deliverable.

The `_context/` directory is the **Project Input Folder (PIF)** for this project — a living repository of project-specific context that feeds every skill. The richer the PIF, the higher the quality of every generated document (Kodukula & Vinueza, 2024).

---

## Interview Protocol

After brainstorming, ask these questions ONE AT A TIME. Do not ask the next until
the previous is answered.

**Q1:** What is the project name? (This becomes the directory name — use hyphens,
e.g., `Livecare-Hospital-ERP`)

**Q2:** In 2–3 sentences, what does this software do and what problem does it solve?
(This pre-populates `_context/vision.md` and is used to deduce the domain)

**Q3:** Which methodology best fits this project?
- A) **Waterfall** — regulated industry, fixed scope, formal IEEE 830 SRS required
- B) **Agile** — iterative delivery, user stories, Scrum/Kanban
- C) **Hybrid** — formal SRS for backend/core + agile user stories for frontend/features

**Q4:** Who is the project owner / primary client contact name?

---

## Domain Deduction (NO USER INPUT REQUIRED)

After Q2, Claude analyses the project description and deduces the domain automatically
using these signals:

| If description mentions... | Deduce domain |
|---|---|
| patients, hospitals, clinics, EMR, EHR, PHI, medical, healthcare, pharmacy, nursing | `healthcare` |
| banking, payments, ledger, transactions, trading, insurance, loans, fintech, accounting | `finance` |
| students, courses, LMS, grades, enrollment, university, school, e-learning | `education` |
| inventory, POS, e-commerce, retail, products, orders, cart, warehouse (retail context) | `retail` |
| fleet, shipments, tracking, logistics, freight, warehouse (supply chain), delivery, routing | `logistics` |
| government, citizens, public services, procurement, permits, case management, municipal | `government` |
| farm, crops, livestock, agriculture, harvest, planting, irrigation, cattle, poultry, FMIS | `agriculture` |

**If ambiguous (two domains equally match):** Ask the user during the brainstorming
session — e.g., "This sounds like it could be healthcare OR government — which primary
domain applies?"

**If no domain matches:** Use `other` — no domain defaults are injected; scaffold
only the directory structure and empty context files.

---

## Scaffold Actions

After the interview, Claude performs these actions in order:

### 1. Create project root
`projects/<ProjectName>/`

Also create **`projects/<ProjectName>/export/`** — deliverable export folder:
- Create an empty `export/` directory with a `.gitkeep` file.
- Treat `export/`, `export-docs.ps1`, and `export-docs.sh` as required project-root paths for every project that generates Word deliverables.
- Create **`projects/<ProjectName>/export-docs.sh`** — bash export script:

```bash
#!/usr/bin/env bash
# export-docs.sh — Copy all .docx deliverables into this project's export/ folder.
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EXPORT_DIR="$SCRIPT_DIR/export"
mkdir -p "$EXPORT_DIR"
echo "Project   : $(basename "$SCRIPT_DIR")"
echo "Exporting : $EXPORT_DIR"
echo ""
count=0
while IFS= read -r -d '' f; do
    dest="$EXPORT_DIR/$(basename "$f")"
    if [ -f "$dest" ]; then
        base="${f%.*}"; ext="${f##*.}"; n=2
        while [ -f "$EXPORT_DIR/$(basename "$base")_${n}.${ext}" ]; do n=$((n+1)); done
        dest="$EXPORT_DIR/$(basename "$base")_${n}.${ext}"
    fi
    cp "$f" "$dest"
    echo "  + $(basename "$f")"
    count=$((count + 1))
done < <(find "$SCRIPT_DIR" -name "*.docx" -not -path "*/export/*" -print0 | sort -z)
echo ""
echo "Done — $count file(s) copied to export/"
```

- Create **`projects/<ProjectName>/export-docs.ps1`** — PowerShell export script:

```powershell
# export-docs.ps1 - Copy all .docx deliverables into this project's export folder.
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$ExportDir = Join-Path $ScriptDir "export"
New-Item -ItemType Directory -Force -Path $ExportDir | Out-Null
Write-Host "Project   : $(Split-Path -Leaf $ScriptDir)"
Write-Host "Exporting : $ExportDir"
Write-Host ""
$files = Get-ChildItem -Path $ScriptDir -Filter "*.docx" -Recurse `
    | Where-Object { $_.FullName -notlike "*\export\*" } | Sort-Object Name
$count = 0
foreach ($f in $files) {
    $dest = Join-Path $ExportDir $f.Name
    if (Test-Path $dest) {
        $base = [System.IO.Path]::GetFileNameWithoutExtension($f.Name)
        $ext = $f.Extension; $n = 2
        while (Test-Path (Join-Path $ExportDir "${base}_${n}${ext}")) { $n++ }
        $dest = Join-Path $ExportDir "${base}_${n}${ext}"
    }
    Copy-Item $f.FullName -Destination $dest
    Write-Host "  + $($f.Name)"
    $count++
}
Write-Host ""
Write-Host "Done - $count file(s) copied to export/"
```

Also create **`projects/<ProjectName>/README.md`** — project README:
```markdown
# <ProjectName>

**Status:** In Progress
**Owner:** <owner>
**Domain:** <domain>
**Methodology:** <methodology>
**Started:** <date>

## Quick Links

- `DOCUMENTATION-STATUS.md` — Full document inventory, generation status, and progress summary
- `_context/vision.md` — Project vision and scope
- `_context/stakeholders.md` — Stakeholder register
- `_context/glossary.md` — Project terminology
- `export/` — Flat copy of all built `.docx` deliverables (run `export-docs.sh` or `export-docs.ps1`)
```

Also create **`projects/<ProjectName>/DOCUMENTATION-STATUS.md`** — documentation status tracker:
```markdown
# Documentation Status — <ProjectName>

**Project:** <ProjectName>
**Owner:** <owner>
**Domain:** <domain>
**Last Updated:** <date>
**Total Documents:** 0

---

## What We Are Building

<Q2 answer — project description>

**Tech stack:** <!-- TODO: specify after populating _context/tech_stack.md -->
**Methodology:** <methodology>

---

## Document Inventory by Phase

### Phase 01 — Strategic Vision 🔲 Not Started

| Document | Sections | `.docx` Built | Status |
|---|---|---|---|
| Product Requirements Document (PRD) | `01-prd/` | — | 🔲 Not started |
| Vision Statement | `02-vision-statement/` | — | 🔲 Not started |
| Business Case | `03-business-case/` | — | 🔲 Not started |

### Phase 02 — Requirements Engineering 🔲 Not Started

| Document | Sections | `.docx` Built | Status |
|---|---|---|---|
| Software Requirements Specification (SRS) | `01-srs/` | — | 🔲 Not started |
| User Stories | `02-user-stories/` | — | 🔲 Not started |
| Stakeholder Analysis | `03-stakeholder-analysis/` | — | 🔲 Not started |

### Phase 03 — Design Documentation 🔲 Not Started

| Document | Files | `.docx` Built | Status |
|---|---|---|---|
| High-Level Design | `01-hld/` | — | 🔲 Not started |
| Low-Level Design | `02-lld/` | — | 🔲 Not started |
| API Specification | `03-api-spec/` | — | 🔲 Not started |
| Database Design | `04-database-design/` | — | 🔲 Not started |
| UX Specification | `05-ux-spec/` | — | 🔲 Not started |

### Phase 04 — Development Artifacts 🔲 Not Started

| Document | Files | `.docx` Built | Status |
|---|---|---|---|
| Technical Specification | `01-technical-spec/` | — | 🔲 Not started |
| Coding Guidelines | `02-coding-guidelines/` | — | 🔲 Not started |

### Phase 05 — Testing Documentation 🔲 Not Started

| Document | Files | Status |
|---|---|---|
| Test Strategy | `01-test-strategy/` | 🔲 Not started |
| Test Plan | `02-test-plan/` | 🔲 Not started |
| Test Report | `03-test-report/` | 🔲 Not started |

### Phase 06 — Deployment Operations 🔲 Not Started

| Document | Files | Status |
|---|---|---|
| Deployment Guide | `01-deployment-guide/` | 🔲 Not started |
| Runbook | `02-runbook/` | 🔲 Not started |

### Phase 07 — Agile Artifacts 🔲 Not Started

| Document | Files | Status |
|---|---|---|
| Sprint Planning | `01-sprint-planning/` | 🔲 Not started |
| Definition of Done | `02-dod/` | 🔲 Not started |
| Definition of Ready | `03-dor/` | 🔲 Not started |

### Phase 08 — End User Documentation 🔲 Not Started

| Document | Files | Status |
|---|---|---|
| User Manual | `01-user-manual/` | 🔲 Not started |
| Installation Guide | `02-installation-guide/` | 🔲 Not started |
| FAQ | `03-faq/` | 🔲 Not started |

### Phase 09 — Governance Compliance 🔲 Not Started

| Document | Files | Status |
|---|---|---|
| Traceability Matrix | `01-traceability-matrix/` | 🔲 Not started |
| Audit Report | `02-audit-report/` | 🔲 Not started |
| Compliance | `03-compliance/` | 🔲 Not started |
| Risk Assessment | `04-risk-assessment/` | 🔲 Not started |

---

## Context Files (`_context/`)

| File | Status |
|---|---|
| `vision.md` | ✅ Populated |
| `domain.md` | ✅ Populated |
| `features.md` | 🔲 TODO |
| `tech_stack.md` | 🔲 TODO |
| `business_rules.md` | 🔲 TODO |
| `quality_standards.md` | 🔲 TODO |
| `glossary.md` | 🔲 TODO |
| `stakeholders.md` | 🔲 TODO |
| `personas.md` | 🔲 TODO |
| `quality-log.md` | ✅ Initialized |
| `metrics.md` | 🔲 TODO |

---

## Progress Summary

| Phase | Documents | Complete | In Progress | Not Started |
|---|---|---|---|---|
| 01 — Strategic Vision | 3 | 0 | 0 | 3 |
| 02 — Requirements Engineering | 3 | 0 | 0 | 3 |
| 03 — Design Documentation | 5 | 0 | 0 | 5 |
| 04 — Development Artifacts | 2 | 0 | 0 | 2 |
| 05 — Testing Documentation | 3 | 0 | 0 | 3 |
| 06 — Deployment Operations | 2 | 0 | 0 | 2 |
| 07 — Agile Artifacts | 3 | 0 | 0 | 3 |
| 08 — End User Documentation | 3 | 0 | 0 | 3 |
| 09 — Governance Compliance | 4 | 0 | 0 | 4 |
| **Total** | **28** | **0** | **0** | **28** |

**Overall document completion: 0 of 28 documents (0%).**

---

## Immediate Next Steps

1. Fill in `_context/` files with real project data
2. Generate Phase 01 documents: PRD, Vision Statement, Business Case
3. Generate Phase 02 documents: SRS and/or User Stories
```

Update this file each time a document is written or built. Use the status
indicators: ✅ Complete, 🔶 Partially Complete, 🔲 Not Started.

### 2. Create `_context/` files

**`_context/vision.md`** — pre-populate with Q2 answer:
```markdown
# Project Vision

**Project:** <ProjectName>
**Client Contact:** <Q4 answer>
**Date:** <today's date>

## Problem Statement
<Q2 answer>

## Goals
<!-- TODO: List 3–5 measurable project goals -->

## Stakeholders
<!-- TODO: List stakeholder roles and their primary needs -->

## Success Criteria
<!-- TODO: Define how project success will be measured -->
```

**`_context/features.md`** — stub with guidance:
```markdown
# Feature List

<!-- TODO: List all features with a brief description each.
Format:
## Feature Name
Brief description of what this feature does and the business value it delivers.
-->
```

**`_context/tech_stack.md`**:
```markdown
# Technology Stack

<!-- TODO: Specify the technologies, frameworks, and infrastructure.
Example:
- Backend: PHP 8.2 / Laravel 10
- Frontend: React 18 / TypeScript
- Database: MySQL 8.0
- Infrastructure: AWS EC2, S3, RDS
-->
```

**`_context/business_rules.md`**:
```markdown
# Business Rules

<!-- TODO: Define the domain-specific rules and constraints.
Example:
- A patient cannot have more than one active appointment per time slot
- Invoices cannot be deleted after 30 days
-->
```

**`_context/quality_standards.md`**:
```markdown
# Quality Standards

<!-- TODO: Define measurable quality targets.
Example:
- Response time: 95th percentile < 500ms under 1,000 concurrent users
- Uptime: 99.9% monthly
- Security: OWASP Top 10 compliance
-->
```

**`_context/glossary.md`**:
```markdown
# Glossary

<!-- TODO: Define project-specific terms using IEEE 610.12-1990 format.
Format:
**Term:** Definition
-->
```

**`_context/stakeholders.md`**:
```markdown
# Stakeholders

<!-- TODO: List all stakeholder groups. Required by Phase 01 skills (Vision Statement, PRD, Business Case).
Format:
## Role Title
- **Influence:** High / Medium / Low
- **Interest:** High / Medium / Low
- **Primary Needs:** What this stakeholder needs from the system
- **Key Concerns:** Risks or constraints they care about
- **Communication Preference:** How and how often to communicate
-->
```

**`_context/personas.md`**:
```markdown
# User Personas

<!-- TODO: Define user personas for the system. Required by Phase 02 Agile user story generation.
Format:
## Persona Name (Role)
- **Age / Background:** Brief demographic context
- **Goals:** What they are trying to accomplish
- **Pain Points:** Current frustrations this system should solve
- **Tech Comfort:** Low / Medium / High
- **Typical Workflow:** Step-by-step description of how they currently do the task
-->
```

**`_context/quality-log.md`** — quality tracking log:
```markdown
# Quality Log

| Date | Skill | Issue Found | Resolution | Resolved By |
|------|-------|-------------|------------|-------------|
| <today's date> | — | Project initialized: <ProjectName> | — | — |
```

Pre-populate the first row with today's date and the project name. The QA engineer updates this log throughout the project lifecycle, recording every `[V&V-FAIL]`, `[CONTEXT-GAP]`, and `[GLOSSARY-GAP]` discovered during skill execution.

**`_context/metrics.md`** — project metrics dashboard:
```markdown
# Project Metrics

## Earned Value Metrics

| Metric | Planned | Actual | Variance |
|--------|---------|--------|----------|
| PV (Planned Value) | | | |
| EV (Earned Value) | | | |
| AC (Actual Cost) | | | |

## KPIs

| KPI | Target | Current | Status |
|-----|--------|---------|--------|

## Phase Gate Criteria

| Gate | Status | Date | Notes |
|------|--------|------|-------|
| Stakeholder Vision | Pending | | |
| Proven Architecture | Pending | | |
| Sufficient Functionality | Pending | | |
| Production Ready | Pending | | |
```

**`_context/domain.md`** — copy content from `domains/<deduced-domain>/INDEX.md`
and prepend:
```markdown
# Domain Profile: <DomainName>
> Auto-populated from domains/<domain>/INDEX.md at scaffold time.
> Domain deduced from project description. Review and remove sections not applicable.
```

If domain is `other`, create:
```markdown
# Domain Profile: Other / Custom
> No standard domain matched. Define domain-specific requirements manually.
```

### 3. Create Phase Directories

Create all 9 phase directories with document subdirectories based on methodology:

**Waterfall methodology** — create all document dirs across all phases.
**Agile methodology** — skip `01-srs/` in Phase 02; create `02-user-stories/` instead.
**Hybrid** — create both `01-srs/` and `02-user-stories/` in Phase 02.

Phase directory → document subdirectories mapping:

```
01-strategic-vision/         → 01-prd/, 02-vision-statement/, 03-business-case/
02-requirements-engineering/ → 01-srs/ and/or 02-user-stories/, 03-stakeholder-analysis/
03-design-documentation/     → 01-hld/, 02-lld/, 03-api-spec/, 04-database-design/, 05-ux-spec/
04-development-artifacts/    → 01-technical-spec/, 02-coding-guidelines/
05-testing-documentation/    → 01-test-strategy/, 02-test-plan/, 03-test-report/
06-deployment-operations/    → 01-deployment-guide/, 02-runbook/
07-agile-artifacts/          → 01-sprint-planning/, 02-dod/, 03-dor/
08-end-user-documentation/   → 01-user-manual/, 02-installation-guide/, 03-faq/
09-governance-compliance/    → 01-traceability-matrix/, 02-audit-report/, 03-compliance/, 04-risk-assessment/
```

### 3b. Create `manifest.md` Stubs

For each document subdirectory created above, also create a `manifest.md` file with this template:

```markdown
# Document Manifest
# List section files in assembly order, one per line.
# Lines starting with # are comments and are excluded from the build.
# If this file is absent, build-doc.sh sorts *.md files alphabetically.
#
# Example:
# 01-introduction.md
# 02-scope.md
# 03-requirements.md
```

This file is empty by default. Claude will populate it with the correct section order when generating sections for this document.

### 3c. Hybrid Branch (when methodology = hybrid)

When the Q3 methodology answer is `Hybrid` (or the hybrid-detection heuristic in `CLAUDE.md` confirms a Water-Scrum-Fall pattern), perform these additional scaffold steps after the standard phase directories are created:

1. **Create `projects/<ProjectName>/_registry/`** and seed `_registry/baseline-trace.yaml` with an empty but schema-valid skeleton:

   ```yaml
   # Populated by `python -m engine sync <project>` and the hybrid-synchronization skill.
   baseline: []
   stories: []
   ```

2. **Create `projects/<ProjectName>/_context/methodology.md`** with hybrid frontmatter and a change-control-body TODO:

   ```markdown
   ---
   methodology: hybrid
   change_control_body: <!-- TODO: name the body that approves baseline changes (e.g., Steering Committee) -->
   sprint_length_weeks: <!-- TODO: sprint cadence in weeks, typically 2 -->
   baseline_signed_off_on: <!-- TODO: YYYY-MM-DD -->
   ---

   # Methodology — Hybrid (Water-Scrum-Fall)

   This project uses a Waterfall baseline executed through Agile sprints. The
   baseline is locked under change control; sprint stories must trace to
   baseline IDs recorded in `_registry/baseline-trace.yaml`.

   <!-- TODO: document baseline lock, flexible features, and sprint cadence
   once the hybrid-synchronization skill has run. -->
   ```

3. **Create `projects/<ProjectName>/07-agile-artifacts/definitions/`** as an empty directory. The `hybrid-synchronization` skill writes `dor-dod.md` into it after Phase 02 sign-off.

After Phase 02 Waterfall SRS is signed off, invoke the `hybrid-synchronization` skill to populate the three hybrid artifacts and satisfy the kernel's `HybridSyncGate`.

### 4. Inject Domain Defaults

If domain is not `other`:
- Read `domains/<domain>/references/nfr-defaults.md`
- Copy all `[DOMAIN-DEFAULT]` blocks into:
  - `02-requirements-engineering/01-srs/06-nfr.md` (waterfall/hybrid)
  - `02-requirements-engineering/02-user-stories/01-epics.md` (agile/hybrid — as tagged notes)

### 4b. Seed Project Control Selection (`_registry/controls.yaml`)

If domain is not `other`:

1. Ensure `projects/<ProjectName>/_registry/` exists.
2. Copy `00-meta-initialization/new-project/templates/controls.yaml.template` to `projects/<ProjectName>/_registry/controls.yaml`.
3. Prompt the consultant to open `domains/<domain>/controls/control-register.yaml` and select the applicable controls. The consultant edits `_registry/controls.yaml` by appending each chosen control as an entry under `selected:` with the control `id`, a free-text `applies_because` justification (minimum 5 characters), and optional `owner` and `exemption` fields.
4. The project-controls file is validated against `engine/registry/schemas/project-controls.schema.json` and consumed by `Phase09Gate`'s `ControlsCheck` and `ObligationsCheck`.

### 5. Print Scaffold Summary

```
Project scaffolded: projects/<ProjectName>/

Domain deduced: <domain> (from project description)

_context/ status:
  ✓ vision.md            — pre-populated from interview
  ✓ domain.md            — <domain> baseline injected
  ○ features.md          — TODO: add feature list
  ○ tech_stack.md        — TODO: specify technologies
  ○ business_rules.md    — TODO: define business rules
  ○ quality_standards.md — TODO: set quality targets
  ○ glossary.md          — TODO: add project terminology
  ○ stakeholders.md     — TODO: add stakeholder register (required by Phase 01)
  ○ personas.md         — TODO: define user personas (required by Phase 02 Agile)
  ✓ quality-log.md      — initialized with project entry
  ○ metrics.md          — TODO: set EVM baselines and KPI targets

Root files:
  ✓ README.md                — pre-populated with project metadata
  ✓ DOCUMENTATION-STATUS.md  — document inventory and generation tracker

Domain defaults injected: <N> [DOMAIN-DEFAULT] requirements
  → 02-requirements-engineering/01-srs/06-nfr.md

Next step: Fill in _context/ files, then say:
  "generate PRD for <ProjectName>"
  "generate SRS for <ProjectName>"
```

---

## Build Document Protocol

When user says "build the [document]" (e.g., "build the SRS", "build the PRD"):

1. Resolve the document directory from the document name using the table below
2. Check for `manifest.md` — if present use it; otherwise sort `*.md` by filename
3. Run: `bash scripts/build-doc.sh <doc-dir> <OutputName>`
4. Report the output path to the user

### Document Name → Directory Mapping

| User says | Directory | Output filename |
|---|---|---|
| "build the PRD" | `01-strategic-vision/01-prd/` | `PRD.docx` |
| "build the vision statement" | `01-strategic-vision/02-vision-statement/` | `VisionStatement.docx` |
| "build the business case" | `01-strategic-vision/03-business-case/` | `BusinessCase.docx` |
| "build the SRS" | `02-requirements-engineering/01-srs/` | `SRS_Draft.docx` |
| "build the user stories" | `02-requirements-engineering/02-user-stories/` | `UserStories.docx` |
| "build the HLD" | `03-design-documentation/01-hld/` | `HLD.docx` |
| "build the LLD" | `03-design-documentation/02-lld/` | `LLD.docx` |
| "build the API spec" | `03-design-documentation/03-api-spec/` | `APISpec.docx` |
| "build the database design" | `03-design-documentation/04-database-design/` | `DatabaseDesign.docx` |
| "build the test plan" | `05-testing-documentation/02-test-plan/` | `TestPlan.docx` |
| "build the deployment guide" | `06-deployment-operations/01-deployment-guide/` | `DeploymentGuide.docx` |
| "build the user manual" | `08-end-user-documentation/01-user-manual/` | `UserManual.docx` |
| "build the risk assessment" | `09-governance-compliance/04-risk-assessment/` | `RiskAssessment.docx` |
| "build the traceability matrix" | `09-governance-compliance/01-traceability-matrix/` | `TraceabilityMatrix.docx` |
