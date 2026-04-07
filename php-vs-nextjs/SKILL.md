---
name: php-vs-nextjs
description: Decision framework for choosing PHP vs Next.js/Node.js for web projects. Covers when to use each, migration strategies, and the hybrid approach. Use when starting a new project, evaluating technology stack, or deciding whether to extend PHP systems vs build new Next.js frontends. Sources: Rambert, Kim, Jain, Krause.
---

# PHP vs Next.js: Technology Decision Framework

## The Core Question

PHP and Next.js are not competing for the same jobs. PHP excels at server-rendered backends, multi-tenant SaaS, and CMS. Next.js excels at React-based full-stack apps, dynamic UIs, and real-time features.

**Default rule:** Start with PHP if the team knows PHP and the use case is a traditional multi-tenant SaaS. Start with Next.js if the frontend needs to be a rich interactive application.

---

## Decision Table

| Factor | Choose PHP | Choose Next.js |
|---|---|---|
| **Team expertise** | PHP team in place | JavaScript/TypeScript team |
| **Frontend complexity** | Simple server-rendered pages, minimal JS | Rich SPA, dashboards, real-time UI |
| **Backend logic** | Complex DB operations, multi-tenant SaaS | Thin backend, mostly API calls to services |
| **Real-time features** | Not needed | WebSockets, live updates, streaming |
| **Rendering strategy** | Server-rendered HTML (traditional) | SSR + SSG + ISR + CSR mix |
| **CMS / WordPress** | WordPress plugin, WooCommerce | Headless CMS with Next.js frontend |
| **Existing codebase** | PHP codebase already exists | Greenfield project |
| **Mobile API** | Laravel/Slim REST API for mobile | Next.js Route Handlers as API |
| **File uploads / processing** | PHP handles well natively | Route Handlers + storage service |
| **SEO** | PHP renders HTML naturally | Next.js SSR/SSG equally good |
| **Deployment infrastructure** | LAMP/WAMP, shared hosting | Vercel, Railway, Docker |
| **Database** | MySQL via PDO/Eloquent | PostgreSQL/MySQL via Prisma |
| **Auth complexity** | Full auth + RBAC + sessions | NextAuth or Clerk |
| **Email / queues** | Laravel Queues, Swift Mailer | BullMQ, Resend, Sendgrid |
| **Multi-tenant SaaS** | Strong — DB isolation per tenant easy | Possible but more setup |
| **Time to first page** | Very fast on VPS | Fast with Vercel Edge |
| **Type safety** | PHP 8 + PHPStan/Psalm | TypeScript end-to-end |

---

## Use PHP When

1. **Existing PHP SaaS** — never rewrite what works. Extend with PHP skills.
2. **Multi-tenant B2B SaaS** — tenant isolation via `franchise_id` is PHP's sweet spot.
3. **CMS-heavy sites** — WordPress, Drupal, custom CMS.
4. **Shared hosting constraint** — client only has cPanel/LAMP hosting.
5. **Simple CRUD API for mobile** — Laravel/Slim is faster to build than Next.js API.
6. **PHP team, no JS expertise** — technical risk of switching is too high.
7. **Complex backend logic** — payment processing, double-entry accounting, inventory.

```php
// PHP strength: multi-tenant query isolation — every query is tenant-scoped
$stmt = $db->prepare('SELECT * FROM invoices WHERE tenant_id = ? AND id = ?');
$stmt->execute([$user['tenant_id'], $id]); // tenant can NEVER see other tenants' data
```

---

## Use Next.js When

1. **React-heavy frontend** — the frontend is the primary product (dashboards, apps).
2. **Same-language full-stack** — team wants TypeScript everywhere, frontend + API.
3. **Real-time features** — live notifications, streaming AI responses, WebSockets.
4. **Hybrid rendering** — page needs ISR for SEO + client interactivity.
5. **AI-enhanced web app** — Vercel AI SDK integrates natively with Next.js.
6. **Component library / design system** — Tailwind + shadcn/ui is the ecosystem.
7. **Modern dev experience** — hot reload, TypeScript first-class, App Router.
8. **Edge functions** — geo-routing, A/B testing at CDN edge with minimal latency.

