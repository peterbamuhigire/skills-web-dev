# Scorecard

The standards scorecard for any system audited under doctrine v1.0.0. Each row is a check; the score is `pass`, `pass-with-caveats`, `fail`, or `n/a`.

## Automatic blockers (any → release `fail`)

Mirror `doctrine/governance/finance-accounting-quality-gate.md`:

- B-001 Framework not identified.
- B-002 US GAAP applied without explicit selection.
- B-003 LIFO presented as IFRS / SME compliant.
- B-010 Direct write to `journal_lines` outside posting service.
- B-011 Single-sided ledger effects.
- B-012 Edit / delete of posted accounting history.
- B-013 Posting into a locked period without reopen workflow.
- B-014 Missing audit-log fields.
- B-020 Free-text accounts.
- B-021 Tax in line memo.
- B-022 Control account without subledger tie-out.
- B-023 Migration suspense non-zero at cutover without sign-off.
- B-030 Hardcoded VAT / PAYE / NSSF / WHT / income-tax / customs value in final artefact.
- B-031 VAT-inclusive without net / tax / gross decomposition.
- B-033 Authority return templates referenced without verified version.
- B-040 Final output uses a value without `verified-current` source-register entry.
- B-050 Cutover without opening-balance and subledger tie-out sign-off.
- B-060 Bank / POS / cash drawer / mobile-money scope without reconciliation plan.
- B-070 `Delete` / `Remove` on posted records.
- B-071 Gross-only transaction display.
- B-072 Dashboard summary without drilldown.
- B-073 Green or red used for non-state purposes.
- B-074 Status text outside the controlled taxonomy.
- B-075 Report without print stylesheet.
- B-080 Vendor-replacement claim without caveats and acceptance criteria.
- B-090 Required reviewer role missing.

## Required checks (must be completed; not blocking individually)

- R-100 Doctrine version referenced.
- R-101 Adopted doctrine version recorded.
- R-102 Quality-gate run logged in manifest.
- R-103 Reconciliation evidence packs attached.
- R-104 Migration cutover pack attached (where applicable).
- R-105 Tax-return packs attached (where applicable).
- R-106 Print preview validated.
- R-107 Accessibility (WCAG AA) recorded.
- R-108 Source-register snapshot attached.

## Standards-mapped checks

| Standard area | Checks |
|---|---|
| Policy hierarchy | Framework header present; selection logic respected; client-specific policies documented; reviewer signed off. |
| Ledger invariants | Posting boundary; double entry; immutability; reversal; period state; audit log; idempotency; control-account tie-out. |
| Chart of Accounts | CoA metadata complete; control accounts identified; dimensions matrix enforced; statement-group taxonomy applied. |
| Tax & VAT | VAT-inclusive decomposition; tax control accounts; WHT / PAYE / NSSF route through controls; tax codes carry effective period; return-ready pack produced. |
| Live-rate verification | Every verifiable value in source register; `verified-current` for final output; `pass-with-caveats` only for drafts; recheck cadence respected. |
| Reconciliation | Triage UI; per-account ageing; evidence pack; sign-off; provider-specific quirks handled. |
| Close | Task list with owner / due / dependency / evidence / review state / release decision; subledger tie-out; sign-off audit-logged. |
| Migration | Cutover pack present; tie-outs zero variance; suspense zero or waived; opening journal posted via posting service. |
| Internal controls | SoD enforced; maker-checker on critical actions; master-data controls; audit-log review; exception monitoring. |
| Management dimensions | Governed; budgets versioned; B vs A by dimension; allocation rules with audit trail; donor restrictions enforced. |
| UI / UX | Two surface modes; role-conditioned shell; semantic colour; drilldown; status taxonomy; print fidelity; accessibility; mobile / low-bandwidth tolerance. |
| Microcopy | Business words on workflow; accountant words on ledger; tone helpful. |
| Reviewer roles | Accountant; Controller; CFO / finance lead; Tax reviewer present and used. |

## Severity ladder

| Severity | Definition |
|---|---|
| blocker | Triggers `fail` on its own. |
| high | Triggers `pass-with-caveats` if otherwise clean. Multiple highs trigger `fail`. |
| medium | Action required; does not by itself prevent release. |
| low | Improvement opportunity. |

## Release-state computation

```
if any blocker:                                                        fail
elif any compliance-affecting check is pending verification only:      pass-with-caveats
elif all required checks complete and no blockers:                     pass
else:                                                                  pass-with-caveats
```

Last reviewed: 2026-05-12. Next review due: 2026-11-12.
