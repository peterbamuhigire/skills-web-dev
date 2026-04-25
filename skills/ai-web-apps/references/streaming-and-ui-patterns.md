# Streaming, UI, and Multi-Modal Patterns

Parent skill: [`ai-web-apps/SKILL.md`](../SKILL.md).

Reference for the UI-facing parts of an AI web app: streaming route handlers, the `useChat` hook, `streamUI` with async-generator tool rendering, multi-modal image input, and middleware composition. These are implementation patterns, not contracts.

## Streaming route handler

```ts
// app/api/chat/route.ts
import { streamText } from 'ai';
import { getSupportedModel } from '@/lib/ai/factory';
import { ChatRequestSchema } from '@/lib/ai/request-schema';

export async function POST(req: Request) {
  const parsed = ChatRequestSchema.safeParse(await req.json());
  if (!parsed.success) return Response.json({ error: 'Invalid request' }, { status: 400 });

  const { messages, provider, model } = parsed.data;
  const result = await streamText({
    model: getSupportedModel(provider, model),
    system: 'You are a helpful assistant.',
    messages,
    maxTokens: 1024,
  });
  return result.toDataStreamResponse();
}

export const maxDuration = 30;
```

Rules:

- `maxTokens` is mandatory on every call. Missing it is a cost incident waiting to happen.
- `maxDuration` on the route is set to cover p95 + headroom, not p99.
- Ledger write happens in `onFinish`, after the stream closes, using the real token counts.

## Client chat UI

```tsx
'use client';
import { useChat } from 'ai/react';

export default function ChatPage() {
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat({
    api: '/api/chat',
    body: { provider: 'gemini', model: 'models/gemini-2.0-flash' },
  });

  return (
    <div className="flex h-screen flex-col">
      <div className="flex-1 space-y-4 overflow-y-auto p-4">
        {messages.map((m) => (
          <div key={m.id} className={m.role === 'user' ? 'text-right' : 'text-left'}>
            <span className="inline-block rounded bg-gray-100 px-3 py-2">{m.content}</span>
          </div>
        ))}
        {isLoading && <span className="animate-pulse">Thinking...</span>}
      </div>
      <form onSubmit={handleSubmit} className="flex gap-2 border-t p-4">
        <textarea
          value={input}
          onChange={handleInputChange}
          className="flex-1 rounded border p-2"
        />
        <button type="submit" disabled={isLoading}>
          Send
        </button>
      </form>
    </div>
  );
}
```

UX rules:

- Stream responses — never wait for full completion before showing anything.
- Show a typing indicator immediately on submit.
- Disable the submit button while `isLoading` to prevent duplicate requests.
- Auto-scroll on new message, but suspend auto-scroll if the user has scrolled up.
- Render markdown through a sanitising component. Never `dangerouslySetInnerHTML`.
- Offer a retry control on errors; LLM APIs fail routinely and users expect retry UX.

## streamUI with tool-call generators

`streamUI` lets a tool call yield interim UI while it executes, then resolve to a final component.

```typescript
import { streamUI } from 'ai/rsc';
import { z } from 'zod';

export async function streamWeatherUI(input: string) {
  const result = await streamUI({
    model: getSupportedModel('openai', 'gpt-4'),
    messages: [{ role: 'user', content: input }],
    text: ({ content }) => <ChatBubble text={content} />,
    tools: {
      getWeather: {
        description: 'Get current weather for a city',
        parameters: z.object({ city: z.string().min(1).max(64) }),
        generate: async function* ({ city }) {
          yield <LoadingSpinner city={city} />;
          const weather = await fetchWeather(city);
          return (
            <WeatherCard
              city={city}
              temp={weather.temp}
              condition={weather.condition}
            />
          );
        },
      },
    },
  });
  return { display: result.value };
}
```

Rules:

- Every tool's `parameters` schema has bounded strings. No `z.string()` without `.max()`.
- Interim `yield` components are skeletons — do not show speculative data there.
- The final returned component is the only one that renders real data.

