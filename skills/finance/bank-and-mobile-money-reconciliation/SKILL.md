---
name: bank-and-mobile-money-reconciliation
description: Bank-account, mobile-money (MTN MoMo, Airtel Money, equivalents), POS cash drawer, card settlement, and clearing-account reconciliation workflow design and implementation. Use whenever a software system, SRS, SDS, test plan, proposal, business plan, or strategy involves bank feeds, mobile-money statements, POS Z-reports, settlements, chargebacks, reversals, bank charges, unmatched deposits, or month-end reconciliation evidence packs.
---

# Bank and Mobile-Money Reconciliation

## Overview

Reconciliation is a first-class accounting workflow in Chwezi systems. Imported external evidence (bank statement, mobile-money statement, POS Z-report, card acquirer settlement) does not silently become accounting. It passes through staging, matching, exception handling, posting, review, and evidence retention.

This skill specifies the workflow, the data model, the UI (via `finance-ui-pattern-library`), the controls, and the acceptance evidence.

## Required first reads

- `doctrine/accounting-finance-doctrine.md`
- `doctrine/references/ledger-invariants.md`
- `doctrine/references/chart-of-accounts.md` (focus on Bank, Mobile Money, Settlement Clearing, Petty Cash, POS Cash Tendered Clearing)
- `doctrine/references/status-taxonomy.md`
- `doctrine/examples/reconciliation-evidence-pack.md`
- This skill's `references/`.

## Scope

| In | Out |
|---|---|
| Bank statement import (CSV, OFX, MT940 where available, PDF + OCR fallback). | Direct bank API integration without authority-verified spec. |
| Mobile-money provider statement import (MTN MoMo Business, Airtel Money Business, equivalent). | Provider-API integration without verified contract. |
| POS Z-report import and cash-drawer reconciliation. | POS hardware drivers (the skill assumes a Z-report exists). |
| Card acquirer settlement reconciliation. | Card-network certification. |
| Clearing-account ageing and exception triage. | |
| Chargebacks, reversals, bank charges, unmatched deposits, customer overpayments. | |
| Evidence-pack production. | |

## Workflow

1. **Stage.** Import the file or feed into a staging table. Capture source, retrieval timestamp, importer identity, file checksum. No GL posting yet.
2. **Match.** Apply automatic match rules (amount, date window, reference, counterparty). Surface ambiguous matches for triage.
3. **Triage.** The reconciler resolves unmatched items: match, split, mark exception, or create a new posting (bank charge, interest credit, unrecorded customer payment, …).
4. **Post.** Approved postings flow through the posting service. Reconciliation is not the posting path; it is a triage that emits posting commands.
5. **Review.** Reviewer sign-off before close.
6. **Pack.** Evidence pack assembled per `doctrine/examples/reconciliation-evidence-pack.md`.

## Data model (minimum)

```sql
-- staging
CREATE TABLE reconciliation_imports (
  id BIGINT PRIMARY KEY,
  source ENUM('bank','momo','airtel','pos','card-acquirer','other'),
  account_code VARCHAR(20),                 -- maps to CoA control account
  external_account_id VARCHAR(80),
  period_start DATE,
  period_end DATE,
  retrieved_at TIMESTAMP,
  retrieved_by BIGINT,
  file_checksum_sha256 CHAR(64),
  archive_path TEXT,
  state ENUM('imported','reconciled','signed-off','superseded')
);

CREATE TABLE reconciliation_lines (
  id BIGINT PRIMARY KEY,
  import_id BIGINT REFERENCES reconciliation_imports(id),
  external_id VARCHAR(120),
  external_ref VARCHAR(120),
  posted_at TIMESTAMP,
  value_at TIMESTAMP,
  amount NUMERIC(20,4),
  currency CHAR(3),
  description TEXT,
  counterparty VARCHAR(200),
  match_state ENUM('unmatched','matched','partial-match','exception','pending-evidence'),
  matched_journal_line_id BIGINT,
  exception_reason TEXT,
  age_days INT,
  assignee BIGINT
);

CREATE TABLE reconciliation_signoff (
  import_id BIGINT REFERENCES reconciliation_imports(id),
  preparer BIGINT, preparer_signed_at TIMESTAMP,
  reviewer BIGINT, reviewer_signed_at TIMESTAMP,
  release_state ENUM('pass','pass-with-caveats','fail'),
  caveats JSON
);
```

