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

## Items 36-83 — Effective TypeScript 2nd ed. (Vanderkam, O'Reilly 2024)

Beyond the 35 condensed items above, these are the 2nd-edition rules most often missed in production reviews. Numbering follows Vanderkam.

### Type design

- **Item 29 — Always represent valid states.** Don't carry redundant flags (`isLoading` + `error` + `data`). Use a discriminated union `loading | success | error`.
- **Item 30 — Be liberal in what you accept, strict in what you produce.** Input types are unions and partials; output types are narrow and concrete (Postel's law).
- **Item 32 — Don't put `null`/`undefined` inside a type alias.** Keep nullability at the call site (`User | null`), not buried in `type User = { ... } | null`.
- **Item 33 — Push null values to the perimeter.** A function should take a `User`, not `User | null`. Filter at the boundary.
- **Item 34 — Prefer unions of interfaces over interfaces with unions of fields.** `LoadingState | DoneState` beats `{ state, value?, error? }`.
- **Item 36 — Use a distinct type for special values** (brand for `-1`/`""` sentinel returns). Don't overload meaning into the primary type.
- **Item 37 — Limit optional properties.** Each `?` doubles state space. Prefer required + union (`{ kind: "anonymous" } | { kind: "named"; name: string }`).
- **Item 38 — Avoid repeated parameters of the same type.** `move(x: number, y: number, z: number)` is bug-prone; use `{ x, y, z }` or named tuples.
- **Item 39 — Prefer unifying types to modeling differences.** If two types are 90% the same, unify and add a discriminator field rather than duplicating.
- **Item 40 — Prefer imprecise types to inaccurate ones.** A type that's slightly looser but always true beats a precise type that lies.
- **Item 42 — Avoid types based on anecdotal data.** When typing an API response, derive from the schema/docs, not from one sample payload.

### Unsoundness and `any`

- **Item 43 — Use the narrowest possible scope for `any`.** Cast a single expression, not a whole variable. Never widen `any` past one line.
- **Item 44 — Prefer precise variants of `any`** — `any[]`, `Record<string, any>`, `(...args: any[]) => any`. They still type-check call sites.
- **Item 45 — Hide unsafe casts in well-typed functions.** Library boundary functions can do dirty work internally if the exported signature is sound.
- **Item 46 — `unknown`, not `any`, for values of unknown shape.** Forces the caller to narrow.
- **Item 47 — Type-safe monkey-patching via module augmentation** (`declare module`) instead of `(window as any).foo`.
- **Item 48 — Soundness traps to memorise:** array index access (use `noUncheckedIndexedAccess`), bivariant method parameters in classes, mutating arrays through `Readonly<T[]>`-typed-but-aliased values, and "function calls don't invalidate refinements" — after `obj.x` is narrowed, calling `mutate(obj)` does NOT re-widen it; TS trusts you. Also: optional-property assignability (`{ a?: string }` is assignable to `{ a?: string | undefined }` only with `exactOptionalPropertyTypes`).
- **Item 49 — Track type coverage** (`type-coverage` package). Set a CI floor (95%+) and ratchet upward.

### Generics & type-level programming

- **Item 50 — Generics are functions between types.** Read `Promise<T>` as "given T, produce Promise<T>". Reason about them like ordinary functions.
- **Item 51 — Avoid unnecessary type parameters.** Rule: if a type parameter appears only once in the signature, it probably doesn't need to be generic — use a concrete type or `unknown`. "If you can't think of two callers that pass different types, drop the generic."
- **Item 52 — Prefer conditional types to overload signatures** when the return type depends on the input type. Overloads stop at the first match and surprise callers.
- **Item 53 — Control distribution with `[T] extends [U]`.** Bare `T extends U` distributes over unions; wrapping in tuples disables distribution. Critical for `IsAny`, `IsNever`, exhaustive maps.
- **Item 54 — Template literal types model DSLs.** Routes (`/users/${id}`), event names, CSS units. Combine with `infer` for parsers at the type level.
- **Item 55 — Write type tests** (`expectTypeOf`, `tsd`, vitest's type tests). Library types must be tested like code.
- **Item 56 — Mind how types display.** Use `Prettify<T> = { [K in keyof T]: T[K] } & {}` to flatten intersections in tooltips. Display ergonomics matters in API design.
- **Item 57 — Tail-recursive generic types.** TS unrolls generic recursion ~50 levels by default; tail-recursive form (accumulator parameter) raises the limit to ~1000. Required for any non-trivial type-level computation.
- **Item 58 — Prefer codegen to giant conditional types.** If a type is hard to read, generate the .d.ts from a schema (Zod, OpenAPI, Prisma) rather than computing it.

### Recipes

- **Item 60 — Iterate objects safely.** `Object.entries` is typed `[string, any][]`; cast keys (`as Array<keyof T>`) or accept the looseness — TS is correct because objects can have extra keys at runtime.
- **Item 61 — `Record<K, V>` to keep keys in sync.** Define `type Color = "red" | "blue"` once, then `const palette: Record<Color, string> = ...`. Adding a colour forces palette update.
- **Item 62 — Variadic tuple types** (`...args: [first: string, ...rest: number[]]`) for typed `apply`, currying, and middleware chains.
- **Item 63 — Optional `never` properties for XOR.** `{ a: string; b?: never } | { a?: never; b: string }` enforces "exactly one of".
- **Item 64 — Brands for nominal typing.** `type UserId = string & { __brand: "UserId" }`. Zero runtime cost; prevents mixing IDs.

### Declarations & `@types`

- **Item 65 — Put `typescript` and `@types/*` in `devDependencies`,** never `dependencies`. They're build-only.
- **Item 66 — Three versions matter:** library version, `@types/library` version, and the TS version those types were built against. Pin compatible triples; mismatch is a common cause of mysterious errors.
- **Item 67 — Export every type that appears in a public API.** Otherwise consumers can't name your function's return type.
- **Item 68 — Use TSDoc** (`/** ... */`) for public APIs. Stays with the symbol, shows in IDEs, drives `typedoc`.
- **Item 69 — Type `this` in callbacks** if it's part of the API (`function(this: HTMLElement, ev: Event)`). Otherwise it defaults to `any` and propagates.
- **Item 70 — Mirror types to sever dependencies.** Don't make a low-level lib depend on `@types/react` just to type one prop — copy the minimal interface inline.
- **Item 71 — Module augmentation** to add fields to library types (e.g. `FastifyRequest.user`, `Express.Request.session`).

### Writing & running

- **Item 72 — Prefer ECMAScript features to TS-only features.** Avoid `enum`, parameter properties (when they hurt readability), namespaces, triple-slash, decorators (until stage 4), and `private`/`protected` (prefer `#field` for true privacy).
- **Item 73 — Source maps for debugging.** Always emit them; ensure your bundler preserves them through chunks.
- **Item 74 — Reconstruct types at runtime via** (a) generating types from a runtime schema (Zod), (b) defining with a runtime lib that produces both (Zod, io-ts, ArkType, Effect Schema), or (c) generating runtime values from types (codegen). One source of truth either way.
- **Item 75 — Know the DOM hierarchy.** `Node > Element > HTMLElement > HTMLInputElement`. Most "property doesn't exist on Element" errors are a missing narrowing cast (`if (el instanceof HTMLInputElement)`).
- **Item 76 — Model your environment accurately.** Don't import `node:fs` types into a browser project. Use tsconfig `lib` and `types` to fence each environment.
- **Item 77 — Type-checking ≠ unit testing.** Types prove shape, not behaviour. Both are needed.
- **Item 78 — Compiler perf:** separate `tsc --noEmit` (typecheck) from build (esbuild/swc/tsup transpile only). Use project references in monorepos. Prune unused deps. Simplify deeply nested generics — they're often the slow path.

### Migration

- **Item 79 — Modern JS first.** Convert to ES modules and classes before adding types; `tsc` rewrites are far easier on modern syntax.
- **Item 80 — `@ts-check` + JSDoc** as zero-cost preview before file-by-file rename.
- **Item 81 — `allowJs`** to let JS and TS coexist during migration.
- **Item 82 — Convert up the dependency graph** (leaves first, then importers). Avoid simultaneous churn in coupled files.
- **Item 83 — Migration is not done until `noImplicitAny` is on.** Until then half your "TS code" is still untyped JS.

## Cross-reference

Parallel of Python's `python-modern-standards/references/pydantic-v2-patterns.md` — both ecosystems converge on "parse, don't validate" and make invalid states unrepresentable.
