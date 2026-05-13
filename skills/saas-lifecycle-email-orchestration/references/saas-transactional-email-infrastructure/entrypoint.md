---
name: saas-transactional-email-infrastructure
description: Use when designing the transactional and lifecycle email infrastructure — ESP selection (Postmark, SES, SendGrid, Customer.io, Braze, Resend), domain authentication (SPF, DKIM, DMARC, BIMI), sender reputation, subdomain separation (transactional vs marketing), suppression list management, bounce/complaint feedback loops, and the event-bridge from product events to email automation. Distinct from `tabler-email-templates` (HTML templates), `subscription-billing` (billing-event triggers), and `saas-lifecycle-email-orchestration` (sequence design).
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# SaaS Transactional Email Infrastructure
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Standing up email infrastructure for a new SaaS — domain auth, ESP selection, sender reputation, event bridge.
- Auditing an existing SaaS's deliverability — open rates < 20%, complaint rate > 0.1%, bounce rate > 2%, marketing emails ending up in spam.
- Adding lifecycle automation (Customer.io / Braze / Iterable) on top of an existing transactional sender.
- Separating transactional and marketing reputations on different subdomains because the marketing send is poisoning the transactional one.
- Designing the suppression list and consent model for multi-tenant SaaS (per-tenant unsubscribe).
- Wiring a deliverability monitoring + alerting stack.

## Do Not Use When

- The task is the HTML template itself — use `tabler-email-templates`.
- The task is the sequence design (what emails to send when) — use `saas-lifecycle-email-orchestration`.
- The task is the trigger for a billing email — use `subscription-billing`.

## Required Inputs

- Domain(s) the SaaS will send from.
- Expected send volume per month (drives ESP selection).
- Mix of transactional / lifecycle / marketing.
- Regulatory profile (GDPR, CAN-SPAM, CASL, POPIA — consent model).
- Existing ESP and sender reputation (if any).

## Workflow

1. Read this `SKILL.md`.
2. Choose subdomain strategy (§2) — separate transactional and marketing subdomains.
3. Set up SPF / DKIM / DMARC / BIMI per subdomain (§3).
4. Pick ESP(s) (§4) — usually one transactional + one lifecycle automation tool.
5. Design the event bridge (§5) — product events → email automation.
6. Build the suppression list (§6) — central, tenant-aware, category-aware.
7. Configure feedback loops (§7) — bounces, complaints, unsubscribes.
8. Stand up deliverability monitoring (§8).
9. Apply the consent model (§9) — separate transactional from marketing consent.
10. Apply anti-patterns (§10).

## Quality Standards

- Bounce rate < 2%, complaint rate < 0.1%, inbox placement > 95% (measured via Postmark / GlockApps / SendForensics).
- Every send categorized as transactional / lifecycle / marketing; suppression honoured per category.
- DMARC at `p=quarantine` minimum within 30 days of launch; `p=reject` within 90 days.
- Suppression list is the source of truth; centralised across all ESPs the SaaS uses.
- Unsubscribe processed within minutes; `List-Unsubscribe` header on every applicable send.
- GDPR delete cascades through the suppression list and ESP contact records.

## Anti-Patterns

- Sending marketing emails from the transactional sender (poisons transactional reputation).
- No DMARC — anyone can spoof your domain.
- Suppressions held only in the ESP — switching ESPs loses years of unsubscribe history.
- No per-tenant unsubscribe — a user unsubscribes from one tenant and stops receiving emails from all tenants.
- Webhook from ESP not idempotent (replay creates duplicate suppressions).
- No warmup for new sending IP/domain — first big broadcast destroys reputation.

## Outputs

- ESP selection ADR.
- Domain auth records (SPF/DKIM/DMARC/BIMI) checked into infrastructure repo.
- Event-bridge spec (product events → ESP).
- Suppression list schema + consent model.
- Deliverability monitoring dashboard.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Architecture | Email infrastructure ADR | ADR markdown | `docs/adr/0012-email-infra.md` |
| Release evidence | Domain auth records | DNS export or Terraform module | `infra/dns/email.tf` |
| Operability | Deliverability dashboard | Dashboard link + screenshots | `docs/email/deliverability-dashboard.md` |

## References

- `references/deliverability-deep-dive.md` — SPF/DKIM/DMARC/BIMI, IP warmup, reputation tools.
- `references/esp-selection-matrix.md` — Postmark vs SES vs SendGrid vs Mailgun vs Resend, per use case.
- `references/event-bridge-design.md` — patterns for product event → email automation.
- `references/suppression-and-consent-model.md` — multi-tenant suppression, GDPR cascade.
- Companion: `tabler-email-templates`, `saas-lifecycle-email-orchestration`, `subscription-billing`, `saas-tenant-data-portability-and-erasure`.

