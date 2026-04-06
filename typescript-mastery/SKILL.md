---
name: typescript-mastery
description: "Comprehensive TypeScript skill covering the full type system: fundamentals, generics, conditional/mapped/template literal types, utility types, strict mode, React patterns, and production tsconfig. Synthesised from Total TypeScript (Pocock), Ultimate TypeScript Handbook (Wellman), and 250 Killer TypeScript One-Liners (Abella). Use when writing TypeScript at any level — from annotating functions to designing advanced generic utilities."
---

# TypeScript Mastery

Production-grade TypeScript. Synthesised from three authoritative books.
Deep dives: see `references/` directory.

---

## 1. Fundamentals

### Basic Types and Inference
```typescript
// Primitives
let name: string = "Alice";
let age: number = 30;
let active: boolean = true;
let id: string | number;     // union
let val: unknown;            // safe unknown — must narrow before use
let never_: never;           // unreachable / exhaustive check

// Arrays — two syntaxes, identical
const ids: string[] = [];
const nums: Array<number> = [1, 2, 3];

// Tuples — fixed-length, each position typed
const entry: [string, number] = ["Alice", 30];
const named: [name: string, age: number] = ["Alice", 30]; // named tuple

// Always annotate function params — inference cannot guess them
const greet = (name: string, age = 30): string => `Hello ${name}`;

// Optional param = ? (cannot combine with default)
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
typeof val === "string"            // typeof guard
err instanceof Error               // instanceof guard
"roles" in user                    // in guard
val != null                        // nullish guard

// Type predicate — caller's type is narrowed
function isAdmin(u: User | AdminUser): u is AdminUser { return "roles" in u }

// Assertion function — narrows without if block
function assertAdmin(u: User | AdminUser): asserts u is AdminUser {
  if (!("roles" in u)) throw new Error("Not admin");
}
assertAdmin(user);
user.roles; // now AdminUser — no if needed
```

---

## 3. Objects and Utility Types

### Built-in Utility Types
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

### Dynamic Keys
```typescript
// Index signature
interface ScoreMap { [subject: string]: number }

// Record (preferred — supports union keys)
type Env = "development" | "production" | "staging";
type Config = Record<Env, { apiBaseUrl: string; timeout: number }>;

// PropertyKey — accepts string | number | symbol
const hasKey = (obj: object, key: PropertyKey) => obj.hasOwnProperty(key);

// Known + dynamic keys combined
interface Scores { math: number; english: number; [subject: string]: number }
```

---

## 4. Deriving Types (DRY Type Design)

```typescript
// keyof — extract keys as union
type AlbumKeys = keyof Album;  // "title" | "artist" | "year"

// typeof — extract type from value
const cfg = { dev: "http://localhost", prod: "https://api.example.com" } as const;
type Env     = keyof typeof cfg;        // "dev" | "prod"
type EnvVals = typeof cfg[keyof typeof cfg]; // union of values

// Indexed access
type ArtistName = Album["artist"]["name"]; // chain access
type TitleOrYear = Album["title" | "year"]; // union access

// Array values as union
const ROLES = ["admin", "user", "guest"] as const;
type Role = typeof ROLES[number]; // "admin" | "user" | "guest"

// Derive from functions (great for third-party libs)
type Params = Parameters<typeof fn>;      // tuple of params
type Return = ReturnType<typeof fn>;      // return type
type Res    = Awaited<ReturnType<typeof asyncFn>>; // unwrap Promise
```

---

## 5. Generics

### Generic Types
```typescript
// Generic with constraint + default
type Result<T, E extends { message: string } = Error> =
  | { success: true;  data: T }
  | { success: false; error: E };

// Usage
const r = createUser(data);
if (r.success) console.log(r.data.id);
else console.error(r.error.message);

// Generic resource pattern
type ResourceStatus<TContent extends { id: number }, TMeta extends object = {}> =
  | { status: "available"; content: TContent; metadata: TMeta }
  | { status: "unavailable"; reason: string };
```

### Generic Functions
```typescript
// Type inferred from argument — no explicit annotation needed at call site
function echo<T>(input: T): T { return input }

// Constraint with extends
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] { return obj[key] }

// Default type argument
function createMap<T = string>(): Map<string, T> { return new Map() }

// Infer element type from array
function unique<T>(arr: T[]): T[] { return [...new Set(arr)] }

// Generic + constraint — error must have message
const addCode = <TError extends { message: string }>(err: TError) =>
  ({ ...err, code: (err as any).code ?? 8000 });
```

### Conditional and Mapped Types
```typescript
// Conditional
type ToArray<T> = T extends any[] ? T : T[];

// Distributive (applies to each union member)
type DistributiveOmit<T, K extends PropertyKey> = T extends any ? Omit<T, K> : never;

// Mapped
type Nullable<T> = { [K in keyof T]?: T[K] | null };

// Key remapping with as + template literal
type Getters<T> = { [K in keyof T as `get${Capitalize<string & K>}`]: () => T[K] };

// Template literal types
type Route     = `/${string}`;
type EventName = `on${Capitalize<string>}`;
type Colors    = `${"red"|"blue"}-${100|200|300}`; // 6 combinations
```

---

## 6. Annotations, Assertions, and satisfies

