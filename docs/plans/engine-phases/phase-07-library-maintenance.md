# Phase 07: Library Maintenance

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Complete three critical stub skills that are blocking entire business verticals, formally deprecate four superseded Android skills, and add workflow automation depth to `microservices-communication` and network security depth to `web-app-security-audit`.

**Architecture:** No new skill directories. This phase is entirely maintenance: stub completion, deprecation marking, and targeted enhancements. Each completed stub becomes a full-depth skill — not a redirect to other skills.

**Tech Stack:** React + Tailwind (webapp-gui-design), POS UI patterns (pos-restaurant-ui-standard), inventory/warehouse domain (inventory-management), n8n + Temporal + Airflow (microservices-communication), WAF + zero-trust + VPN (web-app-security-audit).

---

## Dual-Compatibility Contract

All stubs completed in this phase must receive the full portable contract:
```
Use When → Do Not Use When → Required Inputs →
Workflow → Quality Standards → Anti-Patterns → Outputs → References
```

Frontmatter to add to every stub:
```yaml
metadata:
  portable: true
  compatible_with: [claude-code, codex]
```

Validate every skill after changes:
```bash
python -X utf8 skill-writing/scripts/quick_validate.py <skill-directory>
```

---

## Task 1: Complete `webapp-gui-design`

**Current state:** 27 lines — provides no guidance.

**Files:**
- Rewrite: `webapp-gui-design/SKILL.md`
- Create: `webapp-gui-design/references/saas-component-library.md`
- Create: `webapp-gui-design/references/dashboard-layout-patterns.md`

**Step 1:** Read current `webapp-gui-design/SKILL.md` content, then fully rewrite it.

New content for `webapp-gui-design/SKILL.md` (≤ 500 lines):
- Scope: this skill covers SaaS web app GUI architecture — component hierarchy, layout systems, and design tokens. For React component patterns → `react-development`. For Tailwind utility classes → `tailwind-css`. This skill connects them.
- SaaS layout anatomy: sidebar nav, topbar, main content area, slide-over panels, modals — when each is appropriate
- Component hierarchy: Page → Section → Block → Component — dependency rules, avoid prop drilling across more than 2 levels
- Design tokens in Tailwind: CSS custom properties for brand colours, spacing scale, border radii, typography — `tailwind.config.js` theme extension
- Navigation patterns: sidebar collapse, breadcrumbs, tabs vs. pills, active state handling
- Data display: tables with sorting/filtering/pagination, KPI cards, stat blocks, chart containers
- Forms at scale: multi-step wizards, inline edit, optimistic update with rollback
- Empty states: first-use empty state, filtered-to-nothing empty state, error state — each needs illustration + CTA
- Loading states: skeleton screens (not spinners) for list views, skeleton sizing matches real content
- Responsive strategy for SaaS: tablet sidebar collapses to bottom nav, mobile gets drawer nav — breakpoints for each

Anti-Patterns: building custom component libraries when Shadcn/UI + Tailwind suffice, inconsistent spacing not from the 8pt grid, no empty states, spinners instead of skeletons for content-heavy views.

**Step 2:** Write `references/saas-component-library.md` — recommended component stack: Shadcn/UI components + Tailwind + Radix UI primitives. Covers: Button, Input, Select, Combobox, Dialog, Sheet (slide-over), Toast, Table, Badge, Avatar, Dropdown. Include when to customise vs. use defaults.

**Step 3:** Write `references/dashboard-layout-patterns.md` — full layout templates: analytics dashboard, settings page, list + detail split view, onboarding wizard, billing page. Tailwind grid and flex patterns for each.

**Step 4:** Validate and commit.
```bash
python -X utf8 skill-writing/scripts/quick_validate.py webapp-gui-design
git add webapp-gui-design/
git commit -m "feat: complete webapp-gui-design stub — SaaS GUI architecture, Shadcn/UI, layout patterns"
```

---

## Task 2: Complete `pos-restaurant-ui-standard`

**Current state:** 39 lines — stub blocking the restaurant POS vertical.

**Files:**
- Rewrite: `pos-restaurant-ui-standard/SKILL.md`
- Create: `pos-restaurant-ui-standard/references/order-entry-patterns.md`
- Create: `pos-restaurant-ui-standard/references/kitchen-display-system.md`

**Step 1:** Read current content, then fully rewrite `pos-restaurant-ui-standard/SKILL.md`.

