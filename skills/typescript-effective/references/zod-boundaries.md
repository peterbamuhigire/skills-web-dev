# Zod at boundaries

Every byte that enters the process from outside — HTTP body, env var, database row, queue payload, file content, form submission — passes through a Zod schema. Inside the trust boundary, types are inferred from those schemas. No duplicated type declarations; no hand-rolled validators.

Targeted at Zod 3.22+. Notes for Zod 4 at the end.

## Why Zod

- Single source of truth for shape and runtime validation.
- `z.infer` gives you the static type for free.
- Excellent error ergonomics (`.flatten()`, `.format()`).
- Composable (`.merge`, `.extend`, `.pick`, `.omit`, `.partial`).
- Discriminated unions with full narrowing.

## Basic schema

```ts
import { z } from "zod";

export const UserCreate = z.object({
  email: z.string().email(),
  name: z.string().min(1).max(120),
  age: z.number().int().min(0).max(150),
  role: z.enum(["admin", "member", "viewer"]),
  tags: z.array(z.string()).max(20).default([]),
}).strict();

export type UserCreate = z.infer<typeof UserCreate>;
```

- `.strict()` rejects unknown keys. Use everywhere unless you need a pass-through.
- `.strip()` (default) drops unknown keys silently.
- `.passthrough()` keeps unknown keys — rare, usually smells.

## `parse` vs `safeParse`

```ts
// throws on invalid input
const user = UserCreate.parse(input);

// returns a discriminated result — preferred at boundaries
const parsed = UserCreate.safeParse(input);
if (!parsed.success) return res.status(400).json(parsed.error.flatten());
const user = parsed.data;
```

Prefer `safeParse` at boundaries so you control the HTTP response. Use `parse` in internal code where failure is a programmer bug.

## Composition

```ts
const Base = z.object({ id: z.string().uuid(), createdAt: z.date() });

const User = Base.extend({ email: z.string().email(), name: z.string() });
const UserPatch = User.pick({ email: true, name: true }).partial();
const UserWithRoles = User.merge(z.object({ roles: z.array(z.string()) }));
const PublicUser = User.omit({ email: true });
```

## Refinements

Constraints that cannot be expressed with simple validators:

```ts
const DateRange = z.object({
  from: z.date(),
  to: z.date(),
}).refine((v) => v.to >= v.from, {
  message: "'to' must not be earlier than 'from'",
  path: ["to"],
});

const Password = z.string().min(12).refine(
  (s) => /[A-Z]/.test(s) && /\d/.test(s),
  { message: "must include uppercase and digit" },
);
```

Use `.superRefine` when you need access to Zod's issue context and want to emit multiple errors:

```ts
const Booking = z.object({ from: z.date(), to: z.date(), guests: z.number() })
  .superRefine((v, ctx) => {
    if (v.to < v.from)  ctx.addIssue({ code: "custom", path: ["to"], message: "end before start" });
    if (v.guests < 1)   ctx.addIssue({ code: "custom", path: ["guests"], message: "at least 1" });
  });
```

## Transforms

Parse, then reshape. The inferred type reflects the output, not the input.

```ts
const TrimmedLower = z.string().transform((s) => s.trim().toLowerCase());
const EmailNorm   = TrimmedLower.pipe(z.string().email());

const DateFromIso = z.string().datetime().transform((s) => new Date(s));

const UserRow = z.object({
  email: EmailNorm,
  createdAt: DateFromIso,
});

type UserRow = z.infer<typeof UserRow>;
// { email: string; createdAt: Date }
```

## Discriminated unions

```ts
const Event = z.discriminatedUnion("kind", [
  z.object({ kind: z.literal("login"),    userId: z.string().uuid() }),
  z.object({ kind: z.literal("logout"),   userId: z.string().uuid(), at: z.date() }),
  z.object({ kind: z.literal("purchase"), userId: z.string().uuid(), amount: z.number().positive() }),
]);

type Event = z.infer<typeof Event>;
```

Discriminated unions are faster to parse than plain unions and produce cleaner narrowing in downstream code.

## Environment variables

Fail fast on boot; never ship with missing env.

```ts
// src/env.ts
import { z } from "zod";

const EnvSchema = z.object({
  NODE_ENV: z.enum(["development", "test", "production"]),
  DATABASE_URL: z.string().url(),
  PORT: z.coerce.number().int().min(1).max(65535).default(3000),
  LOG_LEVEL: z.enum(["debug", "info", "warn", "error"]).default("info"),
  JWT_SECRET: z.string().min(32),
  REDIS_URL: z.string().url().optional(),
});

const parsed = EnvSchema.safeParse(process.env);
if (!parsed.success) {
  console.error("invalid env", parsed.error.flatten().fieldErrors);
  process.exit(1);
}
export const env = parsed.data;
```

- `z.coerce.number()` turns env strings into numbers.
- Import `env` everywhere — never reach into `process.env` directly.

## Form data (React Hook Form)

```ts
import { zodResolver } from "@hookform/resolvers/zod";

const Signup = z.object({
  email: z.string().email(),
  password: z.string().min(12),
  confirm: z.string(),
}).refine((v) => v.password === v.confirm, {
  message: "passwords do not match",
  path: ["confirm"],
});

const form = useForm<z.infer<typeof Signup>>({ resolver: zodResolver(Signup) });
```

## API responses (fetch)

```ts
async function fetchUser(id: string): Promise<User> {
  const res = await fetch(`/api/users/${id}`);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return UserSchema.parse(await res.json());
}
```

Never trust a server response by type assertion — validate.

## Async validation

```ts
const Username = z.string().min(3).refine(
  async (u) => !(await db.user.findUnique({ where: { username: u } })),
  { message: "already taken" },
);

await UsernameSchema.parseAsync("peter");
```

Async refinements require `parseAsync` / `safeParseAsync`.

## Error flattening and formatting

```ts
const r = UserCreate.safeParse(body);
if (!r.success) {
  // shape: { formErrors: string[]; fieldErrors: Record<string, string[]> }
  const errors = r.error.flatten();
  return res.status(400).json({ errors });
}
```

For nested objects use `.format()` which mirrors the input shape with `_errors` arrays.

## Reusing schemas across layers

- Shared `packages/schemas` for server + client + mobile.
- Server validates inbound request, outbound response. Client reuses the same schemas.
- tRPC and Hono already integrate Zod schemas at the procedure level.

## Performance

- Keep schemas at module scope (not inside request handlers).
- Prefer discriminated unions over plain unions for >3 variants.
- For very hot paths, run the schema once, cache the typed value, pass it down.

## Zod 4 notes

Zod 4 (released 2024) drops some Zod 3 quirks and adds `.min` on records, faster union parsing, and refined error paths. Migration is mostly drop-in; test thoroughly. See the Zod 4 changelog for exact renames.

## Anti-patterns

- Type then validate separately — always `z.infer<typeof Schema>`.
- `z.any()` — defeats the purpose.
- `z.object({...}).passthrough()` by default — silent data smuggling.
- Validating at the controller then again at the service — validate once at the boundary.
- Constructing a Zod schema inside a hot loop — allocation pressure.
- Casting parsed data back to a wider type — the whole pipeline collapses.

## Cross-reference

Parallel of Python's `python-modern-standards/references/pydantic-v2-patterns.md`. Zod and Pydantic converge on the same idea: parse at the boundary, trust inside.
