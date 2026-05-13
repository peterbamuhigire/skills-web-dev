# Evidence Bundle Spec

A bundle is a tar.gz with a strict layout and a signed manifest. This document is the canonical schema.

## Top-Level Layout

```
inc-1923.tar.gz
├── manifest.json
├── signature.txt
├── snapshots/
│   ├── prompts.json          # prompt registry state at window_end
│   ├── models.json           # model pin registry state
│   ├── index.json            # active retrieval index version per feature
│   ├── prices.json           # provider price-table snapshot
│   └── eval.json             # eval suite results last 7 days
├── traces/
│   ├── <request_id>.json     # full OTel trace per representative failing request
│   └── ...
├── prompts/
│   ├── <request_id>.json     # resolved prompt at request time
│   └── ...
├── models/
│   ├── <request_id>.json     # model + provider + region + version per request
│   └── ...
├── tools/
│   ├── <request_id>.json     # tool calls (request + response) per request
│   └── ...
├── retrieval/
│   ├── <request_id>.json     # chunks retrieved + scores + source doc ids
│   └── ...
├── audit/
│   └── window.jsonl          # AI audit log for the window
├── agent_actions/            # only if feature uses agents
│   └── window.jsonl
├── mitigations/
│   └── window.jsonl          # mitigation log entries for the incident so far
├── affected.json             # tenants affected, counts, severity per tenant
├── reproduce/
│   ├── <request_id>.py       # auto-generated reproduce scripts
│   └── ...
└── README.md                 # human-readable summary of the bundle
```

## manifest.json Schema

```json
{
  "$schema": "https://example.com/ai-evidence-bundle-v1.json",
  "incident_id": "inc-1923",
  "severity": "sev-1",
  "failure_class": "hallucination-spike",
  "signal_id": "hallucination_burn_rate_5x",
  "feature_id": "support-copilot",
  "window": {
    "start": "2026-05-11T14:00:00Z",
    "end":   "2026-05-11T15:00:00Z"
  },
  "exporter": {
    "version": "1.4.2",
    "user": "oncall@example.com",
    "host": "evidence-exporter-3"
  },
  "files": [
    {"path": "snapshots/prompts.json", "sha256": "…", "size": 12483},
    {"path": "snapshots/models.json", "sha256": "…", "size": 2104},
    ...
  ],
  "samples": {
    "total_failing_in_window": 1843,
    "sampled": 50,
    "sampling": "stratified by tenant_tier"
  },
  "affected_tenants_count": 12,
  "redaction_applied": ["email", "phone", "names", "credit_card", "api_keys"],
  "vault_unredacted_uri": "s3://evidence-vault-prod/inc-1923/unredacted.tar.gz",
  "retention_until": "2033-05-11T00:00:00Z",
  "legal_hold": false
}
```

## Per-File Specs

### snapshots/prompts.json
```json
{
  "captured_at": "2026-05-11T15:00:00Z",
  "feature": "support-copilot",
  "active_version": "v18",
  "previous_version": "v17",
  "versions": {
    "v17": {"system": "...", "developer": "...", "released_at": "2026-04-22T..."},
    "v18": {"system": "...", "developer": "...", "released_at": "2026-05-11T13:45:00Z"}
  }
}
```

### snapshots/models.json
```json
{
  "captured_at": "2026-05-11T15:00:00Z",
  "feature_pins": {
    "support-copilot": {
      "primary": "anthropic/claude-sonnet-4-5-20250929",
      "fallback_chain": ["bedrock/anthropic-claude-sonnet-4-5", "openai/gpt-4o-2024-08-06"],
      "pinned_since": "2026-04-12T..."
    }
  }
}
```

### snapshots/index.json
```json
{
  "captured_at": "...",
  "feature": "support-copilot",
  "active_index": "kb-2026-05-10-rebuild",
  "previous_index": "kb-2026-05-03-rebuild",
  "embedding_model": "text-embedding-3-large@2024-01",
  "chunk_count": 482113
}
```

### snapshots/eval.json
- One row per day for last 7 days; per-suite scores.

### traces/<request_id>.json
- Full OTel trace; spans include gateway, safety-in, retrieval, provider call, safety-out, post-processing.
- Attributes per span include `prompt_version`, `model_version`, `index_version`, `tenant_id`, `feature_id`, `request_id`.

### audit/window.jsonl
- AI audit log entries; one JSON per line. Fields per `ai-on-saas-architecture` audit schema.

### agent_actions/window.jsonl
- One row per agent action: `(task_id, step_id, tool, args, response, reversible, executed_at, by)`.

### affected.json
```json
{
  "tenants": [
    {"tenant_id": "t-9182", "tier": "enterprise", "request_count": 412, "high_risk": true},
    {"tenant_id": "t-2204", "tier": "pro",        "request_count": 87,  "high_risk": false}
  ],
  "total_requests_in_window": 1843,
  "estimated_customer_visible_failures": 412
}
```

## Sampling Strategy

Sampling is **stratified by tenant tier** to capture diverse failure modes. Default sample sizes:

| Window size | Sample |
|---|---|
| ≤ 1h | up to 50 representative failing |
| 1–6h | up to 100 |
| 6–24h | up to 200 |
| > 24h | up to 500 (separate bundle per day) |

Always include: every confirmed jailbreak/exfil; every irreversible agent action; every high-risk-tenant failure.

## Versioning

`exporter.version` is a strict semver. Breaking schema changes require a major bump and a written deprecation. Bundles are forward-compatible only within a major.

## Validation

`ai-evidence-validate <bundle.tar.gz>` runs:
- Manifest schema check.
- Per-file sha256 verification.
- Signature verification with the recorded key id.
- Cross-references intact (each `request_id` referenced in `traces/` must have `prompts/`, `models/`, etc.).
- Affected tenant count consistent with `audit/`.

Validation runs at upload time and at any read access. A failed validation raises a custody event.
