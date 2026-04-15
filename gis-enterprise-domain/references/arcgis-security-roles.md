# ArcGIS Enterprise Security and Roles

Portal roles and groups, Server RBAC on published services, SAML/OIDC federation with an enterprise identity provider, audit logging, and the choice between token-based and PKI authentication.

## Portal identity model

Three concepts you must keep distinct:

- **User** — individual account in Portal. Has a role and a licence (user type).
- **Role** — set of privileges (what a user can do). Built-in or custom.
- **Group** — set of users who share content; drives access to items.

Users are licensed via **user types** (Viewer, Mobile Worker, Editor, Field Worker, Creator, GIS Professional). The user type caps what roles and apps the user can use.

### Built-in roles

```text
Role              Typical use
----------------  -------------------------------------------------
Viewer            Read-only consumption of shared content
Data Editor       Edit hosted feature layers where permitted
Publisher         Publish new services and hosted layers
Administrator     Full org-admin, including licences and security
```

### Custom roles

Build custom roles when the built-ins are either too broad or too narrow. Example: a "Data Custodian" role that can publish and update but not delete users or change security settings.

Keep the number of custom roles low (under a dozen). Too many roles becomes unmanageable.

## Groups and sharing

Items (maps, layers, apps) are shared at four scopes:

```text
Scope      Who sees it
---------  --------------------------------------------
Private    Only the owner
Group      Members of a named group
Org        All users in the organisation
Public     Anyone on the internet (no auth)
```

Rules:

- Never share editable feature services as Public.
- For multi-tenant portals, model each tenant as a group; never share across groups by accident.
- Use **shared update groups** for collaborative editing — members can update items they did not create.
- Nest groups via group categories to keep the catalogue searchable.

## Server-side RBAC on services

Portal sharing controls **discoverability** and **access** to hosted items. On federated ArcGIS Server, you can also layer **service-level permissions**:

- Permissions on specific services (read, edit, admin).
- Folder-level inheritance.
- Role-to-permission mappings in Server Manager.

For a multi-tenant feature service exposing tenant data in a single layer, rely on Portal group sharing plus **field-level visibility** and **feature filters** (owner-based or attribute-based) defined on the service. Never rely on client-side filtering.

### Owner-based access control on hosted feature layers

Enable "editor tracking" and "owner-based access" so users can only see or edit features where `created_user` matches them. For multi-tenant scenarios, extend this with a custom attribute (`tenant_id`) and a view that filters by the authenticated user's tenant.

## Identity provider integration (SAML and OIDC)

Integrate Portal with the enterprise IdP so you are not managing passwords in Portal.

### SAML setup (typical)

```text
1. Obtain SAML metadata URL from IdP (Entra ID, Okta, Keycloak).
2. In Portal: Organization -> Security -> Enterprise logins -> Set identity provider.
3. Paste SAML metadata or URL.
4. Configure attribute mapping: NameID -> username, email, givenName, surname.
5. Configure group sync: IdP groups map to Portal groups (optional).
6. Set the default role and user type for new auto-provisioned users.
7. Test: open incognito, go to Portal, you should be redirected to IdP.
8. Enforce: disable built-in logins once every admin has an enterprise login.
```

### OIDC setup

Portal also supports OIDC (OpenID Connect). Same basic shape: issuer URL, client ID, client secret, claims mapping. Prefer OIDC for new deployments over SAML when both are offered.

### Sign-out

Configure **Single Logout** (SAML SLO or OIDC end-session) so logging out of Portal invalidates the IdP session, otherwise users think they logged out but remain signed in.

## Token vs PKI authentication

Two models coexist on ArcGIS Enterprise:

```text
Aspect              Token authentication            PKI (client certificate)
------------------  ------------------------------  --------------------------------
Credential          Username+password -> token      X.509 client cert
Browser UX          Sign-in form                    Cert picker / smart card
Non-browser clients Easy (Authorization header)     Harder, cert distribution
Sensitivity         Normal apps, SaaS consumers     Government, defence, high-trust
Revocation          Expire token                     Revoke cert via PKI infra
Combination         Token is the default            PKI can be layered in front
```

Default for SaaS and commercial deployments is **token authentication** via Portal (ArcGIS tokens) plus SAML/OIDC for interactive users.

Layer **PKI** or **Integrated Windows Authentication (IWA)** only when the enterprise environment already has the infrastructure and the data sensitivity justifies the ops cost.

## Audit logging

Every production deployment must ship logs to a SIEM (Splunk, Elastic, Sumo, Sentinel).

Sources to collect:

- **Portal logs** — `arcgis-portal` logs and the Portal admin activity feed.
- **Server logs** — `arcgis-server` logs per node; enable **Verbose** for security-sensitive services only, `Info` elsewhere.
- **Data Store logs** — PostgreSQL-style logs for the relational store; tail for failed connections and slow queries.
- **Web Adaptor / IIS logs** — request-level logs with client IP, user agent, status code.
- **OS audit logs** — Windows security event log or Linux auditd.

Alert on:

- Admin role changes, especially elevation to Administrator.
- Public sharing of editable services.
- High volume of 401/403 from a single IP.
- Token issuance spikes.
- Failed federation or IdP errors.

## Secrets and keys hygiene

- Rotate the **Portal admin password** on a schedule; treat it like a root credential.
- Rotate **ArcGIS Server certificate and admin token** and store in a secrets manager.
- Configure **HTTPS-only** on every Web Adaptor; redirect HTTP.
- Pin TLS 1.2 minimum (1.3 where supported).
- Disable unused capabilities on services (Sync, Extract, Admin) to reduce the attack surface.

## Multi-tenant SaaS patterns

If Portal is multi-tenant (several customer organisations sharing one deployment):

- Put each customer in their own Portal group; use group-based sharing everywhere.
- Add `tenant_id` to every feature service layer; enforce it via a view or feature filter.
- Namespace item titles and folders by tenant prefix to avoid catalogue collisions.
- Audit every cross-tenant share before go-live.

Or, more robustly, run a separate Portal per tenant (heavier ops, simpler isolation). Pair with the `multi-tenant-saas-architecture` skill.

## Anti-patterns

- Granting Administrator role for convenience during setup and forgetting to reduce it.
- Relying on public sharing "just for a demo" and never switching it off.
- Storing IdP secrets in Portal configuration files rather than a secrets manager.
- Not enabling single logout with the IdP.
- Shipping logs only to local disk where they rotate and are lost.
- Running Portal on HTTP internally and HTTPS externally — gaps between Web Adaptor and Portal.
- Using the same token lifespan for admin and end-user tokens; admin tokens should be short.

## Related references

- `arcgis-components.md` — where identity and federation live in the topology.
- `arcgis-backup-dr.md` — restoring identity configuration after DR event.
- `publishing-services.md` — capability flags that affect the attack surface.
