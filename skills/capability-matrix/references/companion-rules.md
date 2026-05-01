# Companion Rules

Decision rules for when each cross-cutting Companion category attaches to whatever matrix row(s) are loaded. These are *advisory defaults* — Claude can still skip a category if the work genuinely doesn't touch it, but the default is to load.

## UX

**Trigger:** the work has any user-facing surface (web page, mobile screen, dashboard, form, even an admin panel).

**Auto-load:**

- `grid-systems` — column math, baseline rhythm, responsive mapping.
- `practical-ui-design` — colour, typography, spacing, buttons, forms.
- `interaction-design-patterns` — behaviour, navigation, layout, actions, data patterns.

**Add as needed:**

- `laws-of-ux`, `ux-psychology`, `cognitive-ux-framework` — when the design needs principled justification.
- `motion-design` — when transitions, micro-interactions, or animation are involved.
- `responsive-design` — when the surface must work across breakpoints.
- `design-audit` — when reviewing existing UI.
- `web-usability-krug` — when the surface is a public-facing web page.
- `ux-principles-101` — for general UX hygiene during scoping.
- `lean-ux-validation` — when validating a feature hypothesis before build.
- `ux-for-ai`, `ai-ux-patterns`, `ai-slop-prevention` — when the surface displays AI-generated output.
- `healthcare-ui-design` — when the surface is clinical or patient-facing.
- `pos-sales-ui-design`, `pos-restaurant-ui-standard` — for POS surfaces.
- `form-ux-design` — when the surface is form-heavy.
- `mobile-reports`, `mobile-report-tables` — for mobile reports and dashboards.

## Content

**Trigger:** the work includes any user-facing copy (button labels, error messages, empty states, marketing copy, blog posts, manuals).

**Auto-load:**

- `content-writing` — copywriting standards.
- `ux-writing` — microcopy and product copy standards.
- `language-standards` — multilingual tone and style standards.

**Add as needed:**

- `east-african-english` — when the audience is East African.
- `blog-writer`, `blog-idea-generator` — when generating blog content.
- `manual-guide` — when writing end-user manuals for ERP modules.
- `it-proposal-writing` — when writing client-facing proposals.
- `technology-grant-writing` — when writing grant applications.

## Security baseline

**Trigger:** the work touches a web app, API, multi-tenant data, authentication, payments, or anything connected to the public internet.

**Auto-load:**

- `vibe-security-skill` — the default web security baseline.

**Add as needed:**

- `web-app-security-audit` — when reviewing an existing web application.
- `php-security` — for PHP-specific work.
- `ios-app-security`, `android-development` — for native mobile.
- `llm-security`, `ai-security` — for AI-powered features.
- `graphql-security` — for GraphQL APIs.
- `cicd-devsecops` — for pipeline hardening.
- `linux-security-hardening`, `network-security` — for self-managed infrastructure.
- `code-safety-scanner` — when scanning an unfamiliar codebase for safety issues.
- `dpia-generator`, `uganda-dppa-compliance` — when handling personal data under Uganda DPPA 2019.

## Release

**Trigger:** the work is shipping to production (always for any non-throwaway change).

**Auto-load:**

- `deployment-release-engineering` — rollout, rollback, migration-safe shipping, post-deploy verification.
- `validation-contract` — to assemble the Release Evidence Bundle.

**Add as needed:**

- `git-collaboration-workflow` — for branch, review, and merge discipline.
- `cicd-pipelines` — when the release runs through CI.
- `app-store-review`, `google-play-store-review` — for mobile releases.
- `sdlc-post-deployment` — for ISO/IEC/IEEE 14764 post-deployment evaluation reports.

## How to combine

Companions stack on top of matrix rows, not in place of them. Order of loading: Foundation (from row) → Implementation (from row) → Validation (from row) → Companions (from this file). When two categories pull the same skill (e.g., `vibe-security-skill` appears in Validation for Web/SaaS and Security baseline for any Companion trigger), load it once.

A skill referenced in both a row and a Companion category is not double-loaded — it just confirms the recommendation.
