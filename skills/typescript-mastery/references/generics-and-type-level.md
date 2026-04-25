# Generics and type-level programming (Effective TS 2nd ed., Chapter 6)

Distilled depth for Vanderkam items 50-58. Use when designing library types, building inferred APIs, or debugging "why does this type not narrow?"

## Generics ARE functions between types

`Promise<T>` is a function from a type T to a new type. Treat them with the same discipline as runtime functions:

- one job each
- minimum required parameters
- explicit constraints (`<T extends Foo>`) are like parameter types
- name them after what they do, not what they take (`UserOf<TRow>` not `UnpackedRowType<T>`)

## Item 51 — when NOT to use a generic

Heuristic: count how many times the type parameter appears in the signature.

```ts
// SMELLY — T appears once. The generic adds nothing.
function first<T>(arr: T[]): unknown { return arr[0]; }

// GOOD — T appears in input AND output. The generic carries the relationship.
function first<T>(arr: T[]): T | undefined { return arr[0]; }
```

Single-appearance generics typically should be `unknown` or a concrete type. They mislead callers into thinking the function preserves type information that it actually discards.

## Item 52 — conditional types over overloads

```ts
// OVERLOADS — surprise callers when the input is a union
function pad(s: string): string;
function pad(s: number): number;
function pad(s: string | number): string | number { /* ... */ }

const a = pad(Math.random() > 0.5 ? "x" : 1);  // picks the first overload, hides the union

// CONDITIONAL — return type tracks the input properly
function pad<T extends string | number>(s: T): T extends string ? string : number {
  return (typeof s === "string" ? s + " " : s + 1) as any;
}
```

Use overloads only when the return type is genuinely independent across cases. Otherwise a conditional return preserves the relationship.

## Item 53 — distribution over conditional types

`T extends U ? A : B` distributes when `T` is a naked type parameter. Wrap in a tuple to disable.

```ts
type ToArray<T> = T extends any ? T[] : never;
type A = ToArray<string | number>;          // string[] | number[]   (distributed)

type ToArrayNo<T> = [T] extends [any] ? T[] : never;
type B = ToArrayNo<string | number>;        // (string | number)[]   (not distributed)
```

Real-world uses:

- `IsAny<T> = 0 extends 1 & T ? true : false` — only `any` makes the intersection `1`.
- `IsNever<T> = [T] extends [never] ? true : false` — bare form would distribute over `never` (the empty union) and yield `never`.
- Building a `Record`-like map where you want the union of keys, not a distributed mapping per branch.

## Item 54 — template literal types as a DSL

```ts
type HttpRoute = `${"GET" | "POST" | "PUT" | "DELETE"} /${string}`;
type EventName<T extends string> = `on${Capitalize<T>}`;
type CssLength = `${number}${"px" | "rem" | "em" | "%"}`;

type ParseRoute<T> = T extends `${infer M} /${infer P}` ? { method: M; path: P } : never;
type R = ParseRoute<"GET /users/:id">;  // { method: "GET"; path: "users/:id" }
```

Combine with `infer` to parse routes, validate query strings, generate event-handler prop names, etc. Keep depth shallow — TS gives up around 5 nested infer/template levels.

## Item 55 — tests for types

Library types must be tested. Pick one:

```ts
// Vitest 1.x+ built-in
import { expectTypeOf } from "vitest";
expectTypeOf(loadUser("x")).resolves.toEqualTypeOf<Result<User, UserError>>();

// tsd — separate test runner reading expectError comments
import { expectType, expectError } from "tsd";
expectType<string>(parseEmail("a@b.c"));
expectError(parseEmail(123));
```

Run on every PR. Type regressions are otherwise invisible until a downstream consumer breaks.

## Item 56 — display matters

Tooltips and error messages are the API surface for types. Optimise for them.

```ts
// Without Prettify, hovering shows: User & { roles: Role[] } & { ... }
type Prettify<T> = { [K in keyof T]: T[K] } & {};
type AdminUser = Prettify<User & { roles: Role[] }>;
// Now hovering shows the merged shape, not the intersection algebra.
```

Use `Prettify` on returned types from utility helpers, not on input types (the noise can hide the shape).

## Item 57 — tail recursion is mandatory at depth

TS's recursion limit is roughly 50 calls for the naive form, 1000 for tail-recursive form (instantiated lazily into an accumulator).

```ts
// NAIVE — stack-blows around length 50
type Reverse<T extends any[]> =
  T extends [infer H, ...infer R] ? [...Reverse<R>, H] : [];

// TAIL-RECURSIVE — works to length ~1000
type ReverseTR<T extends any[], Acc extends any[] = []> =
  T extends [infer H, ...infer R] ? ReverseTR<R, [H, ...Acc]> : Acc;
```

Pattern: drop the recursive call from any position other than the tail. Use an accumulator parameter. Same trick as runtime tail recursion.

## Item 58 — codegen wins over big types

When a type computation grows past ~50 lines or 5 levels of recursion, generate the .d.ts from a real schema:

- Zod schemas → `z.infer`
- OpenAPI specs → `openapi-typescript`
- GraphQL schemas → `graphql-codegen`
- Prisma → `prisma generate`

Codegen has better error messages, faster compile times, and survives team turnover. Type-level wizardry impresses peers and confuses everyone else.

## Soundness traps to remember (Item 48)

- Array index access returns `T`, not `T | undefined`, unless `noUncheckedIndexedAccess` is on.
- Method parameters in classes are bivariant by default (function-property parameters are contravariant under `strictFunctionTypes`). Bug source for callbacks.
- Mutating an array through one alias, reading through a `Readonly<T[]>` alias — TS won't complain.
- Function calls don't invalidate refinements. After narrowing `obj.x` to a non-null branch, calling `mutate(obj)` does NOT re-widen `obj.x`. TS trusts you.
- `exactOptionalPropertyTypes` distinguishes `{ a?: string }` from `{ a?: string | undefined }`. Without it, `{ a: undefined }` is assignable to `{ a?: string }` — usually not what you want.

## Compiler perf checklist (Item 78)

- Run `tsc --extendedDiagnostics` and `--generateTrace` to find slow files.
- Replace deep conditional / mapped types with codegen.
- Use `interface extends` instead of `type` intersections where possible — TS caches interfaces.
- Avoid `Required<Partial<T>>` chains; collapse manually.
- Project references (`composite: true`) for monorepos so unchanged packages skip type-checking.
- `skipLibCheck: true` in dev, off in CI's library-publish job.
- Prune unused dependencies — even unused types are checked.
