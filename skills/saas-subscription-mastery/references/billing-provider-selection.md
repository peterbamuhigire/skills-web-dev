# Billing Provider Selection

Changing billing providers is painful. Choose with a written scorecard, not by vendor demo or popularity. Consider tax treatment first — it separates Merchant-of-Record (MOR) providers from payment processors and defines your compliance scope for years.

## The providers

| Provider | Type | Primary strength | Watch out for |
|---|---|---|---|
| Stripe Billing | Processor + billing | Developer ergonomics, API depth, global payments | Tax is yours unless you add Stripe Tax; RevRec needs work |
| Paddle | MOR | Handles sales tax / VAT / GST globally | Less flexible billing lifecycle; fees higher |
| Lemon Squeezy | MOR | Simple, fast setup, MOR | Smaller provider; less enterprise; some lifecycle gaps |
| Chargebee | Billing orchestration | Subscription lifecycle, complex pricing, RevRec | Needs a processor (Stripe / Braintree) underneath |
| Recurly | Billing orchestration | Dunning sophistication, enterprise | Smaller ecosystem than Chargebee |
| Orb | Usage billing | Metered billing, complex usage pricing | Newer; best paired with Stripe |
| Maxio (Chargify + SaaSOptics) | Billing + RevRec | B2B SaaS, ASC 606 out of the box | Enterprise pricing |
| Zuora | Enterprise billing | Very large SaaS, complex contracts | Heavy, expensive, long implementation |

## MOR vs non-MOR

- **Merchant of Record** (Paddle, Lemon Squeezy, Gumroad, FastSpring) — the provider is the legal seller. They handle sales tax, VAT, GST globally. You get one fee; compliance is theirs.
- **Non-MOR** (Stripe, Chargebee, Recurly, Braintree, Adyen) — you are the merchant. You handle tax registration in every jurisdiction you're liable. Stripe Tax / Avalara / TaxJar can compute it but you still file.

Rule of thumb:

- Selling globally to consumers / SMB, small team, want no tax overhead — MOR.
- Enterprise, large volumes, want full control over pricing / lifecycle / negotiation — non-MOR.
- Fees: MOR charges 5–10% of revenue; non-MOR charges 2.9% + 0.30 / tx + tax-service fees. MOR is often more expensive at scale but eliminates tax work.

## Scoring rubric

Score each provider 1–5 on these dimensions. Weight by your priorities; sum.

| Dimension | What to look for |
|---|---|
| Tax / compliance | MOR? Auto-file? Coverage of your geos? Handling of EU VAT MOSS, UK VAT, US sales tax, GST (Australia, India, Canada)? |
| Geographies / currencies | Supported currencies; local payment methods (SEPA, iDEAL, BECS, ACH, bank transfer, Apple Pay, Google Pay, local wallets) |
| Subscription lifecycle | Trials, proration at upgrade/downgrade, mid-cycle plan change, pause, coupons, gift subscriptions, grace periods |
| Metered / usage billing | Event ingestion, aggregation models (max, sum, last, unique), pricing curves (tiered, graduated, volume), usage alerts |
| Revenue recognition | ASC 606 / IFRS 15 export, deferred-revenue handling, integration with NetSuite / Xero / QuickBooks / Sage |
| Dunning / retries | Smart retries, email cadence customisation, grace period, account-updater services |
| Integrations | CRM (Salesforce, HubSpot), CDP, warehouse, analytics, accounting |
| Fees | Transaction %, flat fees, platform fees, hidden overages |
| API / webhook quality | OpenAPI spec, SDKs in your languages, webhook reliability, idempotency support |
| Customer portal | Self-serve upgrade/downgrade, invoice history, receipt download, card update |
| Compliance | PCI DSS, SOC 2, GDPR, HIPAA (if relevant) |
| Migration path | Import tools, export tools, track record of customers migrating in / out |

## Typical picks by profile

| Profile | Recommended |
|---|---|
| Early-stage SaaS, global sales, small team | Paddle or Lemon Squeezy (MOR) |
| Growth-stage SaaS, US-centric, want flexibility | Stripe Billing + Stripe Tax |
| Usage-based product (infra, API) | Stripe + Orb, or Chargebee + metered module |
| Complex B2B SaaS, many pricing shapes | Chargebee or Recurly on top of Stripe |
| Enterprise SaaS, multi-entity, RevRec-heavy | Maxio or Zuora |
| Marketplace | Stripe Connect |
| Consumer subscription (apps, content) | Stripe + Apple / Google in-app for mobile, or RevenueCat for mobile unification |

## Decision process

1. Write the scorecard with weights specific to your business.
2. Shortlist 3 providers.
3. Build a decision memo with pros / cons / costs / total fees at current and projected scale.
4. Run a real integration POC — don't rely on demos. Aim to bill a live test account end-to-end.
5. Interview 2–3 current customers of each provider (ask about support, migration, hidden gotchas).
6. Model fees over 3 years at expected growth.
7. Confirm revenue-rec export works with your accounting stack.
8. Get sign-off from Engineering, Finance, and Legal.

## Migration considerations

If you're switching:

- Subscriptions migrate with their next renewal — don't force an early bill.
- Card-on-file migration requires PCI-compliant vaulting (most providers offer import assistance).
- Plan 3–6 months of parallel operation.
- Legacy customers may need to be grandfathered on old plans for the contract term.
- Invoices and historical RevRec must remain queryable — export before cutover.
- Communicate clearly with customers before any payment-method change.

## Cost modelling

At 1m ARR:

- Stripe Billing + Tax: ~2.9% + 0.30/tx + 0.5% Tax Stripe = ~4–5% effective.
- Paddle / Lemon Squeezy: ~5–8% effective (all-in with tax).
- Chargebee on Stripe: Chargebee platform fee (typically 0.5–1.5% of revenue, tiered) + Stripe processing.
- Enterprise tools (Zuora, Maxio): platform fees + implementation; can be 100k GBP+/year at scale.

Plug in 3-year revenue projections and pick the provider where effective cost is reasonable at scale, not just today.

## Anti-patterns

- Choosing by vendor demo without a POC.
- Underestimating tax complexity — "we'll deal with it later" is how businesses get surprised by EU VAT back-filings.
- Building in-house billing to save fees — hidden cost is 10x external in engineering, compliance, accounting.
- Locking into an enterprise tool prematurely.
- Ignoring mobile (Apple / Google) when your product has mobile paths — they take 15–30% and have their own billing.
- Not planning for revenue recognition — finance will regret this within 12 months.

## Cross-references

- `subscription-billing` — billing mechanics, dunning, tax specifics.
- `saas-business-metrics` — what the billing system must report.
- `expansion-revenue.md` — ensure provider supports your expansion mechanics.
