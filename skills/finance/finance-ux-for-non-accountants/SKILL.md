---
name: finance-ux-for-non-accountants
description: Workflow-first UX for cashiers, clerks, managers, family-business users, and other non-accountants who must record sales, receive payments, buy stock, pay suppliers, run payroll, close drawers, and resolve exceptions safely while the underlying accounting stays clean. Use when designing any non-accountant-facing finance / accounting UI in a Chwezi product. Pairs with finance-ui-pattern-library, which provides the components and tokens.
---

# Finance UX for Non-Accountants

## Overview

Cashiers, clerks, managers, and family-business users record sales, receive payments, buy stock, close drawers, and resolve exceptions in plain business language. Posting services convert approved business events into balanced, immutable, source-backed accounting entries. Accountants and auditors drill down later. The non-accountant should never see CoA codes, debit / credit, or journal IDs unless permission is explicitly granted.

## Required first reads

- `doctrine/accounting-finance-doctrine.md`
- `doctrine/references/design-system-finance-accounting.md`
- `doctrine/references/design-anti-patterns.md`
- `doctrine/references/role-conditioned-shell.md`
- `doctrine/references/status-taxonomy.md`
- `finance-ui-pattern-library` SKILL
- This skill's `references/workflow-vocabulary.md`.

## The non-accountant roles

| Role | What they do |
|---|---|
| Cashier | Record sale, receive payment, refund (request only), close drawer. |
| Clerk | Record purchases, supplier deposits, stock receipts. |
| Manager (branch / shop) | Approve refunds under threshold, review drawer closes, view branch dashboard. |
| Family-business helper | Holiday cover; tightest permission set. |
| Inventory hand | Receive stock, count stock, mark damaged. |
| Front-desk / school registrar / clinic receptionist | Receive fees, payments, issue receipts. |
| Site supervisor (construction / agribusiness) | Record materials in, hours, costs, sales of produce. |

## Workflow vocabulary

These are the **only** verbs that appear on the non-accountant workflow surface. The same business event maps to different accounting consequences under the hood — but the user never sees that mapping.

| Workflow verb | Accounting consequence |
|---|---|
| **Record a sale** | Posting: Dr Cash / Bank / Mobile Money / AR — Cr Sales — Cr Output VAT — Dr COGS — Cr Inventory. |
| **Receive payment** | Posting: Dr Cash / Bank / Mobile Money — Cr AR (or customer deposit). |
| **Refund** | Posting: Cr Cash / Bank — Dr Sales Returns — Dr Output VAT reversal — Cr COGS reversal — Dr Inventory. |
| **Record an expense** | Posting: Dr Expense — Cr Cash / Bank / Mobile Money. |
| **Buy stock** | Posting: Dr Inventory — Cr AP / Cash / Bank — Dr Input VAT. |
| **Receive a bill** | Posting: Dr Expense / Inventory — Cr AP — Dr Input VAT — Dr / Cr WHT Payable where applicable. |
| **Pay a supplier** | Posting: Dr AP — Cr Cash / Bank / Mobile Money — Cr WHT Payable for withholding. |
| **Run payroll** | Posting: Dr Gross Salaries — Cr Net Salaries Payable — Cr PAYE — Cr NSSF — Cr WHT — Cr Employer NSSF. |
| **Close my drawer** | Posting: Dr Cash on Hand — Cr POS Cash Tendered Clearing; variance to Cash Over / Short with exception flag. |
| **Match a payment** | Posting: depends on direction; ultimately clears clearing account. |
| **Count stock** | Posting: Dr / Cr Inventory — Cr / Dr Inventory Adjustments. |
| **Mark damaged** | Posting: Dr Inventory Adjustments — Cr Inventory. |
| **Issue a credit note** | Posting: Dr Sales Returns — Dr Output VAT reversal — Cr AR; restore inventory if applicable. |

## Screen patterns

### Home (per role)

