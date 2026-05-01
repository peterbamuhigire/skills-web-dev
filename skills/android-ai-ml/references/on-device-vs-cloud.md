# On-device vs Cloud — Decision Matrix

Companion to `SKILL.md` §7. Synthesis from ML Kit + AICore docs cited in those sections.

## Decision matrix

| Dimension | On-device (ML Kit / LiteRT / Gemini Nano) | Cloud (Gemini API / Anthropic / OpenAI) |
|---|---|---|
| Latency | No network round trip; inference time bounded by device hardware | Network-bound; tens of ms to seconds depending on region |
| Privacy | AICore "doesn't store any record of the input data or the resulting outputs" | Subject to provider data-retention terms |
| Cost | Zero per-call cost after the model is on device | Per-token / per-call cost |
| Model size & freshness | Bounded by device storage; updates ride OS or Play Services | Provider rolls model updates centrally |
| Capability ceiling | Smaller models (Gemini Nano, MobileBERT-class) | Frontier models |
| Offline | Works without connectivity | Fails without network |
| Determinism | Same model build → reproducible | Model rolls under you |
| Battery | Real cost on hot loops (pose, segmentation) | Negligible on-device CPU; radio cost |

## Routing rules of thumb

- On-device for short, latency-critical, privacy-sensitive interactions: barcode scanning, on-screen translation, message proofreading, OCR, message summarisation, tap-to-act entity extraction.
- Cloud for: long-context reasoning, RAG over server-side corpora, anything beyond Gemini Nano's capability ceiling, multi-turn agent loops.
- Hybrid: try on-device first with a 200 ms budget; fall back to cloud on `FeatureNotAvailable`, accuracy threshold miss, or timeout.

## Hybrid fallback ladder

1. AICore feature available? Run on-device.
2. Quality / confidence below threshold? Re-issue to cloud.
3. No connectivity? Show a graceful degraded UI.
4. Cloud timeout (>15 s)? Cancel and surface "try again".

## Telemetry to capture

- Path taken (on-device vs cloud).
- Latency p50/p95.
- Fallback reasons (unavailable, timeout, low confidence).
- Battery impact estimate per session.

Never log prompt or output content for on-device GenAI; the privacy contract is part of the user-facing value.

## Anti-patterns

- Defaulting to cloud "because it's smarter" without measuring whether on-device would meet the bar.
- Defaulting to on-device for reasoning tasks Gemini Nano can't do — silent quality regression.
- Routing the same feature differently across users without telemetry — you'll never debug it.
