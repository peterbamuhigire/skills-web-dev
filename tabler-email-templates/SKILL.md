---
name: tabler-email-templates
description: Use when building transactional or marketing email templates for any app — welcome, confirm-email, magic-link, OTP, invoice, receipt, password reset, security alert, invitation, newsletter, promotions, etc. Ships 80 production HTML email templates (Tabler Emails 3.0) with light + dark variants, mobile-responsive, cross-client tested (Outlook, Gmail, Apple Mail, iOS/Android). Use this instead of hand-rolling MJML or starting from scratch.
---

# Tabler Email Templates

Commercially licensed Tabler Emails 3.0 collection, bundled as a skill so any app in this workspace can generate branded transactional and marketing emails quickly without reinventing responsive HTML email layout.

## When To Use

Trigger this skill whenever an app needs to send HTML email. Common cases:

- account lifecycle: `welcome`, `confirm-email`, `register`, `account-deleted`, `password`, `magic-link`, `otp-code`, `access-token`, `gdpr`
- commerce: `invoice`, `payment`, `order`, `shipped`, `missing-order`, `subscription`, `promo-code`, `offer`, `off-deals`, `promotions`, `promotions-2`, `sale`, `pricing`, `wishlist`, `license`
- engagement: `newsletter`, `blog-post`, `post`, `popular-posts`, `top-comments`, `review`, `featured-photo`, `new-photos`, `last-conversation`, `friend-request`, `message`, `survey`, `survey-emoji`, `valentines-1`, `valentines-2`
- product / ops: `changelog`, `new-app`, `product-available`, `features`, `features-2`, `features-3`, `download`, `progress`, `projects`, `todo`, `activities`, `stats`, `stats-2`, `repo-stats`, `visitors-map`, `uptime-report`, `deployment-failed`, `security-alert`, `domain-configuration`, `help`, `confirmation`, `reminder`, `schedule`, `calendar`, `absence`, `subscribe`, `error`, `empty`
- events / social: `invitation`, `invitation-2`, `event-invitation`, `conference`
- corporate: `company-email`, `collection`
- building blocks: `footer-1`, `footer-2`, `footer-3`, `footer-4`, `ui-colors`, `ui-grid`, `ui-typography`

Full index: `templates/<name>/`.

## Where The Templates Live

```text
tabler-email-templates/
├── SKILL.md
├── LICENSE-tabler.txt
└── templates/
    └── <template-name>/
        ├── source.html            ← light, editable HTML
        ├── source-dark.html       ← dark-mode variant
        ├── compiled.html          ← premailer-inlined, send-ready
        ├── compiled-dark.html
        ├── screenshot.jpg         ← preview (use for picking the right one)
        ├── screenshot-dark.jpg
        ├── screenshot-mobile.jpg
        ├── screenshot-mobile-dark.jpg
        └── assets/                ← self-contained (logo, icons, illustrations, theme.css)
```

Each template is self-contained — `assets/` references are local, so one template can be copied into an app without any shared bundle.

## How To Use From An App

### 1. Pick a template

- Ask the user for the intent (e.g. "receipt", "2FA code", "deployment failure alert") and propose 2–3 candidate template names from the list above.
- Before committing, read the matching `screenshot.jpg` (and `screenshot-dark.jpg` if dark mode matters) so you know the layout you are adopting.
- If the user wants to see options, surface the screenshot paths for preview.

### 2. Copy into the app

Copy the template folder into the app's mail assets directory, e.g.:

```text
<app>/resources/emails/welcome/
<app>/app/Mail/templates/welcome/
<app>/mail/templates/welcome/
```

Always copy `compiled.html` + `compiled-dark.html` + the `assets/` folder as the **send-ready artifact**. Keep `source*.html` only if the team will tweak layout and re-inline later.

### 3. Convert to the app's templating engine

The templates ship as plain HTML. Before sending, convert the editable copy placeholders to the host app's templating engine:

| Stack | Engine | Replace example |
|-------|--------|-----------------|
| PHP (Laravel, custom) | Blade / plain PHP | `Hello John` → `Hello {{ $user->name }}` |
| Node / Next.js | Handlebars, MJML-in-React, `email-templates`, React Email | `Hello John` → `Hello {{name}}` or `{props.name}` |
| Python (FastAPI, Django) | Jinja2 / Django templates | `Hello John` → `Hello {{ name }}` |
| Android (server-rendered) | server-side; do not render in-app | — |
| iOS (server-rendered) | server-side; do not render in-app | — |

Rule: render the final HTML on the server (PHP/Node/Python). Mobile clients should receive the email via the user's mail provider, never render email HTML in-app.

### 4. Swap the brand assets

Replace in `assets/`:

