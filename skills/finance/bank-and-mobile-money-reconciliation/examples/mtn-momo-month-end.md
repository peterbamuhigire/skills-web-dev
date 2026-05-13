# Example — MTN MoMo Business Month-End Reconciliation

Period: 2026-04. Account: Mobile Money — MTN Business (CoA 1200). Provider: MTN MoMo Business.

## Inputs

| Input | Source |
|---|---|
| MTN MoMo statement (CSV) | MTN business portal export, retrieved 2026-05-02 by Accountant Jane Doe. |
| Ledger detail | All journals posted to 1200 in 2026-04. |
| Settlement clearing | All journals posted to 2410 Mobile-Money Settlement Clearing — MTN. |

## Step 1 — Stage the import

The CSV is imported into staging. 312 rows. Checksum hashed and stored. State = `imported`.

## Step 2 — Auto-match

| Rule | Hits | Notes |
|---|---|---|
| R1 Exact | 268 | Standard customer sales with MoMo reference. |
| R2 Amount+date | 14 | Reference missing on a few statement rows. |
| R5 Split | 3 | Single MoMo settlement row covers multiple sales. |
| R6 Merge | 5 | Float top-ups posted separately in ledger; statement showed batched. |
| Unmatched | 22 | To triage. |

## Step 3 — Triage

| Item | Description | Resolution | Posting |
|---|---|---|---|
| MoMo charge UGX 250 × 22 | Provider transaction fees. | Post to 6900 Bank Charges. | Dr 6900 / Cr 1200, dimensions branch=Mukono. |
| Inbound UGX 1,500,000 | Customer payment with no invoice reference. | Identified via amount-and-date match to AR invoice INV-2026-04-0117. | Match in AR; reconcile. |
| Float top-up UGX 5,000,000 | From operating bank account. | Match to transfer journal. | Match. |
| Reversal UGX 80,000 | Customer cancellation. | Match to original sale's reversal posted on 2026-04-21. | Match. |
| Charge UGX 30,000 | Monthly service fee. | Post to 6900 Bank Charges. | Dr 6900 / Cr 1200. |

## Step 4 — Sign-off

Preparer: Jane Doe. Reviewer: Peter Bamuhigire (Controller). Release state: `pass`.

## Step 5 — Evidence pack

Per `doctrine/examples/reconciliation-evidence-pack.md`. Manifest stored at `evidence/recon-1200-2026-04/manifest.yaml`. Pack archive `evidence/recon-1200-2026-04.zip`.

## Postings emitted

All postings flowed through the posting service. None bypassed.

| Journal | Dr | Cr | Account | Notes |
|---|---|---|---|---|
| J-RECON-2026-04-001 | 250 × 22 | | 6900 Bank Charges | Per-transaction MoMo fees |
| J-RECON-2026-04-001 | | 250 × 22 | 1200 Mobile Money — MTN Business | |
| J-RECON-2026-04-002 | 30,000 | | 6900 Bank Charges | Monthly service fee |
| J-RECON-2026-04-002 | | 30,000 | 1200 Mobile Money — MTN Business | |

(Other items resolved through existing journals; no new postings required.)

## Control-account tie-out

- Mobile Money — MTN Business (1200) closing per ledger: UGX 18,750,500.
- MTN MoMo statement closing: UGX 18,750,500.
- Variance: 0.
- Mobile-Money Settlement Clearing — MTN (2410) closing: UGX 0 (all sales swept).

## Outputs released

- Reconciliation report (PDF, print stylesheet applied).
- Reconciliation CSV.
- Exception listing (empty after triage).
- Evidence pack.
- Gate manifest: state `pass`, blockers 0, caveats 0.

Last reviewed: 2026-05-12. Next review due: 2026-11-12.
