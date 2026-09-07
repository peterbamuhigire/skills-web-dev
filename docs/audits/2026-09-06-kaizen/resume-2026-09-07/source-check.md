# Context-bound source contract repair

Owner: Peter Bamuhigire. Implementer/verifier: Codex. Observed: 2026-09-07.
Next review: 2026-09-13 for the repair; 2026-10-03 for the source snapshot.

The portfolio register failed the research currentness gate with two findings:
`context-bound` was unsupported, and its linked claim was not qualified. The
owning currentness policy already permits scoped use of context-bound evidence.
The register also lacked a publication, revision or snapshot date for this row.

Hypothesis: recognising that class with explicit scope and the existing date
controls will reconcile the handoff without accepting undated or overdue evidence.
Nine regression cases were added: before repair, eight failed and one passed;
after repair, the focused source-currency suite passed all 93 cases. The passing
baseline case was the existing overdue-date guard, not a new improvement.
No review threshold or failure exit was weakened.

## Source admission

Claim ID: `claim-impeccable-anti-slop-taxonomy`.
Source ID: `impeccable-slop-catalog`; tier 1 for its own published taxonomy only.
Claim (paraphrase): the publisher provides a web-interface pattern catalogue
that distinguishes AI-default concerns from general quality concerns and
labels different checking modes.

Source: [Impeccable Slop](https://impeccable.style/slop/), sections
"The catalog" and "How to read this", accessed and checked 2026-09-07.
The page was opened successfully through the web tool and those sections were
read. Publication/version date was not established; `as_of=2026-09-07` records
the accessed snapshot instead. Freshness and support status: `context-bound`.
Confidence is high for the limited catalogue-existence/scope claim.

This first-party page does not independently establish detector accuracy,
authorship, prevalence or universal design rules. Those claims are NOT ASSESSED.
No numeric detector claim or new visual doctrine is admitted. Independent
verification by a second reviewer is NOT ASSESSED; this is the implementer's
source check, not an independent review.

Only this source row's access/verification dates were advanced following the
actual check. Its original 2026-09-03 observation remains in the row's history
note and the preflight hash. The existing review deadline was retained; the
other twelve source rows were not reverified or edited.

## Acceptance and recovery

Accept only if the full research suite, native contracts/routing, source-ingestion
gate and real portfolio register pass. Metadata success remains explicitly
noncertifying. Command results are retained in `final-checks.json`.
Stop if a blank scope, undated context-bound source or overdue record passes.
Rollback only this continuation's validator/test/policy/register hunks; preserve
the earlier Kaizen repairs and historical evidence.
