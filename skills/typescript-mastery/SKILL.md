---
name: typescript-mastery
description: 'Comprehensive TypeScript skill covering the full type system: fundamentals,
  generics, conditional/mapped/template literal types, utility types, strict mode,
  React patterns, production tsconfig, and advanced patterns from Boris Cherny (variance...'
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# TypeScript Mastery
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Comprehensive TypeScript skill covering the full type system: fundamentals, generics, conditional/mapped/template literal types, utility types, strict mode, React patterns, production tsconfig, and advanced patterns from Boris Cherny (variance...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `typescript-mastery` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve.
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
| Correctness | Type-system test plan | Markdown doc covering generic, conditional, mapped, and template-literal type tests | `docs/ts/types-tests.md` |

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
Production-grade TypeScript. Synthesised from Total TypeScript (Pocock), Ultimate TypeScript Handbook (Wellman), 250 Killer TypeScript One-Liners (Abella), and Programming TypeScript (Cherny).

---

## 1. Fundamentals

### Basic Types and Inference
```typescript
let name: string = "Alice";
let id: string | number;     // union
let val: unknown;            // safe unknown — must narrow before use
let never_: never;           // unreachable / exhaustive check

const ids: string[] = [];
const entry: [string, number] = ["Alice", 30]; // tuple
const named: [name: string, age: number] = ["Alice", 30]; // named tuple

const greet = (name: string, age = 30): string => `Hello ${name}`;
const concat = (first: string, last?: string) => last ? `${first} ${last}` : first;
```

### Type Aliases vs Interfaces
```typescript
type ID     = string | number;        // unions, primitives → type
type Status = "active" | "inactive";  // literal unions → type

interface User {                      // object shapes → interface (merges)
  id: string;
  name: string;
  email?: string;
}
interface AdminUser extends User { roles: string[] }
type AdminUser = User & { roles: string[] }; // intersection — equivalent
```

---

## 2. Union Types, Literals, and Narrowing

### Discriminated Unions (most important pattern)
```typescript
type Shape =
  | { kind: "circle";    radius: number }
  | { kind: "rectangle"; width: number; height: number };

function getArea(shape: Shape): number {
  switch (shape.kind) {
    case "circle":    return Math.PI * shape.radius ** 2;
    case "rectangle": return shape.width * shape.height;
    default:          return assertNever(shape); // exhaustive
  }
}
function assertNever(x: never): never { throw new Error("Unhandled: " + x) }
```

### Narrowing Guards
```typescript
typeof val === "string"           // typeof guard
err instanceof Error              // instanceof guard
"roles" in user                   // in guard
val != null                       // nullish guard

function isAdmin(u: User | AdminUser): u is AdminUser { return "roles" in u }
function assertAdmin(u: User | AdminUser): asserts u is AdminUser {
  if (!("roles" in u)) throw new Error("Not admin");
}
```

---

## 3. Objects and Utility Types

```typescript
type P  = Partial<User>;                     // all optional
type R  = Required<User>;                    // all required
type RO = Readonly<User>;                    // all readonly
type D  = Omit<User, "id">;                  // without id
type S  = Pick<User, "name" | "email">;      // only these
type Rc = Record<"dev"|"prod", Config>;      // keyed map
type NN = NonNullable<string | null>;        // removes null/undefined
type X  = Extract<"a"|"b"|"c", "a"|"c">;    // "a" | "c"
type Ex = Exclude<"a"|"b"|"c", "a"|"c">;    // "b"
```

---

## 4. Deriving Types (DRY Type Design)

```typescript
type AlbumKeys = keyof Album;
const cfg = { dev: "http://localhost", prod: "https://api.example.com" } as const;
type Env     = keyof typeof cfg;
type EnvVals = typeof cfg[keyof typeof cfg];

const ROLES = ["admin", "user", "guest"] as const;
type Role = typeof ROLES[number]; // "admin" | "user" | "guest"

type Params  = Parameters<typeof fn>;
type Return  = ReturnType<typeof fn>;
type Res     = Awaited<ReturnType<typeof asyncFn>>;
```

---

## 5. Generics

```typescript
type Result<T, E extends { message: string } = Error> =
  | { success: true;  data: T }
  | { success: false; error: E };

function echo<T>(input: T): T { return input }
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] { return obj[key] }
function createMap<T = string>(): Map<string, T> { return new Map() }

// Conditional
type ToArray<T> = T extends any[] ? T : T[];

// Distributive (applies to each union member)
type DistributiveOmit<T, K extends PropertyKey> = T extends any ? Omit<T, K> : never;

// Mapped
type Nullable<T> = { [K in keyof T]?: T[K] | null };

// Key remapping + template literal
type Getters<T> = { [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K] };

// Template literals
type Route     = `/${string}`;
type Colors    = `${"red"|"blue"}-${100|200|300}`; // 6 combinations
```

---

## 6. Annotations, Assertions, and satisfies

```typescript
const routes = { home: "/", about: "/about" } satisfies Record<string, `/${string}`>;
routes.home; // type is "/" not string — satisfies keeps narrow type

const user = getUser() as AdminUser;       // escape hatch (use sparingly)
const btn = document.getElementById("btn")!; // non-null assertion
```

---

## 7. Advanced Type System (Programming TypeScript — Cherny)

### Variance

```typescript
// Covariant (producer — can use subtype where supertype expected)
type Producer<T> = () => T;
declare let catProducer: Producer<Cat>;
declare let animalProducer: Producer<Animal>;
animalProducer = catProducer; // OK — Cat is a subtype of Animal

// Contravariant (consumer — can use supertype where subtype expected)
type Consumer<T> = (t: T) => void;
declare let catConsumer: Consumer<Cat>;
declare let animalConsumer: Consumer<Animal>;
catConsumer = animalConsumer; // OK — Animal consumer handles Cat too

// Function types: params are contravariant, return type is covariant
// "Be liberal in what you accept, conservative in what you return"
```

### The `infer` Keyword

```typescript
// Extract wrapped type from any container
type UnwrapPromise<T> = T extends Promise<infer U> ? U : T;
type UnwrapArray<T>   = T extends Array<infer U>   ? U : T;

// Custom ReturnType
type MyReturnType<F extends (...args: any) => any> = F extends (...args: any) => infer R ? R : never;

// Extract first and last tuple elements
type Head<T extends any[]> = T extends [infer H, ...any[]] ? H : never;
type Last<T extends any[]> = T extends [...any[], infer L] ? L : never;

// Flatten nested arrays
type Flatten<T> = T extends Array<infer U> ? Flatten<U> : T;
```

### Branded / Nominal Types

```typescript
// Prevent mixing structurally identical types (e.g., user ID vs order ID)
type UserId  = string & { readonly __brand: unique symbol };
type OrderId = string & { readonly __brand: unique symbol };

const toUserId  = (id: string): UserId  => id as UserId;
const toOrderId = (id: string): OrderId => id as OrderId;

function getUser(id: UserId) { /* ... */ }
const uid = toUserId('abc');
const oid = toOrderId('abc');
getUser(uid);  // OK
getUser(oid);  // Error — OrderId is not UserId
```

### Option Type (Null-Safe Pattern)

```typescript
type Option<T> = { type: 'some'; value: T } | { type: 'none' };

const some = <T>(value: T): Option<T> => ({ type: 'some', value });
const none: Option<never> = { type: 'none' };

function map<T, U>(opt: Option<T>, fn: (t: T) => U): Option<U> {
  return opt.type === 'none' ? none : some(fn(opt.value));
}
function getOrElse<T>(opt: Option<T>, fallback: T): T {
  return opt.type === 'none' ? fallback : opt.value;
}

// Usage — no null checks needed
const name = getOrElse(map(getUser(id), u => u.name), 'Anonymous');
```

### Returning Exceptions as Union Types

```typescript
// Model failure without throwing — callers must handle errors
type DatabaseError = { type: 'DatabaseError'; message: string };
type NotFoundError = { type: 'NotFoundError'; id: string };

async function findUser(id: string): Promise<User | DatabaseError | NotFoundError> {
  try {
    const user = await db.findById(id);
    if (!user) return { type: 'NotFoundError', id };
    return user;
  } catch (e) {
    return { type: 'DatabaseError', message: String(e) };
  }
}

// Caller must handle all cases
const result = await findUser('123');
if ('type' in result) {
  if (result.type === 'NotFoundError') console.log('Not found:', result.id);
  else console.log('DB error:', result.message);
} else {
  console.log('User:', result.name); // guaranteed User
}
```

### Companion Object Pattern

```typescript
// Pair an interface with a namespace of the same name
interface Currency { unit: string; value: number }

namespace Currency {
  export const from = (value: number, unit: string): Currency => ({ value, unit });
  export const add = (a: Currency, b: Currency): Currency => {
    if (a.unit !== b.unit) throw new Error('Unit mismatch');
    return { value: a.value + b.value, unit: a.unit };
  };
  export const format = (c: Currency) => `${c.value} ${c.unit}`;
}

const usd = Currency.from(100, 'USD');
const total = Currency.add(usd, Currency.from(50, 'USD'));
```

### Typesafe Event Emitters

```typescript
// Map event names to their payload types
type Events = {
  'user:login':    { userId: string; timestamp: Date };
  'user:logout':   { userId: string };
  'order:created': { orderId: string; amount: number };
};

class TypedEventEmitter<T extends Record<string, unknown>> {
  private handlers: { [K in keyof T]?: Array<(payload: T[K]) => void> } = {};

  on<K extends keyof T>(event: K, handler: (payload: T[K]) => void) {
    (this.handlers[event] ??= []).push(handler);
  }

  emit<K extends keyof T>(event: K, payload: T[K]) {
    this.handlers[event]?.forEach(h => h(payload));
  }
}

const emitter = new TypedEventEmitter<Events>();
emitter.on('user:login', ({ userId, timestamp }) => console.log(userId, timestamp));
emitter.emit('user:login', { userId: '123', timestamp: new Date() });
// emitter.emit('user:login', { wrongField: true }); // Error!
```

### Declaration Merging

```typescript
// What can be merged:
// interface + interface → merged properties
// namespace + namespace → merged members
// class + interface → interface adds instance members
// namespace + function → adds static properties
// namespace + enum → adds methods to enum

interface User { name: string }
interface User { age: number }  // merged: { name, age }

// Augment a module's types
declare module 'express' {
  interface Request { userId?: string }
}
```

---

## 8. React Patterns

```typescript
interface ButtonProps {
  label: string;
  onClick: () => void;
  variant?: "primary" | "secondary" | "danger";
  children?: React.ReactNode;
}
const Button = ({ label, onClick, variant = "primary" }: ButtonProps) => (
  <button className={`btn-${variant}`} onClick={onClick}>{label}</button>
);

const [user, setUser] = useState<User | null>(null);
const inputRef = useRef<HTMLInputElement>(null);
const onChange  = (e: React.ChangeEvent<HTMLInputElement>) => setValue(e.target.value);
```

---

## 9. Production tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "isolatedModules": true,
    "declaration": true,
    "sourceMap": true,
    "outDir": "dist"
  }
}
```

`strict` covers: noImplicitAny + strictNullChecks + strictFunctionTypes.
`noUncheckedIndexedAccess`: forces `arr[i]` → `T | undefined`.

---

## 10. Top Type-Level Tricks

```typescript
type Values<T>            = T[keyof T];
type DeepReadonly<T>      = { readonly [K in keyof T]: DeepReadonly<T[K]> };
type Merge<A,B>           = Omit<A, keyof B> & B;
type AsyncReturn<T extends (...args: any) => Promise<any>> = Awaited<ReturnType<T>>;
type Getter<T extends string> = `get${Capitalize<T>}`;
// Strict Omit — only accepts keys that exist in T
type StrictOmit<T, K extends keyof T> = Omit<T, K>;
// Make specific keys required, keep rest as-is
type RequireKeys<T, K extends keyof T> = Required<Pick<T,K>> & Omit<T,K>;
```

---

## 11. Anti-Patterns

```typescript
// BAD: any
function fn(x: any) { return x.val }
// GOOD: unknown + narrowing
function fn(x: unknown) {
  if (typeof x === "object" && x && "val" in x) return (x as { val: unknown }).val;
}

// BAD: Omit on unions (collapses to shared properties)
type R = Omit<A | B, "id">; // WRONG — loses unique properties
// GOOD: DistributiveOmit
type R = DistributiveOmit<A | B, "id">;

// BAD: enum (nominal surprise + JS output)
enum Status { Active = "active" }
// GOOD: as const POJO
const Status = { Active: "active" } as const;
type Status = typeof Status[keyof typeof Status];
```

---

*Sources: Total TypeScript — Matt Pocock (No Starch Press, 2026); Ultimate TypeScript Handbook — Dan Wellman (2023); 250 Killer TypeScript One-Liners — Abella; Programming TypeScript — Boris Cherny (O'Reilly, 2019); Effective TypeScript 2nd ed. — Dan Vanderkam (O'Reilly, 2024)*

## References

- `references/generics-and-type-level.md` — depth on items 50-58 (generics as functions, distribution control, template literal DSLs, type tests, Prettify, tail-recursive types, codegen tradeoffs, soundness traps, compiler perf checklist).