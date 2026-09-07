# Engineering Kaizen: trustworthy validation

The [sequential audit](../audits/2026-09-06-kaizen/portfolio-progress.md) began
with 179 active skills and four failing repository tests. The user confirmed
eleven canonical checkouts under `C:/wamp64/www`.

## Implemented experiments

- Portfolio resolution uses the supplied workspace and explicit per-engine
  overrides. A missing override cannot silently select a different checkout.
  Research resolves to `digital-research-skills`. The twelve-entry registry
  remains intact; installed-checkout checks may target the eleven-engine scope.
- The manifest separates portable repository checks from live installation
  checks. Unit tests exercise temporary complete/missing portfolios, malformed
  registry data, path traversal and duplicate-checkout selection. Live checks
  run explicitly and retain their own result.
- The evidence gate previously scanned one family (15 checked, four exempt).
  It now discovers both active roots (173 checked, six exempt). Empty catalogues
  and unmatched selectors fail rather than reporting a successful empty scan.
  The broader baseline exposed 46 errors and 66 warnings for domain review.
- The local metadata contract accepts additional unique runtime names while
  retaining both required names. Its fixer preserves extra declarations. This
  is a local schema, not a public interchange or host-execution certification.
- Authoring guidance, the quick validator and repository guards use the same
  350-character description limit. Boundary tests cover accepted and rejected
  lengths.
- Execution-plan prompts now declare inputs, ownership, dependencies, acceptance
  evidence and resume checkpoints. Optional process plugins have a sequential
  fallback; unavailable tests remain visible instead of becoming expected
  failures. A new routing fixture guards this route.
- The root router exposes existing desktop, GIS and game routes and explicit
  website/SRS ownership. Two human-index aliases now agree with the registry's
  external design ownership.

## Acceptance and recovery

Run the native catalogue/routing checks, `python -m pytest tests -q`, the changed
skills' quick/evidence validators, and the explicit live checks. Final integrated
counts and unresolved domain evidence belong in the audit evidence record, not
in this change description while independent work is still being integrated.

No skill directories were moved or removed. Reversal is the reviewed patch for
this cycle; preserve unrelated edits. Retest missing and malformed cases when
changing discovery or source-of-truth rules. Next review: 2026-09-13, sooner on
an engine-path, schema or host change.
