# Match Rules

The default match-rule taxonomy. Implementations may add rules; they must not loosen the listed ones without explicit configuration and reviewer approval.

## Rule order

Auto-match runs rules in order. The first rule to match wins.

| # | Rule | Conditions |
|---|---|---|
| R1 | Exact | amount=ledger amount; currency=ledger currency; value-date within ±1 calendar day; reference token contained in ledger description or document reference. |
| R2 | Amount + date | amount=ledger; currency=ledger; value-date within ±2 calendar days; no reference required. |
| R3 | Reference | reference token present in ledger; amount within ±0 tolerance (configurable per entity). |
| R4 | Counterparty | counterparty name fuzzy-matched (Levenshtein ≤ 3 against canonical list); amount and date within R2 windows. |
| R5 | Split (one-to-many) | one statement row matches a sum of ledger lines on the same control account within the date window; tax-line splits respected. |
| R6 | Merge (many-to-one) | many statement rows match a single ledger line (batch deposit, batch payment). |
| R7 | Pattern | recurring vendor / standing order pattern; date predicted from prior period. |

## Match outcome states

- `matched` — match committed.
- `partial-match` — sums don't agree within tolerance; reconciler decides.
- `exception` — no candidate or conflicting candidates; reconciler triages.
- `pending-evidence` — matched but evidence file missing; cleared after attach.

## Match metadata stored

| Field | Description |
|---|---|
| `rule-id` | Which rule produced the match (R1…R7). |
| `confidence` | High, medium, low. |
| `tolerance-applied` | Amount and date tolerance used. |
| `auto-or-manual` | Whether auto or human. |
| `actor` | If manual. |
| `unmatched-residual` | Amount remaining unmatched after a partial. |

## Tolerances

| Tolerance | Default | Notes |
|---|---|---|
| Amount | 0 of smallest currency unit. | Increase only with reviewer approval and per-account audit. |
| Date | ±1 day for R1, ±2 days for R2. | Provider weekends / public holidays push to ±3 with documented reason. |
| Reference fuzzy | None for R1; exact substring required. | |
| Counterparty fuzzy | Levenshtein ≤ 3. | Bank statement abbreviations frequently produce this. |

## Pseudocode (excerpt)

```python
def auto_match(statement_row, ledger_candidates):
    for rule in [R1, R2, R3, R4, R5, R6, R7]:
        candidates = rule.apply(statement_row, ledger_candidates)
        if candidates:
            if len(candidates) == 1:
                return commit_match(statement_row, candidates[0], rule.id, "high")
            return triage(statement_row, candidates, reason="multiple-candidates")
    return triage(statement_row, [], reason="no-candidate")
```

## Forbidden

- Match without checking currency.
- Match across a locked period without reopen.
- Tolerance higher than rule defaults without per-entity reviewer-approved override.
- Auto-match across statement rows of different value dates outside the date window.

Last reviewed: 2026-05-12. Next review due: 2026-11-12.
