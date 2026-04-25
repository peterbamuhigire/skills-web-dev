# Clean code in TypeScript

TypeScript does not rescue a poor design. Types amplify clarity but cannot invent it. This file covers the clean-code principles that pay off most under strict TS.

## SOLID adapted to TS

### Single Responsibility

Each module, class, and function has one reason to change.

```ts
// BEFORE — service does too much
class UserService {
  async register(email: string, password: string) {
    if (!email.includes("@")) throw new Error("bad email");
    const hash = await bcrypt.hash(password, 10);
    const user = await db.user.create({ data: { email, hash } });
    await sendWelcomeEmail(user.email);
    return user;
  }
}

// AFTER — separated
const EmailSchema = z.string().email();
const hashPassword = (pw: string) => bcrypt.hash(pw, 10);

class UserService {
  constructor(
    private readonly db: Db,
    private readonly mailer: Mailer,
  ) {}

  async register(input: RegisterInput): Promise<Result<User, RegisterError>> {
    const email = EmailSchema.safeParse(input.email);
    if (!email.success) return err("invalid_email");
    const hash = await hashPassword(input.password);
    const user = await this.db.user.create({ data: { email: email.data, hash } });
    await this.mailer.sendWelcome(user.email);
    return ok(user);
  }
}
```

### Open/Closed

Extend via new functions or union variants, not by modifying every existing consumer.

```ts
type Notifier = { send(msg: string): Promise<void> };
// add new channel by implementing, not by editing existing code
class Slack implements Notifier { async send(msg: string) { /* ... */ } }
class Email implements Notifier { async send(msg: string) { /* ... */ } }
```

### Liskov

Narrowing a subtype's input or widening its output breaks Liskov. In TS, the compiler catches most violations via contravariant parameter checks (with `strictFunctionTypes`).

### Interface Segregation

Prefer small focused interfaces over a god-interface.

```ts
// BAD
interface Storage { read(): string; write(v: string): void; sync(): Promise<void>; lock(): void; }

// GOOD
interface Reader { read(): string; }
interface Writer { write(v: string): void; }
interface Syncable { sync(): Promise<void>; }

class FileCache implements Reader, Writer {}
```

### Dependency Inversion

High-level modules depend on interfaces; wire concrete types at the edge.

```ts
interface Clock { now(): Date; }
class Token {
  constructor(private readonly clock: Clock) {}
  isExpired(exp: Date) { return this.clock.now() > exp; }
}
// production: new Token({ now: () => new Date() })
// tests: new Token({ now: () => fixedDate })
```

## Small functions

- Ceiling: 40 lines or 3 levels of nesting. Above this, split.
- One level of abstraction per function — either coordinate or compute, not both.
- Return early; avoid deep `else` chains.

```ts
// BEFORE
function process(order: Order) {
  if (order.status === "pending") {
    if (order.items.length > 0) {
      if (order.customer.active) {
        // 30 lines of logic
      }
    }
  }
}

// AFTER
function process(order: Order): Result<Invoice, ProcessError> {
  if (order.status !== "pending") return err("not_pending");
  if (order.items.length === 0) return err("no_items");
  if (!order.customer.active) return err("customer_inactive");
  return ok(buildInvoice(order));
}
```

## Naming

- Verbs for functions: `loadUser`, `parseEmail`, `renderInvoice`.
- Predicates start with `is/has/should/can`: `isActive`, `hasPermission`, `shouldRetry`.
- Domain nouns, not implementation nouns: `cart` not `arrayOfItems`.
- Consistent casing: `camelCase` values, `PascalCase` types, `UPPER_SNAKE` only for true constants (env, protocol versions).
- Don't embed types in names: `userList: User[]` not `userArray: User[]`.
- Don't abbreviate unless the abbreviation is universal: `id`, `url`, `http` ok; `usrMgr` not ok.

## Immutability

### `readonly` on structure

```ts
interface Invoice {
  readonly id: string;
  readonly lines: readonly InvoiceLine[];
  readonly total: number;
}
```

### `Readonly<T>` and `ReadonlyArray<T>`

