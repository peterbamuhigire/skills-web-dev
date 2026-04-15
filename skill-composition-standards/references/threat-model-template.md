# Threat Model Template

Produced by `vibe-security-skill`. Consumed by `api-design-first` (auth model), `deployment-release-engineering` (secret rotation), `observability-monitoring` (security alert rules).

## Template

```markdown
# Threat model — <system or feature name>

**Scope:** <what is in scope; what is not>
**Owner:** <security engineer name>
**Reviewed by:** <staff engineer + product owner>
**Last review:** YYYY-MM-DD

## Assets

What are we protecting?

| Asset | Sensitivity | Who may access |
|---|---|---|
| User credentials (password hashes) | critical | auth service |
| Session tokens | high | auth service, API gateway |
| Payment details | critical (PCI scope) | payment provider only — not stored |
| Order history | medium (PII) | user, support, internal reporting |
| Server-to-server API keys | high | infra services |
| ... | ... | ... |

## Trust boundaries

| Boundary | Left of boundary | Right of boundary | Crossing mechanism |
|---|---|---|---|
| Internet edge | public internet | DMZ (load balancer) | TLS + rate limit |
| DMZ to app | DMZ | app services | mTLS |
| App to DB | app services | data tier | IAM + VPC |
| User session edge | authenticated user | backend | session cookie + CSRF |

## Threats (STRIDE)

Use STRIDE categories. For each, list threats, ratings, and mitigations.

### Spoofing

| Threat | Likelihood | Impact | Risk | Mitigation |
|---|---|---|---|---|
| credential stuffing against login | high | high | H | rate limit + CAPTCHA + breach-password check |
| session token theft via XSS | medium | critical | H | HttpOnly + Secure + SameSite cookies + CSP |
| API key in client bundle | high | critical | H | never ship server keys to client; restrict public keys by referrer/IP |

### Tampering

| Threat | Likelihood | Impact | Risk | Mitigation |
|---|---|---|---|---|
| SQL injection via search param | low | critical | M | parameterised queries; linter rule |
| price tampering via request body | medium | high | H | server recomputes totals; never trust client-sent price |

### Repudiation

| Threat | Likelihood | Impact | Risk | Mitigation |
|---|---|---|---|---|
| user denies placing an order | medium | medium | M | audit log with user id + IP + session; signed request bodies |

### Information disclosure

| Threat | Likelihood | Impact | Risk | Mitigation |
|---|---|---|---|---|
| IDOR (accessing other user's orders) | high | high | H | server-side auth check on every read; not relying on obscurity |
| error messages leak PII | medium | medium | M | error sanitiser middleware; no raw exception text to clients |
| log files contain session tokens | medium | high | H | structured logger with token-scrubbing redactor |

### Denial of service

| Threat | Likelihood | Impact | Risk | Mitigation |
|---|---|---|---|---|
| abuse of expensive endpoint | high | medium | H | per-IP + per-user rate limit; cost-weighted quota |
| zip bomb on upload | low | high | M | size limit on upload; decompression limit; sandbox |

### Elevation of privilege

| Threat | Likelihood | Impact | Risk | Mitigation |
|---|---|---|---|---|
| admin endpoint accessible to normal user | low | critical | M | role check middleware + automated test per admin route |
| JWT forge via weak signing | low | critical | M | asymmetric signing; key rotation; library pinned version |

## Abuse cases

Not defensive — intentional misuse scenarios:

- Scraper extracts product catalogue via public API → mitigation: API quota + Turnstile on first unauth request.
- Fraudster uses stolen cards in checkout → mitigation: 3DS; velocity checks; chargeback monitoring.
- Competitor creates fake accounts for reviews → mitigation: email verification; device fingerprint; moderation.

## Auth/Authz matrix

| Resource | Role: User | Role: Support | Role: Admin | Role: Service |
|---|---|---|---|---|
| /orders (own) | read, write | read | read | read, write |
| /orders (other) | deny | read | read | read |
| /admin/users | deny | deny | read, write | deny |
| /admin/config | deny | deny | write | deny |

Default: deny. A missing cell = deny.

## Secret handling plan

- Storage: Vault / AWS Secrets Manager, accessed at runtime, never in code.
- Rotation: quarterly for API keys; immediately on suspected compromise.
- Access: service identity → secret ARN; audit every read.
- No secrets in logs; logger has a redactor for keys matching `secret|token|key|password`.

## Outstanding mitigations

| Threat | Mitigation plan | Owner | Target date |
|---|---|---|---|
| abuse of expensive endpoint | implement cost-weighted quota | platform team | 2026-05 |
| ... | ... | ... | ... |

## Revision log

| Date | Change | Author |
|---|---|---|
| YYYY-MM-DD | initial | ... |
```

## Rules

1. Every threat has a likelihood × impact = risk rating.
2. Every high-risk (H) threat has a mitigation planned or implemented.
3. Auth/authz matrix is exhaustive — every resource × role combination accounted for.
4. Default = deny. A missing row/column = deny, not allow.
5. Threat model reviewed on major feature changes AND annually.

## Common failures

- **Threat model = list of OWASP Top 10 without system-specific threats.** Generic, not useful.
- **No auth/authz matrix.** Role checks scattered through code; easy to miss one.
- **Impact rated without considering blast radius.** A single-user compromise rated the same as a system-wide compromise.
- **Secrets plan says "use Vault"** but doesn't specify rotation cadence or audit path.
- **Review cadence missing.** Threat model drifts from reality.
