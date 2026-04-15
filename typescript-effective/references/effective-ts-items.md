# Effective TypeScript — 35 items

Condensed, opinionated items. Each: the rule, a before/after, and the decision cue. Aligned to Dan Vanderkam's themes and current (5.4+) idioms.

## 1. Think of TS as JS with types

Type errors do not change runtime. Erased types are still just JS at runtime — a stray `as` does nothing at run-time.

## 2. Use strict mode always

See `tsconfig-production.md`. Without `strict`, the remaining items lose half their value.

## 3. Prefer types that narrow values (branded types)

```ts
// BEFORE
function send(to: string) { /* any string accepted */ }

// AFTER
type Email = string & { readonly __brand: "Email" };
function parseEmail(raw: string): Email | null {
  return /.+@.+\..+/.test(raw) ? (raw as Email) : null;
}
function send(to: Email) { /* only validated emails pass */ }
```

Brands cost zero at runtime, lift invariants into the type.

## 4. Discriminated unions with `assertNever`

```ts
type Shape =
  | { kind: "circle"; r: number }
  | { kind: "square"; side: number }
  | { kind: "rect"; w: number; h: number };

function area(s: Shape): number {
  switch (s.kind) {
    case "circle": return Math.PI * s.r ** 2;
    case "square": return s.side ** 2;
    case "rect":   return s.w * s.h;
    default:       return assertNever(s);
  }
}

function assertNever(x: never): never {
  throw new Error(`unhandled: ${JSON.stringify(x)}`);
}
```

Adding a fourth variant causes a compile error in `area`. Exhaustiveness for free.

## 5. Narrow `unknown`, never trust it

```ts
// BEFORE
function parse(x: any) { return x.user.name; }  // crashes at runtime

// AFTER
function isUser(x: unknown): x is { user: { name: string } } {
  return typeof x === "object" && x !== null
    && "user" in x
    && typeof (x as any).user?.name === "string";
}
function parse(x: unknown): string | null {
  return isUser(x) ? x.user.name : null;
}
```

At boundaries prefer Zod (`zod-boundaries.md`) over hand-rolled guards.

## 6. Structural typing is truth

TS types describe shapes, not nominal identity. Two structurally identical types are interchangeable. Use brands when you need nominal behaviour.

## 7. Prefer `interface` for object shapes you extend; `type` for unions and mapped

```ts
interface User { id: string; email: string; }
interface Admin extends User { permissions: string[]; }

type Role = "admin" | "member";
type Readonly<T> = { readonly [K in keyof T]: T[K] };
```

Either works for most cases. Pick one convention per codebase.

## 8. `as const` for literal inference

```ts
// BEFORE — roles: string[]
const roles = ["admin", "member", "viewer"];

// AFTER — roles: readonly ["admin", "member", "viewer"]
const roles = ["admin", "member", "viewer"] as const;
type Role = (typeof roles)[number];  // "admin" | "member" | "viewer"
```

Derives union types from values, removes duplication.

## 9. `satisfies` for validated-but-not-widened values

```ts
// BEFORE — loses the concrete keys
const config: Record<string, { port: number }> = {
  api: { port: 3000 },
  web: { port: 5173 },
};
config.api.port;  // typed string but we lost "api"

// AFTER
const config = {
  api: { port: 3000 },
  web: { port: 5173 },
} satisfies Record<string, { port: number }>;
config.api.port;      // 3000 literal, autocomplete works
config.unknown;       // compile error
```

`satisfies` checks conformance without widening. Use it everywhere you used to type-annotate object literals.

## 10. `readonly` on parameters by default

```ts
function total(items: readonly Item[]): number {
  return items.reduce((n, i) => n + i.price, 0);
}
```

Prevents accidental mutation; helps the reader.

## 11. Utility types earn their keep

```ts
type UserDto = Omit<User, "passwordHash" | "internalNotes">;
type UserPatch = Partial<Pick<User, "email" | "name">>;
type UserKey = keyof User;
type UserValue = User[keyof User];
```

Prefer `Omit`, `Pick`, `Partial`, `Required`, `Readonly`, `NonNullable`, `Awaited`, `ReturnType`, `Parameters` before reaching for custom conditional types.

## 12. Conditional types — sparingly, well

```ts
type ArrayElement<T> = T extends readonly (infer U)[] ? U : never;
type UserEl = ArrayElement<User[]>;  // User
```

Good for library APIs. For app code, prefer concrete types.

## 13. Template literal types for IDs and routes

```ts
type UserId = `usr_${string}`;
type Route = `/${string}`;
function getUser(id: UserId) { /* ... */ }
getUser("usr_123");     // ok
getUser("plain");       // error
```

## 14. Declaration merging for module augmentation

```ts
// types/fastify.d.ts
import "fastify";
declare module "fastify" {
  interface FastifyRequest { user?: User; }
}
```

Use for extending third-party types; avoid merging your own interfaces — it hurts discoverability.

## 15. Generics should name constraints

