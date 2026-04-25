# Event Schema Registry

The schema registry is the source of truth for every event in the pipeline. Every event name appears once. Every property has a declared type. Breaking changes require a new event name, not silent mutation.

## Standard Event Envelope

Every event, regardless of name, carries this envelope:

```json
{
  "event_name": "activation_achieved",
  "event_version": "1.0.0",
  "event_timestamp": "2026-04-25T14:22:31.417Z",
  "ingested_timestamp": "2026-04-25T14:22:32.001Z",
  "user_id": "usr_01HV7D2N...",
  "anonymous_id": "anon_6e2f...",
  "session_id": "sess_01HV7D...",
  "event_properties": {
    "time_to_activate_seconds": 4127,
    "activation_path": "checklist"
  },
  "context": {
    "device_type": "web",
    "os": "macOS 14.4",
    "app_version": "2026.04.18",
    "locale": "en-UG",
    "ip_country": "UG"
  }
}
```

## Naming Conventions

- Pattern: `verb_noun` in `snake_case`.
- Verb is past tense: `signed_up`, `completed`, `achieved`, `clicked`, `viewed`, `triggered`.
- Noun is the thing the verb acted on.
- Good: `user_signed_up`, `onboarding_step_completed`, `subscription_upgraded`.
- Bad: `signup` (no verb), `UserSignUp` (wrong case), `user_signs_up` (wrong tense), `click` (verb without noun).

## Versioning

- Every event has an `event_version` using semver.
- **Patch** (`1.0.0 → 1.0.1`) — documentation only.
- **Minor** (`1.0.0 → 1.1.0`) — additive property. Consumers that ignore unknown fields keep working.
- **Major** (`1.0.0 → 2.0.0`) — breaking change (renamed property, changed type, removed property). **Do not bump major — create a new event name instead.**

## Schema Evolution Rules

| Change | Allowed? | Action |
|---|---|---|
| Add new optional property | Yes | Minor version bump |
| Add new required property | No | Create new event name |
| Rename a property | No | Create new event name |
| Change property type (int to string) | No | Create new event name |
| Tighten an enum (remove a value) | No | Create new event name |
| Widen an enum (add a value) | Yes | Minor version bump; document the new value |
| Remove a property entirely | Deprecate first | Mark deprecated for 90 days, then drop |
| Change semantic meaning without renaming | Never | This is the worst anti-pattern; produces invisible metric drift |

## Property Type Declarations

Every property in the registry declares type, nullability, and example. Common types:

- `string` — unbounded text; hash/tokenise if PII-suspect.
- `string_id` — opaque identifier with no PII; indexable.
- `int` — integer; specify unit in the property name (`time_to_activate_seconds`, not `time_to_activate`).
- `float` — floating point; specify unit.
- `bool` — true/false.
- `enum<A,B,C>` — closed set of string values; widening requires a minor version bump.
- `timestamp_iso8601` — UTC, millisecond precision.

## Registry File Shape

One file per event under `schemas/events/`:

```yaml
event_name: activation_achieved
event_version: 1.2.0
owner_team: product
description: User reached the activation moment within the 7-day activation window.
business_question: What fraction of signups reach activation within 7 days?
properties:
  time_to_activate_seconds:
    type: int
    required: true
    unit: seconds
    example: 4127
  activation_path:
    type: enum<checklist, template, tour, unknown>
    required: true
    example: checklist
  activation_milestone_count:
    type: int
    required: false
    added_in: 1.2.0
    example: 3
```
