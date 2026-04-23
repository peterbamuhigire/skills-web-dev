---
name: nextjs-app-router
description: 'Next.js App Router patterns for production — server/client components,
  parallel routes, advanced middleware, RBAC three-tier, Redis caching, background
  jobs (BullMQ), data fetching, auth, deployment, CI/CD. Sources: Rambert (Advanced
  Next.js)...'
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Next.js App Router Patterns
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Next.js App Router patterns for production — server/client components, parallel routes, advanced middleware, RBAC three-tier, Redis caching, background jobs (BullMQ), data fetching, auth, deployment, CI/CD. Sources: Rambert (Advanced Next.js)...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `nextjs-app-router` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve.
- Confirm the desired deliverable: design, code, review, migration plan, audit, or documentation.

## Workflow

- Read this `SKILL.md` first, then load only the referenced deep-dive files that are necessary for the task.
- Apply the ordered guidance, checklists, and decision rules in this skill instead of cherry-picking isolated snippets.
- Produce the deliverable with assumptions, risks, and follow-up work made explicit when they matter.

## Quality Standards

- Keep outputs execution-oriented, concise, and aligned with the repository's baseline engineering standards.
- Preserve compatibility with existing project conventions unless the skill explicitly requires a stronger standard.
- Prefer deterministic, reviewable steps over vague advice or tool-specific magic.

## Anti-Patterns

- Treating examples as copy-paste truth without checking fit, constraints, or failure modes.
- Loading every reference file by default instead of using progressive disclosure.

## Outputs

- A concrete result that fits the task: implementation guidance, review findings, architecture decisions, templates, or generated artifacts.
- Clear assumptions, tradeoffs, or unresolved gaps when the task cannot be completed from available context alone.
- References used, companion skills, or follow-up actions when they materially improve execution.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Correctness | Route + middleware test plan | Markdown doc covering server/client component boundaries, parallel routes, and middleware | `docs/web/nextjs-route-tests.md` |
| Security | RBAC three-tier configuration note | Markdown doc covering middleware / server action / data-access guards | `docs/web/nextjs-rbac.md` |

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
## Project Setup

```bash
npx create-next-app@latest my-app \
  --typescript --tailwind --eslint --app --src-dir
```

### Folder Structure (App Router)

```
app/
├── layout.tsx          # Root layout (required)
├── page.tsx            # Home route /
├── (marketing)/        # Route group — no URL segment
├── @notifications/     # Parallel route slot
│   └── page.tsx
├── dashboard/
│   ├── layout.tsx      # Nested layout
│   ├── page.tsx
│   ├── loading.tsx     # Suspense fallback
│   ├── error.tsx       # Error boundary ('use client')
│   └── not-found.tsx
└── api/users/route.ts  # GET/POST /api/users
```

---

## Server vs Client Components

```tsx
// Server component (default) — async, zero JS to client
export default async function UsersPage() {
  const users = await fetch('https://api.example.com/users', {
    cache: 'force-cache',        // static
    // next: { revalidate: 60 } // ISR
    // cache: 'no-store'        // SSR
  }).then(r => r.json());
  return <ul>{users.map(u => <li key={u.id}>{u.name}</li>)}</ul>;
}

// Client component — needs interactivity, browser APIs
'use client';
export default function Counter() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(c => c + 1)}>Count: {count}</button>;
}
```

**Rule:** Push `'use client'` as far down the tree as possible.

---

## Routing

| File | Route |
|------|-------|
| `app/page.tsx` | `/` |
| `app/blog/[slug]/page.tsx` | `/blog/:slug` |
| `app/shop/[...slug]/page.tsx` | `/shop/*` catch-all |
| `app/(auth)/login/page.tsx` | `/login` (route group) |
| `app/@modal/page.tsx` | Parallel slot |

### Dynamic Routes + generateStaticParams

```tsx
export default async function BlogPost({ params }: { params: { slug: string } }) {
  const post = await fetchPost(params.slug);
  return <article><h1>{post.title}</h1></article>;
}
export async function generateStaticParams() {
  const posts = await fetchAllPosts();
  return posts.map(p => ({ slug: p.slug }));
}
```

