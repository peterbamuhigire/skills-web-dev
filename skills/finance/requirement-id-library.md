# Finance Requirement-ID Library

Reusable requirement IDs for any SRS that touches finance / accounting. Aligned to doctrine v1.0.0. Numbering: `FIN-<area>-<NNN>`.

## FIN-LED — Ledger integrity

| ID | Requirement |
|---|---|
| FIN-LED-001 | Feature modules MUST NOT write to `journal_headers` or `journal_lines` directly; they MUST submit accounting events to the approved posting service. |
| FIN-LED-002 | Every posted journal MUST balance debits and credits per currency. |
| FIN-LED-003 | Posted journals MUST be immutable through normal application paths. |
| FIN-LED-004 | Corrections MUST be implemented as a reversal + new posting, with explicit lineage to the original. |
| FIN-LED-005 | Reversals MUST link to the original journal and preserve reason, actor, date, type (full / partial). |
| FIN-LED-006 | The posting service MUST reject postings into a `locked` period. |
| FIN-LED-007 | Every posting MUST write an audit-log entry with actor, time, source-document reference, evidence reference, and posting-service version. |
| FIN-LED-008 | Integration-driven postings MUST carry idempotency keys. |
| FIN-LED-009 | Replays with the same idempotency key and same payload hash MUST return the prior result; replays with same key and different payload MUST be rejected. |
| FIN-LED-010 | Control accounts MUST reconcile to their subledger at every close. |

## FIN-COA — Chart of Accounts

| ID | Requirement |
|---|---|
| FIN-COA-001 | The Chart of Accounts MUST be the backbone for postings, control accounts, reporting groups, dimensions, permissions, and audit evidence. |
| FIN-COA-002 | Each account MUST carry full metadata: class, statement-group, normal side, contra flag, control flag, tax flag, currency rule, dimensions matrix, direct-post permission, reconciliation requirement, evidence requirement. |
| FIN-COA-003 | The system MUST NOT permit free-text accounts. |
| FIN-COA-004 | Postings to dimension-required accounts without those dimensions MUST be rejected. |
| FIN-COA-005 | Direct posting to control accounts MUST be restricted to Controller (or system-only for clearing accounts). |

## FIN-TAX — Tax handling

| ID | Requirement |
|---|---|
| FIN-TAX-001 | VAT-inclusive sales and purchases MUST be decomposed at posting time into net, tax, and gross. |
| FIN-TAX-002 | Output VAT MUST post to the Output VAT control account; Input VAT to the Input VAT control account. |
| FIN-TAX-003 | Tax codes MUST carry rate, jurisdiction, and effective period. |
| FIN-TAX-004 | Tax rates MUST be read from the source register; no hardcoded rates. |
| FIN-TAX-005 | The system MUST produce return-ready packs for every authority in scope (VAT, PAYE, WHT, NSSF, income tax). |
| FIN-TAX-006 | Each return pack MUST include jurisdiction, authority, taxpayer identity, filing period, return type and template version, ledger and subledger source mapping, tax codes with source-register references, source documents, evidence pack, reviewer sign-off, and open gaps. |
| FIN-TAX-007 | EFRIS / eTIMS submission MUST be a parallel system reconciled against the ledger, not the ledger source of truth. |

## FIN-REP — Reporting

| ID | Requirement |
|---|---|
| FIN-REP-001 | Every report MUST carry a framework header (IFRS / IFRS for SMEs / local statutory / client-specific / N/A). |
| FIN-REP-002 | Every figure on every report MUST be drillable to source: report line → account → journal → line → source document → evidence file → audit-log entry. |
| FIN-REP-003 | Every report MUST have a print stylesheet that renders correctly on A4 in monochrome with sign-off boxes. |
| FIN-REP-004 | The audit-ready reporting pack MUST contain the minimum content set per the doctrine's `audit-ready-reporting-pack` skill. |
| FIN-REP-005 | The system MUST produce an auditor export bundle with a single index, hashes, and an audit-log CSV. |

## FIN-AUD — Audit export

| ID | Requirement |
|---|---|
| FIN-AUD-001 | The auditor export MUST contain trial balance, GL detail, journal listing, financial statements, AR / AP / inventory / FA / payroll detail, reconciliations, tax pack, management accounts, donor / grant pack (where applicable), source documents, and audit-log CSV. |
| FIN-AUD-002 | The auditor export MUST be watermarked with auditor identity. |
| FIN-AUD-003 | The auditor view of the ledger MUST be read-only. |

## FIN-MIG — Migration / opening balances

| ID | Requirement |
|---|---|
| FIN-MIG-001 | Cutover MUST start from a named conversion date. |
| FIN-MIG-002 | Migration MUST include legacy TB, CoA mapping, open AR, open AP, inventory, fixed assets, bank balances, mobile-money balances, payroll/tax liabilities. |
| FIN-MIG-003 | Migration suspense MUST reach zero (or be formally waived with sign-off) at acceptance. |
| FIN-MIG-004 | The opening journal MUST be posted via the posting service, balanced per currency, and locked thereafter. |
| FIN-MIG-005 | Subledger tie-outs MUST be evidenced before sign-off. |

## FIN-REC — Reconciliation

| ID | Requirement |
|---|---|
| FIN-REC-001 | Bank, mobile-money, POS cash drawer, card acquirer, and clearing-account flows MUST have a reconciliation workflow. |
| FIN-REC-002 | Imported feeds MUST stage; they MUST NOT commit to the ledger before matching. |
| FIN-REC-003 | Reconciliation MUST be presented as a triage UI with ageing, not as a downloadable report. |
| FIN-REC-004 | Every reconciliation period MUST produce an evidence pack with sign-off. |

## Use

Cite the requirement IDs in SRS / SDS / test plan tables. Each test case carries one or more requirement IDs in its `verifies` field.

Last reviewed: 2026-05-12. Next review due: 2026-11-12.
