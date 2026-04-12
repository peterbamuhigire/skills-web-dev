---
name: ai-web-apps
description: Building AI-enhanced web apps — MCP servers/clients, multi-provider AI factory, streamUI with tool calling generators, composable middleware, per-user quotas, model fallback, multi-modal images, streaming, RAG, structured output, prompt...
---

# AI-Enhanced Web Apps with Next.js + Vercel AI SDK

## Load Alongside

- `world-class-engineering` for release gates and production-quality expectations.
- `frontend-performance` for Core Web Vitals and budgets.
- `vibe-security-skill` and `ai-security` for threat modeling, abuse controls, and secure defaults.
- `api-design-first` when the AI app exposes or depends on external contracts.

## Production Workflow

### 1. Define the AI Interaction Contract

Specify before coding:

- User job to be done
- Input shape and validation limits
- Output shape and failure fallback
- Allowed tools and authority boundaries
- Latency and cost budget per request

### 2. Isolate the Expensive Parts

- Keep model selection, prompting, tool wiring, caching, and billing in dedicated server-side modules.
- Stream results for UX, but keep writes and side effects behind explicit validation gates.
- Put long-running or multi-step AI work on queues when it can exceed request budgets.

### 3. Design for Failure and Abuse

- Treat timeouts, provider outages, malformed tool outputs, quota exhaustion, and prompt injection as normal cases.
- Require schema validation for structured output before it reaches business logic.
- Add audit logs for model, prompt version, tool use, cost, and user/tenant attribution.

### 4. Ship with Budgets

- Set budgets for initial bundle size, server latency, AI latency, token spend, and cache hit rate.
- Do not add an AI feature that breaks the critical path for non-AI users.

## Architecture

```
User (React UI)
  ↓ HTTP / Server Actions
Next.js App Router
  ↓ Vercel AI SDK
AI Providers (OpenAI, Google Gemini, Anthropic)
  ↓ MCP Tools / LangChain.js
External APIs + Vector Stores
```

## Setup

```bash
npm install ai @ai-sdk/openai @ai-sdk/google @ai-sdk/anthropic
```

---

## MCP (Model Context Protocol)

MCP is a standardized protocol for exposing tools to AI models across applications.

### MCP Server

```javascript
// src/stdio/server.js
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { z } from 'zod';

const server = new McpServer({ name: 'my-mcp', version: '1.0.0' });

server.tool('get-data', 'Fetch data from internal API', {}, async () => {
  const data = await fetchInternalData();
  return { content: [{ type: 'text', text: JSON.stringify(data) }] };
});

const transport = new StdioServerTransport();
await server.connect(transport);
```

### MCP Client in Next.js Route

```javascript
// app/api/chat/route.ts
import { streamText, convertToModelMessages, experimental_createMCPClient } from 'ai';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio';

export async function POST(req: Request) {
  const { messages } = await req.json();
  const transport = new StdioClientTransport({ command: 'node', args: ['src/stdio/server.js'] });
  const mcpClient = await experimental_createMCPClient({ transport });
  const tools = await mcpClient.tools();

  const result = streamText({
    model: gemini('gemini-2.5-flash'),
    messages: convertToModelMessages(messages),
    tools,
    onFinish: async () => await mcpClient.close(),
  });
  return result.toUIMessageStreamResponse();
}
```

---

## Multi-Provider AI Factory

