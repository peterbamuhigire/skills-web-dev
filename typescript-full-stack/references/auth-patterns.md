# Auth Patterns — Lucia, better-auth, Clerk, NextAuth

Cross-ref: `vibe-security-skill` for web security baseline; `llm-security` for AI
endpoint exposure; `typescript-effective` for session typing; `multi-tenant-saas-architecture`
for tenant-aware sessions.

Four practical choices. Never roll password hashing, session storage, OAuth PKCE,
CSRF, or MFA yourself — the attack surface is too wide.

## Side-by-side

| Concern | Lucia v3 | better-auth | Clerk | NextAuth/Auth.js v5 |
| --- | --- | --- | --- | --- |
| Type | library, self-hosted | library, self-hosted | SaaS (hosted) | library, self-hosted |
| Session storage | your DB | your DB | Clerk infra | adapter to your DB |
| Password auth | yes (argon2id you pick) | yes (argon2id built in) | yes | yes (adapter) |
| OAuth providers | Arctic (separate) | built-in catalogue | 20+ built-in | built-in catalogue |
| MFA (TOTP, WebAuthn, SMS) | Arctic + hand-roll | built-in | built-in | partial |
| Magic links | hand-roll | built-in | built-in | built-in |
| Passkeys | Arctic | built-in | built-in | plugin |
| Admin UI | no | emerging | full | no |
| Pricing | free | free | per MAU | free |
| Next.js App Router fit | good (manual) | good (manual) | excellent (SDK) | excellent |
| Mobile (RN / Expo) | works | works | SDK | tokens adapter |
| Data residency / on-prem | yours | yours | vendor | yours |
| Migration in / out | easy | easy | hard (lock-in) | easy |

## Session vs JWT — default choice

Default to **opaque session cookies** with a server-side session table. Reach for
JWTs only when you have a legitimate cross-service use case.

| Aspect | Session cookie | JWT |
| --- | --- | --- |
| Revocation | immediate (delete row) | hard (need a denylist) |
| Payload size | ~32 bytes | 300-1500 bytes per request |
| Trust model | server is authority | signature is authority |
| Best for | web apps, first-party mobile | service-to-service, stateless APIs |
| CSRF | required cookie defenses | n/a if in Authorization header |
| XSS exposure | `httpOnly` cookie safe | localStorage JWT is unsafe |

Pattern for SaaS:

- Web app: session cookie (httpOnly, secure, SameSite=Lax).
- Mobile app: opaque refresh token in platform-secure storage; exchange for
  short-lived access token (can be JWT) on each launch.
- Service-to-service: mTLS or short-lived JWT signed by an internal KMS key.

## Password hashing

Only argon2id or bcrypt. Never SHA, never MD5, never "salted SHA".

```ts
import { hash, verify } from "@node-rs/argon2";

const params = {
  memoryCost: 19456,   // 19 MiB
  timeCost: 2,
  parallelism: 1,
} as const;

export const hashPassword = (pw: string) => hash(pw, params);
export const verifyPassword = (stored: string, supplied: string) => verify(stored, supplied);
```

Tune `memoryCost` so single-verify takes 50-100 ms on your production CPU. Lucia and
NextAuth let you plug this in; better-auth provides it; Clerk handles it vendor-side.

## Lucia v3 — database-backed, you own everything

```ts
// packages/auth/src/lucia.ts
import { Lucia } from "lucia";
import { DrizzlePostgreSQLAdapter } from "@lucia-auth/adapter-drizzle";
import { db } from "@acme/db";
import { sessions, users } from "@acme/db/schema";

const adapter = new DrizzlePostgreSQLAdapter(db, sessions, users);

export const lucia = new Lucia(adapter, {
  sessionCookie: {
    attributes: { secure: process.env.NODE_ENV === "production" },
  },
  getUserAttributes: (u) => ({ email: u.email, role: u.role, orgId: u.orgId }),
});

declare module "lucia" {
  interface Register {
    Lucia: typeof lucia;
    DatabaseUserAttributes: { email: string; role: "admin" | "member" | "viewer"; orgId: string };
  }
}
```

