# TypeScript anti-patterns

Twenty-plus concrete patterns to remove on sight. Each: what it looks like, why it's bad, what to do instead.

## 1. `any`

```ts
// BAD
function load(x: any) { return x.data.user.email; }

// GOOD
function load(x: unknown): string | null {
  return UserResponse.safeParse(x).data?.data.user.email ?? null;
}
```

`any` disables the type system. Every time you write it you're saying "I give up." Use `unknown` and narrow; parse with Zod at boundaries.

## 2. `as T` (type assertion)

```ts
// BAD
const user = input as User;

// GOOD
const result = UserSchema.safeParse(input);
if (!result.success) throw new Error("invalid");
const user = result.data;
```

Assertions lie to the compiler. The runtime shape may not match.

## 3. `as unknown as T` (double-cast)

```ts
// BAD — always wrong
const x = maybe as unknown as User;
```

Silences the compiler's last line of defence. If you reach for it, you've skipped parsing. Validate instead.

Allowed exception: declaring a branded type in a parser that has already validated the underlying primitive:

```ts
return raw as Email;  // inside parseEmail, once checked
```

## 4. `!` non-null assertion

```ts
// BAD
const user = users.find((u) => u.id === id)!;
user.email;  // crashes if missing

// GOOD
const user = users.find((u) => u.id === id);
if (!user) throw new NotFoundError(`user ${id}`);
user.email;
```

`!` removes runtime safety. Use narrowing, guards, or assertion functions.

## 5. `Function` type

```ts
// BAD
function onEvent(f: Function) { f(); }

// GOOD
function onEvent(f: () => void) { f(); }
```

`Function` accepts any callable and returns `any`. Use a specific signature.

## 6. `Object` and `{}`

```ts
// BAD
function log(x: Object) { /* x is almost any */ }
function log(x: {})     { /* same */ }

// GOOD — "some non-null object"
function log(x: Record<string, unknown>) { /* ... */ }
// or a specific shape
function log(x: { id: string }) { /* ... */ }
```

`Object` / `{}` match almost everything including primitives. Never what you want.

## 7. `enum` for small string sets

```ts
// BAD
enum Role { Admin = "admin", Member = "member" }

// GOOD
type Role = "admin" | "member";
// or
const Role = { Admin: "admin", Member: "member" } as const;
type Role = (typeof Role)[keyof typeof Role];
```

Numeric enums create reverse-lookup objects in the emit. String enums don't tree-shake well. Unions are cleaner and free.

## 8. `namespace`

```ts
// BAD
namespace Util { export function x() {} }

// GOOD
// util.ts
export function x() {}
```

Namespaces predate ES modules. Use modules; keep `namespace` only for ambient type declarations where unavoidable.

## 9. Class of statics

```ts
// BAD
class StringUtil {
  static trim(s: string) { return s.trim(); }
  static lower(s: string) { return s.toLowerCase(); }
}

// GOOD
// stringUtil.ts
export const trim  = (s: string) => s.trim();
export const lower = (s: string) => s.toLowerCase();
```

A class with no state is a module with extra syntax.

## 10. Mutating function arguments

```ts
// BAD
function addRole(user: User, role: string) { user.roles.push(role); }

// GOOD
function addRole(user: User, role: string): User {
  return { ...user, roles: [...user.roles, role] };
}
```

Mutation leaks side effects, breaks referential transparency, and defeats React/state libraries' change detection.

## 11. Silent `catch`

```ts
// BAD
try { await doThing(); } catch (e) {}

// GOOD
try { await doThing(); }
catch (e) {
  log.error({ err: e }, "do_thing_failed");
  throw e;  // or translate at boundary
}
```

Empty catch hides bugs. At minimum log; usually re-throw or return an Err.

## 12. `delete obj.key`

```ts
// BAD
const copy = { ...user };
delete copy.password;

// GOOD
const { password, ...publicUser } = user;
```

`delete` produces non-optimisable objects (V8 hidden class change). Use destructure-rest to produce a new object without the key.

## 13. Barrel files in large apps

```ts
// BAD — packages/ui/index.ts
export * from "./Button";
export * from "./Input";
export * from "./Modal";
// ...and 80 more
```

Barrels force bundlers to load entire packages on a single import, hurting dev server times and tree-shaking in apps.

Good: allow a top-level barrel for published libraries; skip them inside app code.

## 14. `return await` that is never needed (mostly)

```ts
// POINTLESS — extra await
async function f() { return await g(); }

// GOOD
async function f() { return g(); }

// REQUIRED — keep await when inside try/catch
async function f() {
  try { return await g(); }
  catch { return fallback; }
}
```

Return the promise unless you need the error to propagate through the async function's catch.

