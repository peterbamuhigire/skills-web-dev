---
name: ai-web-apps
description: Building AI-enhanced web apps with Next.js, Vercel AI SDK, LangChain.js, streaming responses, RAG, prompt engineering, and deployment. Source: Build AI-Enhanced Web Apps (Despoudis).
---

# AI-Enhanced Web Apps with Next.js + Vercel AI SDK

## Architecture

```
User (React UI)
  ↓ HTTP / Server Actions
Next.js App Router (frontend + backend)
  ↓ Vercel AI SDK
External AI Providers (OpenAI, Google Gemini)
  ↓ Optional: LangChain.js
LLMs + Vector Stores (RAG, agents)
```

## Setup

```bash
npm install ai @ai-sdk/openai @ai-sdk/google
```

```bash
# .env.local — never expose these as NEXT_PUBLIC_
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIza...
```

---

## Streaming Route Handler

```ts
// app/api/chat/route.ts
import { streamText } from 'ai';
import { openai } from '@ai-sdk/openai';
import { google } from '@ai-sdk/google';

export async function POST(req: Request) {
  const { messages, provider, model } = await req.json();

  const aiModel = provider === 'gemini'
    ? google('models/gemini-2.0-flash')
    : openai(model || 'gpt-4');

  const result = await streamText({
    model: aiModel,
    system: "You are a helpful assistant.",
    messages,
    maxTokens: 512,
  });

  return result.toDataStreamResponse();
}

export const runtime = 'edge'; // optional
export const maxDuration = 30; // timeout for streaming
```

---

## useChat Hook — Client Chat UI

```tsx
'use client';
import { useChat } from 'ai/react';

export default function ChatPage() {
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat({
    api: '/api/chat',
    body: { provider: 'gemini' }, // extra data sent on each request
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
        <textarea
          value={input}
          onChange={handleInputChange}
          onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) handleSubmit(e); }}
          className="flex-1 border rounded p-2"
        />
        <button type="submit" disabled={isLoading}>Send</button>
      </form>
    </div>
  );
}
```

---

## RSC Streaming via Server Actions

```ts
// app/actions.ts
'use server';
import { streamText } from 'ai';
import { createStreamableValue } from 'ai/rsc';
import { google } from '@ai-sdk/google';

export async function continueConversation(history: Message[]) {
  const stream = createStreamableValue<string>();

  (async () => {
    const { textStream } = await streamText({
      model: google('models/gemini-2.0-flash'),
      messages: history,
    });
    for await (const text of textStream) {
      stream.update(text);
    }
    stream.done();
  })();

  return { messages: history, newMessage: stream.value };
}
```

```tsx
// Client consuming the server action
'use client';
import { readStreamableValue } from 'ai/rsc';
import { continueConversation } from '../actions';

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const userMsg = { role: 'user' as const, content: input };
    const { messages: updated, newMessage } = await continueConversation([...messages, userMsg]);

    let text = '';
    for await (const delta of readStreamableValue(newMessage)) {
      text += delta;
      setMessages([...updated, { role: 'assistant', content: text }]);
    }
  };
}
```

---

## Streaming UI Components (streamUI)

```ts
'use server';
import { streamUI, createStreamableUI } from 'ai/rsc';
import { openai } from '@ai-sdk/openai';

// Stream React components from LLM responses
export async function streamComponent(input: string, history: Message[]) {
  const result = await streamUI({
    model: openai('gpt-3.5-turbo'),
    messages: [...history, { role: 'user', content: input }],
    text: ({ content, done }) => <ChatBubble role="assistant" text={content} />,
  });
  return { display: result.value };
}

// Incremental step-by-step UI
export async function runProcess() {
  const ui = createStreamableUI();
  ui.update(<p>Starting...</p>);
  await step1(); ui.append(<p>Step 1 ✓</p>);
  await step2(); ui.append(<p>Step 2 ✓</p>);
  ui.done();
  return ui;
}
// Methods: update() | append() | done() | error()
```

---

## Structured Data Generation

```ts
import { generateObject, streamObject } from 'ai';
import { openai } from '@ai-sdk/openai';
import { z } from 'zod';

const schema = z.object({
  title: z.string(),
  tags: z.array(z.string()),
  sentiment: z.enum(['positive', 'negative', 'neutral']),
  summary: z.string().max(200),
});

// Synchronous structured output
const { object } = await generateObject({ model: openai('gpt-4'), schema,
  prompt: 'Analyse: "Great product, fast shipping!"' });
// object.title, object.tags — fully typed

// Streaming structured output
const { partialObjectStream } = await streamObject({ model: openai('gpt-4'), schema,
  prompt: 'Get weather for New York' });
for await (const partial of partialObjectStream) {
  console.log(partial.temperature); // updates as fields stream in
}
```

---

## Tool / Function Calling

```ts
import { streamText, tool } from 'ai';
import { z } from 'zod';

const result = await streamText({
  model: openai('gpt-4'),
  tools: {
    getWeather: tool({
      description: 'Get current weather for a city',
      parameters: z.object({
        city: z.string().describe('The city name'),
        unit: z.enum(['celsius', 'fahrenheit']).default('celsius'),
      }),
      execute: async ({ city, unit }) => ({ temperature: 22, condition: 'Sunny', city }),
    }),
  },
  messages: [{ role: 'user', content: "What's the weather in London?" }],
});
```

---

## Prompt Engineering Patterns