## Multi-modal image input

```typescript
// server: process image + text together
const processMessages = (
  messages: Message[],
  imageData?: { base64: string; mimeType: string }
) => {
  if (!imageData || !messages.length) return messages;
  const last = messages[messages.length - 1];
  if (last.role === 'user') {
    last.content = [
      { type: 'text', text: typeof last.content === 'string' ? last.content : '' },
      { type: 'image', image: `data:${imageData.mimeType};base64,${imageData.base64}` },
    ];
  }
  return messages;
};

// client: file → base64
const handleFileUpload = (file: File) => {
  if (file.size > 5 * 1024 * 1024) throw new Error('Image too large');
  if (!['image/png', 'image/jpeg', 'image/webp'].includes(file.type)) {
    throw new Error('Unsupported type');
  }
  const reader = new FileReader();
  reader.onload = (e) =>
    setImageData({
      base64: (e.target?.result as string).split(',')[1],
      mimeType: file.type,
    });
  reader.readAsDataURL(file);
};
```

Rules:

- Validate size, type, and dimensions client-side and re-validate server-side.
- Images count heavily against token budgets; include them in cost estimation.
- Strip EXIF before sending to third-party providers — GPS metadata is PII in many jurisdictions.

## Composable middleware pipeline

```typescript
// middleware.ts
import { NextResponse } from 'next/server';

const composeMiddleware =
  (middlewares: Function[]) => async (request: Request) => {
    for (const fn of middlewares) {
      const result = await fn(request);
      if (result?.response) return result.response;
      if (result?.continue === false) break;
    }
    return NextResponse.next();
  };

const handleCORS = async (req: Request) => {
  const origin = req.headers.get('origin');
  if (origin && !allowedOrigins.includes(origin)) {
    return { response: new Response('CORS error', { status: 403 }) };
  }
};

const rateLimit = async (req: Request) => {
  const { success } = await upstashRatelimit.limit(req.ip ?? '127.0.0.1');
  if (!success) {
    return { response: new Response('Too many requests', { status: 429 }) };
  }
};

const authenticate = async (req: Request) => {
  const token = req.headers.get('authorization')?.split(' ')[1];
  if (!token) return { response: new Response('Unauthorized', { status: 401 }) };
};

export default composeMiddleware([handleCORS, rateLimit, authenticate]);
export const config = { matcher: '/api/:path*' };
```

Pipeline ordering matters:

1. CORS — cheapest rejection.
2. Rate limit per IP — stops abusers before authentication cost.
3. Authenticate — identifies the user.
4. Module gate + budget guard — run inside the route, not middleware, because they need feature context.

## Tool / function calling (non-streaming)

```ts
import { streamText, tool } from 'ai';
import { z } from 'zod';

const result = await streamText({
  model: getSupportedModel('openai', 'gpt-4'),
  tools: {
    getWeather: tool({
      description: 'Get current weather for a city',
      parameters: z.object({
        city: z.string().min(1).max(64),
        unit: z.enum(['celsius', 'fahrenheit']).default('celsius'),
      }),
      execute: async ({ city }) => ({ temperature: 22, condition: 'Sunny', city }),
    }),
  },
  messages: [{ role: 'user', content: "What's the weather in London?" }],
});
```

Tool authority rules live in `references/mcp-integration.md`.

## Light-weight IP rate limit (LRU fallback)

```ts
import { LRUCache } from 'lru-cache';
const cache = new LRUCache<string, number>({ max: 500, ttl: 60_000 });

export function checkRateLimit(id: string, limit = 10): boolean {
  const n = cache.get(id) ?? 0;
  if (n >= limit) return false;
  cache.set(id, n + 1);
  return true;
}
```

Use this for local dev or single-instance deployments only. Production uses Redis-backed sliding window (e.g. Upstash) so limits span all instances.
