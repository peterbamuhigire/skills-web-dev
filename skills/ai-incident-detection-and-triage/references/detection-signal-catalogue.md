# AI Detection Signal Catalogue

Every AI signal that can fire an incident, with threshold, owner, runbook link, severity rule. This is the canonical list; new AI features must register their signals here before they ship.

## Schema

```yaml
- id: hallucination_burn_rate_2x
  source: ai-hallucination-slo-and-grounding
  signal: hallucination_rate
  window: 1h
  threshold: 2x_slo
  evaluator: burn_rate
  scope_dims: [feature_id, tenant_tier, tenant_id, region]
  default_severity: sev-2
  escalation_rules:
    - if: scope_dim.tenant_id in HIGH_RISK_TENANTS
      severity: sev-1
    - if: scope_dim.autonomy == "agent_acts_irreversibly"
      severity: sev-1
  owner_rotation: ai_product_oncall
  runbook: ai-incident-response-runbook#hallucination-spike
  evidence_required:
    - trace_bundle
    - prompt_version
    - model_version
    - retrieval_set_sample
    - eval_at_incident_time
```

## Quality Signals

| id | window | threshold | default sev | rotation | runbook |
|---|---|---|---|---|---|
| `hallucination_burn_rate_2x` | 1h | 2× SLO | sev-2 | ai-product | hallucination-spike |
| `hallucination_burn_rate_5x` | 1h | 5× SLO | sev-1 | ai-product | hallucination-spike |
| `citation_accuracy_drop` | 6h rolling | -10pp | sev-2 | ai-product | hallucination-spike |
| `abstain_rate_drop` | 6h rolling | -20% from baseline | sev-2 | ai-product | prompt-drift |
| `refusal_rate_spike` | 1h | +50% from baseline | sev-2 | ai-platform | model-regression |
| `eval_suite_regression` | daily | -5 points overall, -10 points any subset | sev-2 | ai-product | eval-drift |
| `judge_calibration_drift` | weekly | judge-vs-human kappa < 0.6 | sev-3 | ai-product | eval-drift |

## Retrieval Signals

| id | window | threshold | default sev | rotation | runbook |
|---|---|---|---|---|---|
| `retrieval_miss_rate` | 1h | >15% (was <5%) | sev-2 | data | retrieval-drift |
| `topk_score_collapse` | 1h | median top-1 score -30% | sev-2 | data | retrieval-drift |
| `citation_dangling_rate` | 1h | citations pointing to missing chunks >2% | sev-2 | data | retrieval-drift |
| `chunk_quality_drift` | daily | mean chunk length / token-quality drift >20% | sev-3 | data | retrieval-drift |

## Tool / Agent Signals

| id | window | threshold | default sev | rotation | runbook |
|---|---|---|---|---|---|
| `irreversible_action_rate` | 1h | >2× baseline | sev-2 | ai-product | agent-action |
| `tool_error_rate` | 15m | per-tool error >10% | sev-2 | ai-platform | tool-vendor-outage |
| `tool_schema_mismatch_rate` | 1h | >1% | sev-2 | ai-platform | tool-vendor-outage |
| `action_approval_bypass_rate` | any | >0 (single occurrence) | sev-1 | security + ai-product | agent-action |

## Safety Signals

| id | window | threshold | default sev | rotation | runbook |
|---|---|---|---|---|---|
| `jailbreak_classifier_hits` | 1h | >5× baseline | sev-2 | security | jailbreak |
| `confirmed_jailbreak_with_data_exfil` | any | >0 | sev-1 | security | jailbreak |
| `pii_in_output_rate` | 1h | >0.1% | sev-2 | security | jailbreak |
| `cross_tenant_leak_classifier_hits` | any | >0 | sev-1 | security | jailbreak |
| `indirect_injection_marker` | 1h | per-tool >5/h | sev-2 | security | jailbreak |

## Cost Signals

| id | window | threshold | default sev | rotation | runbook |
|---|---|---|---|---|---|
| `tenant_cost_anomaly_z3` | 1h | z-score > 3 | sev-3 | ai-platform | cost-runaway |
| `tenant_cost_anomaly_z5` | 1h | z-score > 5 | sev-2 | ai-platform | cost-runaway |
| `feature_cost_anomaly` | 1h | feature total > 3× rolling 7d median | sev-2 | ai-platform | cost-runaway |
| `feature_cost_runaway` | 1h | feature total > 10× rolling 7d median | sev-1 | ai-platform | cost-runaway |
| `tokens_per_request_p99_drift` | 6h | +50% | sev-3 | ai-product | prompt-drift |
| `provider_rate_limit_429_rate` | 15m | >2% | sev-2 | ai-platform | provider-incident |

## Performance Signals

| id | window | threshold | default sev | rotation | runbook |
|---|---|---|---|---|---|
| `latency_p99_regression` | 15m | +50% | sev-2 | ai-platform | provider-incident |
| `ttft_regression` | 15m | +100% | sev-3 | ai-platform | provider-incident |
| `streaming_abandonment_rate` | 1h | >10% | sev-3 | ai-product | provider-incident |

## Implementation Notes

- Each signal must register in `ops/ai/signals.yaml` as a structured record.
- Each signal's alert payload includes `runbook`, `default_severity`, `evidence_required`, `failure_class_hint` so the on-call lands on the right playbook.
- A weekly job audits the catalogue against the RCA taxonomy in `ai-rca-taxonomy/references/taxonomy-and-patterns.md` and flags any RCA class without a detection signal.
- Threshold tuning is logged with the rationale. Lowering a threshold to silence flapping requires a written justification.