```typescript
// satisfies — validates shape AND keeps narrower inferred type
const routes = {
  home: "/", about: "/about"
} satisfies Record<string, `/${string}`>;
routes.home; // type is "/" not string

// as assertion — escape hatch (use sparingly)
const user = getUser() as AdminUser;

// Non-null assertion — only when certain
const btn = document.getElementById("btn")!;

// @ts-expect-error — suppress one error (better than @ts-ignore)
// @ts-expect-error intentionally wrong
const bad: string = 42;

// satisfies vs annotation vs as
const obj  = {} as Record<string, number>;   // as: forces type
const obj2: Record<string, number> = {};     // annotation: validates + widens
const obj3 = { a: 1 } satisfies Record<string, number>; // validates + keeps narrow
```

---

## 7. Anti-Patterns

```typescript
// BAD: any everywhere
function fn(x: any) { return x.val }   // no safety

// GOOD: unknown + narrowing
function fn(x: unknown) {
  if (typeof x === "object" && x && "val" in x) return (x as { val: unknown }).val;
}

// BAD: Omit on unions (collapses to shared properties only)
type Result = Omit<A | B, "id">; // WRONG — loses unique properties

// GOOD: DistributiveOmit
type Result = DistributiveOmit<A | B, "id">;

// BAD: optional + default (TypeScript error)
function fn(x?: string = "default") {} // ERROR

// GOOD: just the default
function fn(x = "default") {}

// BAD: enum (nominal surprise + JS output)
enum Status { Active = "active" }
// GOOD: as const POJO (structural, zero runtime overhead)
const Status = { Active: "active" } as const;
type Status = typeof Status[keyof typeof Status];
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

// Typed state, ref, events
const [user, setUser] = useState<User | null>(null);
const inputRef = useRef<HTMLInputElement>(null);
const onChange  = (e: React.ChangeEvent<HTMLInputElement>) => setValue(e.target.value);
const onSubmit  = (e: React.FormEvent<HTMLFormElement>) => { e.preventDefault(); };

// Generic component
function Select<T extends string>({ options, value, onChange }: {
  options: T[]; value: T; onChange: (val: T) => void;
}) {
  return <select value={value} onChange={e => onChange(e.target.value as T)}>
    {options.map(o => <option key={o}>{o}</option>)}
  </select>;
}
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
    "forceConsistentCasingInFileNames": true,
    "isolatedModules": true,
    "noEmit": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "outDir": "dist"
  }
}
```

Key rules: `strict` covers noImplicitAny + strictNullChecks + strictFunctionTypes.
`noUncheckedIndexedAccess` forces `arr[i]` → `T | undefined`.
`isolatedModules` required for Babel/esbuild transpilation.

---

## 10. JS-to-TS Gotchas

| JavaScript | TypeScript Behaviour |
|------------|----------------------|
| All function args optional | All required by default; use `?` or default |
| `typeof null === "object"` | Still `"object"` — always check `!== null` |
| Add object keys freely | Must declare; use index signatures or `Record` |
| `arr[i]` always `T` | `T \| undefined` with `noUncheckedIndexedAccess` |
| Excess properties ignored | Error on fresh object literals only |
| `{}` = empty object | TypeScript: `{}` means "anything except null/undefined" |

```typescript
// Empty type gotcha
function fn(x: {}) {}
fn("hello");  // OK! {} means non-nullish
fn(null);     // ERROR

// Excess property check only on fresh literals
const extra = { name: "Alice", extra: 123 };
const u1: User = extra; // OK (stale object — no check)
const u2: User = { name: "Alice", extra: 123 }; // ERROR (fresh literal)
```

---

## 11. Top 15 Type-Level Tricks

```typescript
type Values<T>           = T[keyof T];                         // all values as union
type RequireKeys<T,K extends keyof T> = Required<Pick<T,K>> & Omit<T,K>;
type OptionalKeys<T,K extends keyof T> = Omit<T,K> & Partial<Pick<T,K>>;
type DeepReadonly<T>     = { readonly [K in keyof T]: DeepReadonly<T[K]> };
type Merge<A,B>          = Omit<A, keyof B> & B;               // B wins on conflicts
type Head<T extends any[]> = T extends [infer H, ...any[]] ? H : never;
type Tail<T extends any[]> = T extends [any, ...infer R] ? R : never;
type AsyncReturn<T extends (...args: any) => Promise<any>> = Awaited<ReturnType<T>>;
type Getter<T extends string> = `get${Capitalize<T>}`;         // "getName" etc.
// Branded types — prevent mixing User ID and Order ID
type UserId  = string & { readonly __brand: "UserId" };
type OrderId = string & { readonly __brand: "OrderId" };
const toUserId = (id: string): UserId => id as UserId;
// infer keyword inside conditional types
type UnwrapPromise<T> = T extends Promise<infer U> ? U : T;
type FirstParam<F extends (...args: any) => any> = Parameters<F>[0];
// Distributive conditional — applies to each union member
type IsString<T> = T extends string ? true : false;
// Strict Omit — only allows keys that exist in T
type StrictOmit<T, K extends keyof T> = Omit<T, K>;
```

---

*Sources: Total TypeScript — Matt Pocock (No Starch Press, 2026) · Ultimate TypeScript Handbook — Dan Wellman (Orange AVA, 2023) · 250 Killer TypeScript One-Liners — Hernando Abella*