<!-- dual-compat-end -->

## §1 The Three Categories of Email

| Category | Examples | Consent | Subdomain |
|---|---|---|---|
| **Transactional** | password reset, OTP, receipt, invitation, MFA, security alert, payment failure | Required by service (no opt-out for security-critical) | `notify.app.com` |
| **Lifecycle / product** | welcome, onboarding nudges, feature announcements, churn-prevention, NPS | Implicit on signup, granular opt-out | `notify.app.com` or `mail.app.com` |
| **Marketing** | newsletter, promotions, webinars, broadcast | Explicit opt-in (GDPR/CASL/POPIA) | `mail.app.com` |

These never share a reputation domain. A marketing send that triggers complaints poisons the transactional reputation if they share a domain.

## §2 Subdomain Strategy

```
app.example.com    — the product itself; never sends email
auth.example.com   — auth-only emails (verify, MFA, security alerts)
notify.example.com — transactional + lifecycle product emails
mail.example.com   — marketing broadcasts and campaigns
bounce.example.com — bounce return-path (set in ESP)
```

Reputation is per-subdomain. Pre-warm each independently if you're moving senders.

## §3 Domain Authentication

### 3.1 SPF
TXT record on each sending subdomain authorising the ESP's sending IPs.
```
notify.example.com.   TXT   "v=spf1 include:_spf.mtasv.net include:amazonses.com -all"
mail.example.com.     TXT   "v=spf1 include:mailgun.org -all"
```

### 3.2 DKIM
Per-ESP signing key. Most ESPs generate a CNAME or TXT record per sender.
```
ksubdomain._domainkey.notify.example.com.   CNAME   ksubdomain.dkim.postmarkapp.com.
```

Rotate annually. Both old and new keys live in DNS during rotation to avoid downtime.

### 3.3 DMARC
On the **organisational domain** (root), aligned with SPF/DKIM.
```
_dmarc.example.com.   TXT   "v=DMARC1; p=quarantine; rua=mailto:dmarc-rua@example.com; ruf=mailto:dmarc-ruf@example.com; pct=100; sp=quarantine; aspf=r; adkim=r"
```

Phases:
1. `p=none; rua=...` — monitoring only; collect 2 weeks of reports.
2. `p=quarantine; pct=10` → ramp `pct` up over 4-6 weeks.
3. `p=quarantine; pct=100` → live.
4. `p=reject` after 60-90 days of clean reports.

DMARC reporting tool: Postmark DMARC monitoring, Valimail, dmarcian.

### 3.4 BIMI
Optional but trust-boosting once DMARC is `p=quarantine`+ enforced. Publishes logo to inbox (Gmail/Yahoo/Apple Mail).
```
default._bimi.example.com.   TXT   "v=BIMI1; l=https://example.com/bimi-logo.svg; a=https://example.com/bimi-vmc.pem"
```
Requires a Verified Mark Certificate (VMC) — $1500+/year. Worth it for B2C / consumer-facing SaaS; not essential for B2B.

## §4 ESP Selection

| Use case | Recommended | Why |
|---|---|---|
| **Transactional (receipts, OTP, password reset)** | **Postmark** | Best inbox placement + speed; structured templates; great deliverability tools |
| **High-volume transactional cost-sensitive** | **AWS SES** | Cheapest at scale; need to roll own templating + suppression |
| **Mid-volume transactional + simple marketing** | **SendGrid** or **Mailgun** | Established, OK deliverability, broader feature set |
| **Lifecycle automation (event-driven)** | **Customer.io** or **Braze** or **Iterable** | Event-driven, branched workflows, multi-channel (email + SMS + push) |
| **Marketing broadcasts + simple automation** | **MailerLite** / **ConvertKit** / **Drip** / **Mailchimp** | Lower learning curve, broadcast-focused |
| **Developer-friendly transactional** | **Resend** | Modern API, easy DX, good for startups |
| **Embedded in CRM** | **HubSpot Email** / **Salesforce Marketing Cloud** | If CRM is already source of truth |

**Default SaaS stack:** Postmark (transactional) + Customer.io (lifecycle) — or AWS SES + Customer.io if cost matters at scale.

## §5 The Event Bridge

Pattern:
```
Product app
    → emits event to bus (Kafka / Kinesis / SQS / EventBridge / webhook)
        → Transactional sender (Postmark / SES) for receipt-style emails directly triggered
        → Lifecycle automation (Customer.io / Braze) for delayed / branched flows
        → Warehouse (mirror for analytics + revenue attribution)
        → CRM (HubSpot / Salesforce) for sales/CS visibility
```