New content (≤ 500 lines):
- Order entry: category grid → item grid → modifier sheet → cart — swipe/tap interactions, large touch targets (min 48×48dp)
- Modifier selection: required vs. optional modifiers, multi-select, free text override, unavailable item handling
- Table management: floor plan view, table status (available, occupied, reserved, bill-requested), cover count
- Cart/ticket: running total, item quantity adjust inline, remove item swipe, split-bill flow, merge ticket
- Receipt printing: thermal printer integration (Bluetooth ESC/POS), receipt format, kitchen ticket format
- Kitchen Display System: order queue, item preparation status (new, in-progress, ready, served), bump bar
- Payment flows: cash (change calculation), card (Stripe Terminal or local processor), split payment
- Staff management: PIN login per shift, role-based access (cashier, waiter, manager, admin), void/refund permissions
- Offline mode: accept orders without internet, queue to sync when connectivity restores
- Performance: instant tap response (< 100ms), no spinners on order entry — optimistic UI

Anti-Patterns: small touch targets, modal dialogs for modifier selection (use bottom sheets), required network connection for order entry, no void/refund audit trail.

**Step 2:** Write `references/order-entry-patterns.md` — complete UI flow with state machine diagram (idle → category selected → item selected → modifiers → cart → payment → receipt).

**Step 3:** Write `references/kitchen-display-system.md` — KDS layout, real-time WebSocket order updates, bump/recall interaction, prep time tracking, alert thresholds.

**Step 4:** Validate and commit.
```bash
python -X utf8 skill-writing/scripts/quick_validate.py pos-restaurant-ui-standard
git add pos-restaurant-ui-standard/
git commit -m "feat: complete pos-restaurant-ui-standard stub — full POS UI patterns, KDS, offline mode"
```

---

## Task 3: Complete `inventory-management`

**Current state:** 40 lines — stub blocking pharmacy, logistics, and warehouse verticals.

**Files:**
- Rewrite: `inventory-management/SKILL.md`
- Create: `inventory-management/references/stock-operations.md`
- Create: `inventory-management/references/warehouse-barcode.md`

**Step 1:** Read current content, then fully rewrite `inventory-management/SKILL.md`.

New content (≤ 500 lines):
- Stock model: SKU, variants (size/colour), unit of measure, batch/lot tracking, expiry date (pharmacy), serial number tracking
- Stock levels: quantity on hand, quantity reserved (open orders), quantity available (on-hand minus reserved), reorder point, reorder quantity
- Reorder triggers: automatic purchase order generation when available qty < reorder point, supplier lead time buffer
- Barcode scanning: EAN-13, QR Code, GS1-128 — mobile camera scan (ML Kit / iOS AVFoundation) vs. Bluetooth scanner
- Batch operations: bulk receive (PO receipt), bulk pick (fulfilment), bulk transfer between locations
- Stock-take: partial count (by category), full count (by location), variance report, variance approval workflow
- FIFO/FEFO: picking logic — oldest batch / earliest expiry picked first; critical for pharmacy and food
- Supplier management: supplier catalogue, lead times, preferred suppliers per SKU, price history
- Reporting: stock valuation (FIFO cost), slow-moving stock report, overstock report, expiry alerts dashboard

Anti-Patterns: no batch tracking for perishable goods, not reserving stock on order creation (leads to oversell), manual stocktake without variance approval, no audit log for adjustments.

**Step 2:** Write `references/stock-operations.md` — database schema (products, variants, batches, stock_locations, stock_movements), SQL queries for stock level calculation, FIFO cost calculation.

**Step 3:** Write `references/warehouse-barcode.md` — mobile scanner integration (ML Kit barcode scanning in Compose, AVFoundation in SwiftUI), scan-to-receive workflow, scan-to-pick workflow, error handling for unknown barcodes.

**Step 4:** Validate and commit.
```bash
python -X utf8 skill-writing/scripts/quick_validate.py inventory-management
git add inventory-management/
git commit -m "feat: complete inventory-management stub — stock operations, FIFO, barcode, pharmacy patterns"
```

---

## Task 4: Deprecate Four Superseded Android Skills

**Files:**
- Modify: `android-reports/SKILL.md` — add deprecation header
- Modify: `android-saas-planning/SKILL.md` — add deprecation header
- Modify: `android-report-tables/SKILL.md` — add deprecation header
- Modify: `android-custom-icons/SKILL.md` — add deprecation header

