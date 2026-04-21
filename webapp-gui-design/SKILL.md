---
name: webapp-gui-design
description: Use when designing or building SaaS web application UIs with React, Next.js,
  TypeScript, and Tailwind CSS. Covers the application shell, navigation, dashboards, data
  tables, forms, dialogs, loading and error states, auth flows, uploads, accessibility,
  and interface consistency. For the Bootstrap/Tabler/PHP stack used in the seeder
  template, load the deep-dive files in the `sections/` directory.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Web App GUI Design

<!-- dual-compat-start -->
## Use When

- Building or reviewing a SaaS web UI on React/Next.js/TypeScript/Tailwind
- Standardising app shell, navigation, dashboards, or data-table patterns across products
- Working on the Bootstrap 5 + Tabler + PHP seeder stack — load `sections/01-overview.md` first

## Do Not Use When

- Pure landing or marketing pages — use `frontend-design` for editorial layouts
- Mobile-native screens — use `jetpack-compose-ui` or `swiftui-design`
- Low-level Tailwind syntax questions — use `tailwind-css`

## Required Inputs

The target surface (dashboard, CRUD table, form, settings), the auth/tenant model, and the data model for at least one screen. For the seeder stack, the `seeder-page.php` template path.

## Workflow

1. Place the screen in the app shell (sidebar + topbar + content area).
2. Pick the layout primitive (dashboard grid, table, form, detail-with-tabs).
3. Wire data with React Query; never call `fetch` inside components.
4. Attach loading + error + empty states *before* connecting real data.
5. Check consistency against existing screens and primitives before adding a new pattern.
6. Run the a11y + responsive sweep (§15 checklist) before merge.

## Quality Standards

- Every data screen has a loading, empty, error, and success state.
- Every form uses React Hook Form + Zod with a single `FormField` primitive.
- Every interactive widget is keyboard-operable (Tab, Enter, Escape, Arrow).
- Colour contrast ≥ 4.5:1 for body text, 3:1 for ≥18pt or bold text.
- Buttons use the correct element: `<button>` for actions, `<a href>` for navigation.
- Every decision point has one clear primary action; secondary and tertiary actions must not compete with it.
- Every button ships with enabled, hover, focus, pressed, disabled, and loading states.
- Button labels describe the outcome ("Save changes", "Delete project"), not a vague mechanism ("Submit", "OK").
- Destructive actions use a dedicated danger variant and explicit confirmation or undo when the action is high impact.
- Touch targets are at least 44x44 CSS pixels, including icon-only buttons.

## Anti-Patterns

Spinners on the whole page after initial load; per-route custom chrome; forms with unvalidated submit handlers; empty states that say only "No data"; modals that trap focus incorrectly; buttons used as links; generic CTA copy; loading buttons that remove the action label.

## Outputs

App shell component, route-level layout files, reusable primitives (`DataTable`, `FormField`, `Dialog`, `EmptyState`, `StatusPill`), Tailwind theme tokens, a11y checklist report.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| UX quality | Screen layout + state matrix | Markdown doc covering per-screen layout, states, and component inventory | `docs/ui/screens/orders-list.md` |
| UX quality | Accessibility + responsive sweep | Markdown doc covering a11y findings and responsive behaviour across breakpoints | `docs/ui/a11y-audit-2026-04-16.md` |
| Correctness | UI shell + primitives register | Markdown doc listing layout, data-table, form-field, and dialog primitives used per screen | `docs/ui/primitives-register.md` |

## References

- Companion skills: `react-development`, `nextjs-app-router`, `tailwind-css`, `responsive-design`, `form-ux-design`, `frontend-performance`, `ux-principles-101`.
- Use `references/interface-consistency.md` when a new module risks drifting from the established UI language.
- Free: Shadcn/ui (`ui.shadcn.com`), TanStack Table (`tanstack.com/table`), Atomic Design (`atomicdesign.bradfrost.com`), React Hook Form (`react-hook-form.com`), Zod (`zod.dev`).
- For the Bootstrap/Tabler/PHP seeder stack, load `sections/01-overview.md` and onwards.
<!-- dual-compat-end -->

## Overview

This skill prescribes the component architecture and interaction patterns for a modern SaaS web UI. The house stack is **Next.js App Router + React 19 + TypeScript + Tailwind** with **Shadcn/ui primitives** and **TanStack Query/Table/Form** where appropriate. Every section below is a reusable primitive or a layout pattern; build once, compose everywhere.

