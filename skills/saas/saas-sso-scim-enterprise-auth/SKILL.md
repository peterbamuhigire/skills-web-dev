---
name: saas-sso-scim-enterprise-auth
description: Use when implementing tenant-scoped SAML or OIDC SSO, SCIM provisioning, custom domains, IP allowlists, or enterprise auth migration.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# SaaS Enterprise Auth — SSO, SCIM, Custom Domain
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.


## Required Inputs

| Input | Required | Use |
|---|---|---|
| Tenant, product, and lifecycle scope | yes | Bound the SaaS decision |
| Current architecture, plans, policies, and constraints | yes | Preserve enforceable behaviour |
| Production data or verified evidence | conditional | Validate thresholds and migrations |

## Capability and permission contract

Default to read-only analysis. Change configuration, billing, identity, tenant data, infrastructure, or customer communications only with explicit authority, least-privilege credentials, tenant scope, rollback, and auditable approval. Never expose secrets or cross tenant boundaries.

## Degraded mode

If production access, policy, telemetry, or authoritative records are unavailable, produce a labelled design or dry-run plan. Do not claim deployment, reconciliation, deletion, delivery, or measured outcomes; list missing evidence and verification.

## Decision rules

| Condition | Action | Stop condition |
|---|---|---|
| Tenant isolation, money, identity, or deletion is affected | Require approval and rollback evidence | Scope or authority is ambiguous |
| Evidence supports a reversible change | Stage, test, and record it | Acceptance checks fail |
| Only partial context is available | Return assumptions and validation | A production claim cannot be verified |

## Domain Anti-Patterns

- Applying one tenant's policy or data to another. Fix: enforce tenant scope at every boundary.
- Mutating production from an advisory request. Fix: remain read-only until authority is explicit.
- Inventing limits, prices, metrics, or compliance claims. Fix: use authoritative records or mark them unresolved.
- Shipping without rollback and audit evidence. Fix: stage and retain before/after proof.
- Treating a missing dependency as successful. Fix: name the blocked verification.


<!-- dual-compat-start -->
## Use When

- Adding enterprise auth to a B2B SaaS — SAML 2.0 (Okta, Azure AD, Ping, OneLogin), OIDC (Auth0, Cognito, custom OPs).
- Implementing SCIM 2.0 user provisioning/deprovisioning so the buyer's IdP can lifecycle users into your platform.
- Letting tenants connect their own IdP per tenant (multi-IdP-per-platform).
- Supporting custom domains (`app.customer.com`) with automated cert provisioning.
- Adding IP allowlists per tenant for enterprise-tier security policy.
- Migrating an existing email-password tenant to IdP-enforced login.
- Exposing an audit-log API the customer can pull into their SIEM.

## Do Not Use When

- The task is the customer-facing tenant-admin auth screen — use `dual-auth-rbac`.
- The task is internal staff auth — use `dual-auth-rbac` + MFA + the back-office privileged-access workflow in `saas-admin-backoffice-tooling`.
- The task is OAuth as a *client* (calling Google/Stripe APIs) — use `vibe-security-skill`.

## Required Inputs

- Current auth implementation (which provider / framework — Cognito, Auth0, Clerk, Supabase Auth, custom, etc.).
- Identity model from `saas-control-plane-engineering` (users + memberships).
- Enterprise-tier definition from `subscription-billing` (which plan gates enterprise auth).
- Custom-domain strategy from `saas-deployment-models` / `multi-tenant-saas-architecture`.

## Workflow

1. Read this `SKILL.md`.
2. Decide build-vs-buy (§2). For most teams, **buy** via WorkOS / Ory / Auth0 Enterprise Connections / Clerk / Frontegg.
3. Design the per-tenant IdP configuration model (§3).
4. Implement SAML 2.0 SP-initiated and IdP-initiated SSO (§4).
5. Implement SCIM 2.0 provisioning endpoints (§5).
6. Implement custom domain + auto-TLS (§6).
7. Implement IP allowlists per tenant (§7).
8. Implement audit-log API (§8).
9. Migration plan: email-password → IdP-enforced (§9).
10. Apply anti-patterns (§10).

## Quality Standards

