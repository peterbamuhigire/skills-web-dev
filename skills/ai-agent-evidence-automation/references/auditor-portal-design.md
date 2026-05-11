# Auditor Portal Design

The auditor portal is the read-only surface where the external auditor pulls evidence themselves. It removes the need for the on-call engineer to hand-export bundles.

---

## 1. Goals

- One URL per (control × window) returns a verifiable pack.
- Auditor authenticates with their own identity (not a shared login).
- Every access is logged.
- Scoped to the audit engagement; auditor cannot browse outside.
- Read-only; auditor cannot trigger regeneration or modify packs.

## 2. Authentication and Authorisation

Separate IdP role: `role:external_auditor`. Not the staff IdP; a dedicated tenant.

```sql
CREATE TABLE audit_engagements (
  id                    BIGINT PRIMARY KEY,
  framework             VARCHAR(32) NOT NULL,        -- "SOC2T2","ISO_SURVEILLANCE","HIPAA_REVIEW"
  firm_name             VARCHAR(128) NOT NULL,
  window_start          DATE NOT NULL,
  window_end            DATE NOT NULL,
  in_scope_controls     JSON NOT NULL,                 -- list of control_ids
  status                ENUM('pending','active','closed') NOT NULL,
  opened_at             TIMESTAMP NOT NULL,
  closed_at             TIMESTAMP,
  primary_contact       VARCHAR(128) NOT NULL,
  internal_lead         VARCHAR(128) NOT NULL
);

CREATE TABLE auditor_identities (
  email                 VARCHAR(256) PRIMARY KEY,
  engagement_id         BIGINT NOT NULL REFERENCES audit_engagements(id),
  added_at              TIMESTAMP NOT NULL,
  added_by              VARCHAR(128) NOT NULL,
  last_seen_at          TIMESTAMP,
  status                ENUM('active','revoked') NOT NULL
);
```

Each auditor identity gets an IdP login (SSO or magic-link with MFA). Login scopes the session to `engagement_id`.

## 3. API (OpenAPI excerpt)

```yaml
openapi: 3.1.0
info:
  title: Compliance Auditor Portal API
  version: 1.0.0
security:
  - BearerAuth: []

paths:
  /v1/engagement:
    get:
      summary: Get the current auditor's engagement
      responses:
        "200":
          description: Engagement detail
          content:
            application/json:
              schema:
                $ref: "#/components/schemas/Engagement"

  /v1/controls:
    get:
      summary: List in-scope controls
      responses:
        "200":
          description: Controls in scope for engagement
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: "#/components/schemas/Control"

  /v1/controls/{control_id}:
    get:
      summary: Control narrative + history
      parameters:
        - in: path
          name: control_id
          required: true
          schema: { type: string }

  /v1/controls/{control_id}/packs:
    get:
      summary: Packs for this control within engagement window
      parameters:
        - in: path
          name: control_id
          required: true
          schema: { type: string }
        - in: query
          name: window_start
          schema: { type: string, format: date }
        - in: query
          name: window_end
          schema: { type: string, format: date }

  /v1/packs/{pack_id}:
    get:
      summary: Pack metadata + signed download URL
      parameters:
        - in: path
          name: pack_id
          required: true
          schema: { type: string }

  /v1/packs/{pack_id}/download:
    get:
      summary: One-time signed URL to the pack file
      responses:
        "302":
          description: Redirect to signed storage URL
          headers:
            Location:
              schema: { type: string }

  /v1/incidents:
    get:
      summary: Incident records in scope

  /v1/attestations:
    get:
      summary: Quarterly attestation packs in scope

  /v1/access-log/me:
    get:
      summary: Auditor's own access history (their accountability surface)

components:
  schemas:
    Engagement:
      type: object
      required: [id, framework, window_start, window_end, in_scope_controls]
      properties:
        id: { type: integer }
        framework: { type: string }
        window_start: { type: string, format: date }
        window_end: { type: string, format: date }
        in_scope_controls: { type: array, items: { type: string } }
    Control:
      type: object
      properties:
        control_id: { type: string }
        framework: { type: string }
        name: { type: string }
        owner: { type: string }
        latest_pack_id: { type: string }
        pack_count_in_window: { type: integer }
```