```typescript
// lib/ai-factory.ts
import { createOpenAI } from '@ai-sdk/openai';
import { createGoogleGenerativeAI } from '@ai-sdk/google';
import { createAnthropic } from '@ai-sdk/anthropic';

const providers = {
  openai: { constructor: createOpenAI, models: ['gpt-3.5-turbo', 'gpt-4', 'gpt-4o'] },
  gemini: { constructor: createGoogleGenerativeAI, models: ['models/gemini-2.0-flash', 'models/gemini-2.5-flash'] },
  anthropic: { constructor: createAnthropic, models: ['claude-opus-4-6', 'claude-sonnet-4-6'] },
};

export function getSupportedModel(provider: string, model: string) {
  const cfg = providers[provider as keyof typeof providers];
  if (!cfg) throw new Error(`Unsupported provider: ${provider}`);
  if (!cfg.models.includes(model)) throw new Error(`Unsupported model: ${model}`);
  const apiKey = process.env[`${provider.toUpperCase()}_API_KEY`];
  if (!apiKey) throw new Error(`Missing API key for: ${provider}`);
  return cfg.constructor({ apiKey })(model);
}

// Usage: const model = getSupportedModel('gemini', 'models/gemini-2.0-flash');
```

---

## Streaming Route Handler

```ts
// app/api/chat/route.ts
export async function POST(req: Request) {
  const { messages, provider = 'gemini', model = 'models/gemini-2.0-flash' } = await req.json();
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

---

## useChat Hook — Client Chat UI

```tsx
'use client';
import { useChat } from 'ai/react';
export default function ChatPage() {
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat({
    api: '/api/chat',
    body: { provider: 'gemini', model: 'models/gemini-2.0-flash' },
  });
  return (
    <div className="flex flex-col h-screen">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map(m => (
          <div key={m.id} className={m.role === 'user' ? 'text-right' : 'text-left'}>
            <span className="rounded bg-gray-100 px-3 py-2 inline-block">{m.content}</span>
          </div>
        ))}
        {isLoading && <span className="animate-pulse">Thinking...</span>}
      </div>
      <form onSubmit={handleSubmit} className="p-4 border-t flex gap-2">
        <textarea value={input} onChange={handleInputChange} className="flex-1 border rounded p-2" />
        <button type="submit" disabled={isLoading}>Send</button>
      </form>
    </div>
  );
}
```

---

## streamUI with Tool Calling (Async Generator)

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
        parameters: z.object({ city: z.string() }),
        // Async generator — yields interim UI, returns final component
        generate: async function* ({ city }) {
          yield <LoadingSpinner city={city} />;
          const weather = await fetchWeather(city);
          return <WeatherCard city={city} temp={weather.temp} condition={weather.condition} />;
        },
      },
    },
  });
  return { display: result.value };
}
```

---

## Composable Middleware Pipeline

```typescript
// middleware.ts
import { NextResponse } from 'next/server';

const composeMiddleware = (middlewares: Function[]) => async (request: Request) => {
  for (const fn of middlewares) {
    const result = await fn(request);
    if (result?.response) return result.response;
    if (result?.continue === false) break;
  }
  return NextResponse.next();
};

const handleCORS = async (req: Request) => {
  const origin = req.headers.get('origin');
  if (origin && !allowedOrigins.includes(origin))
    return { response: new Response('CORS error', { status: 403 }) };
};

const rateLimit = async (req: Request) => {
  const { success } = await upstashRatelimit.limit(req.ip || '127.0.0.1');
  if (!success) return { response: new Response('Too many requests', { status: 429 }) };
};

const authenticate = async (req: Request) => {
  const token = req.headers.get('authorization')?.split(' ')[1];
  if (!token) return { response: new Response('Unauthorized', { status: 401 }) };
};

export default composeMiddleware([handleCORS, rateLimit, authenticate]);
export const config = { matcher: '/api/:path*' };
```

---

## Per-User Daily Quotas

```typescript
// lib/quota.ts
import redis from './redis';

export async function checkMessageQuota(userId: string, dailyLimit = 10): Promise<boolean> {
  const today = new Date().toISOString().split('T')[0];
  const key = `quota:${userId}:${today}`;
  const count = await redis.incr(key);
  if (count === 1) await redis.expire(key, 24 * 60 * 60); // TTL: 24h
  return count <= dailyLimit;
}

// In API route
const { userId } = getAuth(req);
if (!await checkMessageQuota(userId, 10)) {
  return Response.json({ error: 'Daily message quota exceeded (10/day)' }, { status: 429 });
}
```

