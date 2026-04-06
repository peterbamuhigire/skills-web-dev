---
name: nextjs-app-router
description: Next.js App Router patterns, server/client components, data fetching, routing, auth, and deployment. Source: Modern Web Apps with Next.js (Jain/Chittezhath) + The Complete Developer (Krause).
---

# Next.js App Router Patterns

## Project Setup

```bash
npx create-next-app@latest my-app \
  --typescript --tailwind --eslint --app --src-dir
```

### Folder Structure (App Router)

```
my-app/
├── app/
│   ├── layout.tsx          # Root layout (required)
│   ├── page.tsx            # Home route /
│   ├── (marketing)/        # Route group — no URL segment
│   │   └── about/page.tsx  # /about
│   ├── dashboard/
│   │   ├── layout.tsx      # Nested layout
│   │   ├── page.tsx        # /dashboard
│   │   ├── loading.tsx     # Suspense fallback
│   │   ├── error.tsx       # Error boundary
│   │   └── not-found.tsx   # 404 for segment
│   └── api/users/route.ts  # GET/POST /api/users
├── components/
├── lib/
├── .env.local              # Never commit
└── next.config.js
```

---

## Server vs Client Components

### Server Components (default in app/)

```tsx
// app/users/page.tsx — no 'use client' needed
export default async function UsersPage() {
  const users = await fetch('https://api.example.com/users', {
    cache: 'force-cache',         // static
    // next: { revalidate: 60 }  // ISR
    // cache: 'no-store'         // dynamic SSR
  }).then(r => r.json());

  return <ul>{users.map(u => <li key={u.id}>{u.name}</li>)}</ul>;
}
```

Server components: async/await, backend access, no useState/events/browser APIs. Zero JS to client.

### Client Components

```tsx
'use client';
import { useState } from 'react';

export default function Counter() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(c => c + 1)}>Count: {count}</button>;
}
```

**Rule:** Push `'use client'` down the tree. Server components can import client components; the reverse is not allowed.

---

## Routing

| File | Route |
|------|-------|
| `app/page.tsx` | `/` |
| `app/blog/[slug]/page.tsx` | `/blog/:slug` |
| `app/shop/[...slug]/page.tsx` | `/shop/*` catch-all |
| `app/(auth)/login/page.tsx` | `/login` (route group) |

### Dynamic Routes

```tsx
// app/blog/[slug]/page.tsx
export default async function BlogPost({ params }: { params: { slug: string } }) {
  const post = await fetchPost(params.slug);
  return <article><h1>{post.title}</h1></article>;
}

export async function generateStaticParams() {
  const posts = await fetchAllPosts();
  return posts.map(p => ({ slug: p.slug }));
}
```

### Special Files

```tsx
// loading.tsx — automatic Suspense boundary
export default function Loading() {
  return <div className="skeleton animate-pulse h-8 w-full" />;
}

// error.tsx — MUST be 'use client'
'use client';
export default function Error({ error, reset }: { error: Error; reset: () => void }) {
  return <div><p>{error.message}</p><button onClick={reset}>Try again</button></div>;
}
```

### Root Layout

```tsx
// app/layout.tsx
import { Inter } from 'next/font/google';
const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: { default: 'My App', template: '%s | My App' },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="en"><body className={inter.className}>{children}</body></html>;
}
```

---

## Data Fetching

### Parallel fetch (server component)

```tsx
async function Page() {
  const [user, posts] = await Promise.all([
    fetch('/api/user').then(r => r.json()),
    fetch('/api/posts').then(r => r.json()),
  ]);
}
```

### React `cache()` for POST/GraphQL deduplication

```tsx
import { cache } from 'react';
export const getUser = cache(async (id: string) => {
  return fetch('/graphql', { method: 'POST', body: JSON.stringify({ query: `{ user(id: "${id}") { name } }` }) }).then(r => r.json());
});
// Multiple components calling getUser('123') → only one network request
```

### SWR for client-side data

```tsx
'use client';
import useSWR from 'swr';
const fetcher = (url: string) => fetch(url).then(r => r.json());

export default function UserList() {
  const { data, error, isLoading } = useSWR('/api/users', fetcher);
  if (error) return <p>Error</p>;
  if (isLoading) return <p>Loading...</p>;
  return <ul>{data.map(u => <li key={u.id}>{u.name}</li>)}</ul>;
}
```

### ISR / Rendering Mode

| Pattern | Code | When |
|---------|------|------|
| Static | `cache: 'force-cache'` | Marketing pages, blogs |
| ISR | `next: { revalidate: 60 }` | Semi-dynamic content |
| Dynamic | `cache: 'no-store'` | User-specific data |
| CSR | `'use client'` + SWR | Highly interactive |

---

## Route Handlers (API Routes)

```ts
// app/api/users/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function GET() {
  const users = await db.user.findMany();
  return NextResponse.json(users);
}

export async function POST(request: NextRequest) {
  const body = await request.json();
  const user = await db.user.create({ data: body });
  return NextResponse.json(user, { status: 201 });
}

// app/api/users/[id]/route.ts
export async function DELETE(req: NextRequest, { params }: { params: { id: string } }) {
  await db.user.delete({ where: { id: params.id } });
  return new NextResponse(null, { status: 204 });
}
```

