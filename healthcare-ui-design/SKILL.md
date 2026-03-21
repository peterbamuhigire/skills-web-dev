---
name: healthcare-ui-design
description: Design clinical and patient-facing healthcare web UIs that prioritize safety, clarity, and regulatory compliance while integrating all backend actions strictly through APIs.
---

# Healthcare UI Design Skill

## Overview

Design healthcare user interfaces for clinical workflows, patient portals, and medical record systems. Prioritize patient safety, regulatory compliance (HIPAA, FDA 21 CFR Part 11), and clarity under high-stress conditions. Ensure all backend activity is API-driven.

## When to Use

- Designing clinical dashboards, patient intake forms, or electronic health record (EHR) screens.
- Creating patient-facing portals for appointment scheduling, lab results, or medication management.
- Reviewing existing healthcare UIs for compliance, accessibility, and usability.
- Defining API-first UI workflows for clinical data entry and retrieval.

## Quick Reference

| Attribute   | Value |
|-------------|-------|
| **Domain**  | Healthcare, clinical, patient-facing |
| **Standards** | HIPAA, FDA 21 CFR Part 11, WCAG 2.1 AA, ISO 62366-1 (Usability Engineering) |
| **Tone**    | Safety-critical, precise, compliant |

## Core Instructions

### 1) Patient Safety First

- Display critical information (allergies, drug interactions, alerts) prominently and persistently.
- Use color coding with redundant text/icon indicators (never color alone per WCAG 2.1).
- Require explicit confirmation for high-risk actions (medication orders, dosage changes).

### 2) Regulatory Compliance

- Implement audit trails for all data modifications (who, what, when).
- Support electronic signatures per FDA 21 CFR Part 11 where applicable.
- Enforce session timeouts and re-authentication for sensitive operations (HIPAA).
- Display patient identifiers consistently (minimum two identifiers per ISO 62366-1).

### 3) Clinical Workflow Efficiency

- Minimize clicks for high-frequency tasks (vitals entry, medication administration).
- Support barcode scanning for patient wristbands and medication verification.
- Provide keyboard shortcuts for power users in clinical settings.
- Design for interruption recovery (clinicians are frequently interrupted mid-task).

### 4) API-First Rule

All backend activity must go through APIs. Never assume direct database access. Keep UI optimistic where safe and reconcile with API responses. Apply strict error handling for clinical data integrity.

## Cognitive UX Evaluation

For cognitive science-based evaluation of clinical UI designs -- particularly the Attention Mind (reducing cognitive load in high-stress clinical environments), Language Mind (clear medical terminology and error messages), and Emotion Mind (trust signals for patient-facing interfaces) -- reference `skills/cognitive-ux-framework/`.

## Accessibility

- WCAG 2.1 AA minimum; AAA for patient-facing interfaces.
- Large touch targets (minimum 48x48px) for tablet-based clinical entry.
- High contrast mode for bright clinical environments.
- Screen reader compatibility for visually impaired patients.

## Common Pitfalls

- Displaying too much information simultaneously (cognitive overload in clinical settings).
- Relying on color alone to indicate alert severity.
- Missing confirmation dialogs on irreversible clinical actions.
- Inadequate session timeout policies for shared clinical workstations.
- Not designing for interruption recovery in clinical workflows.

## Cognitive UX Evaluation

For cognitive science-based evaluation of clinical UI designs — particularly the Attention Mind (reducing cognitive load in high-stress clinical environments), Language Mind (clear medical terminology and error messages), and Emotion Mind (trust signals for patient-facing interfaces) — reference `skills/cognitive-ux-framework/`.

## Motivation & Engagement in Clinical UX

From Hodent (2022) *What UX Is Really About* — Self-Determination Theory (SDT) applied to clinical software.

Clinicians disengage from or work around clinical software when their fundamental motivational needs are violated. Design must satisfy all three SDT needs:

### Competence (Feeling Skilled and In Control)
- New staff need more scaffolding: wizards, contextual help, pre-populated suggestions
- Experienced clinicians need shortcuts: keyboard shortcuts, quick-entry fields, saved templates
- Never design a one-size-fits-all workflow — it makes experts feel clumsy and beginners feel lost
- Show competence growth: highlight when a user masters a new workflow
- Feedback timing: visual acknowledgment within 100ms; meaningful response within 1 second

### Autonomy (Meaningful Choice, Not Forced Paths)
- Rigid workflow sequences that cannot be adjusted cause resistance and workarounds
- Provide clear, well-labelled escape hatches when the standard path does not fit the clinical situation
- Allow users to customise common actions, shortcuts, and default values
- Explain *why* a constraint exists (regulatory, safety-critical) — clinicians respect justified constraints; they resist arbitrary ones

### Relatedness (Connection to Shared Purpose)
- Connect individual data entry actions to visible patient outcomes where possible
- Team context: show who else is viewing or editing a record
- Surface alerts that connect a clinician's action to downstream team members
- Avoid creating a feeling of "I'm just entering data into a machine"

---

## Cognitive Load in High-Stress Clinical Environments

Clinical settings impose maximum intrinsic cognitive load. Every design decision must ruthlessly eliminate extraneous load.

### Core Principles
- **Recognition over recall is mandatory:** Clinicians under stress cannot remember; display everything needed for a decision on the current screen. Never require mental calculation or cross-screen navigation for critical decisions.
- **Interruption recovery:** Save state aggressively. On return to a screen after interruption, show a clear "where were you?" banner: "You were entering vitals for [Patient Name]. Continue?"
- **Error prevention over error recovery:** In clinical contexts, the cost of an error is severe. Force a deliberate pause before irreversible actions (medication orders, dosage changes, record deletions). Require explicit confirmation with specifics shown: "Administer 500mg Paracetamol to [Name]. Confirm?"

### Critical Information Display
- Allergies and contraindications must be visible before any prescribing action — not one click away
- Drug interaction warnings must interrupt the workflow (not a passive banner) for severe interactions
- Vital signs outside normal range must be visually distinct through colour, size, AND icon — never colour alone

### Anxiety Reduction (Emotion Mind)
- Preview outcomes before committing: "You are about to sign off [Document Type] for [Patient Name]"
- Show costs, fees, and complete information before the final confirmation step in patient-facing billing
- Allow easy exit from any flow without losing progress — autosave in the background
- In patient-facing interfaces: use calm, reassuring language; avoid clinical jargon
