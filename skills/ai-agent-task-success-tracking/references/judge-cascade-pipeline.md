# Judge Cascade Pipeline — Implementation

Three-tier scoring pipeline: heuristic → LLM-judge → human. Production-shaped, idempotent, evidence-backed.

## Architecture

```
agent.task.completed (event)
        │
        ▼
[ judge.intake ]   (queue worker; per-feature consumer)
        │
        ▼
load success contract → run heuristic tier
        │
        ├── decisive verdict?  yes ──→ persist + emit
        │
        ├── needs LLM tier
        │   └── call cheap-pinned judge model → verdict + confidence
        │       │
        │       ├── confidence ≥ threshold ──→ persist + emit
        │       │
        │       └── confidence < threshold ──→ queue human
        │
        └── contract demands human (bespoke / shadow eval / sample)
            └── route to human_verification_queue → human verdict ──→ persist + emit
```

The same task may be processed by multiple tiers; only one final verdict row is written per `(task_id, pipeline_version)`.

## Heuristic Tier

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class HeuristicResult:
    verdict: Optional[str]   # 'resolved' | 'unresolved' | None (cascade)
    confidence: float
    signals: dict

def run_heuristic_tier(task, contract) -> HeuristicResult:
    signals = {}

    # Hard fails short-circuit unresolved
    for expr in contract.hard_signals:
        if evaluate(expr, task):
            signals[expr] = True
            return HeuristicResult(verdict='unresolved', confidence=1.0, signals=signals)
        signals[expr] = False

    # Soft signals that are pure heuristics
    heuristic_signals_pass = True
    judge_needed = False
    for name, evaluator in contract.soft_signals_required:
        if evaluator == 'heuristic':
            ok = evaluate_heuristic(name, task)
            signals[name] = ok
            heuristic_signals_pass = heuristic_signals_pass and ok
        elif evaluator == 'judge':
            judge_needed = True
        # 'literal' handled at runtime as direct field check

    if not heuristic_signals_pass:
        return HeuristicResult(verdict='unresolved', confidence=0.95, signals=signals)

    if not judge_needed:
        return HeuristicResult(verdict='resolved', confidence=0.90, signals=signals)

    # Heuristic passes; LLM judge required
    return HeuristicResult(verdict=None, confidence=0.0, signals=signals)
```

Heuristic evaluators are pure functions per feature in a registry.

## LLM Judge Tier

The judge is a *separate, cheap, pinned* model. Never the same model as the agent.

```python
def run_judge_tier(task, contract, heuristic_signals) -> JudgeVerdict:
    bundle = build_judge_bundle(task)
    # bundle includes: user goal, final response, trace summary,
    # tool outputs cited, any user follow-up within window.
    prompt = prompt_registry.get(contract.judge_prompt)
    resp = gateway.call(
        feature='success_judge',
        model_pin=prompt.model_pin,           # cheap pinned model
        prompt_template=prompt.text,
        inputs={
            'success_contract': contract.public_block(),
            'task_bundle': bundle,
            'heuristic_signals': heuristic_signals,
        },
        max_tokens=600,
        temperature=0.0,                      # judge must be deterministic
        seed=task.task_id,
    )
    parsed = parse_judge_response(resp.text)
    return JudgeVerdict(
        verdict='resolved' if parsed.resolved else 'unresolved',
        confidence=parsed.confidence,
        rationale=parsed.rationale,
        prompt_version=prompt.version,
        model_pin=resp.model_pin,
        judge_request_id=resp.request_id,
    )
```

### Judge Prompt Template (excerpt)

```
You are a strict evaluator of agent task resolution.
Your job is to decide if this task was RESOLVED according to the contract.

CONTRACT:
{success_contract}

TASK BUNDLE:
- User goal: {bundle.user_goal}
- Final agent response: {bundle.final_response}
- Tools used: {bundle.tools_summary}
- User follow-ups within {bundle.followup_window}: {bundle.followups}

HEURISTIC SIGNALS (pre-computed): {heuristic_signals}

Output strict JSON:
{
  "resolved": true|false,
  "confidence": 0.0..1.0,
  "rationale": "<one paragraph, cite evidence from bundle>",
  "uncertain_reasons": ["..."]
}

Rules:
- If the response is vague, generic, or non-actionable: resolved=false.
- If the response does not address the user goal: resolved=false.
- If the user re-opened with the same intent: resolved=false.
- Set confidence < 0.70 only when bundle is missing key signal.
```

The judge prompt is **versioned in the prompt registry** (`prompt://judges/...`); old verdicts reproduce against their original version.

