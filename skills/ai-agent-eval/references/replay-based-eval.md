# Replay-Based Eval

Take a recorded agent trace from production (or staging), substitute the prompt / model / tool registry under test, and re-run the loop using the recorded tool observations as fixtures. The diff between original and replayed trajectories is the regression / improvement signal.

## Why Replay

- Goldens are expensive to author. Replay leverages real traffic.
- Goldens drift from production. Replay always reflects current usage.
- New prompt / model / tool versions can be tested against thousands of real scenarios in hours.

## What Replay Cannot Do

- Test changes to tools' behaviour (the original observations are fixed). If a tool's response changes, you need a new golden.
- Surface novel inputs (the input set is whatever production had).
- Be the only eval. Pair with goldens.

## Architecture

```
[traces table]  ── sample ──►  [replay queue]  ── pop ──►  [replay worker]
                                                                │
                                                                ├── load trace (steps, observations)
                                                                ├── set runtime to candidate (prompt v2.3 / model X / tools Y)
                                                                ├── run loop, but every tool call returns recorded observation
                                                                ├── compute scores vs original trace
                                                                └── persist replay_result row
                                                                
[replay_results]  ──► dashboards, CI summary
```

## Sampling

Sample production traces:

```sql
SELECT id FROM agent_tasks
WHERE feature = :feature
  AND completed_at > NOW() - INTERVAL 7 DAY
  AND terminal_state IN ('COMPLETED','BUDGET_EXCEEDED','FAILED')
  AND tenant_id NOT IN (SELECT id FROM tenants WHERE opted_out_of_replay)
ORDER BY RAND()
LIMIT 500;
```

Stratify by terminal_state to make sure failures and budget-exceededs are represented.

## Tool Mocking from Trace

The replay runtime intercepts tool calls. For each, look up the matching original step:

```python
class ReplayToolRuntime(ToolRuntime):
    def __init__(self, original_steps):
        self.steps_by_signature = self._index_by_signature(original_steps)
        self.unmatched_calls = []
    
    def call(self, tool_name, args, ctx):
        sig = (tool_name, canonicalise(args))
        original = self.steps_by_signature.get(sig)
        if original is None:
            # candidate called a tool / args the original didn't
            self.unmatched_calls.append(sig)
            return self._best_match(tool_name, args)
        return original.observation
    
    def _best_match(self, tool_name, args):
        """When candidate args don't exactly match, return the closest observation."""
        candidates = [s for s in self.steps_by_signature.values() if s.tool_name == tool_name]
        if not candidates:
            return {"status": "ok", "data": {}, "replay_no_match": True}
        return min(candidates, key=lambda s: args_distance(s.args, args)).observation
```

`replay_no_match` flag surfaces to the scorer; tool calls without any matching observation are penalised.

## Scoring

Per replayed trace, compute:

| Metric | Calculation |
|---|---|
| Reached same terminal state | bool |
| Used fewer steps | original.steps - replay.steps |
| Used fewer tokens | original.tokens - replay.tokens |
| Used fewer USD | original.usd - replay.usd |
| Tool-set divergence | Jaccard distance between tools used |
| Off-script irreversibles | tools called in replay that weren't in original |
| Unmatched tool calls | count from replay runtime |
| Final-response similarity | judge-LLM score (0-1) |

Aggregate across 500 traces:

```yaml
replay_report:
  feature: support_copilot
  candidate: { prompt: "v2.3", model: "claude-x", tool_set: "v1.5" }
  baseline:  { prompt: "v2.2", model: "claude-x", tool_set: "v1.5" }
  sample_size: 500
  same_terminal_rate: 0.94
  median_step_delta: -1         # candidate uses 1 fewer step on average
  median_token_delta: -1200
  median_usd_delta: -0.04
  off_script_irreversibles_rate: 0.002   # 0.2% of replays
  unmatched_tool_calls_rate: 0.018
  final_response_similarity_p50: 0.86
  regressions:
    - trace_id: tsk_abc, reason: "candidate called payment_refund unexpectedly"
    - trace_id: tsk_xyz, reason: "candidate exceeded step budget"
```

## CI Integration

```yaml
name: agent-replay-eval
on:
  pull_request:
    paths:
      - "prompts/agents/**"
      - "agents/**"
      - "tool_registry/**"
jobs:
  replay-eval:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Pull sanitised replay corpus
        run: ./scripts/pull-replay-corpus.sh --feature=$(cat changed-features.txt) --size=500
      - name: Run replay
        run: python -m eval.replay --candidate-from-pr --baseline=production --report=replay.json
      - name: Check thresholds
        run: python -m eval.check_replay_thresholds replay.json
      - name: Comment PR
        uses: marocchino/sticky-pull-request-comment@v2
        with:
          path: replay-summary.md
```

Thresholds:

```yaml
same_terminal_rate_min: 0.92
off_script_irreversibles_rate_max: 0.005
unmatched_tool_calls_rate_max: 0.05
final_response_similarity_p50_min: 0.80
```

## Sanitised Replay Corpus

Production traces contain PII. The replay corpus is:

1. Sampled from production.
2. Stripped of PII at extraction (email, name, phone, free-text content fields).
3. Stored in a separate read-only bucket.
4. Refreshed weekly.

Goldens for sanitisation rules: a probe set asserts no PII patterns survive after extraction.

## Deterministic Replay

For debugging ("what would the agent do differently?"), the replay runtime supports a `deterministic_seed` so the candidate's LLM calls are seeded (where the provider supports it). This is the basis for the "explain why" surface in `ai-agent-observability-and-replay`.

## Cost of Replay

Replaying 500 traces with a flagship model + judge-LLM scoring runs ~$10-50 depending on feature. Run on every PR that touches an agent. The cost replaces a much more expensive production rollback.

## Anti-Patterns

- Replay against live tools. Charges real cards, sends real emails.
- Replay without PII sanitisation. CI logs leak production data.
- Replay corpus that's a single day's traffic. Misses weekly patterns.
- Scoring only "same terminal state". Ignores efficiency gains.
- Replay corpus not refreshed. Eval drifts from current usage.
- Treating "unmatched tool calls" as failure without inspection — sometimes the candidate is smarter and asks something the original didn't think to.