Sign-in handler:

```ts
import { lucia } from "@acme/auth";
import { verifyPassword } from "@acme/auth/password";

app.post("/sign-in", async (req, reply) => {
  const { email, password } = SignIn.parse(req.body);
  const user = await db.user.findUnique({ where: { email } });
  if (!user) return reply.code(401).send({ error: "invalid_credentials" });
  const ok = await verifyPassword(user.passwordHash, password);
  if (!ok) return reply.code(401).send({ error: "invalid_credentials" });

  const session = await lucia.createSession(user.id, {});
  const cookie = lucia.createSessionCookie(session.id);
  reply.header("Set-Cookie", cookie.serialize());
  return { ok: true };
});
```

OAuth via Arctic (separate library by the same author):

```ts
import { Google } from "arctic";

export const google = new Google(
  process.env.GOOGLE_CLIENT_ID!,
  process.env.GOOGLE_CLIENT_SECRET!,
  `${process.env.APP_URL}/auth/google/callback`
);
```

## better-auth — batteries-included self-hosted

```ts
// packages/auth/src/better.ts
import { betterAuth } from "better-auth";
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { twoFactor, passkey, magicLink, organization } from "better-auth/plugins";
import { db } from "@acme/db";

export const auth = betterAuth({
  database: drizzleAdapter(db, { provider: "pg" }),
  emailAndPassword: { enabled: true, requireEmailVerification: true },
  socialProviders: {
    google: { clientId: process.env.GOOGLE_CLIENT_ID!, clientSecret: process.env.GOOGLE_CLIENT_SECRET! },
    github: { clientId: process.env.GITHUB_CLIENT_ID!, clientSecret: process.env.GITHUB_CLIENT_SECRET! },
  },
  plugins: [
    twoFactor(),
    passkey(),
    magicLink({ sendMagicLink: async ({ email, url }) => sendMail(email, "Login", `Click ${url}`) }),
    organization(),
  ],
  session: { expiresIn: 60 * 60 * 24 * 7, cookieCache: { enabled: true, maxAge: 60 * 5 } },
});
```

Mount in Next.js App Router:

```ts
// app/api/auth/[...all]/route.ts
import { auth } from "@acme/auth";
import { toNextJsHandler } from "better-auth/next-js";
export const { GET, POST } = toNextJsHandler(auth);
```

Client helpers:

```ts
// packages/auth-client/src/index.ts
import { createAuthClient } from "better-auth/react";
export const authClient = createAuthClient({ baseURL: process.env.NEXT_PUBLIC_APP_URL });
```

## Clerk — hosted, fastest to ship

Use when you want a signup UI, MFA, user profile, and org invites on day one. Trade
lock-in and per-MAU cost.

```tsx
// app/layout.tsx
import { ClerkProvider } from "@clerk/nextjs";
export default function Layout({ children }: { children: React.ReactNode }) {
  return <ClerkProvider>{children}</ClerkProvider>;
}

// middleware.ts
import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";
const isProtected = createRouteMatcher(["/app(.*)", "/api(.*)"]);
export default clerkMiddleware((auth, req) => {
  if (isProtected(req)) auth().protect();
});
```

Backend:

```ts
import { getAuth } from "@clerk/fastify";
app.get("/me", async (req) => {
  const { userId, orgId, sessionClaims } = getAuth(req);
  if (!userId) throw new Error("unauth");
  return { userId, orgId, role: sessionClaims?.metadata?.role };
});
```

Exit plan: export users via Clerk Backend API, migrate passwords (Clerk emits bcrypt
hashes), swap middleware. Do this as a drill before depending on them for revenue.

## NextAuth / Auth.js v5