- `sample-logo.png` and `sample-logo-white.png` → the app's logo (keep same pixel dimensions or update the `<img width/height>` in the HTML)
- `sample-download-app-store.png`, `sample-download-google-play.png` → remove if not a mobile app
- update `theme.css` brand colour variables (primary, text, link) if the template uses them
- keep illustration + icon PNGs as-is unless the brand requires new artwork

### 5. Host the images

Email clients must fetch images over HTTPS. Either:

- upload the whole `assets/` folder to the app's public CDN/static bucket and rewrite `src="assets/..."` to absolute URLs, **or**
- inline tiny icons as `data:` URIs (only for < 2 KB sprite-style PNGs; avoid for photos/illustrations because Gmail clips them)

Absolute-URL hosting is the default.

### 6. Inline critical CSS

The bundled `compiled.html` is already premailer-inlined. If you edit `source.html` and need to re-inline:

- Node: `npm i -D juice` → `juice source.html > compiled.html`
- Ruby: `premailer-rails`
- Python: `premailer` package

Never send `source.html` directly — many Outlook versions drop `<style>` blocks.

### 7. Wire to the mailer

Send via the app's existing transactional mail service (SES, Postmark, SendGrid, Resend, Mailgun, SMTP). Set:

- `From` = verified sender of the app brand
- `Reply-To` = support inbox
- text alternative part (`text/plain`) — generate from the HTML, never send HTML-only
- List-Unsubscribe header for marketing templates (`newsletter`, `promotions*`, `offer`, `sale`, `off-deals`, `valentines-*`, `wishlist`)

## Dark Mode

Every template ships a `source-dark.html` / `compiled-dark.html` plus dark illustrations. Two options:

1. **Auto (preferred)** — send only the light `compiled.html`; it already contains the `meta color-scheme` + `prefers-color-scheme` media query so Apple Mail, iOS Mail, and Outlook.com invert correctly.
2. **Forced dark** — send `compiled-dark.html` if the brand uses a fixed dark surface (e.g. developer/ops apps).

Gmail ignores `prefers-color-scheme`. Don't rely on dark mode for legibility; always pass contrast checks on the light variant.

## Accessibility Baseline

Before sending any derived template:

- `<title>` matches the subject line
- every image has a meaningful `alt` attribute (decorative images get `alt=""`)
- minimum 14 px body text, 1.5 line-height (templates already comply)
- CTA buttons have ≥ 44 px tap target (templates already comply)
- colour contrast ≥ 4.5:1 for body, ≥ 3:1 for large text in both light and dark variants
- preview text (first visible text block) under 90 characters summarising the email

## Anti-Patterns

- Do not hand-rewrite layout in `source.html`; prefer swapping text + brand assets and re-inlining.
- Do not reference the shared `images/` folder from the original Tabler zip — it is not bundled here because every template's `assets/` folder is already self-sufficient.
- Do not use CSS features that Outlook drops: flexbox, grid, background images on `<div>`, `transform`, `position`, web fonts beyond the premailer-safe Google Fonts already wired in.
- Do not render emails inside Android/iOS apps — the OS mail client handles it.
- Do not commit customer PII into template snapshots; keep seed data generic.

## License

Tabler Emails is commercial. The included `LICENSE-tabler.txt` is the personal license:

- allowed: unlimited End Products, including ones sold to End Users, for unlimited clients.
- not allowed: redistributing the templates as templates (e.g. open-sourcing this folder, shipping a template marketplace that re-uses them).

When Claude copies a template into an app, the app counts as an End Product and is covered. If this skills repository is ever made public or shared outside the licensee's team, the `templates/` folder must be removed first — the skill can then point back to the original purchase location as a reference instead.

## Quick Decision Guide

```text
User says:                                  → Candidate templates
"new signup confirmation"                   → welcome, confirm-email, register
"verify email"                              → confirm-email, magic-link
"password reset / forgot password"          → password
"2FA / login code"                          → otp-code, magic-link
"payment receipt / invoice"                 → invoice, payment, order
"order shipped"                             → shipped
"subscription renewed / cancelled"          → subscription, account-deleted
"weekly / monthly newsletter"               → newsletter, blog-post, popular-posts
"product update / changelog"                → changelog, new-app, features*
"deploy failed / uptime alert"              → deployment-failed, uptime-report, security-alert
"team / event invitation"                   → invitation, invitation-2, event-invitation
"abandoned cart / promo"                    → promo-code, offer, off-deals, sale, promotions*
"GDPR / data request"                       → gdpr, account-deleted
"empty state notification"                  → empty, reminder, help
"survey / NPS"                              → survey, survey-emoji, review
"company announcement"                      → company-email, collection
```

## Source Path

Original commercial bundle: `F:\Templates & Design Stuff\Tabler\tabler-emails-3.0\` (licensee: Peter Bamuhigire). Re-sync new versions by re-copying the `emails/` folder into `templates/`.
