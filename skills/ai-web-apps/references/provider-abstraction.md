# Provider Abstraction and Model Fallback

Parent skill: [`ai-web-apps/SKILL.md`](../SKILL.md).

The provider abstraction is one of this skill's four formal outputs. Downstream code must never import a provider SDK directly — it goes through this factory.

## Contract

Consumers receive:

- A single `getSupportedModel(provider, model)` function that returns a ready-to-use model instance.
- Strict allow-lists per provider. Unknown provider or model is a 4xx, not a runtime crash.
- Centralised API-key resolution from environment. Keys are never read in feature code.
- A fallback wrapper for cross-provider resilience.

## Multi-provider factory

```typescript
// lib/ai/factory.ts
import { createOpenAI } from '@ai-sdk/openai';
import { createGoogleGenerativeAI } from '@ai-sdk/google';
import { createAnthropic } from '@ai-sdk/anthropic';

const providers = {
  openai: {
    constructor: createOpenAI,
    models: ['gpt-3.5-turbo', 'gpt-4', 'gpt-4o'],
  },
  gemini: {
    constructor: createGoogleGenerativeAI,
    models: ['models/gemini-2.0-flash', 'models/gemini-2.5-flash'],
  },
  anthropic: {
    constructor: createAnthropic,
    models: ['claude-opus-4-6', 'claude-sonnet-4-6'],
  },
} as const;

export function getSupportedModel(provider: string, model: string) {
  const cfg = providers[provider as keyof typeof providers];
  if (!cfg) throw new UnsupportedProviderError(provider);
  if (!cfg.models.includes(model)) throw new UnsupportedModelError(provider, model);
  const apiKey = process.env[`${provider.toUpperCase()}_API_KEY`];
  if (!apiKey) throw new MissingCredentialError(provider);
  return cfg.constructor({ apiKey })(model);
}
```

Rules:

- Allow-list, not deny-list. A new model must be added explicitly.
- Throw typed errors so the API layer can map them to clean HTTP responses.
- Never accept a provider / model directly from request body without going through this function.

## Provider-selection decision table

| Need | Provider / model first choice | Fallback |
|---|---|---|
| Latency-critical chat, short outputs | `gemini-2.0-flash` | `gpt-3.5-turbo` |
| High-quality reasoning, long tool chains | `claude-sonnet-4-6` | `gpt-4o` |
| Cheapest structured JSON extraction | `gemini-2.0-flash` | `gpt-3.5-turbo` |
| Vision + text | `claude-sonnet-4-6` or `gpt-4o` | Gemini flash vision |
| Strict output schema adherence | `gpt-4o` with `generateObject` | Claude with tool-call schema |
| On-prem or residency constraint | self-hosted / regional deployment | fail closed, no cross-region fallback |

Wrong choice cost:

- Flash-tier model on a reasoning task: low cost, low quality, user dissatisfaction.
- Frontier model on cheap extraction: 10–30x cost multiplier for no quality gain.
- Cross-region fallback under residency constraint: compliance breach.

## Model fallback

```typescript
// lib/ai/fallback.ts
import { createFallback } from 'ai-fallback';
import { createGoogleGenerativeAI } from '@ai-sdk/google';
import { createOpenAI } from '@ai-sdk/openai';

export const primaryChatModel = createFallback({
  models: [
    createGoogleGenerativeAI({ apiKey: process.env.GEMINI_API_KEY! })('models/gemini-2.0-flash'),
    createOpenAI({ apiKey: process.env.OPENAI_API_KEY! })('gpt-3.5-turbo'),
  ],
  onError: (error, modelId) => logger.warn({ modelId, error }, 'model_fallback_triggered'),
  shouldRetryThisError: (error) => [429, 500, 502, 503, 504].includes(error.statusCode),
  modelResetInterval: 60_000,
});
```

Rules:

- Fallback only on transient provider-side errors (429/5xx). Never fall back on a 4xx caused by input.
- Emit `model_fallback_triggered` at warn-level; page on sustained fallback (>5% of requests for 5 min).
- The fallback target must be allow-listed in the factory; otherwise cost accounting breaks.

## Input validation layer

The factory assumes `(provider, model)` is pre-validated by the route. Pair it with Zod:

```typescript
// lib/ai/request-schema.ts
import { z } from 'zod';

export const ChatRequestSchema = z.object({
  messages: z
    .array(
      z.object({
        role: z.enum(['user', 'assistant', 'system']),
        content: z.string().max(4000),
      })
    )
    .max(50),
  provider: z.enum(['openai', 'gemini', 'anthropic']).default('gemini'),
  model: z.string().max(64),
});
```

Pattern: parse the request, then call `getSupportedModel` — two gates, both typed.