Event contract:
```json
{
  "event_id": "evt_2026_05_11_abc123",
  "event_type": "user.signed_up",
  "occurred_at": "2026-05-11T10:23:00Z",
  "tenant_id": "ten_456",
  "user_id": "usr_789",
  "user_email": "alice@example.com",
  "properties": {
    "plan": "trial-pro",
    "acquisition_channel": "google_organic",
    "signup_source": "web"
  },
  "idempotency_key": "user_789_signed_up"
}
```

Idempotency at every consumer — replay must not duplicate sends.

## §6 Suppression List

**Central, durable, ESP-independent.** Survives ESP migrations.

```sql
CREATE TABLE email_suppressions (
    id            BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    email_hash    CHAR(64) NOT NULL,         -- SHA-256 of normalised email (GDPR-friendly)
    email         VARCHAR(255),              -- nullable; can be wiped on GDPR delete
    category      ENUM('hard_bounce','complaint','unsubscribe_marketing','unsubscribe_lifecycle','unsubscribe_all','gdpr_erasure','admin') NOT NULL,
    tenant_id     BIGINT UNSIGNED,           -- nullable: NULL = global suppression
    source        VARCHAR(64),               -- 'postmark_webhook', 'user_action', 'admin'
    reason        TEXT,
    suppressed_at DATETIME NOT NULL,
    UNIQUE KEY uq_hash_category_tenant (email_hash, category, tenant_id)
);
```

Send check:
```python
def can_send(email, tenant_id, category):
    suppression = SuppressionList.lookup(
        email_hash=hash(email),
        tenant_id=tenant_id,
        category_chain=expand_categories(category)
    )
    return suppression is None
```

`expand_categories` includes broader categories: a `marketing` send checks for `unsubscribe_marketing`, `unsubscribe_all`, `complaint`, `hard_bounce`, `gdpr_erasure`.

## §7 Feedback Loops

Every ESP exposes webhooks for delivery events:
- `delivered`
- `bounce` (hard / soft)
- `complaint` (FBL from inbox provider)
- `unsubscribe`
- `open` (pixel)
- `click`

Pattern:
```
ESP webhook → signed verify → enqueue → consumer:
  - bounce.hard → suppression_list += {email, hard_bounce}
  - bounce.soft x3 → suppression_list += {email, hard_bounce}
  - complaint    → suppression_list += {email, complaint}
                  → audit + investigate (often indicates marketing in transactional)
  - unsubscribe  → suppression_list += {email, unsubscribe_<category>, tenant_id?}
  - delivered/open/click → warehouse for analytics
```

## §8 Deliverability Monitoring

Dashboards:
- **Send volume** per category per day.
- **Bounce rate** rolling 7-day; alert > 2%.
- **Complaint rate** rolling 7-day; alert > 0.1%.
- **Inbox placement rate** via seed-list (GlockApps, Mailtrap inbox placement).
- **DMARC report ingestion** — domains spoofing you; misalignments.
- **Top failing recipients / domains** (Gmail temp-block, Yahoo greylist).

Alerts:
- Bounce or complaint rate above threshold.
- DMARC failures from a domain that should be aligned.
- Sender score (SenderScore.org) drop.

## §9 Consent Model (Multi-Tenant Nuance)

Three consents per user-per-tenant:
- **Transactional** — implicit, cannot opt out (legal need).
- **Lifecycle (product)** — implicit on signup; per-category opt-out.
- **Marketing (broadcast)** — explicit opt-in (GDPR); easy opt-out.

**Multi-tenant subtlety:** a user belongs to multiple tenants. Unsubscribing from one tenant's marketing must not stop the other tenants' marketing. Store `tenant_id` on suppression rows; global suppression only on GDPR erasure or hard bounce.

## §10 Anti-Patterns

- **No DKIM rotation plan** — single key, never rotated, becomes a liability.
- **Mixed transactional + marketing on one subdomain** — one viral newsletter complaint thread tanks transactional.
- **Suppression list only inside the ESP** — switching ESPs loses years of unsubscribe history.
- **Per-tenant unsubscribe missing** — global unsubscribe kills lifecycle for tenants the user is still active in.
- **Webhook handler not idempotent** — replay creates duplicate suppressions or skipped sends.
- **No DMARC report monitoring** — domain spoofing goes unnoticed.
- **First big send from a fresh IP without warmup** — reputation tanks immediately.
- **Marketing email lacks `List-Unsubscribe` header** — Gmail/Yahoo penalise; some now require RFC 8058 one-click unsubscribe.

## §11 Read Next

- `tabler-email-templates` — the HTML templates this infrastructure ships.
- `saas-lifecycle-email-orchestration` — the sequences (welcome, behavioral, retention, etc.) built on top.
- `subscription-billing` — billing events that trigger transactional emails.
- `saas-tenant-data-portability-and-erasure` — GDPR cascade through the suppression list.
- `observability-monitoring` — emit deliverability metrics into the central observability stack.