```ts
// System prompts
const result = await streamText({
  model: openai('gpt-4'),
  system: `You are a senior software engineer specialising in React.
  Always provide TypeScript examples. Be concise — max 200 words.`,
  messages,
});

// Few-shot learning
const messages = [
  { role: 'system', content: 'Classify customer sentiment.' },
  { role: 'user', content: 'This product is amazing!' },
  { role: 'assistant', content: 'positive' },
  { role: 'user', content: 'Terrible service.' },
  { role: 'assistant', content: 'negative' },
  { role: 'user', content: userInput }, // actual query
];

// Prompt versioning
// lib/prompts.ts
export const PROMPTS = {
  v1: { system: 'You are a helpful assistant.', template: (q: string) => q },
  v2: { system: 'You are an expert. Be concise.', template: (q: string) => `${q}\nFormat: markdown` },
} as const;
const prompt = PROMPTS[process.env.PROMPT_VERSION as 'v1' | 'v2' || 'v2'];
```

---

## Embeddings and RAG

```ts
import { embed, embedMany } from 'ai';
import { openai } from '@ai-sdk/openai';

const { embedding } = await embed({
  model: openai.embedding('text-embedding-3-small'),
  value: 'What is machine learning?',
}); // embedding: number[] (1536 dims)
```

### RAG Pipeline with LangChain.js

```bash
npm install langchain @langchain/openai @langchain/core
```

```ts
import { RecursiveCharacterTextSplitter } from 'langchain/text_splitter';
import { MemoryVectorStore } from 'langchain/vectorstores/memory';
import { OpenAIEmbeddings } from '@langchain/openai';
import { RunnableSequence, RunnablePassthrough } from '@langchain/core/runnables';
import { StringOutputParser } from '@langchain/core/output_parsers';
import { formatDocumentsAsString } from 'langchain/util/document';

// 1. Chunk documents
const docs = await new RecursiveCharacterTextSplitter({ chunkSize: 500, chunkOverlap: 50 })
  .createDocuments([documentText]);

// 2. Embed into vector store
const vectorStore = await MemoryVectorStore.fromDocuments(docs, new OpenAIEmbeddings());

// 3. Build RAG chain
const chain = RunnableSequence.from([
  { context: vectorStore.asRetriever().pipe(formatDocumentsAsString), question: new RunnablePassthrough() },
  promptTemplate,
  llm,
  new StringOutputParser(),
]);

const answer = await chain.invoke({ question: 'Summarise key points.' });
```

---

## Rate Limiting

```ts
// lib/rate-limit.ts
import { LRUCache } from 'lru-cache';

const cache = new LRUCache<string, number>({ max: 500, ttl: 60_000 });

export function checkRateLimit(id: string, limit = 10): boolean {
  const n = cache.get(id) ?? 0;
  if (n >= limit) return false;
  cache.set(id, n + 1);
  return true;
}

// In route handler
const ip = req.headers.get('x-forwarded-for') || 'unknown';
if (!checkRateLimit(ip, 20)) return new Response('Rate limit exceeded', { status: 429 });
```

---

## Displaying AI Content Safely

```tsx
'use client';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';

export function ChatMessage({ content, role }: { content: string; role: 'user' | 'assistant' }) {
  if (role === 'user') return <p className="text-right">{content}</p>; // plain text — never dangerouslySetInnerHTML

  return (
    <ReactMarkdown remarkPlugins={[remarkGfm]} components={{
      code({ inline, className, children }) {
        const lang = /language-(\w+)/.exec(className || '')?.[1];
        return !inline && lang
          ? <SyntaxHighlighter language={lang}>{String(children)}</SyntaxHighlighter>
          : <code className="bg-gray-100 px-1 rounded">{children}</code>;
      },
    }}>
      {content}
    </ReactMarkdown>
  );
}

// Auto-scroll to latest message
export function AutoScroll({ track }: { track: boolean }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => { if (track) ref.current?.scrollIntoView({ behavior: 'smooth' }); });
  return <div ref={ref} />;
}
```

---

## Input Validation

```ts
import { z } from 'zod';

const schema = z.object({
  messages: z.array(z.object({
    role: z.enum(['user', 'assistant', 'system']),
    content: z.string().max(4000),
  })).max(50),
  provider: z.enum(['openai', 'gemini']).default('gemini'),
});

export async function POST(req: Request) {
  const parsed = schema.safeParse(await req.json());
  if (!parsed.success) return Response.json({ error: 'Invalid request' }, { status: 400 });
  const { messages, provider } = parsed.data;
  // ...
}
```

---

## Security Checklist

- Store all API keys as server-only env vars — no `NEXT_PUBLIC_` prefix
- Use `'use server'` on all AI interaction code
- Sanitise user input before passing to LLM (prevent prompt injection)
- Validate and parse AI-generated JSON before using it (`safeParse`)
- Rate-limit per IP/user — prevent abuse
- Set `maxTokens` on every call — cap costs
- Handle LLM errors gracefully — wrap in try/catch
- Log AI calls for audit and billing

## UX Patterns

1. Show loading indicator immediately — AI takes time
2. Stream responses — perceived performance boost
3. Auto-scroll to latest message
4. Disable send while loading — prevent duplicate requests
5. Handle errors with a retry button, not a raw error
6. Format AI output as Markdown — improves readability
7. Validate images before upload (size, type, dimensions)

## Anti-Patterns to Avoid

- Never put API keys in client components or `NEXT_PUBLIC_` vars
- Never render AI output with `dangerouslySetInnerHTML` without sanitisation
- Never skip error handling — LLM APIs fail, timeout, and rate-limit
- Never call AI APIs from `useEffect` — use server actions or route handlers
- Never skip `maxTokens` — unbounded responses cause runaway costs
- Avoid prompt injection: sanitise user input before including in prompts
