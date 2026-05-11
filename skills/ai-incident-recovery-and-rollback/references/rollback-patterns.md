# Rollback Patterns

Every rollback in an AI incident is one of these patterns. Each has: what's pinned, how to flip, how to verify, how to un-pin.

## prompt-pin

What's pinned: the prompt version for a feature.

Flip:
```sh
ai-ops gateway prompt-pin --feature support-copilot --version v17 --reason "inc-1923"
```

Verify:
- Trace `prompt_version` label = `v17` for new requests within 5 minutes.
- Faithfulness on production sample recovers within 30 minutes.

Un-pin (re-promotion):
```sh
ai-ops gateway prompt-unpin --feature support-copilot --reason "inc-1923 re-promoted to v19"
```
Pre-conditions: gate-runner pass per `eval-gated-re-promotion.md`.

State logging:
- `ai_incident_mitigation_log` entry on pin and on un-pin.
- `ai_prompt_pin_registry` row showing active pin.

## model-pin

What's pinned: the model version per feature (and optionally per region/tier).

Flip:
```sh
ai-ops gateway model-pin \
    --feature support-copilot \
    --model anthropic/claude-sonnet-4-5-20250929 \
    --reason "inc-1925"
```

Verify:
- Trace `model_version` label = pinned value.
- Quality / cost metrics recover.

Special: avoid `*-latest` references. Always pin to dated model labels. If a provider's deprecation calendar reaches the pinned model's date, open a model-migration incident class.

## index-pin

What's pinned: the retrieval index snapshot for a feature.

Flip:
```sh
ai-ops retrieval index-pin \
    --feature support-copilot \
    --snapshot-id snap-2026-05-09-good \
    --reason "inc-1929"
```

Verify:
- Retrieval spans show `index_version` = pinned value.
- Retrieval-miss rate returns to baseline.

Un-pin: must include the embedding-model version check; if the embedding model changed, re-embedding is a pre-condition.

## tool-pin / tool-disable

What's pinned: the tool's version (or "disabled" state) per feature.

Flip (disable):
```sh
ai-ops agent tool-disable --feature draft-assistant --tool slack_send --reason "inc-1931"
```

Flip (version-pin):
```sh
ai-ops agent tool-pin --feature draft-assistant --tool slack_send --version v3.2 --reason "inc-1931"
```

Verify:
- Tool-call traces show the pinned version (or zero calls if disabled).
- Tool-error rate returns to acceptable.

Un-pin: contract test against the live tool passes; the agent's eval suite using the tool passes.

## gateway routing pin

What's pinned: the provider/region per feature.

Flip:
```sh
ai-ops gateway routing-pin --feature support-copilot --provider bedrock --reason "inc-1930"
```

Verify:
- Provider distribution shifts; error rate drops; latency stable.

Un-pin: provider's status page green for N days; eval comparing both providers on goldens still acceptable for the desired provider.

## per-tenant feature pause

What's paused: the feature for one or a list of tenants.

Flip:
```sh
ai-ops feature pause --feature support-copilot --tenant t-9182 --reason "inc-1923, customer request"
```

Verify:
- Per-tenant call rate drops to ~0 within 60s.

Un-pause: customer consent confirmed; underlying root cause addressed; per-tenant smoke test pass.

## quota cap

What's capped: tokens/cost/requests per scope.

Flip:
```sh
ai-ops gateway quota-cap --feature support-copilot --max-tokens-per-min 1000000 --reason "inc-1927"
```

Verify:
- Cost rate plateaus at cap.

Un-cap: root cause addressed; cap value reviewed; soft cap retained at lower level.

## full feature rollback

What's rolled back: the feature flag's variant for everyone (or a tier).

Flip:
```sh
flag-platform set ai.support-copilot.variant = previous --scope all
```

Verify:
- Variant distribution shifts; metrics recover.

Un-rollback: new variant with fixes passes shadow + canary stages per `eval-gated-re-promotion.md`.

## Combined Pin Decision Tree

If multiple pins are needed (e.g., prompt-pin and index-pin both apply), pin in this order:
1. Most-specific cause first (prompt before model; index before chunk-quality-fix).
2. Verify containment after each pin; do not bundle pins without observing the effect of each.

## Make-Permanent Rule

A pin is "permanent" only when:
- Postmortem decision documents the choice.
- `ai_*_pin_registry` row's `pinned_by_incident` is cleared and `permanent: true` flag is set.
- Removal of the pin is scheduled or formally declined ("we are on v17 indefinitely until X").

Without these, a pin is "active rollback" and shows on the open-rollback list reviewed weekly.

## Anti-Patterns

- Pin set; no `reason` populated. Postmortem can't reconstruct intent.
- Pin set in one environment, not propagated to all regions / replicas.
- Pin-set logs missing from `ai_incident_mitigation_log` — observability gap.
- Un-pin during off-hours without on-call coverage.
- Two pins set for the same feature with conflicting intent.
- "Pin" via PR + deploy instead of an operator surface — too slow at 02:14.
