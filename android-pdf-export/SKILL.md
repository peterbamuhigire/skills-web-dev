---
name: android-pdf-export
description: Native Android PDF export system using PdfDocument API (zero dependencies).
  Reusable Canvas-based generator with branded letterheads, data tables, summary cards,
  and share-via-Intent. Use when adding PDF export to any Android app screen —...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---


## Platform Notes

- Optional helper plugins may help in some environments, but they must not be treated as required for this skill.

# Android PDF Export (Native PdfDocument)

<!-- dual-compat-start -->
## Use When

- Native Android PDF export system using PdfDocument API (zero dependencies). Reusable Canvas-based generator with branded letterheads, data tables, summary cards, and share-via-Intent. Use when adding PDF export to any Android app screen —...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `android-pdf-export` or would be better handled by a more specific companion skill.
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

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
Generate professional branded PDF documents from any Android screen using the built-in `android.graphics.pdf.PdfDocument` API. Zero external dependencies — pure Canvas drawing. Supports A4 portrait/landscape, multi-page pagination, letterheads, tables, summary cards, info sections, status badges, and charts.

## Overview

**Library choice:** Native `android.graphics.pdf.PdfDocument` (0 KB added to APK). Alternatives like iText (AGPL license), PDFBox-Android (stale since 2023), and OpenPDF (requires java.awt hack) were rejected.

**Architecture:** A core `DmsPdfGenerator` object provides reusable drawing primitives. Per-module exporters (Sales, Inventory, Network) compose these primitives for each screen. `PdfExportHelper` handles file I/O and sharing via `FileProvider`.

```
core/pdf/
  DmsPdfGenerator.kt         — Reusable drawing primitives (letterhead, tables, cards, footer)
  PdfExportHelper.kt          — Save to cache + share via FileProvider Intent

core/ui/components/
  PdfExportButton.kt          — Reusable TopAppBar button (icon + "PDF" label)

Per-module exporters (one object per feature module):
  SalesReportPdfExporter.kt   — Sales reports + invoice list
  InventoryPdfExporter.kt     — Stock levels, PO/transfer/adjustment details + lists
  NetworkPdfExporter.kt       — Distributor list/detail, genealogy
```

## Additional Guidance

Extended guidance for `android-pdf-export` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `Dependencies`
- `Step 1: FileProvider Setup`
- `Step 2: PdfExportHelper`
- `Step 3: Core PDF Generator`
- `Step 4: Per-Module Exporters`
- `Step 5: PdfExportButton Component`
- `Step 6: Screen Integration`
- `Step 7: String Resources`
- `Step 8: Franchise Info for Letterheads`
- `PDF Design Specification`