## 15. Overusing class inheritance

```ts
// BAD — five-level hierarchy
class A { ... }
class B extends A { ... }
class C extends B { ... }
// C depends on every change in A and B

// GOOD — composition
class C {
  constructor(private readonly deps: { a: A; b: B }) {}
}
```

Inheritance locks structure. Composition is easier to test, reason about, refactor.

## 16. `Promise.all` with mixed fail-modes

```ts
// BAD — one failure cancels the rest
const results = await Promise.all(users.map(loadProfile));

// GOOD — collect partial results
const results = await Promise.allSettled(users.map(loadProfile));
```

Choose `allSettled` when you want per-item outcomes; `all` when a single failure should short-circuit.

## 17. Floating promises

```ts
// BAD — unhandled
doThing();
nextStep();

// GOOD — await or explicit fire-and-forget
await doThing();
nextStep();

// or
void doThing();  // truly fire-and-forget; error-handled internally
```

ESLint `@typescript-eslint/no-floating-promises` catches this.

## 18. `async` functions that never await

```ts
// BAD
async function x() { return 1; }  // unnecessary Promise wrap

// GOOD
function x() { return 1; }
// or use async only when needed
async function x() { return await fetchOne(); }
```

## 19. Using `Record<string, T>` when keys are known

```ts
// BAD
const statusCodes: Record<string, number> = { ok: 200, notFound: 404 };
statusCodes.oops;  // undefined, typed as number — bug

// GOOD
const statusCodes = { ok: 200, notFound: 404 } as const;
type StatusName = keyof typeof statusCodes;
```

`Record<string, ...>` widens the key set to all strings. Use `as const` or an explicit union.

## 20. Wide `catch (e: any)`

```ts
// BAD (pre useUnknownInCatchVariables)
try {} catch (e: any) { e.message }

// GOOD
try {} catch (e) {  // e: unknown
  if (e instanceof Error) log.error(e.message);
  else log.error(String(e));
}
```

Always on `useUnknownInCatchVariables` via `strict`.

## 21. Re-declaring types that already exist

```ts
// BAD
type MyUser = { id: string; email: string };  // duplicates User

// GOOD
import type { User } from "./user";
type UserDto = Pick<User, "id" | "email">;
```

Duplicated types drift.

## 22. `interface Props {}` on every component

```ts
// OK
interface ButtonProps { label: string; onClick: () => void; }
function Button(props: ButtonProps) { /* ... */ }

// ALSO OK for one-off small components — inline
function Button({ label, onClick }: { label: string; onClick: () => void }) { /* ... */ }
```

Don't over-formalise. Exported components deserve a named prop type; tiny internals don't.

## 23. Parameter object bloat

```ts
// BAD
createUser({ email, name, age, role, tenantId, createdBy, notify, welcomeEmail, roleOverride })

// GOOD
createUser({
  input: { email, name, age, role },
  context: { tenantId, createdBy },
  options: { notify, welcomeEmail },
});
```

When a param object grows >6 keys, group by responsibility.

## 24. Testing implementation, not behaviour

```ts
// BAD
expect(userService["cache"].size).toBe(1);  // private, implementation detail

// GOOD
expect(await userService.load(id)).toEqual(ok(user));
expect(repo.find).toHaveBeenCalledTimes(1);  // called once — caching worked
```

## 25. `JSON.parse(JSON.stringify(x))` for deep clone

```ts
// BAD — loses Date, Map, Set, undefined
const copy = JSON.parse(JSON.stringify(user));

// GOOD
import { structuredClone } from "node:util";   // Node 17+
const copy = structuredClone(user);
// or a typed utility for your shape
```

## 26. `==` instead of `===`

```ts
// BAD — implicit coercion
if (x == null) { ... }   // matches null AND undefined — this specific use is arguably OK

// GOOD — explicit
if (x === null || x === undefined) { ... }
// or
if (x == null) { /* only idiomatic use of == */ }
```

Always `===` except the documented "null or undefined" idiom, which linters allow.

## Anti-pattern quick grep

```bash
rg -n "\bany\b" src/            # spot any
rg -n " as [A-Z]" src/          # type assertions
rg -n " as unknown as " src/    # double-cast
rg -n "![^=]" src/              # non-null ops (tune)
rg -n "catch \(e\) *\{\}" src/  # silent catch
rg -n "\benum\b" src/           # enum use
rg -n "namespace " src/         # namespaces
```

Run these in CI as forbidden-pattern checks, with explicit allowlist comments where truly needed.

## Cross-reference

Parallels `python-modern-standards/references/anti-patterns.md` — each language has its own noise surface, but the underlying habit (silence the tool instead of fixing the signal) is the same.
