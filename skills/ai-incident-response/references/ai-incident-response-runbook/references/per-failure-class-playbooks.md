# Per-Failure-Class Playbooks

Each playbook follows the same shape:
- **Detection signal**
- **First mitigation** (executed at T+10 to T+15)
- **Verification check**
- **Second mitigation** (if first fails)
- **Evidence to capture** (in addition to baseline)
- **Comms posture**
- **Recovery handoff**

Failure-class labels are canonical and map to RCA labels in `ai-rca-taxonomy/references/taxonomy-and-patterns.md`.

---

## hallucination-spike

**Detection.** `hallucination_burn_rate_2x` or `5x`; `citation_accuracy_drop`.

**First mitigation.** **Abstain-mode**: raise abstain-threshold on the affected feature so the system answers fewer queries and refuses ambiguous ones.

```sh
ai-ops feature abstain --feature support-copilot --threshold 0.85 --reason "inc-1923"
```

**Verification.** Abstain rate rises in 10 minutes; faithfulness on production sample recovers. Check eval-on-prod metric.

**Second mitigation.** Prompt-rollback to last-known-good prompt version (`prompt-pin`). If prompt rollback doesn't recover, model-pin to last-known-good model.

**Evidence.** Capture 50 failing samples with prompt+model+retrieval+output for each. Include `eval_at_incident_time` snapshot.

**Comms.** Status-page entry: "We are seeing reduced answer quality on <feature>. We have raised the conservative-answer threshold; you may see more 'I don't know' responses while we investigate."

**Recovery handoff.** `ai-incident-recovery-and-rollback`, sub-pattern `prompt-pin-and-re-promote` or `model-pin-and-re-promote`.

---

## prompt-drift

**Detection.** Deploy in last 24h matches prompt change; quality signal regressed after deploy.

**First mitigation.** **Prompt-pin** to last-known-good version (the previous prompt id).

```sh
ai-ops gateway prompt-pin --feature support-copilot --version v17 --reason "inc-1924"
```

**Verification.** Trace `prompt_version` label = `v17` across new requests; quality signal recovers within 30 min.

**Second mitigation.** Full feature rollback via flag platform if prompt-pin doesn't fix (suggests model or retrieval is also at play).

**Evidence.** Diff of v18 vs v17 prompt; eval suite results on v18 vs v17; release log for v18.

**Comms.** Sev-2: status page entry; sev-3: silent (mitigation invisible to customer).

**Recovery handoff.** Goldens + red-team tests added before v19 is composed.

---

## model-regression

**Detection.** Provider model version changed; or our pin moved; quality signal regressed.

**First mitigation.** **Model-pin** to last-known-good model version. If our pin moved unintentionally, revert pin. If provider silently changed the model behind a label like "gpt-4o-latest", switch to a dated model version.

```sh
ai-ops gateway model-pin --feature support-copilot --model anthropic/claude-sonnet-4-5-20250929 --reason "inc-1925"
```

**Verification.** Trace `model_version` label = pinned version; quality signal recovers within 30 min.

**Second mitigation.** Route to fallback provider via gateway routing pin (if fallback chain quality is acceptable on goldens).

**Evidence.** Eval suite results new model vs old; provider changelog snapshot; trace samples before/after.

**Comms.** Status-page entry referencing "underlying AI model update" without naming the provider unless contractually required.

**Recovery handoff.** Track the new model on shadow-mode; do not re-promote until eval suite + canary stage pass.

---

## jailbreak

**Detection.** `jailbreak_classifier_hits` spike, `confirmed_jailbreak_with_data_exfil`, `cross_tenant_leak_classifier_hits`, `pii_in_output_rate`.

**First mitigation.** **Tighten safety classifier threshold** on input and output; add jailbreak pattern (the actual prompt that worked) to the input deny-list at the gateway. If data exfil is confirmed, **kill-switch the feature** for affected tenant(s) immediately.

```sh
ai-ops safety pattern-add --pattern "<sanitised pattern>" --feature support-copilot --reason "inc-1926"
ai-ops feature pause --feature support-copilot --tenant <tenant-id> --reason "inc-1926"  # if exfil confirmed
```

**Verification.** Classifier-hit rate returns to baseline; replay the original jailbreak prompt — system now refuses.

**Second mitigation.** Switch to a more conservative system prompt; revoke any compromised credentials/data; rotate API keys if relevant.

**Evidence.** The exact jailbreak prompt(s); the response; what data was leaked; the affected tenant(s); the timeline from first hit to mitigation. **Chain of custody is critical here** — this evidence may be subpoenaed.

**Comms.** Sev-1 if exfil. Affected tenants notified within 30 min. EU AI Act Art. 73 clock starts; GDPR 72-hour breach clock starts if personal data leaked. Use regulator templates.

**Recovery handoff.** Red-team test added covering this attack class; safety review of the feature; threat model updated.

---

## cost-runaway

**Detection.** `feature_cost_runaway` (>10× baseline) or `tenant_cost_anomaly_z5`.

**First mitigation.** **Quota cap** at the affected scope to stop the bleed.

```sh
ai-ops gateway quota-cap --feature support-copilot --max-tokens-per-min 1000000 --reason "inc-1927"
# or per-tenant:
ai-ops gateway quota-cap --tenant <tenant-id> --max-usd-per-day 50 --reason "inc-1927"
```

