# Model Price Table Template — Reference

The price table is checked into the gateway repo and reviewed like any other production artifact. Pricing changes are PRs.

## Format

```yaml
# pricing/prices.yaml
version: "2026-05-11"
currency: USD
effective_from: 2026-05-01T00:00:00Z   # when this row applies
notes: |
  Updated when providers re-price.
  Append-only by `effective_from`; resolver picks the row valid at request time.

models:
  # Anthropic
  - key: anthropic:claude-3.7-sonnet
    family: anthropic
    model: claude-3.7-sonnet
    context_tokens: 200000
    input_per_1k:  0.003
    output_per_1k: 0.015
    cache_write_per_1k: 0.00375     # if prompt caching used
    cache_read_per_1k:  0.0003
    image_per_image: 0.0048
    regions: [us-east-1, eu-west-1, ap-southeast-1]
    capabilities: [text, vision, tools, streaming, json-mode, prompt-cache]

  - key: anthropic:claude-3-haiku
    family: anthropic
    model: claude-3-haiku
    context_tokens: 200000
    input_per_1k:  0.00025
    output_per_1k: 0.00125
    regions: [us-east-1, eu-west-1]
    capabilities: [text, tools, streaming, json-mode]

  # OpenAI
  - key: openai:gpt-4o
    family: openai
    model: gpt-4o
    context_tokens: 128000
    input_per_1k:  0.005
    output_per_1k: 0.015
    image_per_image: 0.00765
    regions: [us, eu]
    capabilities: [text, vision, tools, streaming, json-mode]

  - key: openai:gpt-4o-mini
    family: openai
    model: gpt-4o-mini
    context_tokens: 128000
    input_per_1k:  0.00015
    output_per_1k: 0.0006
    regions: [us, eu]
    capabilities: [text, vision, tools, streaming, json-mode]

  # Bedrock-hosted Anthropic (different pricing)
  - key: bedrock:anthropic.claude-3-5-sonnet
    family: bedrock
    model: anthropic.claude-3-5-sonnet
    context_tokens: 200000
    input_per_1k:  0.003
    output_per_1k: 0.015
    regions: [us-east-1, eu-central-1]
    capabilities: [text, vision, tools, streaming, json-mode]

  # Self-hosted vLLM (cost = infra; treated as a flat per-hour amortised)
  - key: selfhost:llama-3.1-70b-instruct
    family: selfhost
    model: llama-3.1-70b-instruct
    context_tokens: 128000
    amortised_per_1k_in:  0.0002
    amortised_per_1k_out: 0.0008
    regions: [eu-west-1]
    capabilities: [text, streaming, json-mode]
```

## Resolver

```python
class PriceResolver:
    def __init__(self, table_path):
        self.snapshots = self._load_versioned(table_path)

    def cost(self, model_key, ts, tokens_in, tokens_out, **extras):
        row = self._row_at(model_key, ts)
        c = (tokens_in / 1000) * row["input_per_1k"] \
          + (tokens_out / 1000) * row["output_per_1k"]
        if "cache_read_tokens" in extras and "cache_read_per_1k" in row:
            c += (extras["cache_read_tokens"] / 1000) * row["cache_read_per_1k"]
        if "images" in extras and "image_per_image" in row:
            c += extras["images"] * row["image_per_image"]
        return round(c, 6)
```

A request from May 10 uses the row whose `effective_from <= 2026-05-10`. A request from April 20 uses the previous snapshot. Historical costs never change.

## Process

1. Provider announces a price change.
2. PR adds a new entry with the new `effective_from`.
3. CI runs cost-table tests (known token sets → known USD totals on fixed dates).
4. Merge.
5. The price change applies to new requests from `effective_from`; historical reports stay correct.

## Self-hosted models

For self-hosted LLMs (vLLM / TGI / Triton), `amortised_per_1k_*` is derived from:

```
amortised_per_1k = (instance_hourly_cost * 24 * 30) / monthly_tokens_in_or_out
```

Re-derive monthly from observed throughput. Always overestimate by 15% to cover idle time.

## Self-tests

```python
@pytest.mark.parametrize("model,ti,to,expected", [
    ("anthropic:claude-3.7-sonnet", 1000, 1000, 0.018),
    ("anthropic:claude-3-haiku",    1000, 1000, 0.0015),
    ("openai:gpt-4o",               1000, 1000, 0.02),
])
def test_price_table(model, ti, to, expected):
    assert PriceResolver("pricing/prices.yaml").cost(model, NOW, ti, to) == expected
```

Any PR that changes prices must update tests; CI fails on drift.
