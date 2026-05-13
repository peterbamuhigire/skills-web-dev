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

## Additional Guidance

Extended project-scaffold guidance was moved to [references/new-project-deep-dive.md](references/new-project-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `Scaffold Actions`
- `Quick Links`
- `What We Are Building`
- `Document Inventory by Phase`
- `Context Files (`_context/`)`
- `Progress Summary`
- `Immediate Next Steps`
- `Problem Statement`
- `Goals`
- `Stakeholders`
- `Success Criteria`
- `Feature Name`
- Additional deep-dive sections continue in the reference file.
