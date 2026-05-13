# Eval CI Gate — Reference

The CI gate is the runtime that blocks regressions before they ship.

## Trigger

PRs touching any of:
- `prompts/**` — prompt registry contents.
- `eval/**` — golden suites, scorers, manifests.
- `gateway/providers/**` — provider adapters and price table (affects model behaviour).
- `services/*/ai_*.py` — feature-side prompt rendering.

## Job

`.github/workflows/ai-eval.yml`:

```yaml
name: ai-eval
on:
  pull_request:
    paths:
      - 'prompts/**'
      - 'eval/**'
      - 'gateway/providers/**'
      - 'services/**/ai_*'
permissions:
  contents: read
  pull-requests: write
jobs:
  eval-gate:
    runs-on: ubuntu-latest
    timeout-minutes: 30
    env:
      ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY_EVAL }}   # rate-limited eval key
      OPENAI_API_KEY:    ${{ secrets.OPENAI_API_KEY_EVAL }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install -r eval/requirements.txt

      - name: discover affected features
        id: features
        run: python -m eval.runner.discover_affected --base ${{ github.base_ref }} > features.json

      - name: run eval (base)
        run: python -m eval.runner.run --features features.json --ref base --out base.json

      - name: run eval (head)
        run: python -m eval.runner.run --features features.json --ref head --out head.json

      - name: compare
        run: python -m eval.runner.compare --base base.json --head head.json --out report.md

      - name: comment PR
        uses: marocchino/sticky-pull-request-comment@v2
        with:
          path: report.md

      - name: gate
        run: python -m eval.runner.gate --report head.json  # exit 1 on regression below threshold
```

## Comparison logic

```python
def compare(base, head, manifest):
    issues = []
    for metric, threshold in manifest.thresholds.items():
        base_val = base.metrics[metric]
        head_val = head.metrics[metric]
        if head_val < threshold:
            issues.append(("absolute", metric, head_val, threshold))
        if head_val < base_val - manifest.allowed_drop.get(metric, 0):
            issues.append(("regression", metric, base_val, head_val))
    return issues
```

Two failure modes:
1. **Absolute**: metric below its threshold regardless of base.
2. **Regression**: metric dropped vs base by more than allowed drop.

Both block merge.

## PR comment shape

```
### AI Eval Report (PR #312)

| feature                  | metric        | base | head | Δ      | gate |
|--------------------------|---------------|-----:|-----:|-------:|------|
| support-copilot.answer   | correctness   | 0.91 | 0.88 | -0.03  | ⚠️   |
| support-copilot.answer   | faithfulness  | 0.96 | 0.96 |  0.00  | ✅   |
| analytics.sql-from-q     | format        | 1.00 | 0.97 | -0.03  | ❌   |

Failing examples:
- analytics.sql-from-q / sql_form_0017 — invalid JSON in output (see attached)
- support-copilot.answer / sup_ans_0091 — judge score 2/4
```

Drilldown links go to a static HTML report uploaded as an artifact.

## Performance + cost discipline

A naive eval is expensive. Tactics:
- Only re-run features affected by the diff.
- Cache scorer outputs keyed by `(prompt_id, prompt_version, model, candidate_hash)`.
- Use a smaller judge model on PR runs; full judge on nightly.
- Pre-batch eval requests (Anthropic / OpenAI batch APIs) for offline jobs (not PR runs — latency matters).

Set a CI cost budget per month and alert on overrun.

## Nightly drift job

Same harness, different trigger:

```yaml
on:
  schedule:
    - cron: '0 4 * * *'   # 04:00 UTC daily
```

Replays the previous 24h's sampled production requests through the eval harness. Compares distributions per (feature, model, prompt_version) to a rolling baseline. Posts a Slack summary; pages on > 2-sigma persistent shift.

## Per-tenant pre-promotion gate

A manual workflow (workflow_dispatch) takes `feature`, `prompt_version`, `tenant`. Runs that tenant's golden subset. Writes outcome to `tenant_prompt_pins.eval_passed_at` so the prompt registry can permit promotion.
