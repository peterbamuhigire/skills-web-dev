# Anti-Patterns Catalog

Each entry describes a concrete failure, the symptom, the root cause, and the fix.

## 1. Over-Instrumentation

- **Failure:** team logs every hover, every scroll tick, every viewport change. Cloud bill triples. Dashboards multiply. No new decisions get made.
- **Symptom:** event volume grows 10x year-over-year while product decisions-per-quarter stays flat.
- **Root cause:** events were added without tying them to business questions.
- **Fix:** impose the rule — every event must map to a row in the instrumentation plan with a specific business question and an owning team. Run a quarterly review; deprecate events with zero queries in 90 days.

## 2. Inconsistent Identifiers

- **Failure:** signup funnel shows 80% visit-to-signup conversion. The actual number is 4%. The discrepancy is because anonymous visitors use a GUID cookie on page A, a different GUID cookie on page B, and only get a `user_id` after signup — so the "visitors who signed up" count double-counts and the denominator is wrong.
- **Symptom:** implausibly high conversion rates; funnels that only work end-to-end when the user is already logged in.
- **Root cause:** no canonical identifier hierarchy.
- **Fix:** adopt `user_id > anonymous_id > device_id` with explicit stitching at login. At login, issue a `user_identified` event that maps the prior anonymous_id to the user_id. Rebuild all funnel queries to follow the stitch.

## 3. Logging PII in Event Properties

- **Failure:** engineering warehouse contains user emails, phone numbers, and raw addresses in `event_properties`. A compliance audit flags it; the fix is a 6-month data deletion and reprocessing project.
- **Symptom:** DPPA/GDPR auditor raises a finding; a breach scenario exposes direct user contact details instead of tokenised identifiers.
- **Root cause:** instrumentation authors treated the warehouse as a general data store instead of an engineering-purpose store.
- **Fix:** at ingestion, hash or tokenise any property flagged PII (email, phone, address, payment PAN). Never log payment details at all. Maintain a PII-property allow/deny list enforced at transformation.

## 4. Measuring Outputs Without Measuring Absence

- **Failure:** dashboard shows "clicks on the upsell card" rising steadily. Team celebrates. Three months later, discovery that card impressions also rose — click-through rate actually fell.
- **Symptom:** numerator-only metrics; no denominator; cannot compute rates.
- **Root cause:** instrumentation logged the success event but not the impression event.
- **Fix:** for every conversion event, log the upstream exposure event. `upsell_card_clicked` requires `upsell_card_viewed`. For every feature usage event, log the feature-available event.

## 5. Dashboards Without Owners

- **Failure:** growth team inherits 40 dashboards from a departed PM. Six months later, 22 are pointing at deprecated events, 8 have broken queries, and the exec team is citing numbers from a dashboard with a broken metric definition.
- **Symptom:** "why is this number different from last quarter?" with no one to answer.
- **Root cause:** dashboards were created without an ownership contract.
- **Fix:** every dashboard has a named owner and a last-reviewed date. Dashboards not reviewed in 90 days auto-archive. The BI tool must enforce this (Metabase, Looker, Superset all support ownership fields).

## 6. Alert Fatigue

- **Failure:** on-call receives 50 alerts per day. Real outages are missed because the Slack channel is noise. SRM alerts get ignored, experiments ship on broken platforms.
- **Symptom:** mean time to acknowledge real incidents exceeds 30 minutes.
- **Root cause:** alerts were created for every possible anomaly with no tiering.
- **Fix:** three tiers — page (the five pipeline-health alerts), email (warnings), dashboard-only (informational). Any alert that pages more than 3 times per week without a real incident gets retuned or demoted. Ownership of the alert catalog belongs to the data platform lead, not the analysts who requested the alerts.
