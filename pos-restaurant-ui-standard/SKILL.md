---
name: pos-restaurant-ui-standard
description: Standard Restaurant POS UI derived from the Restaurant POS redesign plan.
  Use for any restaurant POS screen to enforce the approved layout, components, accessibility,
  and speed workflow.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

## Platform Notes

- Optional helper plugins may help in some environments, but they must not be treated as required for this skill.

# Restaurant POS UI Standard

<!-- dual-compat-start -->
## Use When

- Standard Restaurant POS UI derived from the Restaurant POS redesign plan. Use for any restaurant POS screen to enforce the approved layout, components, accessibility, and speed workflow.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `pos-restaurant-ui-standard` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve; load `references` only as needed.
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
| UX quality | Restaurant POS UI audit | Markdown doc covering the standard restaurant POS layout, input speed, and back-of-house integration findings | `docs/pos/restaurant-ui-audit.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->

Use this skill for any restaurant POS screen. It enforces the approved UI layout, workflow, and accessibility targets from the Restaurant POS redesign plan.

## When to Use

- Building or refactoring restaurant POS screens for tablet, kiosk, or handheld.
- Reviewing restaurant POS UX for speed, clarity, and kitchen integration.
- Standardising restaurant order entry, split billing, and KDS behaviour.

## Required Baseline

- Follow the three-level hierarchy: context (floor plan, table, covers), order (cart, modifiers), actions (send, pay, void).
- Use large touch targets (minimum 48×48dp; 56×56dp for primary actions; 64×64dp preferred for kitchen-floor use).
- Auto-focus search on order-entry load; debounce at 150 ms.
- Quick-access lanes for Recent, Favourites, and Popular items, refreshed per service.
- Sticky or floating cart with a single dominant Pay call-to-action.
- Never generate a fiscal invoice until Pay is confirmed; bills are non-fiscal previews.
- WCAG 2.2 AA compliance for contrast, focus order, and target size on every interactive surface.

## Restaurant POS Flow Overview

The canonical transaction lifecycle runs from seating through close. Every screen in the POS maps to exactly one phase in this lifecycle; screens that blur phase boundaries are rejected in review.

```text
+-----------+    +-----------+    +-----------+    +-----------+
| 1. Seat   | -> | 2. Order  | -> | 3. KDS    | -> | 4. Prep   |
|  table    |    |  entry    |    |  ticket   |    |  cook     |
+-----------+    +-----------+    +-----------+    +-----------+
                                                        |
                                                        v
+-----------+    +-----------+    +-----------+    +-----------+
| 8. Close  | <- | 7. Pay    | <- | 6. Bill   | <- | 5. Serve  |
|  table    |    |  settle   |    |  preview  |    |  runner   |
+-----------+    +-----------+    +-----------+    +-----------+
```

Lifecycle rules:

- Seat to Order: tap a table on the floor plan, pick covers, and the order entry screen opens with table and server pre-bound.
- Order to KDS: pressing Send routes items to the kitchen station printer or KDS screen and starts the prep timer.
- KDS to Serve: the kitchen bumps each ticket; the runner view shows "Ready" items grouped by table.
- Serve to Bill: Bill is a preview only; it does not commit revenue and can be reprinted any number of times.
- Pay to Close: payment settles the check, triggers accounting postings, and returns the table to Dirty until bussed.

## Floor Plan View

The floor plan is the default home screen for servers. It supports two layout modes toggled from the top bar: Grid (auto-arranged rectangles) and Freeform (drag-positioned tables, saved per venue).

Table status colour codes:

- Available: `#10B981` (green).
- Occupied: `#3B82F6` (blue).
- Reserved: `#F59E0B` (amber).
- Bill-Pending: `#EF4444` (red).
- Dirty: `#6B7280` (grey).

Status state table:

| From | To | Trigger | Side effect |
|------|----|---------|-------------|
| Available | Occupied | Seat covers | Start table timer |
| Occupied | Bill-Pending | Request bill | Lock item adds without manager PIN |
| Bill-Pending | Dirty | Payment settled | Post revenue, free check number |
| Dirty | Available | Busser marks clean | Reset timer, clear server binding |
| Available | Reserved | Booking synced | Lock seating window ±15 min |

Interaction rules:

- Minimum touch target per table tile: 56×56dp; tiles scale up to 88×88dp on 12" tablets.
- Tap assigns the current server; long-press opens the table detail sheet (covers, server, elapsed time, open check).
- Colour is never the only status cue; every tile also shows a status label and an icon for colour-blind operators.
- Floor plan auto-refreshes every 5 seconds while idle and immediately on status-change events from the server.

