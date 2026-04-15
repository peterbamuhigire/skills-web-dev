# Output Validation and Guardrails

Parent skill: [`ai-web-apps/SKILL.md`](../SKILL.md).

Validation and guardrail rules for AI output are one of this skill's four formal outputs. Every byte returned by a model is untrusted until a guard has passed it. This reference covers the structural, semantic, and render-time guards that sit between the model and the user or the database.

Defence-in-depth belongs to `ai-security` and `llm-security`. This reference covers the concrete web-app enforcement points.

## The three guard layers

| Layer | Guards | Failure mode if missing |
|---|---|---|
| Structural | Zod schema on `generateObject`, JSON-schema tool params | Silent data corruption, crashes downstream |
| Semantic | Business rules, allow-lists, range checks, PII scrubbing | Valid-looking nonsense reaches users or DB |
| Render | Markdown-only rendering, HTML sanitiser, URL allow-list | XSS, phishing redirect, stored attacks |

Skip any layer and you import that layer's failure mode into production.

## Layer 1 — Structural

Use `generateObject` with a Zod schema whenever the downstream consumer expects a specific shape.

```typescript
import { generateObject } from 'ai';
import { z } from 'zod';

const ReviewAnalysis = z.object({
  title: z.string().min(1).max(120),
  tags: z.array(z.string().min(1).max(32)).max(10),
  sentiment: z.enum(['positive', 'negative', 'neutral']),
  summary: z.string().max(400),
});

const { object } = await generateObject({
  model: getSupportedModel('openai', 'gpt-4'),
  schema: ReviewAnalysis,
  prompt: 'Analyse this review: "Great product, fast shipping!"',
});
```

Rules:

- The schema is the contract. If the model returns something that cannot be parsed, the route returns a 502, not a partial object.
- Schemas include range + length bounds, not just types. `z.string()` with no `max` is a DoS vector.
- For tool calling, wrap the schema in `tool({ parameters: ... })` — same rules apply.

## Layer 2 — Semantic

Structural validity is not correctness. A sentiment of `"positive"` for a one-star review is structurally valid and semantically wrong.

Guards to apply:

- Range check against business facts (e.g. `unit_price >= 0`, `discount_percent <= 100`).
- Reference integrity (e.g. returned `product_id` exists in the catalogue).
- Allow-list for categorical fields the model might hallucinate (e.g. currency codes, status strings).
- PII scrubbing on any free-text summary before persistence.
- Confidence threshold: if the model returns a confidence field below the feature's bar, route to human review instead of auto-acting.

```typescript
function assertSemantic(object: ReviewAnalysis, context: { catalogueIds: Set<string> }) {
  if (object.tags.length === 0) throw new GuardError('EMPTY_TAGS');
  if (containsPII(object.summary)) throw new GuardError('PII_LEAK');
  // Further business checks...
}
```

## Layer 3 — Render

Model output must never reach the DOM as HTML. Two rules:

- Render as Markdown through a sanitising component (`react-markdown` with `rehype-sanitize`).
- Never pass model output to `dangerouslySetInnerHTML`, even through a "safe" wrapper.

Links and images inside AI output are separately hazardous:

| Concern | Rule |
|---|---|
| External URLs | pass through an allow-list; deny by default |
| Images from the model | treat as untrusted; proxy through your CDN with a HEAD check |
| Markdown tables rendering HTML | disable raw HTML in the Markdown parser |
| Auto-link detection | explicit only; no heuristic autolinker on AI text |

## Guardrails against prompt injection

Prompt injection bypasses the guards by convincing the model to emit attacker-chosen structured output. Pair structural guards with:

- Trust-tiering: tool outputs fetched from the public web are `untrusted`; prompts derived from them never carry authority to trigger privileged tools.
- Instruction-hierarchy markers: keep system-prompt guardrails first; parse user content inside a clearly-labelled user block.
- Output-side filters: detect attempts to exfiltrate secrets (e.g. model returns a string that looks like an API key) and redact.

Detailed playbook: `ai-security` and `llm-security`.

## Tool-result validation

Tool outputs are model-adjacent but arrive with authority (they often cause writes). Validate them with the same Zod rigour as `generateObject`:

```typescript
const WeatherResult = z.object({
  city: z.string(),
  temperature_c: z.number().gte(-80).lte(60),
  condition: z.enum(['Sunny', 'Cloudy', 'Rain', 'Snow', 'Storm']),
});
```

If a tool can trigger writes (payment, email, deletion), do not act on its result directly from the model flow. Surface a confirmation to the user and act only on the confirmation event.

## Streaming output

For `streamText`, structural validation only happens once the stream closes. Two strategies:

- Stream the raw text to the UI for responsiveness, but do not persist or act on it until `onFinish` has validated the final object.
- For tool calls inside streams, validate each tool's parameters before executing its generator — never trust the model to keep passing the schema.

## Error shape

All guard failures emit the same response:

```json
{
  "error": {
    "code": "GUARD_FAILED",
    "guard": "structural" ,
    "detail": "tags[3] exceeds 32 chars",
    "request_id": "..."
  }
}
```

`detail` is logged server-side too; UX treats it as "try again" rather than surfacing the raw message.

## Observability

Every guard failure emits a metric: `ai.guard_failures_total{guard, feature_code, model}`. Alert on a sustained rise — it typically signals either a prompt regression or a new attack vector.