### Parallel Routes (@slot)

```tsx
// app/support/layout.tsx — load @tickets and @chat independently
export default function SupportLayout({ tickets, chat }: {
  tickets: React.ReactNode; chat: React.ReactNode;
}) {
  return (
    <div className="grid grid-cols-2 gap-4">
      <aside>{tickets}</aside>
      <main>{chat}</main>
    </div>
  );
}
// Directories: app/support/@tickets/page.tsx  app/support/@chat/page.tsx
// Use case: dashboards, live feeds, multi-pane UIs loading at different speeds
```

---

## Data Fetching

### ISR Revalidation Guidelines

| Content Type | Revalidate | Pattern |
|---|---|---|
| Blog / docs | 60s | `next: { revalidate: 60 }` |
| News feed | 10s | `next: { revalidate: 10 }` |
| Products / pricing | 300s | `next: { revalidate: 300 }` |
| Static marketing | 86400s | `cache: 'force-cache'` |
| User-specific | Dynamic | `cache: 'no-store'` |
| Real-time (stock) | N/A | SSR or WebSocket |

### Parallel Fetch + React cache()

```tsx
// Parallel fetching
const [user, posts] = await Promise.all([
  fetch('/api/user').then(r => r.json()),
  fetch('/api/posts').then(r => r.json()),
]);

// Deduplication for POST/GraphQL requests
import { cache } from 'react';
export const getUser = cache(async (id: string) => db.user.findUnique({ where: { id } }));
```

---

## Route Handlers (API Routes)

```ts
// app/api/users/route.ts
export async function GET() {
  return NextResponse.json(await db.user.findMany());
}
export async function POST(request: NextRequest) {
  const body = await request.json();
  return NextResponse.json(await db.user.create({ data: body }), { status: 201 });
}
```

---

## Server Actions

```tsx
'use server';
import { revalidatePath } from 'next/cache';
export async function createTodo(formData: FormData) {
  const title = formData.get('title') as string;
  await db.todo.create({ data: { title } });
  revalidatePath('/todos');
}

// Use directly in form — no API route needed
<form action={createTodo}><input name="title" /><button>Add</button></form>
```

### Server Actions vs API Routes

| Use | When |
|---|---|
| Server Action | Form submissions, mutations from UI, same-app data changes |
| API Route | Public APIs, webhooks, third-party consumers, complex error handling |

---

## Middleware

```ts
// middleware.ts — project root
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const { pathname, url } = request.nextUrl;

  // Auth redirect
  const token = request.cookies.get('token')?.value;
  if (!token && pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', url));
  }

  // IP blocking
  const ip = request.ip || request.headers.get('x-forwarded-for') || '';
  const blocked = ['192.168.1.100'];
  if (blocked.includes(ip)) return new NextResponse('Forbidden', { status: 403 });

  // Geo-routing
  const country = request.geo?.country;
  if (country === 'FR' && !pathname.startsWith('/fr')) {
    return NextResponse.rewrite(new URL('/fr' + pathname, url));
  }

  // Custom headers
  const res = NextResponse.next();
  res.headers.set('X-Request-ID', crypto.randomUUID());
  return res;
}

export const config = { matcher: ['/dashboard/:path*', '/api/:path*'] };
```

---

## RBAC — Three-Tier Protection

```ts
// Tier 1: Middleware (route-level gating)
if (pathname.startsWith('/admin')) {
  const role = request.cookies.get('role')?.value;
  if (role !== 'admin') return NextResponse.redirect(new URL('/unauthorized', url));
}

// Tier 2: Server component (page-level protection)
import { auth } from '@/auth';
import { redirect } from 'next/navigation';
export default async function AdminPage() {
  const session = await auth();
  if (!session || session.user.role !== 'admin') redirect('/unauthorized');
  return <div>Admin Panel</div>;
}

// Tier 3: API route (data-level protection)
export async function GET(req: NextRequest) {
  const session = await getServerSession(authOptions);
  if (!session || session.user.role !== 'admin')
    return Response.json({ error: 'Unauthorized' }, { status: 403 });
  return Response.json(await db.adminData.findMany());
}
```

---

## Redis Caching