## Order Entry Flow

The order entry screen uses a three-panel layout optimised for 10" to 13" tablets in landscape. Portrait mode collapses the cart into a slide-over sheet.

Panel layout:

- Left panel (20% width): category tabs stacked vertically with icon plus label; selected tab uses `#3B82F6` background and white text.
- Centre panel (55% width): item grid with 3 to 5 columns depending on viewport; each item card shows name, price, and a small availability dot.
- Right panel (25% width): cart with line items, quantity steppers, modifier summary, and a sticky subtotal row.

Controls:

- Search bar pinned to the top of the centre panel, 48dp tall, auto-focused on load.
- Quantity stepper: circular +/- buttons at 48×48dp minimum; tapping the number opens a numeric pad for values above 9.
- Subtotal strip sticky at the bottom of the cart panel with Send and Pay buttons side by side; Send is secondary, Pay is primary.

React sketch:

```tsx
<OrderEntry>
  <CategoryTabs value={category} onChange={setCategory} />
  <ItemGrid
    items={items.filter(i => i.category === category)}
    onTap={addToCart}
    columns={responsive(3, 4, 5)}
  />
  <Cart
    lines={cart.lines}
    onQtyChange={updateQty}
    onRemove={removeLine}
    subtotal={cart.subtotal}
    onSend={sendToKitchen}
    onPay={openPayment}
  />
</OrderEntry>
```

Tailwind conventions:

- Item card: `rounded-2xl border border-slate-200 p-3 active:bg-slate-100`.
- Cart line: `flex items-center gap-2 py-2 border-b border-slate-100`.
- Primary Pay button: `h-14 px-6 rounded-xl bg-emerald-600 text-white text-lg font-semibold`.

## Modifier Selection

Modifiers open in a bottom sheet on tablets and a side sheet on wider screens. Each modifier group declares a selection rule and an optional price delta per option.

Group rule table:

| Group type | Selection | Example | Confirm rule |
|------------|-----------|---------|--------------|
| Mandatory single | exactly 1 | Protein: Beef, Chicken, Fish | Confirm disabled until picked |
| Mandatory multi | min N, max M | Sides: pick 2 of 4 | Confirm disabled until min met |
| Optional single | 0 or 1 | Sauce on side | Confirm always enabled |
| Optional multi | 0 to M | Extras: cheese, bacon | Confirm always enabled |

Rendering rules:

- Price delta is shown inline: `+UGX 2,000` or `-UGX 500`, right-aligned and using the monospaced numeric variant.
- Selected options use `#3B82F6` border and a check glyph; unselected use `#E5E7EB` border.
- A running modifier subtotal appears at the bottom of the sheet next to the Confirm button.

React component sketch:

```tsx
function ModifierSheet({ groups, onConfirm }) {
  const [selected, setSelected] = useState<Record<string, string[]>>({});
  const satisfied = groups
    .filter(g => g.mandatory)
    .every(g => (selected[g.id]?.length ?? 0) >= g.min);
  return (
    <Sheet>
      {groups.map(g => (
        <ModifierGroup
          key={g.id}
          group={g}
          value={selected[g.id] ?? []}
          onChange={v => setSelected(s => ({ ...s, [g.id]: v }))}
        />
      ))}
      <ConfirmBar
        disabled={!satisfied}
        delta={sumDelta(selected, groups)}
        onConfirm={() => onConfirm(selected)}
      />
    </Sheet>
  );
}
```

## Kitchen Display System (KDS)

The KDS renders each open ticket as a card on a dark canvas to reduce kitchen glare. Cards sort oldest-first and wrap to new columns on overflow.

Card anatomy:

- Header row: table number in 32dp bold, server initials, and elapsed time clock.
- Body: itemised list, with modifiers indented under their parent and allergen flags in `#EF4444`.
- Footer: prep time estimate, course tag (Starter, Main, Dessert), and the Bump button spanning full width.

Elapsed-time colour coding:

| Elapsed | Background | Border | Meaning |
|---------|------------|--------|---------|
| 0 to 5 min | `#064E3B` | `#10B981` | On track |
| 5 to 10 min | `#78350F` | `#F59E0B` | Watch |
| 10 min or more | `#7F1D1D` | `#EF4444` | Late, expedite |

Interaction rules:

