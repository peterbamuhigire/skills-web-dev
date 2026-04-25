# Access Control Flaws

Purpose: a defender's reference for identifying and preventing broken access control in PHP/JS/HTML SaaS applications.
Covers IDOR, privilege escalation, multi-tenant isolation, admin interfaces, and centralised authorization.

## 1. Authorization vs Authentication

These two terms are frequently conflated. They are not the same thing, and confusing them produces whole classes of bugs.

- **Authentication** answers *"who are you?"* — it verifies identity. Login forms, session cookies, JWT signature verification, and API keys all belong here.
- **Authorization** answers *"what are you allowed to do?"* — it decides, for every request, whether the authenticated identity has permission to perform the action on the requested resource.

A common mistake is treating authentication as sufficient. A logged-in user is still an attacker if they can reach another tenant's data. Every authenticated request must also be authorized against the specific resource it touches.

Access control is the umbrella term that includes both. You cannot enforce permissions until you know who the user is, and you must never stop at "they logged in, so we're fine".

## 2. Access Control Models

| Model | Decision basis | Good fit | Pain points |
|------|----------------|----------|-------------|
| DAC (Discretionary) | Resource owner grants rights to others | File sharing, document ownership | Hard to audit; owners grant over-broadly |
| RBAC (Role-Based) | User role maps to a permission set | SaaS admin/user/viewer, HR systems | Explodes when roles multiply per tenant |
| ABAC (Attribute-Based) | Policy over user + resource + context attributes | Regulated data, conditional access | Policy engine complexity |
| ReBAC (Relationship) | Graph of relations (owns, member-of, parent-of) | Multi-org SaaS, collaborative docs, Google Drive-style | Graph queries cost; tricky to debug |

Most SaaS platforms start with RBAC (roles like `owner`, `admin`, `manager`, `user`, `viewer`) and grow into hybrid RBAC plus per-resource ownership checks. ABAC becomes attractive once you have conditional rules like *"managers can see their branch only"*. ReBAC shines when the unit of sharing is an arbitrary object graph.

Pick the simplest model that fits; complexity in the authorization layer is where exploits hide.

## 3. IDOR (Insecure Direct Object Reference)

IDOR is the most common and most dangerous access control flaw on the web. It occurs when an endpoint accepts a resource identifier from the client (a URL parameter, a form field, a JSON property) and trusts it without checking whether the current user is allowed to touch that resource.

### Example

```http
GET /invoice/123
```

The backend reads `123` from the URL, fetches the invoice, and returns it. Any authenticated user can enumerate IDs and read every invoice in the database.

### Why it is so common

- It is easy to introduce: every new endpoint that takes an ID is a fresh opportunity.
- It is hard to test exhaustively: you need a test for every resource type, every role, and every cross-tenant combination.
- Framework scaffolding usually omits the ownership check; developers paste it in "later" and forget.
- Scanners rarely catch it because the behaviour is indistinguishable from a legitimate request.

### The Defence

Always verify ownership or permission at the point of fetch. The rule is: **never return a resource until you have proven the current user is allowed to see it**.

```php
<?php
declare(strict_types=1);

final class InvoiceController
{
    public function __construct(
        private InvoiceRepository $invoices,
        private AuthContext $auth,
    ) {}

    public function show(int $invoiceId): Response
    {
        $user = $this->auth->currentUser();

        $invoice = $this->invoices->findByIdForTenant(
            $invoiceId,
            $user->tenantId,
        );

        if ($invoice === null) {
            // 404, not 403 — never leak existence
            return Response::notFound();
        }

        if (!$this->auth->can('invoice.view', $invoice)) {
            return Response::notFound();
        }

        return Response::ok($invoice);
    }
}
```

Two defences are layered here: the repository only returns rows for the current tenant, and the policy call checks per-user permission (for example, a sales rep might only see their own invoices).

### UUIDs Are Not a Fix

Using opaque identifiers like UUIDs slows enumeration, but IDOR is still IDOR. The attacker only needs to learn one ID — via a shared link, a leaked log, a referer header, or a colleague — to access the object. **UUIDs are a minor mitigation, not a control**. Always do the authorization check.

## 4. Horizontal Privilege Escalation

One user at a given privilege level accesses another user's data at the same level. User A reads User B's profile, messages, or orders.

The defence is strict scoping of every query by the owning identifier. In a multi-tenant SaaS this usually means `tenant_id`, and often `user_id` within the tenant:

```php
$stmt = $pdo->prepare('
    SELECT id, total, status
    FROM orders
    WHERE id = :id
      AND tenant_id = :tenant_id
');
$stmt->execute([
    'id' => $orderId,
    'tenant_id' => $currentUser->tenantId,
]);
```