---

## Model Fallback

```typescript
import { createFallback } from 'ai-fallback';
import { createOpenAI } from '@ai-sdk/openai';
import { createGoogleGenerativeAI } from '@ai-sdk/google';

const model = createFallback({
  models: [
    createGoogleGenerativeAI({ apiKey: process.env.GEMINI_API_KEY! })('models/gemini-2.0-flash'),
    createOpenAI({ apiKey: process.env.OPENAI_API_KEY! })('gpt-3.5-turbo'),
  ],
  onError: (error, modelId) => console.error(`Model ${modelId} failed:`, error),
  shouldRetryThisError: (error) => [429, 500, 503].includes(error.statusCode),
  modelResetInterval: 60_000,
});
```

---

## Multi-Modal Image Input

```typescript
// Backend: process image + text together
const processMessages = (messages: Message[], imageData?: { base64: string; mimeType: string }) => {
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

// Frontend: file → base64
const handleFileUpload = (file: File) => {
  const reader = new FileReader();
  reader.onload = (e) => setImageData({
    base64: (e.target?.result as string).split(',')[1],
    mimeType: file.type,
  });
  reader.readAsDataURL(file);
};
```

---

## Structured Output

```ts
import { generateObject } from 'ai';
import { z } from 'zod';

const { object } = await generateObject({
  model: getSupportedModel('openai', 'gpt-4'),
  schema: z.object({
    title: z.string(),
    tags: z.array(z.string()),
    sentiment: z.enum(['positive', 'negative', 'neutral']),
    summary: z.string().max(200),
  }),
  prompt: 'Analyse this review: "Great product, fast shipping!"',
});
// object.title, object.tags — fully typed
```

---

## Tool / Function Calling

```ts
import { streamText, tool } from 'ai';
import { z } from 'zod';

const result = await streamText({
  model: getSupportedModel('openai', 'gpt-4'),
  tools: {
    getWeather: tool({
      description: 'Get current weather for a city',
      parameters: z.object({ city: z.string(), unit: z.enum(['celsius', 'fahrenheit']).default('celsius') }),
      execute: async ({ city }) => ({ temperature: 22, condition: 'Sunny', city }),
    }),
  },
  messages: [{ role: 'user', content: "What's the weather in London?" }],
});
```

---

## Rate Limiting (LRU)

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

---

## Input Validation

```ts
import { z } from 'zod';
const schema = z.object({
  messages: z.array(z.object({ role: z.enum(['user', 'assistant']), content: z.string().max(4000) })).max(50),
  provider: z.enum(['openai', 'gemini', 'anthropic']).default('gemini'),
});
const parsed = schema.safeParse(await req.json());
if (!parsed.success) return Response.json({ error: 'Invalid request' }, { status: 400 });
```

---

## Security Checklist

- Store API keys server-only — never `NEXT_PUBLIC_`
- Validate all user input with Zod before passing to LLM
- Set `maxTokens` on every call — prevent runaway costs
- Rate-limit per IP AND per user (quota + sliding window)
- Never `dangerouslySetInnerHTML` AI output — use ReactMarkdown
- Log all AI calls for audit and billing
- Keep tool permissions narrower than the chat UI appears to allow
- Sanitize and validate tool outputs before using them in writes or privileged actions
- Separate retrieval corpora by tenant and access policy

## UX Patterns

1. Stream responses — never wait for full completion
2. Show typing indicator immediately
3. Auto-scroll to latest message
4. Disable send while loading — prevent duplicate requests
5. Format AI output as Markdown with syntax highlighting
6. Validate images before upload (size, type, dimensions)
7. Retry button on errors — LLM APIs fail regularly

---

*Source: Despoudis, T. — Build AI-Enhanced Web Apps (Packt, 2024)*