- Bump gesture: single tap arms the ticket, a second tap within 3 seconds confirms and hides it; a slide-back pill offers a 10-second undo.
- Audio chime on new ticket: short 400 ms tone; muted during staff-configured quiet windows.
- Course firing: the expeditor taps Fire on a course to promote it from Hold to Active; held items render at 40% opacity.
- Item strike-through is not used; cancelled items are removed and a separate red Cancel banner surfaces the change.

## Table Management

Table operations are exposed from the table detail sheet and from the floor-plan long-press menu.

Core operations:

- Seat assignment: pick covers 1 to 8 with a stepper; values above 8 open a numeric pad. Covers are required before the first item send.
- Merge tables: drag table A onto table B; a confirmation dialog lists combined covers, merges open checks, and retains the earliest seat time.
- Split table: open the split sheet, drag seats from the source to a new table tile, and the source check forks into two linked checks.
- Table transfer: move the entire order from table A to table B with a single action; the KDS receives an update event so in-flight tickets reroute.

Merge and split rules:

- Merge is blocked when either table is in Bill-Pending; the user must settle or cancel the pending bill first.
- Split creates a new check that inherits the service charge and tax policy of the parent; tips are reallocated by cover count unless overridden.
- All merge, split, and transfer actions log an audit entry with the actor, timestamp, and source and target table IDs.

## Split Billing

Split billing is triggered from the check screen and supports three independent modes. Each mode generates one payment tab per split so the cashier settles them in any order.

Mode 1: Split by item.

- Seat tiles across the top of the screen show the cover count.
- The server drags each line item to a seat tile; unassigned items remain in a shared pool.
- A "Shared" pool divides its total equally across all seats on settlement.

Mode 2: Split by percentage.

- Presets for 50/50, 60/40, and 70/30; a Custom option lets the server type N shares that must sum to 100%.
- The preview shows the computed amount per share, rounded to the currency's smallest unit with the residual assigned to the first share.

Mode 3: Split by count.

- Even split across the seated cover count; the UI shows "UGX X per cover" and rounds the residual to cover 1.
- Supports a partial-count override for guests leaving early while others continue.

Common rules:

- Service charge and tax are split proportionally to each tab's subtotal share.
- Each split tab produces its own receipt and its own revenue posting reference; they share the parent check number with a suffix (`-A`, `-B`).
- Switching modes after the first payment is captured requires a manager PIN and voids the prior captures.

## Void & Refund Flow

Voids and refunds are privileged actions and always route through a manager PIN modal. The modal cannot be dismissed by tapping outside; it requires explicit Cancel.

Flow steps:

1. Server taps Void on a line or check.
2. Manager PIN modal opens; four- to six-digit PIN with lockout after 5 failures in 10 minutes.
3. Reason code dropdown appears with the fixed set: Entered in error, Customer cancelled, Kitchen mistake, Comp, Other (requires free-text note of at least 10 characters).
4. Void preview shows the impact on subtotal, tax, service charge, and tip.
5. Confirm writes the void event, notifies the KDS if the item was already fired, and updates the check total.

Refund rules:

- Refund is available only after a payment is settled; partial refunds are allowed down to a single line.
- Refunds post to the original payment method when the gateway supports it; cash refunds open the cash drawer with an audit record.
- Both voids and refunds appear on the end-of-day reconciliation under dedicated totals, never netted into gross sales.

## Receipt Design

Receipts target 80mm thermal printers. The layout uses a monospaced font at 12pt body and 14pt for totals to keep character alignment under heat variance.

Vertical order:

1. Logo, capped at 80px height and 400px width, centred.
2. Restaurant name, address line, phone, and tax identifier.
3. Date and time, table number, server name, and check number.
4. Itemised list with modifiers indented 2 characters under their parent.
5. Subtotal, tax line per rate, service charge, and grand total, right-aligned.
6. Payment method, amount tendered, and change due.
7. Footer with a QR code linking to the digital receipt and feedback form.

Formatting rules:

- Currency amounts are right-aligned to a fixed column; the item name is left-aligned and truncated with an ellipsis at column 28.
- Modifier price deltas are shown in parentheses next to the modifier name.
- The QR code is 120×120 px and is quiet-zoned by 4 modules on all sides.
- Re-printed receipts carry a "REPRINT" watermark and a sequence number.

## End-of-Day Reconciliation

Shift close opens a reconciliation workflow that a manager must complete before the POS will accept a new shift.

Summary sections:

- Gross sales, voids, refunds, and net sales, shown as currency totals and as counts.
- Sales by category: Food, Beverage, and Other, each with subtotal, tax, and tip share.
- Sales by payment method: Cash, Card, MoMo, Airtel Money, Bank Transfer, and House Account.
- Tip total by server and a separate pooled-tip figure when tip pooling is enabled.
- Discrepancy report comparing expected cash-drawer balance to the counted balance; differences over a configurable threshold require a manager note.

