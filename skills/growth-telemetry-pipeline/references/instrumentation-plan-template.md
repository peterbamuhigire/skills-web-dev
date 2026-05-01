# Instrumentation Plan Template

Every event in the pipeline must map to a business question. This template makes the mapping explicit. If a proposed event does not fit a row in this table, it does not get instrumented.

## Header

- **Product:**
- **North Star metric:**
- **Author:**
- **Review date:**

## Question-Driven Table

| Business question | Required event | Event name | Key properties | Trigger location | Owning team |
|---|---|---|---|---|---|
| What fraction of signups reach activation within 7 days? | User hit the activation moment | `activation_achieved` | `user_id`, `time_to_activate_seconds`, `activation_path` | Server-side after the activation condition is met | Product |
| Which acquisition channels produce the highest day-30 retention? | User signed up with attribution | `user_signed_up` | `user_id`, `acquisition_channel`, `utm_source`, `utm_campaign`, `referrer_user_id` | Server-side on account creation | Growth |
| Where do users drop off in the onboarding funnel? | User advanced through each step | `onboarding_step_completed` | `user_id`, `step_number`, `step_name`, `time_on_step_ms` | Client-side on step transition, posted to server | Product |
| Do power users differ from light users in feature breadth? | User used a feature | `feature_used` | `user_id`, `feature_name`, `feature_surface`, `count_in_session` | Server-side on feature entry-point | Product |
| Are experiments diluting? | User became eligible for a variant | `experiment_triggered` | `user_id`, `experiment_id`, `variant`, `trigger_type` | Server-side at divergence point | Growth |
| Is the pipeline healthy? | Pipeline stage processed a batch | `pipeline_batch_processed` | `stage`, `row_count`, `lag_ms` | Pipeline internals | Data Platform |

## Rules for New Rows

- Every row must name a specific business question. "Track clicks on the button" is not a question; "Does moving the CTA above the fold increase signup rate?" is.
- Every row must name the owning team. No owner means no maintenance.
- Every row must specify server-side or client-side firing, and if client-side, must describe the server-side persistence.
- Rows are reviewed quarterly. Events with zero queries in 90 days are candidates for deprecation.

## Deprecation Rules

- Mark events deprecated in the schema registry for 90 days before removing instrumentation code.
- Notify dashboard owners listed against the event before deprecation.
- Remove the event from the registry only after 90 days of zero queries and zero dashboard references.
