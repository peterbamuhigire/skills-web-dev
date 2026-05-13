# BAA (Business Associate Agreement) Implications for LLM Providers

A BAA is required between a Covered Entity (or upstream Business Associate) and any vendor that creates, receives, maintains, or transmits PHI on its behalf — including LLM providers reached over an API.

This document is the engineering reference for deciding which LLM provider can power which PHI-scoped agent.

---

## 1. Who Needs a BAA

| Party | BAA Status |
|---|---|
| Your SaaS (the platform) | Business Associate to Covered Entity tenants |
| LLM provider (OpenAI, Anthropic, AWS Bedrock, Azure OpenAI, Google Cloud Vertex, ...) | Subcontractor → must sign BAA with you |
| Self-hosted models on your infrastructure | No external BAA; internal controls apply |
| Open-source models hosted by a third party | BAA with the host |

Without a BAA in place, the platform cannot disclose PHI to the provider. "Test" or "PoC" with real PHI is the most common breach root cause; mock data only outside the BAA boundary.

## 2. BAA Decision Tree

```
agent feature with PHI scope = read_phi | write_phi | transmit_phi | clinical_write
│
├── Will the LLM provider see PHI?
│   ├── NO (PHI redacted before leaving your boundary; provider receives masked tokens only)
│   │   └── BAA still recommended for residual disclosure risk; some providers refuse zero-PHI claims
│   └── YES
│       ├── Does provider offer BAA?
│       │   ├── NO → BLOCK
│       │   │   └── Choose a BAA-offering alternative OR descope feature OR redact aggressively
│       │   └── YES
│       │       ├── BAA signed and current revision?
│       │       │   ├── NO → BLOCK until signed
│       │       │   └── YES → continue
│       │       ├── Zero-retention configured?
│       │       │   ├── NO → escalate to HIPAA Security Officer; default DENY
│       │       │   └── YES → continue
│       │       ├── Training opt-out configured?
│       │       │   ├── NO → BLOCK (training on PHI is unauthorised use)
│       │       │   └── YES → continue
│       │       ├── Data residency satisfies tenant requirement?
│       │       │   ├── NO → BLOCK or route to compliant region
│       │       │   └── YES → continue
│       │       └── Scope of BAA covers this feature's PHI scope?
│       │           ├── NO → BLOCK
│       │           └── YES → ALLOW
```

## 3. Provider BAA Register

```sql
CREATE TABLE llm_provider_baa (
  provider_id           VARCHAR(64) PRIMARY KEY,
  provider_name         VARCHAR(128) NOT NULL,
  service_name          VARCHAR(128) NOT NULL,    -- e.g. "openai-gpt-4o", "anthropic-claude-3.5"
  baa_signed            BOOLEAN NOT NULL,
  baa_signed_at         DATE,
  baa_version           VARCHAR(64),
  baa_expiry            DATE,
  baa_url               VARCHAR(512),             -- internal vault URL
  zero_retention        BOOLEAN NOT NULL,
  training_opt_out      BOOLEAN NOT NULL,
  data_residency        VARCHAR(64),
  allowed_phi_scopes    JSON,                     -- ["read","write","transmit","clinical_write"]
  in_scope_features     JSON,                     -- feature ids
  reviewed_at           DATE NOT NULL,
  reviewed_by           VARCHAR(128) NOT NULL,
  next_review_due       DATE NOT NULL,
  notes                 TEXT
);
```

## 4. Provider Config as Code

The provider config is part of the change-controlled baseline. A change to `zero_retention=true → false` at the provider must be detected within 24h and trigger an incident.

```python
# compliance/baa_drift_detector.py
def detect_baa_drift():
    for row in LLMProviderBAA.all_signed():
        live = ProviderAPI(row.provider_id).get_settings()
        if live.zero_retention != row.zero_retention:
            raise BAADrift(provider=row.provider_id,
                            expected_zr=row.zero_retention,
                            observed_zr=live.zero_retention)
        if live.training_opt_out != row.training_opt_out:
            raise BAADrift(provider=row.provider_id,
                            expected_to=row.training_opt_out,
                            observed_to=live.training_opt_out)
```

Run as a daily cron + as a pre-call invariant for clinical_write features.

## 5. Common Provider Patterns (engineering notes — verify with current provider terms)

| Provider | BAA Pattern | Zero-Retention Default | Training Opt-Out |
|---|---|---|---|
| OpenAI Enterprise / API | Available on Enterprise; project-level | Configurable via Enterprise / Zero Data Retention | Default opt-out for API |
| Azure OpenAI | Available under Microsoft BAA | Configurable | Default opt-out |
| AWS Bedrock | Available under AWS BAA | Default (no provider retention) | Default opt-out |
| GCP Vertex AI | Available under Google BAA | Default | Default opt-out |
| Anthropic Enterprise | Available on Enterprise; tenant-level | Configurable | Default opt-out |
| Self-hosted (Llama, Mistral, etc.) | N/A — controls are internal | N/A | N/A |

**Confirm current terms with your legal team — provider terms change.** Do not paste this table into a contract; verify before each new contract.

## 6. Subcontractor / Subprocessor Disclosure

The BAA chain extends downstream:

- Platform → Tenant (Covered Entity)  uses platform as BA
- Platform → LLM Provider              provider is BA to platform
- Provider → Cloud Provider             cloud is BA to provider
- Provider → Their LLM hosts            hosts in BA chain

The platform's privacy notice and DPA must list every LLM provider as a subprocessor. The subprocessor list is one of the auditor's first asks.

## 7. Breach Notification Through the BAA Chain

If the provider experiences a breach affecting your tenants' PHI:

- Provider notifies platform within 60 days (per BAA § 164.410).
- Platform notifies affected Covered Entity tenants without unreasonable delay.
- Covered Entity tenants notify individuals within their 60-day clock.

Your incident response runbook must include a "BAA-chain breach received from provider" branch. The platform is liable to its tenants for timely notification.

## 8. End-of-Service Procedures

When you stop using a provider:

- Confirm provider deletes residual PHI per BAA termination clause.
- Obtain a deletion attestation.
- Archive the deletion attestation alongside the historical BAA in the vault.
- Update the subprocessor list and notify tenants.

The deletion attestation is the evidence artefact for §164.308(b)(1) at decommissioning.

## 9. Engineering Anti-Patterns

- BAA signed but enterprise / project / org-level zero-retention not configured. PHI persists at provider.
- BAA covers "API calls" but feature uses provider's eval / monitoring UI — out of BAA scope.
- Provider changes their BAA template; old BAA still in your register; gap until you re-sign.
- Subprocessor list out of date; auditor cross-checks vs your incident pages.
- Training opt-out configured at API key creation but a different API key (without opt-out) is used in production.
- "We don't send PHI to the provider — we mask it" — but the mask is reversible to anyone with the key, and the provider gets the key.