**Cardinal rule:** every data surface has four states — *loading, empty, error, success* — wired up *before* real data arrives. Screens without all four leak into production as broken pages.

---

## 1. SaaS Application Shell

Three regions: **sidebar** (primary nav), **topbar** (tenant switcher, search, user menu), **content**. The shell is a route group layout.

```tsx
// app/(app)/layout.tsx
import { Sidebar } from '@/components/shell/Sidebar';
import { Topbar } from '@/components/shell/Topbar';
export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="grid min-h-screen grid-cols-[auto_1fr] bg-slate-50 dark:bg-slate-950">
      <Sidebar />
      <div className="flex min-w-0 flex-col">
        <Topbar />
        <main className="flex-1 overflow-x-hidden p-6">{children}</main>
      </div>
    </div>
  );
}
```

The sidebar controls its own width with `data-collapsed` state persisted to `localStorage`. Never reach into the shell from a page — pages only fill `main`.

---

## 2. Navigation Patterns

Sidebar: collapsible, per-section groups, active-route highlight, hover-expand on collapsed state. Mobile: off-canvas drawer behind a hamburger; closes on route change.

```tsx
<Link
  href={item.href}
  aria-current={active ? 'page' : undefined}
  className={cn(
    'flex items-center gap-3 rounded-md px-3 py-2 text-sm',
    'hover:bg-slate-100 dark:hover:bg-slate-800',
    active && 'bg-slate-200 font-medium dark:bg-slate-700',
  )}
>
  <item.icon className="h-4 w-4 shrink-0" /> <span className="truncate">{item.label}</span>
</Link>
```

Breadcrumbs render from the matched route segments — never hand-coded per page. Use `usePathname()` + a `routeTitles` map.

---

## 3. Dashboard Layout

12-column grid on `lg:`, stacking on `sm:`. Hero KPI strip (3–4 cards), chart area (8 cols), activity feed (4 cols), recent items table full-width below.

```tsx
<div className="grid grid-cols-1 gap-4 lg:grid-cols-12">
  <KpiCard label="MRR" value="$42.3k" trend="+8.2%" className="lg:col-span-3" />
  <KpiCard label="Active users" value="1,284" trend="+3.1%" className="lg:col-span-3" />
  <KpiCard label="Churn" value="1.9%" trend="-0.4%" className="lg:col-span-3" />
  <KpiCard label="NRR" value="112%" trend="+2%" className="lg:col-span-3" />
  <RevenueChart  className="lg:col-span-8" />
  <ActivityFeed  className="lg:col-span-4" />
  <RecentOrders  className="lg:col-span-12" />
</div>
```

KPI cards show loading as shimmer blocks of the same height — never collapse vertical rhythm.

---

## 4. Data Table Architecture (TanStack Table)

One `DataTable<T>` primitive. Column definitions live in the feature folder. Server-side pagination, sorting, filtering — client-side only when the dataset is bounded (<500 rows).

```tsx
const columns: ColumnDef<Order>[] = [
  { accessorKey: 'number', header: 'Order' },
  { accessorKey: 'customer', header: 'Customer' },
  { accessorKey: 'total', header: 'Total',
    cell: ({ row }) => formatCurrency(row.original.total, row.original.currency) },
  { id: 'actions', cell: ({ row }) => <RowActions order={row.original} /> },
];

const table = useReactTable({
  data, columns,
  pageCount, state: { pagination, sorting, columnFilters },
  manualPagination: true, manualSorting: true, manualFiltering: true,
  onPaginationChange: setPagination, onSortingChange: setSorting,
  getCoreRowModel: getCoreRowModel(),
});
```

Row actions open a dropdown *anchored to the row*, never a global menu. Use `stickyHeader` on tables taller than a viewport.

---

## 5. Form Architecture (React Hook Form + Zod)

Every form is a Zod schema + RHF hook + `FormField` primitives. Submit handlers are async and return a typed result — never throw into the void.

```tsx
const schema = z.object({
  name: z.string().min(2, 'Too short').max(60),
  email: z.string().email(),
  role: z.enum(['admin', 'editor', 'viewer']),
});
type Values = z.infer<typeof schema>;

export function InviteUserForm({ onSuccess }: { onSuccess: () => void }) {
  const form = useForm<Values>({ resolver: zodResolver(schema) });
  const mutation = useMutation({ mutationFn: inviteUser });
  return (
    <form onSubmit={form.handleSubmit(async (v) => {
      await mutation.mutateAsync(v);
      onSuccess();
    })} className="space-y-4">
      <FormField control={form.control} name="name" label="Full name" />
      <FormField control={form.control} name="email" label="Email" type="email" />
      <FormSelect control={form.control} name="role" label="Role"
        options={[['admin','Admin'],['editor','Editor'],['viewer','Viewer']]} />
      <Button type="submit" disabled={mutation.isPending}>
        {mutation.isPending ? 'Sending…' : 'Send invite'}
      </Button>
    </form>
  );
}
```