If the row is not owned by the requester's tenant, the `WHERE` clause returns zero rows. This is defence in depth even if a higher-level check fails.

## 5. Vertical Privilege Escalation

A regular user performs an admin-only action: deleting a user, changing billing, exporting the full member list.

### Defences

- **Role check at every admin endpoint.** No exceptions.
- **RBAC middleware**, not inline ad-hoc checks, so that forgetting the check is structurally impossible.
- **Deny-by-default routing.** New routes must explicitly declare the required permission; anything without a declaration returns 403.
- **Test the negative path.** Write automated tests where a non-admin user calls the admin endpoint and expects 403.

```php
// Middleware registration
$router->group(
    ['prefix' => '/admin', 'middleware' => ['auth', 'role:admin']],
    function ($r) {
        $r->get('/users', [AdminUserController::class, 'index']);
        $r->delete('/users/{id}', [AdminUserController::class, 'destroy']);
    },
);
```

## 6. Forced Browsing

Hiding a page from the UI does nothing: the URL is still routable. An attacker guesses `/admin/export`, types it in, and pulls the data.

The defence is that server-side authorization runs on every page and every asset — not the UI. "If the user cannot see the button they cannot call the action" is false on the web.

Checklist:

- Every controller action has an explicit permission requirement.
- Static assets containing private data (CSV exports, PDFs, reports) are not served directly from a public directory. They go through an authenticated handler.
- Debug and development routes (`/phpinfo.php`, `/debug`, `/_profiler`) are disabled in production.

## 7. Parameter Tampering for Privilege

The form POSTs `role=admin` and the controller blindly trusts it. Or a hidden field `user_id=7` is changed to `1`, and the handler updates the target user.

### Defences

- **Never accept privilege fields from the client.** Role, tenant, owner, plan — all read from the session or the database, not from the request body.
- **Explicit allow-list of writable fields.** Bind only the fields you intended to accept.
- **Server-side identity.** `user_id` for "who am I" is the session's user id, never a form field.

```php
// WRONG
$user->fill($request->all());
$user->save();

// RIGHT
$user->update([
    'display_name' => $request->input('display_name'),
    'email' => $request->input('email'),
    // role, tenant_id, is_admin deliberately excluded
]);
```

## 8. Path-Based Access Control Bypass

If access decisions are based on matching URL paths, attackers exploit canonicalization gaps:

- Case sensitivity: `/Admin` reaches the handler but misses the check on `/admin`.
- Trailing slash: `/admin/` vs `/admin`.
- URL encoding: `%2e%2e`, `%2f`, `%2E%2E`.
- Double URL encoding: `%252e`.
- Unicode tricks and overlong UTF-8 sequences.

### Defences

- Use framework routing, not hand-rolled string matching.
- Canonicalize the path once before matching: decode, normalize case, strip duplicate slashes, resolve `..`.
- Make the authorization decision on the resolved route name or controller, not the raw URL.

## 9. Multi-Tenant Isolation Flaws

In a multi-tenant SaaS, a single database (or single schema) hosts many customers. A cross-tenant leak — Tenant A seeing Tenant B's data — is usually a company-ending incident.

The recurring bug is a query that forgets `WHERE tenant_id = ?`. The cause is almost always the same: ownership checking is sprinkled across controllers and one gets missed.

### Defences

- **Mandatory tenant scoping in the query builder or ORM.** Make it impossible to build a query without a tenant id, or use a query-rewriter that appends the predicate automatically.
- **Row-level security at the database.** PostgreSQL RLS lets you express the policy at the database layer so even a buggy query cannot return cross-tenant rows.
- **Composite primary keys that include the tenant id.** `PRIMARY KEY (tenant_id, id)` on every tenant-owned table.
- **Database role per tenant** where practical, with the role bound to the session.

### Tenant Isolation Checklist

- Every tenant-owned table has `tenant_id` and an index including it.
- Every repository method requires a `tenantId` parameter; there is no "find by id" without tenant.
- Foreign keys reference `(tenant_id, id)` composites where possible, so a foreign key cannot point across tenants.
- Unique constraints are scoped to tenant: `UNIQUE (tenant_id, email)` not `UNIQUE (email)`.
- Background jobs and webhooks always carry the tenant id; handlers re-establish the tenant context before any DB access.
- Shared caches (Redis) are namespaced by tenant key.
- File storage paths include the tenant id.
- Automated tests assert that a request from Tenant A for a Tenant B id returns 404.

## 10. Admin Interfaces

Admin surfaces are high-value targets and must be segregated from the user-facing application.