---

## Server Actions

```tsx
// app/actions.ts
'use server';
import { revalidatePath } from 'next/cache';

export async function createTodo(formData: FormData) {
  const title = formData.get('title') as string;
  await db.todo.create({ data: { title } });
  revalidatePath('/todos');
}

// app/todos/page.tsx — use in form directly
import { createTodo } from '../actions';
export default function TodoPage() {
  return <form action={createTodo}><input name="title" /><button type="submit">Add</button></form>;
}
```

---

## Next.js Built-in Components

```tsx
import Image from 'next/image';
import Link from 'next/link';

// next/image — automatic optimisation
<Image src="/hero.jpg" alt="Hero" width={800} height={600} priority />

// fill parent container
<div className="relative h-64 w-full">
  <Image src="/bg.jpg" alt="" fill style={{ objectFit: 'cover' }} />
</div>

// next/link — client-side navigation
<Link href="/dashboard">Dashboard</Link>
<Link href={`/blog/${slug}`} prefetch={false}>Post</Link>
```

### Metadata API

```tsx
// Static
export const metadata: Metadata = {
  title: 'Page', description: 'SEO desc',
  openGraph: { title: 'Page', images: ['/og.jpg'] },
};

// Dynamic
export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const post = await fetchPost(params.slug);
  return { title: post.title, openGraph: { images: [post.thumbnail] } };
}
```

---

## Middleware

```ts
// middleware.ts — project root (NOT in app/)
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const token = request.cookies.get('token')?.value;
  if (!token && request.nextUrl.pathname.startsWith('/dashboard')) {
    return NextResponse.redirect(new URL('/login', request.url));
  }
  return NextResponse.next();
}

export const config = {
  matcher: ['/dashboard/:path*', '/api/protected/:path*'],
};
```

---

## Authentication (NextAuth v5)

```ts
// auth.ts
import NextAuth from 'next-auth';
import GitHub from 'next-auth/providers/github';

export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [GitHub({ clientId: process.env.GITHUB_ID!, clientSecret: process.env.GITHUB_SECRET! })],
  callbacks: {
    jwt({ token, user }) { if (user) token.userId = user.id; return token; },
    session({ session, token }) { session.user.id = token.userId as string; return session; },
  },
});

// app/api/auth/[...nextauth]/route.ts
export { handlers as GET, handlers as POST } from '@/auth';
```

```tsx
// Server component — protect page
import { auth } from '@/auth';
import { redirect } from 'next/navigation';
export default async function ProtectedPage() {
  const session = await auth();
  if (!session) redirect('/login');
  return <div>Welcome {session.user.name}</div>;
}

// Client component
'use client';
import { useSession, signIn, signOut } from 'next-auth/react';
export function AuthButton() {
  const { data: session } = useSession();
  return session
    ? <button onClick={() => signOut()}>Sign Out</button>
    : <button onClick={() => signIn('github')}>Sign In</button>;
}
```

---

## Environment Variables

```bash
# .env.local — never commit
DATABASE_URL="postgresql://..."
NEXTAUTH_SECRET="your-secret"        # server-only
NEXT_PUBLIC_STRIPE_KEY="pk_test_..." # exposed to browser
```

Only `NEXT_PUBLIC_` vars are available in client components. Keep API keys without this prefix.

---

## Database (Prisma Singleton)

```ts
// lib/prisma.ts — prevents connection exhaustion in dev HMR
import { PrismaClient } from '@prisma/client';
const globalForPrisma = globalThis as unknown as { prisma: PrismaClient };
export const db = globalForPrisma.prisma || new PrismaClient({ log: ['query'] });
if (process.env.NODE_ENV !== 'production') globalForPrisma.prisma = db;
```

---

## Deployment

### Vercel (zero-config)

```bash
npm install -g vercel && vercel --prod
```

Set env vars in Vercel Dashboard → Settings → Environment Variables.

### Docker (self-hosted)

```dockerfile
FROM node:20-alpine AS base
FROM base AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci

FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

FROM base AS runner
WORKDIR /app
ENV NODE_ENV production
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
EXPOSE 3000
CMD ["node", "server.js"]
```

```js
// next.config.js — required for standalone Docker output
module.exports = { output: 'standalone' };
```

---

## Testing Setup

```js
// jest.config.js
const nextJest = require('next/jest');
const createJestConfig = nextJest({ dir: './' });
module.exports = createJestConfig({ testEnvironment: 'jest-environment-jsdom' });
```

```tsx
import { render, screen } from '@testing-library/react';
import Header from '@/components/Header';
it('renders logo', () => {
  render(<Header />);
  expect(screen.getByAltText('Logo')).toBeInTheDocument();
});
```

---

## Anti-Patterns to Avoid

- Do NOT add `'use client'` to every component — default is server
- Do NOT use `getServerSideProps`/`getStaticProps` in the App Router (pages/ only)
- Do NOT store secrets in `NEXT_PUBLIC_` env vars
- Do NOT use `useEffect` for data fetching — fetch in server components
- Do NOT create separate Express.js servers — use Route Handlers
- Do NOT use `any` in TypeScript — use precise types
- Do NOT await fetches sequentially — use `Promise.all` for parallel fetches