`FormField` owns the label, error, description, and the input. Load `form-ux-design` for field-level patterns across web + mobile.

---

## 6. Modal & Drawer Patterns

Modals for focused edits; slide-over drawers for "view-with-actions" where context behind matters. Never more than one stacked modal. Destructive actions always go through `ConfirmDialog` with a typed confirm label.

```tsx
<ConfirmDialog
  open={open} onOpenChange={setOpen}
  title="Delete workspace" description="This cannot be undone."
  confirmLabel="Delete" destructive
  onConfirm={() => deleteWorkspace(id)}
/>
```

Dialog content is always in a Radix `Dialog` — focus trap and escape-to-close are not negotiable.

---

## 7. Loading States

Skeleton screens for initial route loads; spinners only for button-level pending states. Use Suspense boundaries around the content area so route transitions paint the shell immediately.

```tsx
<Suspense fallback={<DashboardSkeleton />}>
  <DashboardContent />
</Suspense>
```

Optimistic updates: React Query `onMutate` sets the new value; `onError` rolls back; `onSettled` invalidates.

---

## 8. Error Boundaries

Every route has an error boundary. Global handler sends to Sentry; the UI offers "Try again" and a support channel link.

```tsx
// app/(app)/orders/error.tsx
'use client';
export default function Error({ error, reset }: { error: Error; reset: () => void }) {
  useEffect(() => { Sentry.captureException(error); }, [error]);
  return (
    <EmptyState
      icon={AlertTriangle}
      title="Something went wrong"
      description={error.message}
      primary={{ label: 'Try again', onClick: reset }}
      secondary={{ label: 'Contact support', href: '/support' }}
    />
  );
}
```

Never show a raw stack in production. Log the `digest` to give support a lookup handle.

---

## 9. Toast Notifications

Sonner for SaaS — one per result, stacked top-right. Success toasts auto-dismiss in 4 s; error toasts require dismissal.

```tsx
toast.success('Invite sent', { description: values.email });
toast.error('Failed to save', { description: err.message, duration: Infinity });
const t = toast.loading('Uploading…');
upload().then(() => toast.success('Uploaded', { id: t })).catch(() => toast.error('Failed', { id: t }));
```

Never use toast for navigation-required errors — route to an error page or a banner instead.

---

## 10. Authentication Flow UI

Login, register, forgot-password, reset-password, 2FA. Single-column, narrow (`max-w-sm`), centred, with a subtle brand header. Auth pages never render the shell.

```tsx
// app/(auth)/login/page.tsx
export default function Login() {
  return (
    <div className="mx-auto mt-24 max-w-sm space-y-6">
      <BrandMark />
      <h1 className="text-2xl font-semibold">Sign in</h1>
      <LoginForm />
      <p className="text-sm text-slate-500">
        New here? <Link className="underline" href="/register">Create an account</Link>
      </p>
    </div>
  );
}
```

Post-login redirect: honour `?redirect=` if same-origin; fall back to `/`. 2FA input is a 6-digit `<OTPInput>` — no free-form text field.

---

## 11. Multi-Tenant Switcher

Tenants identify by slug and appear in the URL: `/[tenant]/orders`. The `TenantSwitcher` lives top-left in the topbar, persists the last-chosen tenant, and shows a quick-filter for power users with many tenants.

```tsx
<Combobox
  value={current.slug}
  onChange={(slug) => router.push(`/${slug}${restOfPath}`)}
  options={tenants.map(t => ({ value: t.slug, label: t.name, meta: t.plan }))}
  placeholder="Switch workspace"
/>
```

Tenant-scoped API requests derive the tenant from context; never from a client-provided header that the user could forge. Load `multi-tenant-saas-architecture` for the backend isolation model.

---

## 12. Dark Mode

Class strategy (`dark:`) with a tri-state switch (system / light / dark). Persist to `localStorage`; set on `<html>` before first paint to avoid flicker.