```ts
function sum(xs: ReadonlyArray<number>): number {
  return xs.reduce((a, b) => a + b, 0);
}
```

### `as const` for literal data

```ts
const ROLES = ["admin", "member", "viewer"] as const;
type Role = (typeof ROLES)[number];
```

### Avoid in-place mutation

```ts
// BAD
function activate(user: User) { user.active = true; return user; }

// GOOD
function activate(user: User): User { return { ...user, active: true }; }
```

## Pure functions

A pure function depends only on its inputs and produces no observable side effects. Tests are trivial; memoisation is safe.

```ts
// pure — ideal
function tax(amount: number, rate: number): number { return amount * rate; }

// impure — isolate
async function charge(id: string): Promise<Result<Receipt, PaymentError>> {
  /* side effects */
}
```

Push side effects to the edges; keep the domain pure.

## Comments explain WHY

- Types explain *what*. Tests explain *how*. Comments explain *why*.
- Good: "We retry 3x because the upstream times out under cold-start." Bad: "retry loop."
- Document surprise: non-obvious ordering, historical constraints, workarounds.
- Don't write autogenerated JSDoc that restates the signature.

```ts
// GOOD
/**
 * Chosen over async-mutex because we need fair queueing when >50 workers
 * contend for the same room-code key (see incident #4021).
 */
export class FairLock { /* ... */ }

// BAD
/** Gets the user. @param id the id @returns the user */
function getUser(id: string): User { /* ... */ }
```

## DRY vs WET — balance, not dogma

- WET (Write Everything Twice) is fine for two callers that may diverge.
- DRY after the third occurrence, when the abstraction is clear.
- Premature abstraction costs more than duplication. Measure before extracting.

```ts
// Three validators that share nothing but shape — don't extract
const isUkPostcode = (s: string) => /^[A-Z]{1,2}\d/.test(s);
const isUsZip = (s: string) => /^\d{5}(-\d{4})?$/.test(s);
const isCaPostal = (s: string) => /^[A-Z]\d[A-Z] \d[A-Z]\d$/.test(s);
```

## Dependency injection patterns

### Constructor DI for classes

```ts
class OrderService {
  constructor(
    private readonly repo: OrderRepo,
    private readonly pay: Payments,
    private readonly log: Logger,
  ) {}
}
```

### Parameter DI for functions

```ts
function sendWelcome(mailer: Mailer, user: User): Promise<void> {
  return mailer.send(user.email, "Welcome");
}
```

### Factory functions for complex wiring

```ts
export const createOrderService = (deps: {
  repo: OrderRepo; pay: Payments; log: Logger;
}) => ({
  async place(order: Order) { /* ... */ },
  async cancel(id: string)   { /* ... */ },
});
type OrderService = ReturnType<typeof createOrderService>;
```

## Error strategy

At boundaries, return `Result`. Internally, `throw` for truly exceptional conditions. See `error-handling-result.md`.

## File and module layout

- One module = one concept. Multiple exports are fine if they belong together.
- Co-locate tests: `foo.ts` + `foo.test.ts`.
- Avoid `index.ts` barrel files in apps (hurt tree-shaking and build speed); libraries can have one top-level barrel.
- Group by feature, not by kind (`users/` not `controllers/users.ts + models/user.ts`).

## Classes vs functions

Prefer functions and closures for behaviour unless you need:

- long-lived stateful objects (connection pools, caches);
- polymorphism with true substitutability;
- framework integration (NestJS, TypeORM entities).

Static-method-only classes are a smell — use a plain module.

## Anti-patterns in this theme

- Flag arguments: `doThing(..., isAdmin: boolean)`. Split into two functions.
- Long parameter lists. Four+ params suggests passing an object.
- Output parameters: mutating a passed-in object as a "result".
- Silent catch.
- Temporal coupling: methods that must be called in a specific order with no type enforcement. Use builder pattern or phantom types.

## Cross-reference

Parallel of `python-modern-standards/references/error-handling.md` and the SOLID mirror in `python-modern-standards`. The discipline transfers directly.