```typescript
// Next.js strength: full-stack TypeScript, types shared between frontend and backend
type Invoice = { id: string; amount: number; tenantId: string }; // shared type

// Server component fetches directly from DB — no extra API round trip
export default async function InvoicePage({ params }: { params: { id: string } }) {
  const invoice = await db.invoice.findFirst({ where: { id: params.id, tenantId: getSession().tenantId } });
  return <InvoiceView invoice={invoice} />;
}
```

---

## The Hybrid Architecture (Best of Both)

Many production systems use both:

```
┌─────────────────────────────────────────────────────────┐
│                    User's Browser                       │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        ▼                             ▼
┌───────────────┐            ┌────────────────┐
│ Next.js App   │            │  PHP Backend   │
│ (Frontend UI) │◄──────────►│ (Business API) │
│ React + TS    │   REST API │ Laravel/Slim   │
└───────────────┘            └────────────────┘
                                     │
                             ┌───────▼───────┐
                             │  MySQL / Redis │
                             └───────────────┘
```

**Pattern:** PHP handles business logic, multi-tenant data, auth tokens. Next.js handles the rich UI, SSR/ISR for SEO, and calls PHP API.

```typescript
// Next.js fetches from PHP backend
export default async function DashboardPage() {
  const data = await fetch(`${process.env.PHP_API_URL}/api/v1/dashboard`, {
    headers: { Authorization: `Bearer ${await getToken()}` },
    next: { revalidate: 30 }, // ISR — refresh every 30s
  }).then(r => r.json());
  return <Dashboard data={data} />;
}
```

---

## Migration Strategy: PHP → Next.js

Never rewrite everything at once — migrate incrementally.

### Strangler Fig Pattern

```
Phase 1: New pages in Next.js, PHP handles existing routes
         /new-feature → Next.js
         /old-feature → PHP (unchanged)

Phase 2: Migrate high-value pages one at a time
         /dashboard → Next.js (better UX)
         /settings  → Next.js
         /legacy    → PHP (still running)

Phase 3: PHP becomes pure API backend
         All UI → Next.js
         All data → PHP REST API
```

### What to Migrate First

| Priority | Reason |
|---|---|
| Marketing pages | Quick wins: ISR for SEO, fast deploy |
| Dashboard / analytics | Rich React components, real-time |
| User-facing UI | End-user experience improvement |
| Admin panels | TypeScript safety reduces bugs |
| Auth flow | NextAuth handles social providers |

### What to Keep in PHP

| Component | Reason |
|---|---|
| Business logic / calculations | Complex, tested, working |
| Multi-tenant data layer | Proven isolation patterns |
| Payment processing | Risk too high to rewrite |
| Background jobs | Laravel Queues mature |
| File storage / image processing | PHP handles well |
| Email system | Existing templates, tested |

---

## When Neither — Consider Alternatives

| Situation | Consider |
|---|---|
| Pure mobile backend | Laravel API (PHP) or Hono (Node.js) |
| Real-time chat / gaming | Go, Elixir, or Node.js + Socket.io |
| Data-heavy analytics | Python FastAPI |
| Microservices | Each service picks its own language |
| WordPress site | Stay WordPress, use ACF + REST API |

---

## PHP vs Node.js Performance Context

- **PHP-FPM + Nginx:** 10,000–50,000 req/s for CRUD-heavy workloads
- **Node.js (Next.js API):** 20,000–80,000 req/s for I/O-bound operations
- **Edge functions (Vercel):** Sub-5ms globally for lightweight responses
- **Verdict:** Performance is rarely the deciding factor. Choose by team expertise and use case fit.

---

## Quick Decision Checklist

```
Is the frontend a rich React SPA?        YES → Next.js
Does the team know PHP?                  YES → PHP (unless above)
Is there an existing PHP codebase?       YES → Extend PHP
Do you need real-time features?          YES → Next.js
Is this a multi-tenant SaaS backend?     YES → PHP
Is this AI-powered (LLMs, streaming)?   YES → Next.js
Are you on shared/LAMP hosting?          YES → PHP
Do you want TypeScript end-to-end?       YES → Next.js
```