```tsx
// app/layout.tsx — inline script before hydration
<script dangerouslySetInnerHTML={{ __html: `
  try {
    const t = localStorage.getItem('theme');
    if (t === 'dark' || (!t && matchMedia('(prefers-color-scheme: dark)').matches))
      document.documentElement.classList.add('dark');
  } catch {}
` }} />
```

Theme tokens live as CSS variables (`--bg`, `--fg`, `--muted`, `--accent`) so charts + third-party widgets can read them. Avoid hard-coded Tailwind greys in components — use semantic tokens.

---

## 13. File Upload Patterns

Drag-and-drop zone with keyboard fallback (button + hidden `<input type="file">`). Client-side size + type validation before upload begins. Upload via a signed-URL path — never stream through the app server.

```tsx
const { getRootProps, getInputProps, isDragActive } = useDropzone({
  accept: { 'image/*': ['.png', '.jpg', '.jpeg', '.webp'] },
  maxSize: 10 * 1024 * 1024,
  onDrop: (files) => startUpload(files),
});
return (
  <div {...getRootProps()} aria-label="Upload file"
    className={cn('rounded-md border-2 border-dashed p-8 text-center',
      isDragActive ? 'border-indigo-500 bg-indigo-50' : 'border-slate-300')}>
    <input {...getInputProps()} />
    <p>Drop files here or <span className="underline">browse</span></p>
  </div>
);
```

Progress bars read from the `XMLHttpRequest.upload` `progress` event or from the signed-URL provider's SDK. Every upload is cancellable with `AbortController`.

---

## 14. Empty State Design

Empty lists, empty dashboards, first-run onboarding. Three components: icon, short headline, concrete next action. Never just "No data."

```tsx
<EmptyState
  icon={Inbox}
  title="No invoices yet"
  description="When you bill a customer, invoices will appear here."
  primary={{ label: 'Create invoice', href: '/invoices/new' }}
  secondary={{ label: 'Read the billing guide', href: '/docs/billing' }}
/>
```

First-use onboarding: a checklist card on the dashboard; tick items as they complete; dismiss after all done with a "show me tips" toggle. See `ux-principles-101` for empty-state rules #34–#38.

---

## 15. Accessibility

Non-negotiables at merge time:

- **Keyboard:** every interactive widget reachable by Tab, activated by Enter/Space, dismissed by Escape. Radix primitives get this right by default — do not reinvent.
- **Focus:** `:focus-visible` outlines on all interactive elements. Tailwind's `focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-indigo-500` is the house token.
- **ARIA:** label every icon-only button with `aria-label`; mark live regions (`aria-live="polite"`) for toast containers; use `aria-current="page"` for active nav.
- **Contrast:** body text ≥ 4.5:1 against its background; ≥ 3:1 for 18pt or bold 14pt. Run `axe` in CI.
- **Motion:** respect `prefers-reduced-motion`. `motion-safe:` / `motion-reduce:` Tailwind variants.
- **Forms:** every input has a visible label; errors use `aria-invalid` and `aria-describedby`.

**Responsive sweep:** test at 360 px (mobile small), 768 px (tablet), 1280 px (laptop), 1920 px (desktop). No horizontal overflow, no content clipped behind fixed headers.

---

## Using This Skill with the Bootstrap/Tabler/PHP Seeder Stack

The repository's PHP seeder template uses Bootstrap 5 + Tabler + SweetAlert2 + DataTables + Flatpickr. The architecture, permissions, AJAX, photo, and responsive patterns for *that* stack are in the `sections/` directory. Load them progressively:

1. [Overview & Stack](./sections/01-overview.md) — when starting any PHP page.
2. [Security, Print/PDF, Dates](./sections/02-security-print-dates.md)
3. [Architecture, Panels, Menus](./sections/03-architecture-panels-menus.md)
4. [Permissions & Searchable Dropdowns](./sections/04-permissions-dropdowns.md)
5. [Templates & UI Components](./sections/05-templates-components.md)
6. [AJAX & Utilities](./sections/06-ajax-utilities.md)
7. [Responsive, Photo Cards, Flatpickr](./sections/07-responsive-photo-flatpickr.md)
8. [Best Practices & Aesthetics](./sections/08-best-practices-aesthetics.md)
9. [Interface Design](./sections/09-interface-design.md)
10. [SaaS UX Principles](./sections/10-saas-ux-principles.md)

The patterns in §§1–15 above apply to the React/Next.js stack; the `sections/` deep-dives apply to the PHP stack. Pick the one your codebase uses — do not mix.
