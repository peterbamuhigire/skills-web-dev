# Remediation Master Plan Format

The plan shape produced by `finance-module-audit`. Phased, owner-led, evidence-driven.

## Plan header

- Target system.
- Doctrine version.
- Plan version.
- Date.
- Owners (engineering lead, finance lead, project lead).
- Release-state target (`pass` / `pass-with-caveats`).
- Target close-of-plan date.

## Phasing

| Phase | Objective | Trigger |
|---|---|---|
| Phase 0 — Stop the bleeding | Quarantine forbidden patterns shipping today. | Any blocker in current production. |
| Phase 1 — Doctrine adoption | Wire the canonical doctrine and quality gate into routing. | Phase 0 complete. |
| Phase 2 — Ledger integrity | Implement / fix posting boundary, double entry, immutability, reversal, period state, audit log, idempotency, control-account tie-out. | Doctrine adopted. |
| Phase 3 — Tax and statutory | VAT-inclusive decomposition; return-ready packs; source-register entries verified-current. | Phase 2 substantive. |
| Phase 4 — Reconciliation & close | Bank / mobile-money / POS / card / cash triage UIs; close playbook; evidence packs. | Phase 2 substantive. |
| Phase 5 — Reporting & UX | Audit-ready reporting pack; role-conditioned shell; drilldown; status taxonomy; print stylesheet. | Phase 2 substantive. |
| Phase 6 — Migration & controls | Cutover pack; SoD; maker-checker; master-data controls; audit-log review; exception monitoring. | Live data importing. |
| Phase 7 — Sector annexes & country extensions | Sector overlays; country extensions for non-Uganda jurisdictions. | Client demand. |
| Phase 8 — Operationalisation | `finance-module-audit` becomes the standard release harness; CI lint integrated; quarterly verification. | Phases 1–6 complete. |

## Item schema

```yaml
- id: REM-2026-001
  phase: 2
  area: ledger-integrity
  title: "Move 7 direct writes to journal_lines into the posting service"
  finding-ids: [B-010]
  owner-role: "Backend Engineer"
  owner-name: "..."
  dependencies: []
  acceptance-evidence:
    - "All direct writes removed; CI lint passes."
    - "Posting-service tests cover the new paths."
    - "Reviewer checklist signs off."
  effort: "M"          # XS / S / M / L / XL
  target: "2026-06-15"
  state: backlog | in-progress | blocked | done
```

## Acceptance evidence rules

Every item ends with **observable evidence** — code change, migration, test, report output, source-register entry, screenshot, approval log, exported audit pack. No item is closed on prose alone.

## Reviewer roles

Each phase carries reviewer roles:

| Phase | Reviewer roles |
|---|---|
| 0 | Controller. |
| 1 | Controller + CFO. |
| 2 | Accountant + Controller + Backend lead. |
| 3 | Tax Reviewer + Accountant + Controller. |
| 4 | Accountant + Controller. |
| 5 | Accountant + Designer / Frontend lead. |
| 6 | Controller + Internal Audit. |
| 7 | Accountant + Sector SME. |
| 8 | Cross-repo quality owner. |

## Plan release

A plan is `released` when phase 0 and phase 1 are complete and a `pass-with-caveats` decision is achievable. Later phases continue under the released plan.

## Forbidden patterns in the plan

- Items without owners.
- Items without acceptance evidence.
- Items that say "TBD".
- Items that close without observable evidence.
- Plans without a target date.

Last reviewed: 2026-05-12. Next review due: 2026-11-12.
