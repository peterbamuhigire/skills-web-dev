# Embeddable SLA Widget

A widget the tenant embeds in their own admin app or public-facing pages to display the agent SLA status. Two variants: iframe (default) and JS SDK.

## Use Cases

- Enterprise tenant embedding into internal status board.
- B2B tenant displaying trust signal to their own end-customers.
- Status page integration (status.example.com).

## Token-Based Auth

The tenant generates a per-tenant widget token from the admin console. The token is scoped:

```
scopes = ['sla:widget:read']
audience = 'sla-widget'
tenant_id = <tenant>
features = ['support_copilot', 'log_investigator']  # optional subset
ttl_hours = 12
```

Signed with the platform's widget-signing key. Customer rotates by regenerating; revocation list checked at widget render.

## iframe Variant

```html
<iframe
  src="https://app.example.com/sla/widget?token=eyJhbGciOiJFZERTQS...&theme=light"
  width="100%"
  height="240"
  frameborder="0"
  loading="lazy"
></iframe>
```

The iframe URL params:
- `token` — required, signed JWT.
- `theme` — `light` | `dark` | `auto` (default).
- `compact` — `true` | `false`. Compact strips the exclusion strip.
- `feature` — optional; renders single-feature widget.

The iframe renders server-side from cached aggregates. No client JS. Loads ≤ 200ms p95.

### Sample HTML (server-rendered)

```html
<div class="sla-widget" data-theme="light">
  <div class="sla-widget-header">Agent SLA — Pro (class-A)</div>
  <div class="sla-widget-metrics">
    <div class="sla-tile sla-met">
      <div class="label">Resolution rate (30d)</div>
      <div class="value">87%</div>
      <div class="floor">floor 85%</div>
    </div>
    <div class="sla-tile sla-met">
      <div class="label">Irreversible</div>
      <div class="value">0</div>
      <div class="floor">target 0</div>
    </div>
    <div class="sla-tile sla-met">
      <div class="label">TTR p95</div>
      <div class="value">2m 14s</div>
      <div class="floor">≤ 3m</div>
    </div>
  </div>
  <div class="sla-widget-footer">
    Powered by Acme — <a href="...">SLA details</a>
  </div>
</div>
```

CSS is inlined or served from a stable URL with long cache TTL. Total payload ≤ 10KB compressed.

## JS SDK Variant

For dynamic dashboards that need live updates:

```html
<script src="https://app.example.com/sdk/sla-widget.js"></script>
<script>
  AcmeSla.mount('#sla-widget', {
    token: 'eyJ...',
    theme: 'auto',
    refreshSeconds: 300,   // optional; default 600
    onUpdate: (data) => { console.log('sla update', data); },
  });
</script>
<div id="sla-widget"></div>
```

SDK fetches from `/v1/sla/status` (public API) every `refreshSeconds`. SDK file ≤ 40KB minified.

## Widget Data Contract

```typescript
interface SlaWidgetData {
  sla_class: 'class-B' | 'class-A' | 'class-AA' | 'bespoke';
  plan: string;
  features: Array<{
    feature: string;
    metrics: {
      resolution_rate_30d: { value: number, floor: number, status: 'met' | 'at_risk' | 'breach' };
      intervention_rate_30d: { value: number, ceiling: number, status: 'met' | 'at_risk' | 'breach' };
      irreversible_count_30d: { value: number, target: 0, status: 'met' | 'breach' };
      ttr_p95_seconds: { value: number, target?: number, status: 'met' | 'at_risk' | 'breach' | 'advisory' };
      availability_month: { value: number, target: number, status: 'met' | 'at_risk' | 'breach' };
    };
    exclusions_30d: Array<{
      start: string;       // ISO 8601
      end: string;
      kind: string;
      summary: string;
      evidence_url?: string;
    }>;
  }>;
  credits: {
    pending_cents: number;
    last_invoice_cents: number;
    currency: string;
  };
  generated_at: string;
}
```

## Security

- The widget never exposes per-task PII. Only aggregates.
- The token is single-purpose (`sla:widget:read`); cannot read other tenant data.
- Token rotation supported; old tokens revoked at the next widget render after revocation timestamp.
- iframes set `Content-Security-Policy: frame-ancestors *` (the customer chooses where to embed); or per-tenant allow-list of origins for Enterprise.
- Cross-tenant data isolation: every query has `WHERE tenant_id=` enforced at the data layer, not the controller.

## Performance

- Widget data cached at the edge per `(tenant_id, feature_subset)` with 5-minute TTL.
- Cache invalidated on `agent.resolution.*` and `sla.credit.issued` events.
- Median render time ≤ 80ms; p95 ≤ 200ms.

## Branding

Default widget shows "Powered by <Acme>" footer.

For Enterprise tenants on `bespoke` SLA class, this footer is configurable (white-label option in contract). The footer link still leads to a tenant-facing SLA history page hosted by the platform (we don't relocate audit data to the tenant's domain).

## Localization

Widget supports en, fr, es, de, sw at launch. Language inferred from `Accept-Language`; `?lang=xx` override.

## Failure States

If the widget data API is unavailable:

```html
<div class="sla-widget sla-widget-error">
  Agent SLA data is temporarily unavailable. Last known status:
  <a href="https://app.example.com/sla/...">view on Acme</a>.
</div>
```

Last-known cache served up to 24h stale before degrading to error. Customer is never shown a misleading "all green" when the data is missing.

## Audit

Every widget render logs `(tenant_id, token_hash, feature_subset, origin_referrer, generated_at)` to a sampled audit log (10% sample), useful for confirming widget usage and detecting token leakage.

## Tests

- iframe renders in < 200ms with cached data.
- iframe renders correct content under a regenerated token; rejects revoked token.
- SDK refresh interval honored; no thundering herd if many widgets on one page.
- No cross-tenant data leak under any query param manipulation.
- Widget shows correct exclusion summary when in breach window.