## Match rules (default order)

1. Exact match: amount + currency + value date ± 1 day + reference token.
2. Amount + date window match where reference is missing.
3. Counterparty match within an amount tolerance per entity (default 0).
4. Multi-line match (one statement row to N ledger lines, or N to 1) for split deposits / batch settlements.
5. Pattern match for recurring items (rent, payroll, standing orders).

Unmatched items appear in the triage UI with ageing.

## Exception handling

Common exceptions:

| Exception | Resolution |
|---|---|
| Bank charge with no ledger entry. | Post bank-charge journal; match. |
| Interest credit with no ledger entry. | Post interest-income journal; match. |
| Customer payment without invoice reference. | Investigate via AR; either match to an open invoice or hold as a customer credit. |
| Provider settlement net of fees. | Split rule: gross sale → settlement clearing; fee → fee expense. |
| Chargeback / reversal. | Reverse the original posting; re-open the customer invoice. |
| Standing order from supplier (rent, utilities, lease). | Match to recurring schedule; auto-post next month. |
| Bounced cheque. | Reverse the original cash receipt; restore AR open item; record charge. |

## Mobile-money specifics

MTN MoMo Business / Airtel Money Business operate as bank-like accounts with provider statements. Build expectations:

- Daily statement import where the provider offers it; otherwise daily manual export.
- Provider transaction reference is the match key.
- Provider fees are typically itemised — post to a dedicated fee expense account.
- Settlement may be net of fees and net of float top-ups; the reconciliation must distinguish.
- For customer-paid sales settled via mobile money, the sale posts to Mobile-Money Settlement Clearing at the point of sale; the provider statement clears the clearing into Mobile Money — \<provider\>.

## POS cash drawer reconciliation

- Z-report at drawer close lists tendered totals by tender type.
- Cash tender flows: Drawer open → cashier sales increase POS Cash Tendered Clearing → drawer close moves the clearing balance to Cash on Hand or a bank deposit.
- Cash variance (counted vs computed) goes to Cash Over/Short with an exception entry; thresholds escalate to manager review.

## Card acquirer settlement reconciliation

- Acquirer batches settle to the bank account net of fees and chargebacks.
- The sale posts to Card Settlement Clearing at the point of sale; the acquirer settlement clears the clearing to the bank, with fees posted to Card Fees expense.
- Chargebacks reverse the original sale (with linked journal) and post the chargeback fee.

## Evidence pack

Produced per `doctrine/examples/reconciliation-evidence-pack.md`. Required at month-end before close release.

## Required UI

- Reconciliation triage (per `finance-ui-pattern-library` `ReconciliationTriage`).
- Ageing summary in the header.
- Exception list with assignee and ageing.
- Evidence pack export button.
- No `Delete` on imported feed rows. Use `Supersede` if a re-import is needed; the original import remains in the audit log.

## Controls

- Maker-checker on every posting emitted by the triage.
- No editing of the imported file once staged; corrections are by supersede + new import.
- Reviewer sign-off required before close release.
- Period-state respected: a reconciliation against a locked period requires the reopen workflow.

## Acceptance evidence (tests)

| Test | Pass criterion |
|---|---|
| Import a valid bank CSV. | Staging populated; no GL effect. |
| Auto-match exact row. | Match state `matched`; no exception. |
| Auto-match split (one statement row → multiple invoices). | Each ledger line matched; match state `matched`; partial-match if amounts don't sum. |
| Unmatched statement row triggers triage. | Appears in triage with ageing `1`. |
| Bank charge with no ledger row posts and matches. | New journal posted via posting service; match state `matched`. |
| Chargeback reverses original. | Reversal journal posted; original AR open item restored. |
| Re-import of same file with same checksum. | Rejected as duplicate. |
| Re-import after `supersede`. | New import accepted; previous marked `superseded`. |
| Reconciliation against locked period without reopen. | Rejected. |
| Sign-off without reviewer. | Cannot release. |

## Files

- `SKILL.md` — this file.
- `references/match-rules.md` — full match-rule taxonomy and pseudocode.
- `references/provider-quirks.md` — known quirks of MTN MoMo, Airtel Money, common Uganda banks.
- `references/data-model.sql` — full DDL.
- `examples/mtn-momo-month-end.md` — worked end-to-end example.

Last reviewed: 2026-05-12. Next review due: 2026-11-12.