```ts
// auth.ts
import NextAuth from "next-auth";
import Credentials from "next-auth/providers/credentials";
import Google from "next-auth/providers/google";
import { DrizzleAdapter } from "@auth/drizzle-adapter";
import { db } from "@acme/db";

export const { handlers, signIn, signOut, auth } = NextAuth({
  adapter: DrizzleAdapter(db),
  providers: [
    Google,
    Credentials({
      credentials: { email: {}, password: {} },
      authorize: async (creds) => {
        const user = await db.user.findUnique({ where: { email: creds.email as string } });
        if (!user) return null;
        const ok = await verifyPassword(user.passwordHash, creds.password as string);
        return ok ? { id: user.id, email: user.email, name: user.name } : null;
      },
    }),
  ],
  session: { strategy: "database" },
  callbacks: {
    session: async ({ session, user }) => ({
      ...session,
      user: { ...session.user, id: user.id, role: (user as any).role, orgId: (user as any).orgId },
    }),
  },
});
```

Default to `session: { strategy: "database" }` unless you specifically want JWT.

## MFA (TOTP)

With better-auth, the `twoFactor` plugin covers enrolment, QR code, backup codes.

With Lucia, hand-roll using `otpauth`:

```ts
import { TOTP } from "otpauth";

const totp = new TOTP({
  issuer: "Acme",
  label: user.email,
  algorithm: "SHA1",
  digits: 6,
  period: 30,
  secret: user.totpSecret, // base32, 160 bits
});

const valid = totp.validate({ token: submitted, window: 1 }) !== null;
```

Store backup codes as argon2id hashes; consume on use.

## WebAuthn / passkeys

Prefer library support. `@simplewebauthn/server` for Lucia path; better-auth and
Clerk include it. Do not hand-roll assertion verification.

## OAuth flow — Authorization Code + PKCE

For OAuth with third parties in a public client:

1. Generate `state` (random 32 bytes) and `code_verifier`.
2. `code_challenge = SHA256(code_verifier)`.
3. Redirect to provider with `code_challenge`, `state`.
4. On callback, validate `state` matches and exchange `code` + `code_verifier` for
   tokens.
5. Validate ID token signature, `iss`, `aud`, `exp`, `nonce`.

Arctic and better-auth handle all of this. Do not skip `state` or `PKCE`.

## Cookie vs token storage — the rule

```text
Web browser            -> httpOnly, Secure, SameSite=Lax cookie. Never localStorage.
Mobile (native)        -> Keychain (iOS) / EncryptedSharedPreferences (Android).
Server-to-server       -> short-lived JWT in Authorization header, mTLS preferred.
CLI tools              -> OS keyring via keytar-equivalent.
```

## Session hijack and CSRF defenses

- `SameSite=Lax` blocks most cross-site POSTs; use `SameSite=Strict` where possible.
- Mutations additionally require a CSRF token (double-submit cookie or synchronizer
  token) — better-auth and NextAuth include this; verify it's on.
- Rotate session IDs on privilege elevation (after sign-in, after MFA, after role
  change).
- Revoke all sessions on password change.

## Multi-tenant sessions

Store `orgId` on the session, not just the user. When the user switches orgs in the
UI, mint a new session (or a scoped claim) rather than flipping a cookie value. This
keeps audit logs correct and prevents confused-deputy bugs.

## Anti-patterns

- Password policies that ban pastes, force rotation every 30 days, require symbols.
  NIST says long, unique, and checked against breach lists.
- Storing OAuth refresh tokens unencrypted at rest.
- JWT with `alg: none`. Reject on the library level.
- Cookies without `Secure` in production. Cookies without `httpOnly` if the client
  doesn't need JS access.
- Single long-lived token on mobile — always pair access + refresh with rotation.
- Inventing your own MFA numeric OTP over SMS as the sole factor. SMS OTP is a
  fallback, not a primary.

## Decision rules

```text
MVP in two weeks, budget for MAU pricing             -> Clerk
Production SaaS, control data + cost, need MFA/OAuth -> better-auth
Want tiny deps, happy to assemble pieces             -> Lucia + Arctic
Already on Auth.js, happy with it                    -> NextAuth v5
Regulated industry, data residency strict            -> Lucia or better-auth
Shipping to App Store + Play Store                   -> Clerk SDKs or better-auth tokens
```
