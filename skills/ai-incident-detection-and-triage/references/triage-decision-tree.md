# AI Triage Decision Tree

When paged on an AI signal, the on-call engineer follows the right branch and reaches a **failure class** in ≤ 10 minutes (sev-1) or ≤ 30 minutes (sev-2). The class label then routes to the right playbook in `ai-incident-response-runbook`.

## Branch 0: Universal First Step

Before branching, check:
- Is the platform itself green? (5xx rate, latency on non-AI endpoints, gateway health.) If platform is red, this might not be AI-specific.
- Is the foundation-model provider's status page green? (Anthropic, OpenAI, Bedrock, etc.) If red, see `provider-incident` playbook.
- Was there a deploy in the last 24h? (Check release log: code, prompts, model version pin, retrieval index version, eval gates.) Note all of them.
- Was there an infra change? (Region failover, gateway routing change.) Note it.

These four facts go on the incident channel within 2 minutes.

## Branch 1: Hallucination / Quality Burn

Signal: `hallucination_burn_rate_*`, `citation_accuracy_drop`, `abstain_rate_drop`.

Check in order:
1. **Eval drift vs production drift?** Compare daily golden-suite score with production sample faithfulness. If only production drifted, real regression. If both drifted, real regression. If only eval drifted, judge or golden-set issue → `eval-drift`.
2. **Deploy in last 24h?**
   - Prompt change → `prompt-drift`.
   - Model version change → `model-regression`.
   - Retrieval index rebuild → `retrieval-drift`.
   - Embedding model change → `retrieval-drift`.
3. **Is it tenant-specific?** Split metric by `tenant_id`. If concentrated on one or few tenants, look at their data (customer-data evolution, new content types) → `data-shift`.
4. **Is the judge calibrating?** If `judge_calibration_drift` also firing, it might be the meter, not the meal → `eval-drift`.
5. **Provider-side regression?** Check provider status page and changelog. Foundation models can silently change behaviour → `model-regression`.

If none of the above explains it within 15 minutes, classify as `unknown-quality-regression`, freeze the feature (abstain-mode), and continue investigation.

## Branch 2: Cost Anomaly

Signal: `tenant_cost_anomaly_*`, `feature_cost_anomaly`, `feature_cost_runaway`.

Check in order:
1. **Provider price change?** Pull provider price-table snapshot from yesterday vs today. If price changed → `commercial-incident`.
2. **Prompt bloat?** Check `tokens_per_request_p99` for the affected feature; if it rose, recent prompt change inflated tokens → `prompt-drift` with cost lens.
3. **Loop?** Check if any agent is in a retry loop or a tool-call loop. Look at step-distribution per task → `agent-action`.
4. **Tenant-side?** A single tenant integrated a noisy webhook or runs a load test. Per-tenant breakdown → not an incident, but a quota event → notify tenant, raise tier cap if Enterprise.
5. **Provider rate-limit downgrade / fallback chain misfiring?** Check fallback-chain metrics. If we're falling back to the expensive model unnecessarily → `gateway-misconfig`.

## Branch 3: Retrieval Drift

Signal: `retrieval_miss_rate`, `topk_score_collapse`, `citation_dangling_rate`.

Check in order:
1. **Index rebuild in last 24h?** If yes, suspect index version → `retrieval-drift`.
2. **Embedding model change?** Embedding-model version pin moved → `retrieval-drift / embedding-change`.
3. **Chunk-quality drift?** New content ingested with different shape (very long PDFs, scans) → `data-evolution`.
4. **Index corruption?** Spot-check a known query and verify the expected chunk is retrievable.
5. **Permissions?** Per-tenant filters broken (e.g., tenant ID filter dropping correct chunks) → `tenant-isolation-bug`.

## Branch 4: Safety / Jailbreak

Signal: `jailbreak_classifier_hits`, `confirmed_jailbreak_with_data_exfil`, `pii_in_output_rate`, `cross_tenant_leak_classifier_hits`, `indirect_injection_marker`.

Check in order:
1. **Confirmed exfil?** Pull the trace, check the output. If real data leaked → **sev-1**, security on-call leads, freeze feature, evidence bundle now.
2. **Classifier-only or real?** If only the classifier fired, sample 20 events; if all false positives, the classifier is flapping → `safety-classifier-flap` (don't disable the classifier in production until proven).
3. **Vector of attack?** Direct (user input) vs indirect (tool output, retrieved chunk, web page). Look at the trace's input layer chain → `direct-injection` or `indirect-injection`.
4. **Cross-tenant?** Was the leaked data from another tenant? → tenant-isolation incident, security + privacy lead.

## Branch 5: Tool / Agent

Signal: `tool_error_rate`, `tool_schema_mismatch_rate`, `irreversible_action_rate`, `action_approval_bypass_rate`.

Check in order:
1. **Vendor outage?** Check the tool's status page → `tool-vendor-outage`.
2. **Schema change?** Diff the tool's OpenAPI / SDK against last week. Vendor changed the contract → `tool-vendor-change`.
3. **Agent escalation?** Did the agent use one tool's output to invoke a higher-privilege tool outside its approved scope? → `agent-action / action-escalation` — **sev-1**, freeze agent.
4. **Bypassed approval?** Did the agent take an action that should have required approval? → `agent-action / bypass` — **sev-1**, freeze agent.

## Branch 6: Provider Latency / 5xx

Signal: `latency_p99_regression`, `ttft_regression`, `provider_rate_limit_429_rate`.

Check in order:
1. **Provider status page red?** → `provider-incident`. Activate fallback chain.
2. **Our gateway?** Per-stage latency in the gateway breakdown — is the latency in the provider call or in safety filters / retrieval?
3. **Region issue?** Region-scoped failover. Activate alternate region.

## Decision-Tree Tooling

```python
# tools/triage.py — a thin CLI that asks the questions and ends with a class label.
import sys, json
from dataclasses import dataclass

@dataclass
class Branch:
    signal_class: str
    checks: list  # ordered list of (prompt, follow_up_dict)

# (skeleton — full tree maintained in YAML at ops/ai/triage-tree.yaml)
```

A simple operator-facing CLI walks the tree and emits a classification + the matching playbook anchor. Keep it in version control; review every quarter against postmortem trends.

## Failure to Classify

If after 15 minutes (sev-1) or 30 minutes (sev-2) no class fits, classify as `unknown` and:
- Freeze the affected feature (abstain-mode or kill-switch).
- Pull a full evidence bundle (`ai-incident-evidence-capture`).
- Escalate to the next rotation tier.
- Open the incident with "unknown failure class" so postmortem captures the gap.