**Verification.** Cost rate plateaus within 15 minutes at the cap.

**Second mitigation.** Identify the cause via the triage tree (price change → gateway routing pin to cheaper provider; prompt bloat → prompt-rollback; agent loop → agent kill-switch; fallback misfire → fix routing rule).

**Evidence.** Cost breakdown by feature × model × tenant for last 24h; price-table snapshot today vs yesterday; provider invoices if accessible; agent step-distribution if agent-driven.

**Comms.** If a single tenant: contact tenant directly, raise their cap if Enterprise, recommend a fix. If platform-wide: status page if customer-visible (e.g., higher latency from fallback chain), internal otherwise.

**Recovery handoff.** Per-feature soft caps re-tuned; per-tenant alert thresholds re-tuned; prompt-bloat regression added to release gates.

---

## agent-action

**Detection.** `irreversible_action_rate` spike, `action_approval_bypass_rate` > 0, or a customer report.

**First mitigation.** **Agent kill-switch** for the affected scope: pause all in-flight agent tasks for the feature/tenant.

```sh
ai-ops agent kill-switch --feature draft-assistant --tenant <tenant-id> --reason "inc-1928"
```

**Verification.** In-flight task count drops to 0 for scope within 60s.

**Second mitigation.** Inventory recent agent actions (action audit log); classify reversible vs irreversible. Undo reversible ones in coordination with customer. Document irreversible ones for restoration.

**Evidence.** Full action audit log for affected scope last 7 days; agent trace for failing tasks; tool calls (input + output); approval log; the prompt that triggered the action.

**Comms.** Sev-1 if irreversible customer harm. Direct tenant notification with named actions list. Possible regulator notification if irreversible action affects regulated data or finances.

**Recovery handoff.** Reversibility classification reviewed for the agent; approval gate added or tightened; red-team test added for the action escalation path.

---

## retrieval-drift

**Detection.** `retrieval_miss_rate`, `topk_score_collapse`, `citation_dangling_rate`.

**First mitigation.** **Index-pin** to last-known-good index snapshot.

```sh
ai-ops retrieval index-pin --feature support-copilot --snapshot-id snap-2026-05-09-good --reason "inc-1929"
```

**Verification.** Retrieval-miss rate returns to baseline; spot-check known query.

**Second mitigation.** Pause ingest pipeline if data is corrupting the index. Roll forward index from clean source.

**Evidence.** Index version metadata; embedding model version; sample retrieval traces before/after; recent ingestion log.

**Comms.** Usually invisible to customer; sev-2 internal.

**Recovery handoff.** Index rebuild test in CI; embedding-model upgrade procedure tightened; ingestion validation strengthened.

---

## training-data-shift / data-evolution

**Detection.** Quality regression concentrated on a tenant or content type; no deploy in last 24h.

**First mitigation.** **Abstain-mode** on affected slices (or the entire feature if slice not bound).

**Verification.** Faithfulness on the affected slice recovers.

**Second mitigation.** Add the new data shape to goldens + judge calibration set; tune prompt to handle the new shape; if the data is malformed at ingest, fix the ingest pipeline.

**Evidence.** Affected tenant's data sample; comparison with last-month's data shape; metric breakdown by content type.

**Comms.** Direct tenant notification if single-tenant; status page if broader.

**Recovery handoff.** Data-shape monitoring added; affected slices added to eval suite.

---

## provider-incident

**Detection.** `provider_rate_limit_429_rate`, `latency_p99_regression`, vendor status page red.

**First mitigation.** **Gateway routing pin** to the fallback provider for affected features. If no acceptable fallback, **read-only-mode** or **kill-switch**.

```sh
ai-ops gateway routing-pin --feature support-copilot --provider bedrock --reason "inc-1930"
```

**Verification.** Provider distribution shifts as expected within 5 min; error rate drops.

**Second mitigation.** If fallback provider degrades on goldens, hold there but raise abstain to prevent quality drop reaching customers.

**Evidence.** Provider status page snapshot; our internal latency/error metrics for the affected window; trace samples.

**Comms.** Status-page entry: "Underlying AI provider is degraded; we have switched to the backup provider and AI responses may be slightly slower / different style."

**Recovery handoff.** Fallback chain quality validated periodically; provider liaison opens a post-incident ticket; consider re-balancing routing weights.

---

## tool-vendor-outage / schema-change

**Detection.** `tool_error_rate` spike on a tool; `tool_schema_mismatch_rate`.

**First mitigation.** **Tool-disable**: instruct the gateway to refuse this tool to agents for the affected feature. Agent reverts to "I can't take that action right now" behaviour.

```sh
ai-ops agent tool-disable --feature draft-assistant --tool slack_send --reason "inc-1931"
```

**Verification.** Tool-call rate to the disabled tool drops to 0; agent error rate stabilises.

**Second mitigation.** If the tool is critical and there's a replacement, swap; otherwise hold in degraded mode.

**Evidence.** Tool error sample; vendor changelog if changed; trace samples of failing tool calls.

**Comms.** Status page if customer-visible.

**Recovery handoff.** Tool-schema validation tightened; vendor SLA reviewed; agent test cases for tool failure added.
