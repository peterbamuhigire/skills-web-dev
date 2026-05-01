# Context Map Template

The canonical artifact produced by `system-architecture-design` — lists the services/modules in the system, their ownership, and their relationships. Downstream skills (database, API, security, observability) consume this.

## Template

```markdown
# Context Map — <system name>

**As of:** YYYY-MM-DD
**Owner:** <team>

## Bounded contexts

| Context | Purpose | Owner team | Language / stack |
|---|---|---|---|
| checkout | order submission, payment authorisation | payments | Node + TS |
| catalogue | product browsing, search | commerce | PHP + MySQL |
| identity | auth, sessions, user profile | platform | Node + TS |
| ... | ... | ... | ... |

## Relationships

Use Domain-Driven-Design relationship labels. Direction indicates which context depends on which.

| Upstream | Downstream | Relationship | Notes |
|---|---|---|---|
| identity | checkout | Customer-Supplier | checkout depends on identity for the user's session |
| catalogue | checkout | Shared Kernel | both teams co-own the `product` record schema |
| checkout | payments-external-provider | Anticorruption Layer | translates external provider's API into our domain language |
| ... | ... | ... | ... |

Relationship types:

- **Partnership** — two contexts succeed or fail together, tightly coupled by agreement.
- **Customer-Supplier** — downstream depends on upstream; upstream considers downstream's needs during planning.
- **Shared Kernel** — a shared subset of the model, co-owned.
- **Conformist** — downstream accepts upstream's model as-is.
- **Anticorruption Layer** — downstream translates upstream's model into its own language.
- **Open Host Service** — upstream exposes a public protocol/interface (e.g., public API).
- **Published Language** — a formal shared language (e.g., an industry standard).
- **Separate Ways** — intentional disconnection; no integration.
- **Big Ball of Mud** — exists, should be escaped.

## External systems

| System | Purpose | Integration type | Contract owner |
|---|---|---|---|
| Stripe | payment processing | REST + webhooks | payments team |
| Sendgrid | transactional email | REST | platform team |
| ... | ... | ... | ... |

## Data ownership

| Data | Owner context | Where stored | Derived views |
|---|---|---|---|
| order | checkout | orders-db | analytics warehouse |
| product | catalogue | catalogue-db | search index |
| user | identity | identity-db | none |
| ... | ... | ... | ... |

## Out of scope

<Things that look like part of the system but are deliberately excluded. Often an important clarifier.>

## Revision log

| Date | Change | Author |
|---|---|---|
| YYYY-MM-DD | initial version | ... |
| YYYY-MM-DD | added fulfilment context | ... |
```

## Rules

1. Every bounded context has exactly one owner team.
2. Every cross-context arrow has a relationship label — no unlabelled arrows.
3. Every piece of data has exactly one owning context.
4. External systems are modelled explicitly, not hidden as "third-party".
5. Revision log is appended, never rewritten.

## Common failures

- **Contexts named by technology** ("nodejs service") instead of capability ("checkout"). The map should survive a stack migration.
- **Missing ownership.** If no team owns a context, it will rot.
- **Arrow without a label.** Unlabelled dependencies accumulate and become the big ball of mud.
- **No out-of-scope section.** Readers infer the scope; inference is wrong.
