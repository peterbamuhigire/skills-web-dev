# Zod Shared Schemas (`packages/schemas`)

Cross-ref: `typescript-effective` for inference idioms; `typescript-mastery` for
branded types and schema composition; `form-ux-design` for consumption in forms.

The goal: one schema per concept, consumed by API validation, DB input checks, form
validation, test fixtures, and OpenAPI — without duplication.

## Package layout

```text
packages/schemas/
|-- src/
|   |-- primitives.ts      (Email, PhoneE164, UUID, Slug, Cuid, ISODate)
|   |-- enums.ts           (Role, Status, Currency)
|   |-- user.ts
|   |-- org.ts
|   |-- billing.ts
|   |-- common.ts          (Pagination, Problem, ApiError)
|   `-- index.ts           (barrel)
|-- package.json
`-- tsconfig.json
```

Rules:

- `primitives.ts` holds branded wrappers everything else builds on.
- One file per business concept; barrel from `index.ts`.
- No runtime dependencies except `zod`. No `@acme/db`, no `@acme/api`.
- Versioned shapes live side by side: `UserV1`, `UserV2` if you ship public API.

## Primitives

```ts
// src/primitives.ts
import { z } from "zod";

export const UUID = z.string().uuid().brand<"UUID">();
export type UUID = z.infer<typeof UUID>;

export const Email = z
  .string()
  .trim()
  .toLowerCase()
  .email()
  .max(254)
  .brand<"Email">();
export type Email = z.infer<typeof Email>;

export const Slug = z
  .string()
  .min(1)
  .max(64)
  .regex(/^[a-z0-9](?:[a-z0-9-]*[a-z0-9])?$/)
  .brand<"Slug">();
export type Slug = z.infer<typeof Slug>;

export const ISODate = z.coerce.date();

export const PhoneE164 = z
  .string()
  .regex(/^\+[1-9]\d{7,14}$/)
  .brand<"PhoneE164">();

export const NonEmptyString = (max = 255) => z.string().trim().min(1).max(max);
```

Branded primitives prevent mixing a raw `string` where a validated `Email` is
expected — the type system rejects `send(rawString)` until you parse through
`Email.parse(...)`.

## Enums — single source

```ts
// src/enums.ts
import { z } from "zod";

export const Role = z.enum(["admin", "member", "viewer"]);
export type Role = z.infer<typeof Role>;

export const SubscriptionStatus = z.enum([
  "trialing",
  "active",
  "past_due",
  "canceled",
  "paused",
]);
export type SubscriptionStatus = z.infer<typeof SubscriptionStatus>;
```

Use the same enum for Prisma:

```prisma
enum Role {
  admin
  member
  viewer
}
```

And the same for Drizzle:

```ts
import { Role } from "@acme/schemas";
export const roleEnum = pgEnum("role", Role.options);
```

Changing the enum becomes a single schema edit with downstream compile errors.

## Composition — base, create, update, public

```ts
// src/user.ts
import { z } from "zod";
import { UUID, Email, NonEmptyString, ISODate } from "./primitives.js";
import { Role } from "./enums.js";

const base = z.object({
  id: UUID,
  email: Email,
  name: NonEmptyString(100),
  role: Role,
  orgId: UUID,
  createdAt: ISODate,
  updatedAt: ISODate,
});

export const User = base.brand<"User">();
export type User = z.infer<typeof User>;

// Strip server-assigned fields for creation input
export const UserCreate = base
  .omit({ id: true, createdAt: true, updatedAt: true })
  .strict();
export type UserCreate = z.infer<typeof UserCreate>;

// Partial for PATCH, but name and email can never be empty strings
export const UserUpdate = UserCreate.partial().strict().refine(
  (v) => Object.keys(v).length > 0,
  { message: "must include at least one field" }
);
export type UserUpdate = z.infer<typeof UserUpdate>;

// Public (what non-admins can see) — drop sensitive fields
export const UserPublic = User.pick({ id: true, name: true, role: true });
export type UserPublic = z.infer<typeof UserPublic>;
```

Rule: derive, don't duplicate. `UserCreate`, `UserUpdate`, `UserPublic` are all
derived from `base`. Add a field once and downstream shapes reflect it.

## `.strict()` vs `.passthrough()`

- Client input: always `.strict()`. Unexpected keys are attacks or bugs.
- DB projection: `.strict()` to catch schema drift.
- Third-party payload you don't fully control (Stripe events): `.passthrough()` on
  inner objects; still pin the keys you read.