- Top bar with entity / book / period / role.
- A few large cards: the role's most frequent action, the day's summary, an alert if any reconciliation is overdue.
- Bottom nav with at most 4 destinations.

### Record screens

- One primary action per screen ("Receive payment", "Record sale", …).
- Business-event fields first; accounting is auto-derived.
- Status pill shows where in lifecycle: `draft` → `awaiting-approval` → `posted`.
- After post: `View receipt`, `Reverse` (if permission), and a clear next-step CTA ("Record another sale").

### Drawer-close screen

- Big number: counted cash.
- Big number: expected cash.
- Variance: if any, large and obvious, in semantic colour.
- "Submit drawer close" requires manager review if variance exceeds the configured threshold.

### Match a payment

- A list of "money in" the user is unsure about.
- For each, a list of suggested AR invoices to match.
- A simple "match" button per pair.
- Or "hold as customer deposit" / "send to accountant".

### Notifications

- "Your refund request has been approved by your manager."
- "A bank deposit yesterday matches no sale; check it with the accountant."
- "Drawer close yesterday had a shortage of UGX 12,500; please add a note."

### Help

- One-tap help on every screen.
- Help is short, plain language, with a single example.
- "Talk to the accountant" button on every screen — opens a thread, not a help article.

## Guided corrections

When a non-accountant must "fix" a posted record:

- The system never offers `Edit`.
- The system offers `Reverse and re-do` (workflow surface verb), which under the hood produces a reversal and a new posting.
- The reversal carries the user's role and the reason from a short controlled list.
- The new posting follows the normal flow including approval if applicable.

## Approvals and reviewers

- Refunds, manual journal-like corrections, opening balances, supplier master-data changes, payroll changes, and period reopen always need the relevant reviewer.
- The approval UI is plain: "Your manager will review this. You'll get a notification when it's done."

## Exceptions are visible and actionable

The exception model is not "an error popup". It is a queue that the user (or another role) can act on:

- "3 deposits not matched to a sale."
- "1 supplier payment without a bill."
- "Your drawer close had a shortage."

## Microcopy rules

- Business words on workflow surfaces.
- No accountant jargon (`accrual`, `clearing`, `subledger`, `journal`).
- No system error codes unless paired with a plain explanation.
- Tone: helpful, never blaming. "We could not save this — let's try again" is correct; "Invalid input" is not.
- Action labels are verbs ("Receive payment", "Record sale"), not nouns ("Payment", "Sale").

## Permissions

Permissions are scoped narrowly. A cashier cannot create a supplier; only request one. A clerk cannot post a manual journal; only request one. The manager can approve refunds under threshold, not above. See `doctrine/references/role-conditioned-shell.md` for the matrix.

## Mobile considerations

- One-handed use.
- 44 px minimum touch targets.
- Skeleton + optimistic post + reconcile under flaky connectivity.
- Drawer close works offline; syncs when connected.
- Sale works offline; syncs when connected; EFRIS submission queues and confirms.

## Forbidden patterns

- CoA codes shown on the workflow surface.
- Debit / credit labels on the workflow surface.
- `Delete` button anywhere.
- Multi-tap journeys for one-tap actions ("Receive payment").
- Toasts that auto-close before being read.
- Approval-pending records left without an obvious "where it is" state.
- Help text dropped behind multiple taps.
- Hover-only affordances.

## Acceptance evidence

- Microcopy lint in the design system catches accountant jargon on workflow screens.
- Touch-target audit on every screen.
- Offline-cycle test for sale and drawer close.
- Reviewer-flow test from request → approved → posted.

## Files

- `SKILL.md`.
- `references/workflow-vocabulary.md` — the full vocabulary table.
- `references/microcopy-style.md` — voice and tone guide.
- `examples/cashier-day-flow.md` — a cashier's complete day on the workflow surface.

Last reviewed: 2026-05-12. Next review due: 2026-11-12.