- **Separate hostname**: `admin.example.com` distinct from `app.example.com`. Separate cookie scope, separate CSP, separate rate limits.
- **Network restriction**: IP allow-list, VPN, or bastion. Admin consoles should not be reachable from the public internet by default.
- **Mandatory MFA** for every admin account, enforced at authentication — not user-opt-in.
- **Separate session cookies**. A compromised user session must not yield admin access, even if the same user holds both roles.
- **Short session timeouts** and forced reauthentication for destructive actions.
- **Extra logging**: every admin action is written to an append-only audit log with actor, target, timestamp, before/after.

## 11. API Access Control Patterns

Public APIs (consumed by mobile, partners, third parties) have different authorization needs than the first-party web app.

- **Use bearer tokens**, not reused session cookies. Session cookies belong to the browser; APIs should use signed tokens.
- **Token scopes** (OAuth2-style): each token declares what it is allowed to do — `invoice:read`, `invoice:write`, `user:admin`. The server enforces the scope on every endpoint.
- **JWT claims** can carry per-tenant and per-role information, but the server must still check every request. Never trust a JWT claim to decide ownership without a database lookup — tokens can be stale.
- **Revocation**: maintain a denylist or short token lifetimes with refresh. A leaked token must be killable.
- **Rate limits per token**, not just per IP.

## 12. Centralised Authorization

Sprinkled `if ($user->role === 'admin')` checks are the graveyard of access control. They are impossible to audit, they drift as the codebase grows, and new endpoints forget them.

Instead, centralise the decision in **policy objects** (sometimes called authorizers, voters, or ability classes). One place holds the rules; controllers delegate.

```php
<?php
declare(strict_types=1);

final class InvoicePolicy
{
    public function view(User $user, Invoice $invoice): bool
    {
        if ($user->tenantId !== $invoice->tenantId) {
            return false;
        }

        if ($user->hasRole('admin')) {
            return true;
        }

        if ($user->hasRole('sales') && $invoice->ownerId === $user->id) {
            return true;
        }

        return false;
    }

    public function delete(User $user, Invoice $invoice): bool
    {
        return $user->hasRole('admin')
            && $user->tenantId === $invoice->tenantId;
    }
}
```

Controllers call `$policy->view($user, $invoice)`. Tests exercise the policy in isolation with every role and every edge case. When the rules change, there is exactly one place to change them.

## 13. Defender's Audit Checklist

- [ ] Every endpoint requires authentication (except clearly public ones: login, signup, public landing).
- [ ] Every endpoint has an explicit authorization check for the specific resource, not just "is logged in".
- [ ] `tenant_id` is present in every multi-tenant query.
- [ ] Authorization logic lives in policy objects, not scattered across controllers.
- [ ] No UI-only access control — hidden buttons are not a defence.
- [ ] Privilege fields (`role`, `tenant_id`, `owner_id`, `is_admin`) are never read from the request body.
- [ ] Mass assignment is blocked by explicit allow-lists.
- [ ] Admin interfaces live on a separate host with IP restriction and mandatory MFA.
- [ ] Public APIs use bearer tokens with scopes, not session cookies.
- [ ] Automated tests exist for the negative path: unauthorized user attempts each protected action and receives 404 or 403.
- [ ] Cross-tenant tests exist: Tenant A requests Tenant B's resource and gets 404.
- [ ] Forgotten/legacy routes (`/admin/legacy`, `/debug`, `/_profiler`) are removed or firewalled in production.

## 14. Anti-Patterns

- **UI-only hiding**: the button is hidden but the endpoint is still callable. This is the single most common access control mistake.
- **Trusting client-side role**: `if (request.role === 'admin')`.
- **"We use UUIDs so we're safe"**: UUIDs make IDs harder to guess, not harder to use once learned.
- **Admin on the same domain as the user app**: shared cookies, shared CSP, shared attack surface.
- **Ownership checks in the controller but not in the service layer**: background jobs and internal calls bypass them.
- **Per-field role checks in templates**: impossible to audit and always out of date.
- **"Default allow"** routing: new routes inherit no restriction and are publicly reachable until someone remembers to lock them down.
- **Authorization decisions cached in the session without invalidation**: a demoted user keeps admin access until they log out.
- **Internal services with no authorization** because they are "behind the firewall" — zero trust assumes the firewall will be bypassed.
- **Returning 403 instead of 404** for resources the user cannot see. 403 confirms existence and helps enumeration.

## Cross-References

- `input-validation-patterns.md` — validating the inputs that access control relies on
- `business-logic-flaws.md` — workflow, race conditions and state machine bypasses
- `audit-checklist-detailed.md` — the parent skill's master audit checklist
- `php-security` skill — PHP-specific session, CSRF and input-handling patterns
- `dual-auth-rbac` skill — dual auth plus RBAC reference implementation
- `multi-tenant-saas-architecture` skill — tenant isolation architecture
- `vibe-security-skill` — general secure coding baseline
- OWASP Top 10: A01 Broken Access Control