## Human Tier

Trigger conditions:
- contract.sample_rate hit (random 5%)
- contract.full_when conditions met
- judge confidence below threshold (default 0.70)

```python
def route_to_human(task, contract, judge_result=None):
    review = human_verification_queue.create({
        'task_id': task.task_id,
        'tenant_id': task.tenant_id,
        'feature': task.feature,
        'priority': priority_for(task),       # bespoke > shadow > sample > low-conf
        'sla_decide_by': now() + timedelta(hours=4 if business_hour else 24),
        'context_url': f'/admin/agent/tasks/{task.task_id}',
        'judge_rationale': judge_result.rationale if judge_result else None,
    })
    return review
```

Reviewer UI loads the task viewer (`ai-agent-observability-and-replay`) and shows a three-button decision: **resolved / unresolved / cannot determine**. Reviewer must enter a rationale.

`cannot determine` cases:
- Are not counted in resolution-rate (excluded from denominator).
- Triggered an automatic escalation to the feature owner for contract clarification.
- Capped: > 10% cannot-determine in a week opens an investigation.

## Persistence

```python
def persist_verdict(task, tier, verdict, evidence_ref, contract):
    with db.transaction() as txn:
        existing = txn.fetch_one(
            'SELECT verdict FROM task_success_verdicts WHERE task_id = %s AND pipeline_version = %s',
            (task.task_id, PIPELINE_VERSION),
        )
        if existing:
            return  # idempotent
        txn.execute(
            '''
            INSERT INTO task_success_verdicts (
              task_id, tenant_id, feature, verdict, tier, confidence,
              heuristic_signals, judge_prompt_version, judge_model_pin,
              judge_rationale, judge_request_id, human_reviewer_id,
              evidence_ref, pipeline_version, created_at
            ) VALUES (...)
            ''', (...)
        )
    emit_event({
        'name': 'agent.resolution.completed' if verdict.verdict == 'resolved' else 'agent.resolution.unresolved',
        'task_id': task.task_id,
        'tenant_id': task.tenant_id,
        'feature': task.feature,
        'tier': tier,
        'verdict_id': task.task_id,
        'pipeline_version': PIPELINE_VERSION,
    })
```

The `agent.resolution.completed` event is the **billing trigger** for `ai-agent-attempted-vs-completed-billing`.

## Calibration

Quarterly:

1. Sample 200 production tasks per feature, stratified by tier (heuristic / judge / human).
2. Two independent humans label each.
3. Compute agreement:
   - human vs human (inter-rater) — target ≥ 90%; below = contract is ambiguous.
   - judge vs majority human — target ≥ 80%; below = judge needs retraining or contract refinement.
   - heuristic vs majority human — target ≥ 95%; heuristics should be conservative-correct.
4. If judge agreement drops below 80%, hold a new judge prompt PR. Re-evaluate.
5. Publish a calibration report; auditors will ask.

## Drift Monitor

```sql
-- Compare production verdict distribution to golden eval distribution
WITH prod AS (
  SELECT feature,
         SUM(CASE WHEN verdict='resolved' THEN 1 ELSE 0 END) * 1.0 / COUNT(*) AS rate
  FROM task_success_verdicts
  WHERE created_at >= NOW() - INTERVAL 7 DAY
  GROUP BY feature
), gold AS (
  SELECT feature, golden_resolved_rate AS rate FROM golden_eval_summary
)
SELECT prod.feature, prod.rate AS prod_rate, gold.rate AS golden_rate,
       (prod.rate - gold.rate) AS delta_pp
FROM prod JOIN gold USING (feature)
WHERE ABS(prod.rate - gold.rate) > 0.05;
```

> 5pp drift opens an investigation. Common causes: tenant traffic mix shifted, agent regressed, judge regressed, contract obsolete.

## Idempotency and Replay

- `task_id + pipeline_version` is the dedupe key.
- A replay (re-run the full cascade for a single task) writes to a new `pipeline_version` row; original remains for audit.
- A contract version bump produces a new `pipeline_version`; old verdicts are never mutated.

## Cost Targets

| Tier | Cost / verdict | Latency | Share |
|---|---|---|---|
| Heuristic | $0 | < 100ms | 70% |
| LLM judge | ~$0.005 | ~3s | 25% |
| Human | ~$0.50–$2.00 | hours | 5% |

Blended ~$0.04 / verdict. Budget into agent COGS via `ai-cost-per-tenant-attribution`.
