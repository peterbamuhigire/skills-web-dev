# Email Deliverability — Deep Dive

The infrastructure that gets your email into the inbox instead of the spam folder. The single largest hidden cost in SaaS email — bad deliverability silently kills lifecycle revenue.

## The Four DNS Records

### SPF (Sender Policy Framework)
Authorizes which IPs / ESPs can send mail on behalf of a domain.

```
notify.example.com.   TXT   "v=spf1 include:_spf.mtasv.net include:amazonses.com -all"
```

- One SPF record per subdomain (DNS does not allow merging).
- `-all` = hard fail; receivers reject unauthorized senders.
- 10 DNS lookup limit — `include:` mechanisms count.
- SPF alone does not survive forwarding; DKIM does.

### DKIM (DomainKeys Identified Mail)
Cryptographic signature on each email. Receiver verifies via DNS-published public key.

```
ksubdomain._domainkey.notify.example.com.   CNAME   ksubdomain.dkim.postmarkapp.com.
```

- Sign with 2048-bit keys (1024 is being phased out).
- Rotate keys annually; publish both old and new during transition.
- DKIM survives forwarding (unlike SPF) — required for forwarded mail to authenticate.

### DMARC (Domain-based Message Authentication, Reporting & Conformance)
Tells receivers what to do if SPF/DKIM fail; also tells receivers where to send reports.

```
_dmarc.example.com.   TXT   "v=DMARC1; p=quarantine; rua=mailto:dmarc-rua@example.com; ruf=mailto:dmarc-ruf@example.com; pct=100; sp=quarantine; aspf=r; adkim=r; fo=1"
```

Phases:
1. `p=none; rua=...` — monitor only; 2-week minimum.
2. `p=quarantine; pct=10` → ramp pct: 25 → 50 → 100 over 4-6 weeks.
3. `p=reject; pct=100` — fully enforced.

Tools that ingest DMARC RUA reports:
- Postmark DMARC monitor (free)
- dmarcian
- Valimail
- EasyDMARC

### BIMI (Brand Indicators for Message Identification)
Once DMARC is `p=quarantine`+, you can publish a logo for the inbox.

```
default._bimi.example.com.   TXT   "v=BIMI1; l=https://example.com/bimi-logo.svg; a=https://example.com/bimi-vmc.pem"
```

Requires:
- SVG logo (Tiny PS profile, square).
- Verified Mark Certificate (VMC) — $1500+/year (DigiCert, Entrust).
- Helps Gmail/Yahoo/Apple Mail show your logo. Trust-boost.

## Sender Reputation

Maintained per sending IP + sending domain. Receivers (Gmail, Yahoo, Microsoft, Apple) score you.

### Building it
- **Warmup**: gradually ramp send volume on a new IP/domain. Start at 50/day, double every other day, cap at expected daily volume over 4-6 weeks.
- **Engagement signals**: high open rates, high click rates, low complaint rates push reputation up.
- **Consistency**: spikes from 100/day to 100,000/day look like a hijacked sender.

### Damaging it
- High bounce rate (> 2% rolling 7d).
- High complaint rate (> 0.1% rolling 7d).
- Spam-trap hits (purchased lists or scraped emails).
- Sudden volume spikes.
- Sending to long-inactive recipients.

## Bounces

| Type | Action |
|---|---|
| Hard bounce (553, 550, 511) | Immediately suppress; never retry |
| Soft bounce (421, 451, 4xx) | Retry 3-5 times with backoff; suppress if persistent |
| Block (mailbox provider blocked you) | Investigate; may need to contact provider postmaster |

## Complaints (FBL — Feedback Loop)

Mailbox providers expose Feedback Loops — when a recipient hits "Spam", you receive an automated notification.

- Sign up for FBL with: Yahoo, Microsoft, AOL, Comcast, USA-CDX, La Poste.
- Gmail does not have an FBL; you get aggregate stats via Postmaster Tools instead.
- Every FBL complaint → immediately add to suppression list. Investigate why (often: marketing in transactional, or no-consent send).

## Inbox Placement

Even with everything green, mail can land in Spam. Monitor:
- **Seed lists**: GlockApps, Litmus, Mailtrap — send test emails to seed addresses; report on placement per provider.
- **Postmaster Tools**: Google, Yahoo, Microsoft give domain-level inbox placement stats.
- **Sender Score**: SenderScore.org — IP-level reputation 0-100.

Target: > 95% inbox placement across major providers.

## Subdomain Strategy

Critical for reputation isolation:
- `app.example.com` — the product. **Never send mail from this**.
- `auth.example.com` — auth-only emails (verify, MFA, security). Highest trust, smallest volume.
- `notify.example.com` — transactional + lifecycle product emails.
- `mail.example.com` or `news.example.com` — marketing.
- `bounce.example.com` — return-path / bounce-handling (set in your ESP).

Each has its own SPF + DKIM + reputation. A marketing-send burst that triggers complaints poisons only `mail.example.com`, leaving transactional `notify.example.com` clean.

## ESP-Specific Notes

| ESP | Strength | Watch out |
|---|---|---|
| **Postmark** | Best transactional inbox placement; great deliverability tools | Pricier per email |
| **AWS SES** | Cheap at scale | Sandbox mode by default; reputation building is on you |
| **SendGrid** | Mature; broad features | Shared IP reputation can be poor on lower tiers |
| **Mailgun** | Good API; cleanup tools | Mid-tier deliverability |
| **Resend** | DX-friendly modern | Smaller market history |
| **Customer.io** | Best automation/segmentation | Bring your own deliverability via SES/SendGrid |
| **Braze / Iterable** | Enterprise-grade automation | Cost |

## DMARC Report Monitoring

DMARC reports (aggregate and forensic) reveal:
- Who is sending mail claiming to be your domain (legit + spoofers).
- Which senders fail SPF/DKIM alignment.
- Which receivers are quarantining/rejecting.

Without monitoring, you don't see spoofing. With monitoring, you can:
- Onboard internal senders (Workday, Greenhouse, Salesforce, Zendesk) into SPF/DKIM.
- Identify legitimate senders failing alignment and fix.
- Identify spoofers and refer to abuse channels.

## List Hygiene

Engagement-based pruning:
- Drop from broadcast lists addresses with no open/click in 90 days.
- Keep them eligible for transactional only.
- Re-engagement campaign before drop — sometimes recovers 5-10%.

Email validation services (NeverBounce, ZeroBounce, Kickbox):
- Run lists through them before importing to ESP.
- Catches typos (`@gnail.com`), defunct addresses, role accounts.
- Costs pennies per address.

## Anti-Patterns

- One SPF record with 12 `include:`s blowing the lookup limit.
- DKIM key never rotated; same since 2017.
- DMARC stuck at `p=none` indefinitely — no enforcement, anyone can spoof.
- Marketing burst from the transactional subdomain.
- No FBL signups → complaints invisible.
- No DMARC report ingestion → spoofing invisible.
- New sending IP / domain hits production volume on day 1 → reputation craters.
- Sending to purchased lists → spam-trap hits, blacklisting, permanent reputation damage.

## See Also

- `saas-transactional-email-infrastructure` — overall infrastructure skill.
- `saas-lifecycle-email-orchestration` — sequence design that respects deliverability.
- `tabler-email-templates` — HTML that renders consistently across clients.