```ts
// lib/redis.ts
import Redis from 'ioredis';
const redis = new Redis(process.env.REDIS_URL!);
export default redis;

// API route with cache-aside pattern
export async function GET() {
  const cached = await redis.get('users');
  if (cached) return Response.json(JSON.parse(cached));

  const users = await db.user.findMany();
  await redis.set('users', JSON.stringify(users), 'EX', 600); // 10 min
  return Response.json(users);
}

// Invalidate on mutation
export async function POST(request: NextRequest) {
  const user = await db.user.create({ data: await request.json() });
  await redis.del('users');
  return Response.json(user, { status: 201 });
}
```

---

## Background Jobs (BullMQ)

```ts
// lib/queue.ts
import { Queue, Worker } from 'bullmq';
import Redis from 'ioredis';
const connection = new Redis(process.env.REDIS_URL!);
export const emailQueue = new Queue('email', { connection });

// Worker (separate process or dedicated route)
new Worker('email', async (job) => {
  const { to, subject, body } = job.data;
  await sendEmail(to, subject, body);
}, { connection });

// Enqueue from API route
export async function POST(req: NextRequest) {
  const { email } = await req.json();
  await emailQueue.add('welcome', { to: email, subject: 'Welcome!' });
  return Response.json({ queued: true });
}
```

---

## Authentication (NextAuth v5)

```ts
// auth.ts
export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [GitHub({ clientId: process.env.GITHUB_ID!, clientSecret: process.env.GITHUB_SECRET! })],
  callbacks: {
    jwt({ token, user }) { if (user) token.role = user.role; return token; },
    session({ session, token }) { session.user.role = token.role as string; return session; },
  },
});
```

---

## Database (Prisma Singleton)

```ts
// lib/prisma.ts — prevents connection exhaustion in dev HMR
import { PrismaClient } from '@prisma/client';
const globalForPrisma = globalThis as unknown as { prisma: PrismaClient };
export const db = globalForPrisma.prisma || new PrismaClient({ log: ['query'] });
if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = db;
```

### Database Selection

| Database | Use When |
|---|---|
| PostgreSQL + Prisma | Relational data, transactions, production default |
| MongoDB + Mongoose | Document/flexible schemas, content management |
| Firebase Firestore | Real-time sync, serverless, mobile-first |

---

## CI/CD (GitHub Actions)

```yaml
name: CI/CD
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with: { node-version: '20.x' }
      - run: npm ci
      - run: npm run lint
      - run: npm test
      - run: npm run build
  deploy:
    needs: build
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: npm install -g vercel && vercel --prod --token=${{ secrets.VERCEL_TOKEN }}
```

---

## Deployment

| Platform | Best For |
|---|---|
| **Vercel** | Zero-config, global CDN, Edge Network, native Next.js |
| **Railway** | Simple self-hosted, easy DB provisioning |
| **AWS Amplify** | Full AWS ecosystem, enterprise |
| **Docker/Self-hosted** | Full control, no vendor lock-in |

```dockerfile
# next.config.js: module.exports = { output: 'standalone' }
FROM node:20-alpine AS runner
WORKDIR /app
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
CMD ["node", "server.js"]
```

---

## Built-in Components

```tsx
import Image from 'next/image';
import Link from 'next/link';

<Image src="/hero.jpg" alt="Hero" width={800} height={600} priority />
<Link href="/dashboard">Dashboard</Link>
<Link href={`/blog/${slug}`} prefetch={false}>Post</Link>
```

---

## Anti-Patterns

- Do NOT `'use client'` every component — server by default
- Do NOT use `getServerSideProps`/`getStaticProps` in App Router
- Do NOT store secrets in `NEXT_PUBLIC_` vars
- Do NOT `useEffect` for data — fetch in server components
- Do NOT create separate Express servers — use Route Handlers
- Do NOT await fetches sequentially — use `Promise.all`
- Do NOT skip `loading.tsx` — every dynamic route needs a Suspense boundary

---

*Sources: Rambert — Advanced Next.js for Everyone (2024); Kim — The Next.js Handbook (2023); Jain — Modern Web Applications with Next.js (2024); Krause — The Complete Developer (2024)*