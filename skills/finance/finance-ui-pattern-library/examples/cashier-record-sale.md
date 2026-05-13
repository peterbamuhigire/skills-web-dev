# Example — Cashier Record-Sale Screen (Workflow Surface, Mobile)

Mobile, comfortable density, light theme, role = Cashier.

## Wireframe

```
┌──────────────────────────────────────────────────────────┐
│  Chwezi Demo Ltd  ·  Tax book  ·  May 2026 [open]  ·     │
│  Cashier  ·  prod                              🔔  👤    │
├──────────────────────────────────────────────────────────┤
│                                                          │
│   Record a sale                                          │
│                                                          │
│   Items                                          + Add   │
│   ┌────────────────────────────────────────────────┐    │
│   │ 250 ml soda × 2                       UGX 4,000│    │
│   │ Bread loaf  × 1                      UGX 4,500 │    │
│   │ Tea sachet  × 3                      UGX 1,500 │    │
│   └────────────────────────────────────────────────┘    │
│                                                          │
│   Net                                       UGX 8,475    │
│   VAT (UG-VAT-STD)                          UGX 1,525    │
│   Gross                                    UGX 10,000    │
│                                                          │
│   Tendered                                               │
│   [ ●  Cash ]  [    Mobile money    ]  [   Card    ]    │
│                                                          │
│   Amount tendered                          UGX 10,000    │
│   Change                                       UGX 0     │
│                                                          │
│   ┌────────────────────────────────────────────────┐    │
│   │            Receive payment                      │    │
│   └────────────────────────────────────────────────┘    │
│                                                          │
│   Status: draft                                          │
│                                                          │
├──────────────────────────────────────────────────────────┤
│  🏠 Home    📥 Record    🔁 Reconcile    ⋯ More           │
└──────────────────────────────────────────────────────────┘
```

## What this screen does and does not do

**Does**

- Captures the business event (a sale) in plain business words.
- Decomposes gross into net + tax automatically at posting time.
- Reads the VAT rate from the source register; surfaces the tax code on the screen and on the printed receipt.
- Submits to the posting service when "Receive payment" is tapped.
- Stays usable on a low-spec Android with 3G.

**Does not**

- Show CoA account codes.
- Show journal lines or debits / credits.
- Allow `Delete` on a posted receipt.
- Allow editing once posted.

## Status lifecycle

- `draft` while the cashier is building the cart.
- `posted` when the cashier taps "Receive payment" and the posting service commits.
- `efris-submitted` → `efris-confirmed` runs in the background after `posted`.

## Drilldown

The cashier sees only this screen. The accountant who later opens the journal sees the lines (Dr POS Cash Tendered Clearing 10,000; Cr Sales — Goods 8,475; Cr Output VAT Control 1,525) plus the inventory COGS journal, and can drill from the journal back to this receipt and the EFRIS confirmation.

## What forbidden patterns are avoided

- No `Delete` button.
- No raw debit / credit on the cashier surface.
- Net / tax / gross shown as three rows, never collapsed.
- No green / red for chrome; the only colour signal in this view is the period chip (`open` = neutral). The status pill on the bottom is neutral until `posted` (then `gain` semantic green).

## Offline behaviour

If the device is offline:

- The receipt is accepted locally and posted to a local queue.
- The status reads `draft (offline)`.
- A skeleton chip in the top bar shows `pending sync: 3`.
- When connectivity returns, the queue posts to the server; the receipt confirms and EFRIS submission begins.

## Print

The thermal-printer rendering (40 columns) preserves a separate tax line:

```
   CHWEZI DEMO LTD
   TIN 1000123456 · Mukono Branch
   ----------------------------------------
   POS-2026-05-12-0042   Cashier: J. Doe
   2026-05-12  14:32
   ----------------------------------------
   250 ml soda                 2  UGX 4,000
   Bread loaf                  1  UGX 4,500
   Tea sachet                  3  UGX 1,500
   ----------------------------------------
   Net                            UGX 8,475
   VAT (UG-VAT-STD)               UGX 1,525
   Gross                         UGX 10,000

   Cash                          UGX 10,000
   Change                            UGX 0

   URA fiscal number: <…>
   Thank you.
```

Last reviewed: 2026-05-12. Next review due: 2026-11-12.