## 4. Scoping Enforcement

Every request is filtered by engagement:

```python
# portal/auth.py
def current_engagement() -> AuditEngagement:
    ident = AuditorIdentity.get(current_user.email)
    if not ident or ident.status != "active":
        raise PermissionDenied()
    eng = AuditEngagement.get(ident.engagement_id)
    if eng.status != "active":
        raise PermissionDenied()
    AuditorIdentity.touch_last_seen(ident.email)
    return eng

def filter_packs(control_id: str, window_start: date, window_end: date):
    eng = current_engagement()
    if control_id not in eng.in_scope_controls:
        raise PermissionDenied(reason="control not in scope")
    # Clamp window to engagement window
    ws = max(window_start or eng.window_start, eng.window_start)
    we = min(window_end or eng.window_end, eng.window_end)
    return EvidencePackRegistry.find(control_id, ws, we)
```

## 5. Access Log

Every portal request writes one row:

```sql
CREATE TABLE auditor_portal_access (
  id                BIGINT PRIMARY KEY,
  occurred_at       TIMESTAMP NOT NULL,
  auditor_email     VARCHAR(256) NOT NULL,
  engagement_id     BIGINT NOT NULL,
  route             VARCHAR(256) NOT NULL,
  control_id        VARCHAR(64),
  pack_id           VARCHAR(128),
  ip_address        VARCHAR(64),
  user_agent        VARCHAR(256),
  response_status   INT NOT NULL,
  bytes_served      BIGINT
);
```

Monthly export to `evidence/portal/access-YYYY-MM.jsonl`. Internal lead reviews monthly; anomalies (mass-download outside engagement scope) page CISO.

## 6. Pack Download

Pack download uses **one-time signed URLs** to the evidence vault. The portal never streams the pack directly (avoids replay attacks on the bearer token).

```python
def download(pack_id: str):
    eng = current_engagement()
    pack = EvidencePackRegistry.get(pack_id)
    if pack.control_id not in eng.in_scope_controls:
        raise PermissionDenied()
    if not _within_engagement_window(pack, eng):
        raise PermissionDenied()
    url = EvidenceVault.signed_url(pack.vault_key, ttl_seconds=300, one_time=True)
    AuditorPortalAccess.record(route="download",
                                 control_id=pack.control_id,
                                 pack_id=pack.pack_id,
                                 url=url)
    return redirect(url, status=302)
```

## 7. UI Notes

- Plain HTML table; no fancy JS framework. Auditor's tools may need to scrape.
- CSV / JSON export of pack listings for the auditor's working papers.
- "Open pack" button → metadata view → "Download" button.
- "Run verify.py instructions" — link to the cross-platform verification guide.
- Banner: "All access is logged. You agreed to this in the engagement letter."

## 8. Onboarding / Offboarding

- Onboarding: internal lead adds auditor emails; portal sends SSO invite; auditor sets password + MFA.
- Offboarding (engagement closed): all auditor identities for the engagement set to `revoked`; portal access denied.
- Re-engagement: new engagement record; previous identities re-activated by explicit action (not automatic).

## 9. Anti-Patterns

- One shared "auditor" login. Cannot tell who pulled what.
- Auditor identity assigned to an engineering account ("just easier"). Engineer's audit trail polluted.
- Portal allows triggering regeneration. Auditor inadvertently produces fresh evidence post-hoc.
- Portal allows access outside engagement window. Scope creep into out-of-engagement data.
- Pack download URL valid for hours. Replay attack from auditor's compromised endpoint serves the pack indefinitely.
- Access log written to the same DB the application can mutate. Auditor cannot trust the log.

## 10. Integration with Compliance Console

The internal compliance console (`saas-admin-backoffice-tooling`) is the operator's counterpart:

- Operators see all packs, all engagements.
- Operators can open / close engagements.
- Operators can re-run a collector (creates a new pack; old preserved).
- Operators can issue / revoke auditor identities.
- Operators see the auditor portal access log.

Operators **cannot delete a pack**. Pack retention is enforced at storage layer.

The portal is the auditor's view; the console is the operator's view. They share the underlying evidence vault.
