# Audit Report Template

The shape of the deliverable produced by `finance-module-audit`.

## 1. Cover

- Target system name.
- Audit version, doctrine version, date.
- Auditor (named human or named agent).
- Sponsor / requester.
- Scope summary (one paragraph).
- Release decision: `pass` / `pass-with-caveats` / `fail`.

## 2. Executive summary

- One page. The story of the audit in plain language.
- Top three findings.
- Decision rationale.

## 3. Scope record

Per `audit-protocol.md` Phase 1.

## 4. Money-flow map

For each in-scope flow: trigger → role → surface → posting → CoA → subledger → reconciliation → close → reporting → tax.

## 5. Findings register

A single ordered list. Each finding:

```yaml
- id: B-031
  category: tax-and-statutory
  severity: blocker
  title: "VAT-inclusive postings without net / tax / gross decomposition"
  standard: "doctrine §6 + governance B-031"
  evidence: "src/services/posting.service.php:142-178; tests/posting/test_vat.py absent"
  observation: "Sale posted as single line on 4000 at gross amount; tax not separated."
  risk: "Output VAT not reconcilable to return; net revenue overstated by tax."
  required-fix: "Decompose at posting; route tax to 2100 Output VAT Control; preserve gross as document reference."
  acceptance-evidence: "Test case TC-VAT-001 passes; example posting reviewed by accountant."
  owner: "Backend Engineer"
  reviewer: "Accountant"
  due: "2026-06-15"
```

## 6. Standards scorecard

Per `scorecard.md` — checks listed, scored, with one-line evidence per row.

## 7. Master plan

Per `remediation-master-plan.md` — phased, with owners, dependencies, acceptance evidence.

## 8. Open verification gaps

Rates / thresholds / templates not yet verified-current. Each with topic, expected source, owner, target verification date.

## 9. Appendices

- A. Sampled journals (50 rows).
- B. Reconciliation evidence-pack samples.
- C. UI screenshot inventory.
- D. Source-register snapshot.
- E. Audit-log sample (last 1000 high-risk events).

## 10. Sign-off

| Role | Name | Signature | Date |
|---|---|---|---|
| Auditor | | | |
| Reviewer | | | |
| Approver | | | |

## Print fidelity

The report uses the print stylesheet from `finance-ui-pattern-library/references/print-stylesheet-template.md`. A4, monochrome-readable, page X of Y, sign-off boxes on the last page, stamp area on the cover.

Last reviewed: 2026-05-12. Next review due: 2026-11-12.
