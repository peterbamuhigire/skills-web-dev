# AICore + Gemini Nano

Companion to `SKILL.md` §5. Sources: developer.android.com/ai/aicore (fetched 2026-05-01).

## What it is

> "An Android system service that enables on-device execution of GenAI foundation models" and "the interface between your app and the Gemini Nano model, managing model updates and safety while leveraging on-device hardware."

## Public surface (via ML Kit GenAI)

- Prompt
- Summarization
- Proofreading
- Rewriting
- Image description
- Speech recognition

There is no raw chat surface — apps consume capability-shaped APIs.

## Privacy contract (verbatim)

> "AICore is built to isolate each request and doesn't store any record of the input data or the resulting outputs after processing them to protect user privacy."

## Latency contract (verbatim)

> "While this removes network latency, inference speed depends on device hardware."

## Availability gating

```kotlin
val features = AICore.getFeatureAvailability(context)
if (features.isAvailable(Feature.SUMMARIZATION)) {
  val model = GenerativeModel(generationConfig { temperature = 0.2f })
  val summary = model.generateContent("Summarise: $longText").text
} else {
  // Fallback to cloud via ai-llm-integration
}
```

Always check at runtime — availability can change after a system update or model rollback. Cache the result for the session, not across launches.

## Device support

The supported-device list moves with each Pixel/Samsung release. Verify the current list on developer.android.com/ai/aicore at publication time and re-verify on every flagship release that touches Gemini Nano. Never hardcode a device allow-list in app code; rely on `getFeatureAvailability()`.

## Common patterns

- Summarisation of long article content offline.
- Proofreading drafts in a notes app without sending text to a server.
- Rewriting suggestions in messaging.
- Image description for accessibility.

## Fallback ladder

1. Try AICore (`getFeatureAvailability` true).
2. On unavailable or timeout (>200 ms warm-up acceptable, >2 s for inference treat as fail), fall back to cloud via `ai-llm-integration`.
3. On no connectivity and no AICore, return a graceful "this feature needs an update" UI.

## Telemetry

Log: feature requested, availability outcome, latency, fallback path taken. Never log the prompt or output text — AICore guarantees privacy and your telemetry must not break it.
