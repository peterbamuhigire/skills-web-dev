# Error handling — Result/Either, neverthrow, and boundaries

Throwing is fine for truly exceptional conditions inside a module. At boundaries — HTTP handlers, queue workers, CLI entrypoints, UI event handlers — return typed errors. This file explains when, how, and which library.

## The Result type

```ts
export type Ok<T>  = { readonly ok: true;  readonly value: T };
export type Err<E> = { readonly ok: false; readonly error: E };
export type Result<T, E> = Ok<T> | Err<E>;

export const ok  = <T>(value: T):  Ok<T>  => ({ ok: true,  value });
export const err = <E>(error: E): Err<E> => ({ ok: false, error });
```

## Why Result

- Errors are visible in the signature — the compiler forces the caller to handle them.
- No hidden control flow via `throw`.
- Exhaustive error types via discriminated unions.
- Safe refactors — add a new error variant and the compiler lists every caller to update.

```ts
async function loadUser(id: string): Promise<Result<User, "not_found" | "db_down">> {
  try {
    const user = await db.user.findUnique({ where: { id } });
    return user ? ok(user) : err("not_found");
  } catch (e) {
    log.error({ err: e }, "db_down");
    return err("db_down");
  }
}

const r = await loadUser(id);
if (!r.ok) {
  switch (r.error) {
    case "not_found": return res.status(404).end();
    case "db_down":   return res.status(503).end();
    default:          return assertNever(r.error);
  }
}
res.json(r.value);
```

## When to throw vs return

Throw when:

- The condition is a programmer bug or invariant breach (`assertNever`, `assertDefined`).
- The surrounding code has no meaningful way to recover.
- You're inside a pure module and the caller at the boundary translates it.

Return a `Result` when:

- The failure is part of normal business flow (validation, not-found, payment declined).
- Multiple callers need to distinguish outcomes.
- You are crossing a boundary (HTTP, queue, RPC, UI event).

## Boundary translation

Domain errors map to protocol errors at the edge. The domain never knows about HTTP status codes.

```ts
// domain
type UserError = "not_found" | "email_taken" | "db_down";

// boundary (HTTP)
function toStatus(e: UserError): number {
  switch (e) {
    case "not_found":   return 404;
    case "email_taken": return 409;
    case "db_down":     return 503;
    default:            return assertNever(e);
  }
}

app.post("/users", async (req, res) => {
  const parsed = CreateUser.safeParse(req.body);
  if (!parsed.success) {
    return res.status(400).json({ errors: parsed.error.flatten() });
  }
  const r = await userService.create(parsed.data);
  if (!r.ok) return res.status(toStatus(r.error)).json({ error: r.error });
  res.status(201).json(r.value);
});
```

## Discriminated error unions for richer info

```ts
type PayError =
  | { kind: "card_declined"; code: string; message: string }
  | { kind: "insufficient_funds"; balance: number }
  | { kind: "network"; retryable: true }
  | { kind: "unknown"; message: string };

async function charge(amount: number): Promise<Result<Receipt, PayError>> { /* ... */ }
```

Prefer these when error payloads carry data (messages, codes, retry hints) or when you want to present friendly UI.

## Error classes for things you actually throw

```ts
export class DomainError extends Error {
  constructor(message: string, public readonly cause?: unknown) {
    super(message);
    this.name = new.target.name;
  }
}
export class NotFoundError extends DomainError {}
export class ConflictError extends DomainError {}
```

- Always extend `Error`.
- Set `name` from `new.target.name` for clean stack traces.
- Accept a `cause` — TS supports `Error` `cause` option in `ES2022+`.

```ts
throw new DomainError("import failed", { cause: e });
```

## `useUnknownInCatchVariables`

```ts
try { /* ... */ }
catch (e) {
  // e: unknown — must narrow
  if (e instanceof NotFoundError) { /* ... */ }
  else if (e instanceof Error)    { log.error(e.message); }
  else                            { log.error(String(e)); }
}
```

Always on. Catches "you can throw any value in JS" once and for all.

## neverthrow tour

`neverthrow` is the most-adopted Result library. Use when you want combinators beyond hand-rolled types.

```ts
import { Result, ok, err, ResultAsync } from "neverthrow";

function parseEmail(raw: string): Result<Email, "invalid"> {
  return /.+@.+/.test(raw) ? ok(raw as Email) : err("invalid");
}

const loadUser = (id: string): ResultAsync<User, "not_found"> =>
  ResultAsync.fromPromise(
    db.user.findUnique({ where: { id } }).then((u) => u ?? Promise.reject("missing")),
    () => "not_found" as const,
  );

// chain
const result = await parseEmail(input.email)
  .asyncAndThen((email) => loadUserByEmail(email))
  .map((u) => toDto(u));
```

Key methods:

- `map(f)` — transform the ok value.
- `mapErr(f)` — transform the error.
- `andThen(f)` — flatMap; `f` returns a `Result`.
- `orElse(f)` — recover; `f` returns a `Result`.
- `match(okFn, errFn)` — terminal, both cases.
- `unwrapOr(default)` — extract with a fallback.

Avoid `unsafeUnwrap` — it defeats the pattern.

## ts-results (alternative)

Smaller API surface (`Ok`, `Err`, `.map`, `.unwrap`), but `.unwrap()` throws. Prefer neverthrow unless you want minimal deps.

## Hand-rolled is fine

For app-level code, hand-rolling `ok`/`err` keeps deps small. A helper `all` combinator covers most needs:

```ts
async function all<T, E>(
  promises: ReadonlyArray<Promise<Result<T, E>>>,
): Promise<Result<readonly T[], E>> {
  const out: T[] = [];
  for (const p of promises) {
    const r = await p;
    if (!r.ok) return r;
    out.push(r.value);
  }
  return ok(out);
}
```

## Logging + returning

Log once, at the boundary. Don't log and throw and log and throw.

```ts
// domain — return
return err("db_down");

// boundary — log then respond
if (!r.ok) {
  log.error({ code: r.error, userId: id }, "load_user_failed");
  return res.status(503).json({ error: r.error });
}
```

## Framework integration

### Fastify

```ts
app.setErrorHandler((err, req, reply) => {
  if (err instanceof NotFoundError) return reply.code(404).send({ error: err.message });
  req.log.error({ err }, "unhandled");
  reply.code(500).send({ error: "internal" });
});
```

### Express

```ts
app.use((err: unknown, req, res, next) => {
  if (err instanceof NotFoundError) return res.status(404).json({ error: err.message });
  req.log.error({ err }, "unhandled");
  res.status(500).json({ error: "internal" });
});
```

### tRPC

Throw `TRPCError` at procedure boundaries — tRPC already implements Result semantics for clients.

## Anti-patterns

- Throwing a string: `throw "nope"`. Always throw an `Error` subclass.
- Catching and ignoring: `catch (e) {}`. Log at minimum.
- Re-throwing with lost stack: `catch (e) { throw new Error("failed") }`. Always chain `cause`.
- Returning `null` to mean "error". Use `Result`; reserve `null` for "value is intentionally absent".
- Using `Result` inside hot numeric loops — allocation overhead. Throw or use sentinels there.

## Cross-reference

Parallels `python-modern-standards/references/error-handling.md` — Python's approach (exceptions with typed hierarchy + explicit `Result` at message boundaries) converges on the same split.
