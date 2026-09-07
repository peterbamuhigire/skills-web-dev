# Evidence-separated scorecard

Observation date: 2026-09-06. These results describe the evolving local patch,
not an immutable release. Baseline revision and commands are in the
[method](01-methodology-and-rubric.md) and [progress record](portfolio-progress.md).

| Dimension | Baseline | Latest observed state | Evidence limit |
|---|---|---|---|
| Repository tests | 18 passed, 4 failed | 57 passed, with `SKILL_ENGINE_LIVE_TESTS=1` | Local Python/Windows run; not target-product execution |
| Routing fixtures | 143/157 top one; 157/157 top three | 144/158 top one; 158/158 top three | Retrieval proxy; remaining top-one misses are not hidden |
| Catalogue compliance | 91/179 fully compliant | 153/179; zero metadata failures | Structural scanner, not semantic score |
| Evidence discovery | 15 checked, 4 exempt | 173 checked, 6 exempt; 0 errors, 66 warnings | Expanded baseline: 46 errors, 66 warnings |
| Independent validator review | Two boundary defects found | Both closed at scoped recheck | Windows junctions tested; POSIX execution NOT ASSESSED |
| Taxonomy | 52/100 assessor judgement | No re-score | [Named baseline deficiencies](02-coverage-and-taxonomy.md) |
| Standards-currentness controls | 50/100 assessor judgement | Scoped guidance repaired; no re-score | [Named findings and support boundaries](06-standards-benchmark.md) |
| Output instruction readiness | Individual judgements in linked report | No aggregate or re-score | [Per-output rows](05-per-output-type-readiness.md) |
| Per-skill/group depth | Retained semantic census unavailable | [Structural census](03-existing-groups-audit.md); semantic gaps retained | Do not substitute metadata compliance |
| Behavioural product readiness | NOT ASSESSED | NOT ASSESSED | No connected target-product execution retained |
| Production outcomes | NOT ASSESSED | NOT ASSESSED | No deployment, user acceptance or measured operational outcome |
| Overall engine | NOT ASSESSED | NOT ASSESSED | Evidence does not support a weighted whole-engine score |

Latest test command, executed from this checkout:

```powershell
$env:SKILL_ENGINE_LIVE_TESTS='1'
python -X utf8 -m pytest tests -q -p no:cacheprovider --tb=short
```

Observed: `57 passed in 1.12s`. The flag is scoped to the execution shell.
The independent reviewer separately recorded its narrower recheck; do not
describe the full-suite result as independently repeated.

The roadmap's 95/100 is an improvement objective, not an observed result.
Apply the reporting cap and evidence restrictions in the method at re-audit.