## Using the same schema across layers

### API validation (tRPC / Fastify)

```ts
import { UserCreate } from "@acme/schemas";

t.procedure.input(UserCreate).mutation(async ({ input }) => {
  // input is UserCreate with full validation already applied
});
```

### Prisma write, Drizzle write

Neither ORM accepts Zod directly, but runtime validation guards the boundary:

```ts
const data = UserCreate.parse(req.body);
await db.user.create({ data });
```

Prisma types happen to be assignable from `UserCreate` because both derive from the
same shape. When they disagree (e.g., a DB-only field with a default), Prisma's type
error tells you to extend the schema.

### React Hook Form

```tsx
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { UserCreate } from "@acme/schemas";

const { register, handleSubmit, formState } = useForm<UserCreate>({
  resolver: zodResolver(UserCreate),
  defaultValues: { role: "member" },
});
```

### Test fixtures

```ts
import { UserCreate } from "@acme/schemas";

export const aUserCreate = (overrides: Partial<UserCreate> = {}): UserCreate =>
  UserCreate.parse({
    email: "t@example.com",
    name: "Test",
    role: "member",
    orgId: "018f0c02-0000-7000-a000-000000000000",
    ...overrides,
  });
```

Parsing through the schema catches stale fixtures the moment the schema changes.

### OpenAPI emission

```ts
import { extendZodWithOpenApi } from "@asteasolutions/zod-to-openapi";
import { z } from "zod";
import { User } from "@acme/schemas";

extendZodWithOpenApi(z);
const UserDoc = User.openapi("User", { example: { /* ... */ } });
```

See `rest-plus-openapi.md`.

## Transformations and coercion

Schemas are the place to normalise:

```ts
export const SearchParams = z.object({
  q: z.string().trim().min(1).optional(),
  limit: z.coerce.number().int().min(1).max(100).default(25),
  cursor: UUID.optional(),
});
```

A GET handler receives `?limit=25` as a string; `z.coerce.number()` parses it once.
Downstream consumers see `number`.

## Discriminated unions for events

```ts
export const DomainEvent = z.discriminatedUnion("type", [
  z.object({
    type: z.literal("user.created"),
    occurredAt: ISODate,
    data: User.pick({ id: true, email: true, orgId: true }),
  }),
  z.object({
    type: z.literal("user.deleted"),
    occurredAt: ISODate,
    data: z.object({ id: UUID }),
  }),
  z.object({
    type: z.literal("subscription.status_changed"),
    occurredAt: ISODate,
    data: z.object({
      subscriptionId: UUID,
      from: SubscriptionStatus,
      to: SubscriptionStatus,
    }),
  }),
]);
export type DomainEvent = z.infer<typeof DomainEvent>;
```

Consumers `switch` on `type` and TypeScript narrows `data` automatically.

## Versioning schemas

When the external contract changes:

```ts
// src/user.ts
export const UserV1 = baseV1.brand<"UserV1">();
export const UserV2 = baseV2.brand<"UserV2">();

export const toV2 = (v1: z.infer<typeof UserV1>): z.infer<typeof UserV2> => ({
  ...v1,
  displayName: v1.name, // renamed
});
```

Internal code moves to `UserV2`; the API continues to emit `UserV1` from a migration
layer until the deprecation window closes.

## Performance

- `z.parse` is fast but not free — a validated hot path doing 50k rps will feel it.
- For Fastify, prefer TypeBox on the hot path; keep Zod for shared layers (forms,
  tests, tRPC).
- Do not wrap deeply nested schemas in `.refine` chains of 10+ predicates; collapse
  into one function for clarity and speed.

## Anti-patterns

- Two schemas for the "same" concept, one in frontend and one in backend. Kill one.
- `z.any()` and `z.unknown()` except at trust boundaries where you immediately
  narrow.
- `.optional()` everywhere out of habit — an optional field is a state you own.
- Hand-authored TS interfaces alongside a Zod schema. `z.infer` only.
- Exposing brand types across the wire without unwrapping — the JSON wire has no
  brand; parse on the receiving side.

## Decision rules

```text
Shape exists only server-side, one-off          -> inline z.object, no package entry
Shape crosses two layers                         -> hoist to packages/schemas
Shape exposed to external consumers              -> version it
Need a brand                                     -> add in primitives.ts, reuse
Need a lookup / enum                             -> enums.ts, reuse for DB + UI
```