```ts
// BEFORE — too permissive
function key<T>(obj: T, k: keyof T) { return obj[k]; }

// AFTER — constraint describes intent
function key<T extends Record<string, unknown>, K extends keyof T>(
  obj: T,
  k: K,
): T[K] {
  return obj[k];
}
```

## 16. Don't overload when a union works

```ts
// BEFORE
function len(x: string): number;
function len(x: unknown[]): number;
function len(x: string | unknown[]): number { return x.length; }

// AFTER
function len(x: string | readonly unknown[]): number { return x.length; }
```

Overloads only when the result type truly depends on input type (rare in app code).

## 17. Avoid `enum`; prefer string union or `as const` object

```ts
// BEFORE
enum Status { Active = "active", Inactive = "inactive" }

// AFTER
const Status = { Active: "active", Inactive: "inactive" } as const;
type Status = (typeof Status)[keyof typeof Status];
```

`enum` breaks erased-types philosophy and pollutes the output. String unions tree-shake better.

## 18. `never` for impossible states

```ts
type Loading = { state: "loading" };
type Error = { state: "error"; message: string };
type Done = { state: "done"; value: User };
type View = Loading | Error | Done;

// compile error if you try to access view.value without narrowing
```

"Make illegal states unrepresentable."

## 19. Avoid `any`. When forced, isolate and mark it

```ts
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const untyped = thirdPartyLib() as any;
const typed = UserSchema.parse(untyped);  // Zod gives us back safety
```

## 20. Prefer `unknown` to `any` at API boundaries

```ts
async function fetchJson(url: string): Promise<unknown> {
  const r = await fetch(url);
  return r.json();
}
```

Callers must narrow; that's the point.

## 21. Type guards are first-class functions

```ts
function isNonEmpty<T>(xs: readonly T[]): xs is readonly [T, ...T[]] {
  return xs.length > 0;
}
```

Use `x is T` return types to teach the compiler.

## 22. `asserts` for precondition guards

```ts
function assertDefined<T>(x: T | undefined, msg: string): asserts x is T {
  if (x === undefined) throw new Error(msg);
}
const user = findUser(id);
assertDefined(user, "missing user");
user.email;  // narrowed
```

Prefer Result return types for boundaries; use `asserts` for true invariants.

## 23. Function types — signatures over `Function`

```ts
// BAD
function use(f: Function) { /* any call is allowed */ }

// GOOD
function use(f: (e: Event) => void) { /* ... */ }
```

## 24. Parameter properties — optional, contextual

```ts
class UserService {
  constructor(private readonly db: Db, private readonly log: Logger) {}
}
```

Compact when the class is a thin shell over dependencies. When the class has logic, declare fields explicitly for readability.

## 25. `Object`, `{}` are almost never what you want

Use `Record<string, unknown>` for "any object", or a concrete shape.

## 26. `void` vs `undefined` in return types

`void` — caller shouldn't care what you return. `undefined` — you explicitly return `undefined`. Callbacks often want `void` to accept any return.

## 27. Prefer function return type inference, annotate for contracts

```ts
// internal helper — infer
const double = (x: number) => x * 2;

// exported API — annotate to lock the contract
export function loadUser(id: string): Promise<Result<User, UserError>> { /* ... */ }
```

## 28. Immutable data with `Readonly<T>` / `ReadonlyArray<T>`

Write tests that mutate — they fail to compile, proving immutability.

## 29. Distinguish `null` and `undefined` intentionally

Pick one per codebase for "absent". `null` for "explicit empty value" (JSON), `undefined` for "not provided". Be consistent.

## 30. Accept wide, return narrow

Accept `readonly Item[]`; return `Item[]` only when callers must mutate (rare). This composes better.

## 31. Prefer composition over inheritance

TS classes are fine but the instinct to extend often creates over-coupled hierarchies. Pass dependencies in.

## 32. Lift shared logic into discriminated unions + functions, not class hierarchies

```ts
type Payment =
  | { method: "card"; last4: string }
  | { method: "bank"; iban: string }
  | { method: "cash" };

function describe(p: Payment): string {
  switch (p.method) {
    case "card": return `card ending ${p.last4}`;
    case "bank": return `bank ${p.iban}`;
    case "cash": return "cash";
  }
}
```

## 33. Validate at the edge, trust inside

Parse external input once with Zod at the boundary; downstream code receives a trusted type. See `zod-boundaries.md`.

## 34. Use `Awaited<T>` and `ReturnType<F>` to avoid type duplication

```ts
type User = Awaited<ReturnType<typeof loadUser>>;  // auto-tracks signature
```

## 35. Write types that match runtime shape exactly

If your API returns `{ user: null }` on empty, your type must be `User | null`, not `User | undefined`. JSON knows no `undefined`.

## Cross-reference

Parallel of Python's `python-modern-standards/references/pydantic-v2-patterns.md` — both ecosystems converge on "parse, don't validate" and make invalid states unrepresentable.