Close rules:

- The reconciliation snapshot is immutable once signed; corrections are posted as adjustments to the next shift.
- Exports are written as CSV and PDF to the shift archive and pushed to the accounting module through the companion `saas-accounting-system` skill.
- Any open check on the floor plan blocks close; the manager must settle or transfer it explicitly.

## Staff Management UI

Staff operations live in a dedicated back-office tab. The front-of-house POS exposes only clock-in, clock-out, and tip summary.

Clock-in and clock-out:

- 4-digit PIN entry with an optional selfie photo for shift audit.
- Lockout after 5 failed PIN attempts within 10 minutes; manager override clears the lock.
- Clock events write to the timekeeping table and surface in the shift reconciliation.

Tip allocation view:

- Totals by server and by shift, with filters for date range and service (Lunch, Dinner, All-day).
- Pooled-tip view shows the pool, the allocation rule (by hours, by sales, or by points), and each recipient's computed share.

Server performance:

- Orders completed, average ticket size, and upsell rate expressed as a percentage of eligible tickets that added a premium modifier or upsell item.
- Ranked table with the top and bottom 5 performers; rankings are advisory and are never surfaced to guests.

## Offline Mode

The POS must keep taking orders when the network is unavailable. Offline mode uses an IndexedDB queue (Dexie.js) and a cached menu snapshot.

Offline behaviours:

- Menu cache is refreshed on login and every 15 minutes while online; the cache carries a signed version tag.
- Orders, voids, and payments are written to a local queue keyed by a client-generated UUID so retries are idempotent.
- KDS routing falls back to a station printer when the KDS is unreachable; tickets are replayed on reconnect with a duplicate-suppression window.
- The UI surfaces an offline banner in `#F59E0B` with a queued-operation count; tapping the banner opens the queue inspector.

Conflict resolution:

- Default is last-writer-wins on non-financial fields.
- Price, tax rate, and modifier price are server-authoritative; on conflict the local record is recomputed and the operator is notified if the total changes.
- Conflicts that cannot be auto-resolved are parked in a review queue and block close until a manager acknowledges them.

Cross-reference: `pwa-offline-first` for the underlying queue, service-worker, and sync mechanics.

## Accessibility

The POS is used under bright kitchen light, with gloved hands, and across long shifts. Accessibility is a functional requirement, not a bolt-on.

Touch and pointer:

- All interactive targets are at least 48×48dp; primary flow targets are 56×56dp. WCAG 2.2 target size AA is 24×24 CSS px, but the kitchen-floor minimum is 48.
- Spacing between adjacent targets is at least 8dp to prevent mis-taps with gloves.
- Long-press is never the only path to an action; every long-press has a visible button equivalent.

Colour and contrast:

- Text contrast ratio is at least 4.5:1 against its background for body copy and 3:1 for large text (18pt or 14pt bold).
- A high-contrast theme toggle swaps the palette to a near-black background with `#FFFFFF` text and `#FBBF24` focus rings, tuned for bright kitchens.
- Status colour is always paired with an icon and a label, never colour alone.

Input and feedback:

- Audio feedback is opt-in per device and uses distinct tones for Send, Void, and Error.
- Haptic feedback mirrors audio where the device supports it.
- All forms expose visible focus, programmatic focus, and keyboard navigation for external-keyboard users at the cashier station.

## Canonical Source

The canonical layout and component specs live in:

- `docs/plans/restaurant-pos/2026-02-03-restaurant-pos-ui-redesign.md` (project-local design reference when present).

## Companion Skills

- `pos-sales-ui-design` — general POS patterns (cart, checkout, payment).
- `webapp-gui-design` — React/Next.js/Tailwind design-system conventions.
- `pwa-offline-first` — offline order queueing and sync.
- `mobile-rbac` — roles for waiter, cashier, manager.
- `saas-accounting-system` — revenue lines for food/beverage/other.
- `inventory-management` — ingredient-level depletion on order completion.

## Sources

- Apple HIG for iPad POS — `developer.apple.com/design/human-interface-guidelines`
- Material Design for Android tablets — `m3.material.io`
- WCAG 2.2 target size — `w3.org/TR/WCAG22`
- Square POS product docs (industry reference) — `squareup.com`

## References

- [references/restaurant-pos-ui-standard.md](references/restaurant-pos-ui-standard.md)