**Step 1:** For each of the four files, add this as the very first line (before frontmatter or content):

```
> DEPRECATED: Use `mobile-reports` instead. This skill will be removed in a future cleanup.
```

Use the correct replacement for each:
- `android-reports` → `mobile-reports`
- `android-saas-planning` → `mobile-saas-planning`
- `android-report-tables` → `mobile-report-tables`
- `android-custom-icons` → `mobile-custom-icons`

**Step 2:** Commit.
```bash
git add android-reports/ android-saas-planning/ android-report-tables/ android-custom-icons/
git commit -m "chore: mark four android-* skills as deprecated (superseded by mobile-* equivalents)"
```

---

## Task 5: Enhance `microservices-communication`

**Files:**
- Modify: `microservices-communication/SKILL.md`
- Create: `microservices-communication/references/workflow-automation-engines.md`

**Step 1:** Read `microservices-communication/SKILL.md` in full before editing.

**Step 2:** Add **Workflow Automation Engines** section:
- n8n: self-hosted workflow automation, webhook triggers, node types, AI node, code node for custom logic — use for business process automation (send invoice → update CRM → notify Slack)
- Temporal: durable workflow execution, Activity/Workflow concepts, retry policies, `workflow.sleep()` for long-running processes — use for critical business workflows requiring durability (subscription billing, order fulfilment)
- Airflow: DAG-based data pipeline orchestration — use for data engineering and scheduled batch jobs, not real-time workflows
- Decision table: n8n (integration automation, low code) vs. Temporal (critical business logic, code-first) vs. Airflow (data pipelines, batch)

**Step 3:** Validate and commit.
```bash
python -X utf8 skill-writing/scripts/quick_validate.py microservices-communication
git add microservices-communication/
git commit -m "feat: enhance microservices-communication — workflow automation engines (n8n, Temporal, Airflow)"
```

---

## Task 6: Enhance `web-app-security-audit`

**Files:**
- Modify: `web-app-security-audit/SKILL.md`
- Create: `web-app-security-audit/references/network-security-layer.md`

**Step 1:** Read `web-app-security-audit/SKILL.md` in full before editing.

**Step 2:** Add **Network Security Architecture** section:
- Firewall design: ingress rules (allow 80/443 only to web tier, allow DB port only from app tier), egress allow-list
- WAF: Cloudflare WAF vs. AWS WAF — managed rule sets (OWASP Top 10, bot protection), custom rules for your app
- Zero-trust: no implicit trust by network position, mTLS between services, short-lived credentials, continuous verification
- VPN design: WireGuard for team access to private subnets, split tunnelling, multi-factor auth requirement

**Step 3:** Validate and commit.
```bash
python -X utf8 skill-writing/scripts/quick_validate.py web-app-security-audit
git add web-app-security-audit/
git commit -m "feat: enhance web-app-security-audit — network security layer, WAF, zero-trust, VPN"
```

---

## Success Gate

- [ ] `webapp-gui-design` is now a full skill (was 27 lines) — passes validator
- [ ] `pos-restaurant-ui-standard` is now a full skill (was 39 lines) — passes validator
- [ ] `inventory-management` is now a full skill (was 40 lines) — passes validator
- [ ] Four android-* files have DEPRECATED header
- [ ] `microservices-communication` passes validator after enhancement
- [ ] `web-app-security-audit` passes validator after enhancement

---

## Reading Material

| Priority | Resource | Format | Cost | Unlocks |
|----------|----------|--------|------|---------|
| 1 | Shadcn/UI documentation | Free (ui.shadcn.com) | Free | `webapp-gui-design` component stack |
| 2 | Radix UI documentation | Free (radix-ui.com) | Free | Accessible primitive components |
| 3 | n8n documentation | Free (docs.n8n.io) | Free | Workflow automation section |
| 4 | Temporal documentation | Free (docs.temporal.io) | Free | Durable workflow patterns |
| 5 | Cloudflare WAF documentation | Free (developers.cloudflare.com) | Free | WAF rules and bot protection |
| 6 | WireGuard documentation | Free (wireguard.com) | Free | VPN design patterns |

**Read first:** Shadcn/UI docs (for the webapp-gui-design stub) and Temporal docs (for workflow automation depth).

---

*Next → `phase-08-competitive-moats.md`*