- SAML metadata XML validated; signatures verified; assertion replay-protected (`InResponseTo`, recent timestamp).
- SCIM endpoints conform to RFC 7644 (Users + Groups resources, PATCH with `Operations`).
- Custom domain TLS auto-renewed (cert-manager / ACM / Let's Encrypt).
- IP allowlists enforced at the edge (gateway / WAF), not in the app.
- Audit log API supports pagination, time-range, structured JSON, cursor + idempotent reads.
- Enterprise-auth features gated by plan via `saas-entitlements-and-plan-gating`.

## Anti-Patterns

- Rolling custom SAML — auth code is full of subtle bugs (XML Signature Wrapping, comment-injection, certificate pinning). Use a vetted library or buy.
- One global IdP for the whole platform when the platform should support **per-tenant IdP**.
- SCIM as "we read your IdP nightly" — fragile, slow. SCIM is push from IdP; implement the receiving endpoints.
- IP allowlists enforced only in app code (bypass via direct API call).
- Email-password permanently bypassable on enterprise-IdP-enforced tenants ("emergency login" door). If you need a break-glass, make it audited and time-limited.

## Outputs

- Build-vs-buy ADR.
- Per-tenant IdP configuration schema.
- SAML endpoints (ACS, metadata, SLO).
- SCIM endpoints (Users + Groups CRUD).
- Custom domain provisioning automation.
- IP allowlist policy + enforcement layer.
- Audit log API spec.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Security | Enterprise auth ADR | ADR markdown | `docs/adr/0015-enterprise-auth.md` |
| Security | Per-tenant IdP config schema | Markdown doc + SQL | `docs/saas/tenant-idp-config.md` |
| Release evidence | SCIM endpoint spec | Markdown doc with example payloads | `docs/saas/scim-spec.md` |

## References

- `references/saml-implementation.md` — SAML 2.0 flow, attribute mapping, validation pitfalls.
- `references/scim-provisioning.md` — SCIM 2.0 endpoints, PATCH semantics, Okta/Azure quirks.
- `references/custom-domain-and-tls.md` — DNS verification, cert-manager, fingerprint validation.
- `references/audit-log-api.md` — API surface, retention, format.
- Companion: `multi-tenant-saas-architecture`, `dual-auth-rbac`, `saas-control-plane-engineering`, `saas-entitlements-and-plan-gating`, `vibe-security-skill`.

<!-- dual-compat-end -->

## §1 The Enterprise-Auth Pack

Selling to enterprises requires:
1. **SSO via SAML 2.0** (and/or OIDC) with per-tenant IdP.
2. **SCIM 2.0** so the buyer can provision/deprovision via their IdP.
3. **Custom domain** (`app.customer.com` CNAME).
4. **IP allowlists** per tenant.
5. **Audit log API** the buyer's SIEM pulls.
6. **MFA enforcement** policies per tenant.
7. **Session control** — max session length, idle timeout, forced re-auth on privileged actions.

Mersch (*Hacking SaaS*) is emphatic — these are not edge cases; they are **price of entry** to the enterprise segment. Shipping the first enterprise deal without them stalls a four-week deal into a four-month deal.

## §2 Build vs Buy

| Option | Cost | Time | Notes |
|---|---|---|---|
| **WorkOS** | $$$ | 1-2 weeks | Best-in-class enterprise auth API; SAML + SCIM + Directory Sync; charges per active connection |
| **Frontegg** | $$$ | 1-2 weeks | All-in-one B2B identity, includes admin portal for tenants |
| **Ory** (open source / managed) | $-$$$ | 2-4 weeks | Self-hostable; more control; more ops |
| **Auth0 Enterprise** | $$$$ | 1-2 weeks | Mature; expensive at scale |
| **Clerk** | $$$ | 1 week | Strong DX; expanding enterprise feature set |
| **AWS Cognito** | $-$$ | 2-4 weeks | If already on AWS; SAML works; SCIM limited |
| **Roll custom** | Eng time | 2-3 months | Don't. The auth surface is enormous and one bug is a CVE. |

**Default recommendation for SaaS up to $10M ARR:** WorkOS (best ROI on enterprise-auth complexity). Migrate to in-house only if cost + control require it at $50M+ ARR.

## §3 Per-Tenant IdP Configuration

```sql
CREATE TABLE tenant_idp_configurations (
    tenant_id          BIGINT UNSIGNED PRIMARY KEY,
    enforced           BOOLEAN NOT NULL DEFAULT FALSE,  -- if true, email-password blocked
    protocol           ENUM('saml','oidc','none') NOT NULL DEFAULT 'none',

    -- SAML
    saml_metadata_xml  TEXT,
    saml_entity_id     VARCHAR(255),
    saml_sso_url       VARCHAR(512),
    saml_certificate   TEXT,
    saml_attr_email    VARCHAR(128) DEFAULT 'NameID',
    saml_attr_name     VARCHAR(128) DEFAULT 'displayName',
    saml_attr_groups   VARCHAR(128) DEFAULT 'groups',

    -- OIDC
    oidc_issuer        VARCHAR(512),
    oidc_client_id     VARCHAR(255),
    oidc_client_secret VARCHAR(512),    -- encrypted at rest

    -- SCIM
    scim_enabled       BOOLEAN NOT NULL DEFAULT FALSE,
    scim_bearer_token_hash CHAR(64),    -- SCIM endpoint auth
    scim_group_mapping JSON,            -- IdP group → tenant role

    -- Misc
    domain_verified    BOOLEAN NOT NULL DEFAULT FALSE, -- buyer proved ownership of email domain
    email_domain       VARCHAR(255),     -- e.g., 'acme.com'

    configured_by      BIGINT UNSIGNED,
    configured_at      DATETIME,
    updated_at         DATETIME
);
```

**Domain claim flow** is essential — if any user with email `@acme.com` can claim the Acme tenant, you have a takeover risk. Domain verification via DNS TXT record or a verified-by-IT click flow.

## §4 SAML 2.0 Implementation

### Endpoints

| Endpoint | Purpose |
|---|---|
| `GET /sso/saml/{tenant}/metadata` | Your platform's SP metadata XML |
| `POST /sso/saml/{tenant}/acs` | Assertion Consumer Service — IdP posts SAMLResponse here |
| `GET /sso/saml/{tenant}/login` | SP-initiated login (redirect to IdP) |
| `GET /sso/saml/{tenant}/logout` | Single Logout (SLO) initiation |
| `POST /sso/saml/{tenant}/sls` | Single Logout Service — IdP posts logout here |

### Flow

```
User → app.example.com → "Sign in with SSO" → enters email → email domain → resolve tenant
     → redirect to /sso/saml/{tenant}/login
     → SAMLRequest built, signed, redirect to tenant.saml_sso_url
     → User authenticates at IdP
     → IdP posts SAMLResponse to /sso/saml/{tenant}/acs
     → Validate signature, audience, recipient, NotBefore/NotOnOrAfter, InResponseTo
     → Extract attributes (email, name, groups)
     → Match or create user; bind to tenant; resolve roles from group mapping
     → Issue platform session
     → Redirect to app
```

### Validation pitfalls (these are CVE-tier when wrong)

- Always verify the XML signature against the configured certificate.
- Reject if `NotOnOrAfter` in the past.
- Reject if `Recipient` does not match your ACS URL.
- Reject if `Audience` does not match your SP entity ID.
- Reject if the assertion has been seen before (replay protection: cache `Assertion.ID` for the validity window).
- Beware XML Signature Wrapping — validate the signed element is the one you're consuming.
- Beware XXE — parse with external-entity resolution disabled.

### Library recommendations

- Python: `python3-saml` (OneLogin) — well-maintained.
- Node: `passport-saml` / `samlify`.
- Go: `crewjam/saml`.
- PHP: `onelogin/php-saml`.
- Or: **don't roll** — use WorkOS / Auth0 / Cognito and avoid these pitfalls.

## §5 SCIM 2.0 Implementation

SCIM is **push from IdP to platform** — provisioning/deprovisioning runs on the IdP's schedule.

### Endpoints (under `/scim/v2/{tenant}/`)

| Endpoint | Method | Purpose |
|---|---|---|
| `/Users` | GET | List users (paginated) |
| `/Users` | POST | Create user |
| `/Users/{id}` | GET | Read user |
| `/Users/{id}` | PUT | Replace user |
| `/Users/{id}` | PATCH | Partial update (most-used) |
| `/Users/{id}` | DELETE | Deprovision user |
| `/Groups` | GET / POST / etc. | Group CRUD |
| `/ServiceProviderConfig` | GET | Platform capabilities |
| `/Schemas` | GET | Resource schemas |
| `/ResourceTypes` | GET | Resource types |

### Auth

Bearer token per tenant. Tenant admin generates it once in the platform UI; pastes into Okta/Azure SCIM connector.

### PATCH semantics

`PATCH /Users/{id}` body:
```json
{
  "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
  "Operations": [
    {"op": "replace", "path": "active", "value": false}
  ]
}
```

Implementing PATCH correctly is the hardest SCIM problem. Test against Okta + Azure AD + OneLogin payloads — they all send slightly different shapes.

### Group mapping

Map IdP groups (e.g., `acme-saas-admins`) to your platform roles (e.g., `admin`). Stored in `tenant_idp_configurations.scim_group_mapping`.

## §6 Custom Domain + Auto-TLS

Customer wants their users to log in at `app.acme.com` instead of `acme.your-saas.com`.

### Flow

1. Tenant admin enters `app.acme.com` in your platform's domain settings.
2. Platform displays a CNAME to add: `app.acme.com CNAME tenant-acme.your-saas.com`.
3. Tenant adds CNAME at their DNS.
4. Platform verifies CNAME resolves to your CNAME target (polling).
5. Platform provisions TLS cert via Let's Encrypt / ACM / cert-manager (HTTP-01 or DNS-01 challenge).
6. Once cert issued and CNAME verified, custom domain becomes active for that tenant.
7. Cert auto-renews; failures alert.

### Routing

Edge layer (nginx / Cloudflare / ALB) accepts the custom domain; SNI extracts hostname; resolves to tenant; routes to backend with `X-Tenant-Id` header. The backend trusts the header **only** because it came from the trusted edge.

## §7 IP Allowlists Per Tenant

Enforced at the edge (WAF / ALB / Cloudflare / Cloudfront). App-layer enforcement is a fallback only.

```sql
CREATE TABLE tenant_ip_allowlists (
    id           BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    tenant_id    BIGINT UNSIGNED NOT NULL,
    cidr         VARCHAR(43) NOT NULL,
    description  VARCHAR(255),
    added_by     BIGINT UNSIGNED,
    added_at     DATETIME NOT NULL,
    INDEX idx_tenant (tenant_id)
);
```

Edge consults the allowlist (cached) and rejects with 403 before the request hits the app. App-layer enforcement is a safety net but never the sole gate.

Caveats:
- Mobile-app users have rotating IPs; allowlists usually only apply to web + SCIM endpoints.
- API tokens may need a separate allowlist (often more permissive than web).

## §8 Audit Log API

Customers want to pull audit logs into Splunk/Datadog/Elastic.

```
GET /api/v1/admin/audit-log?from=2026-05-01T00:00:00Z&cursor=<opaque>
Authorization: Bearer <tenant_admin_api_key>

→ 200 OK
{
  "data": [ { id, occurred_at, actor_email, action, target_resource, target_id, ip, metadata } ],
  "cursor": "<next-page-opaque>",
  "has_more": true
}
```

Pagination: cursor-based, not page-based (avoid skip-N inefficiency at large scale).

Retention exposed via `/api/v1/admin/audit-log/retention-policy`.

What to include: tenant-scoped events the customer cares about — user login/logout, MFA changes, role changes, plan changes, member invited/removed, data export, integration created/revoked.

## §9 Migration: Email-Password → IdP-Enforced

Once tenant configures SSO, decide:
- **Optional SSO** — users can choose SSO or email-password.
- **Enforced SSO** — email-password blocked; all logins go through IdP.

Enforced is the enterprise expectation. Migration steps:
1. Tenant admin configures IdP, verifies metadata, tests SP-initiated login.
2. Tenant admin invites the rest of the team (or relies on SCIM provisioning).
3. Tenant admin schedules enforcement date.
4. Platform sends email warning to all tenant users.
5. On enforcement date, set `tenant_idp_configurations.enforced = TRUE`.
6. Email-password logins return: "Your organisation requires SSO. Sign in via your company SSO."

Break-glass: super-admin in the back-office can temporarily disable enforcement for a tenant (audited, time-boxed, justified).

## §10 Anti-Patterns

- **Rolling custom SAML.** Use a library; ideally use WorkOS / Auth0.
- **SCIM as nightly pull.** SCIM is push from IdP; your endpoints must accept the push.
- **IP allowlist enforced only in app code.** Trivially bypassable. Edge-level enforcement is required.
- **One SAML configuration globally.** Each tenant has its own IdP; per-tenant config is mandatory.
- **Email-password "emergency login" left enabled silently.** Audit logs hidden; security catastrophe. If kept, audited + time-boxed + alert-on-use.
- **No domain claim.** Anyone can SSO-link a tenant they're not part of via email-domain assertion.
- **Audit log API rate-limited too aggressively.** Customers pull large windows; need pagination + reasonable rate.

## §11 Read Next

- `dual-auth-rbac` — base auth implementation this skill extends.
- `multi-tenant-saas-architecture` — tenant binding model.
- `saas-control-plane-engineering` — identity service this skill plugs into.
- `saas-entitlements-and-plan-gating` — gate enterprise auth behind enterprise plan.
- `saas-admin-backoffice-tooling` — staff break-glass workflow.
- `vibe-security-skill` — security review baseline.
