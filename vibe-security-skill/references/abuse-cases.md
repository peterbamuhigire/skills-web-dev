# Abuse Case Catalogue

Parent: [../SKILL.md](../SKILL.md).

Abuse cases are intentional misuse scenarios — not bugs, but features being used against the product. Produced by `vibe-security-skill`, consumed by `advanced-testing-strategy` (abuse tests) and `observability-monitoring` (alert rules).

## Template

Each abuse case captures:

| Field | Content |
|---|---|
| Name | short handle |
| Actor | who performs it and their motive |
| Target | the resource being abused |
| Steps | how the abuse happens |
| Detection | what signal is visible |
| Mitigation | the control that prevents or bounds it |
| Residual risk | what remains once mitigation is in place |

## Catalogue — SaaS common cases

### AC-1 Catalogue scraping

- Actor: competitor or broker.
- Target: public product/pricing API.
- Steps: iterate ids or pagination without auth; export to CSV.
- Detection: sustained high request rate from narrow IP range; low session depth.
- Mitigation: per-IP rate limit + CAPTCHA on first unauth request; Turnstile; product-level decoy records.
- Residual: distributed residential-proxy abuse still possible.

### AC-2 Credential stuffing

- Actor: fraudster with breach-list credentials.
- Target: login endpoint.
- Steps: POST /login in a loop with username/password pairs.
- Detection: high login-failure rate with diverse usernames.
- Mitigation: rate limit per IP and per username; device fingerprint; breach-password check; step-up on risky login (new device, new geo).
- Residual: slow-and-low from residential proxies; addressed by 2FA on account.

### AC-3 Fake account farming

- Actor: competitor or influence operation.
- Target: registration; reviews; ratings.
- Steps: create many accounts via disposable email and residential proxies.
- Detection: many accounts per device fingerprint; emails from disposable domains; high same-content submissions.
- Mitigation: email verification; device fingerprint; phone verification for review privilege; rate limit per device; moderation queue.
- Residual: sophisticated farms still produce some noise.

### AC-4 Payment fraud

- Actor: carder using stolen cards.
- Target: checkout.
- Steps: test-charge many cards; settle on working ones; chargeback.
- Detection: high rate of failed auth; unusual BIN distribution; mismatched IP vs billing country.
- Mitigation: 3D Secure; velocity checks (cards per device, cards per hour); AVS and CVV checks; integration with fraud scoring.
- Residual: 3DS-approved fraud still occurs; chargeback monitoring needed.

### AC-5 Coupon / referral abuse

- Actor: deal hunter or fraud ring.
- Target: promotion code endpoint.
- Steps: create multiple accounts; redeem new-user bonuses; self-referrals.
- Detection: same device fingerprint; same payment instrument across accounts; same delivery address.
- Mitigation: per-device redemption limit; link coupons to payment instrument or delivery address; manual review above a spend threshold.
- Residual: distributed farms bypass device limits.

### AC-6 Resource exhaustion on expensive endpoint

- Actor: abusive user or competitor.
- Target: search, export, AI-inference, report generation.
- Steps: hammer the expensive endpoint; cost the vendor money.
- Detection: per-user resource usage spike; high p99 latency; vendor bill spike.
- Mitigation: cost-weighted quota (tokens, seconds, rows), not request count; circuit breaker; vendor budget cap; per-plan ceilings.
- Residual: per-user-within-quota abuse still noisy; addressed by per-tenant billing.

### AC-7 Upload-based attack

- Actor: attacker uploading hostile files.
- Target: file upload endpoint.
- Steps: upload SVG with script; zip bomb; polyglot files; executables in image types.
- Detection: upload triggers anti-virus; decompression runs long; file magic-bytes mismatch.
- Mitigation: magic-byte validation (not Content-Type); file-size and decompression limits; sandboxed parsing; separate storage domain; AV scan.
- Residual: zero-day parser vulnerabilities.

### AC-8 Data export abuse (exfiltration by insider)

- Actor: employee or compromised account with legitimate access.
- Target: any data they can legitimately read.
- Steps: bulk export via admin tooling.
- Detection: unusual export volume; export at unusual hour; access pattern deviates from role norm.
- Mitigation: export rate limit per operator; export audit log; JIT access with ticket reference; DLP on egress.
- Residual: small-volume exfiltration remains hard to detect.

### AC-9 Password reset enumeration

- Actor: attacker confirming whether an email is registered.
- Target: password reset endpoint.
- Steps: POST /password-reset with email; compare response.
- Detection: high rate of unique-email resets from a single source.
- Mitigation: constant-time response (same message whether the email exists or not); rate limit; CAPTCHA.
- Residual: side-channel (email delivery latency) — low severity.

### AC-10 Webhook replay

- Actor: attacker who captured a legitimate webhook.
- Target: webhook endpoint.
- Steps: replay the signed payload.
- Detection: duplicate event ids.
- Mitigation: timestamp window in signature verification (Stripe rejects > 5 min by default); idempotency table keyed by provider event id.
- Residual: replay within the timestamp window if event id not idempotently handled.

### AC-11 Admin-action impersonation

- Actor: attacker with a stolen admin session.
- Target: tenant data, user records, billing.
- Steps: legitimate admin API calls from an illegitimate session.
- Detection: new device/geo for an admin account; bulk-change burst; privilege-sensitive action outside business hours.
- Mitigation: step-up auth on admin actions (WebAuthn); admin session short lifetime; admin audit log with notifications.
- Residual: admin with social-engineered step-up still possible.

### AC-12 Referer / Origin bypass in CORS

- Actor: XSS-adjacent attacker leveraging misconfigured CORS.
- Target: authenticated API.
- Steps: trick user into visiting attacker site; abuse permissive CORS.
- Detection: logs show cross-origin request succeeding from unexpected Origin.
- Mitigation: strict allow-list of origins; no `Access-Control-Allow-Origin: *` on authenticated routes; `Access-Control-Allow-Credentials` only on trusted origins.
- Residual: same-site attackers.

## How to build your catalogue

1. Walk the critical-flow table. For each flow, ask "how could a competent adversary abuse this?"
2. For each abuse case, name the detection signal and the mitigation.
3. Hand the detection signals to `observability-monitoring` as alert inputs.
4. Hand the abuse cases to `advanced-testing-strategy` as abuse tests.
5. Review quarterly and after every major feature change.

## Common failures

- Cases written as generic ("someone might scrape us") without concrete steps.
- No detection signal → the mitigation exists but nobody knows when it fires.
- Mitigation listed but not implemented, with no target date.
- No residual-risk note → the team believes the case is "solved" when it is only bounded.
