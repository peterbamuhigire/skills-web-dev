# Phase 06: Mobile & PWA Completeness

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Close the Android AI/ML gap (achieving parity with `ios-ai-ml`), add offline-first PWA capability for East Africa's variable connectivity, and extend `ios-ai-ml` to cover Apple Intelligence APIs.

**Architecture:** Two new skill directories (`android-ai-ml`, `pwa-offline-first`) plus an enhancement pass on `ios-ai-ml`. PWA patterns are calibrated for low-bandwidth environments (Workbox + IndexedDB + background sync). Android AI covers on-device ML via ML Kit, TFLite, and Gemini Nano.

**Tech Stack:** ML Kit, TensorFlow Lite, MediaPipe, Gemini Nano (Android 14+), Workbox, Service Workers, IndexedDB/Dexie.js, Web App Manifest, Cache API, Background Sync API, Apple Intelligence (iOS 18+).

---

## Dual-Compatibility Contract

Every `SKILL.md` must include:
```
Use When → Do Not Use When → Required Inputs →
Workflow → Quality Standards → Anti-Patterns → Outputs → References
```

Frontmatter:
```yaml
metadata:
  portable: true
  compatible_with: [claude-code, codex]
```

Platform Notes only. Validate after every write:
```bash
python -X utf8 skill-writing/scripts/quick_validate.py <skill-directory>
```

---

## Task 1: Create `android-ai-ml` skill

**Files:**
- Create: `android-ai-ml/SKILL.md`
- Create: `android-ai-ml/references/ml-kit-tasks.md`
- Create: `android-ai-ml/references/tflite-custom-models.md`
- Create: `android-ai-ml/references/gemini-nano-on-device.md`

**Step 1:** Write `android-ai-ml/SKILL.md` covering:

- Decision tree: ML Kit (pre-trained, fast setup) vs. TFLite (custom model) vs. Gemini Nano (generative, on-device) vs. cloud API (unlimited, network-dependent)
- ML Kit tasks: text recognition (OCR), barcode scanning, face detection, language ID, translation, smart reply, entity extraction — use cases for each in SaaS apps
- ML Kit setup: `com.google.mlkit` dependency, task client lifecycle, Kotlin coroutines integration
- TensorFlow Lite: `.tflite` model loading, `Interpreter` API, input/output tensor binding, GPU delegate for acceleration, model quantisation trade-offs
- MediaPipe Tasks: pose estimation, hand landmark, object detection — Compose UI integration
- Gemini Nano: `com.google.ai.edge.aicore` (Android AICore), `GenerativeModel` in Kotlin, availability check (`isAvailable()`), streaming response in Compose UI
- Privacy: on-device processing advantages, what data never leaves the device, user consent for ML features
- Performance: model warm-up on app start, background model loading, battery and thermal impact

Anti-Patterns: blocking the main thread with inference, loading models from network on first use, not handling `ModelNotDownloadedException`, ignoring thermal throttling.

**Step 2:** Write `references/ml-kit-tasks.md` — Kotlin code examples for OCR, barcode scanning, language ID, entity extraction with Compose UI integration.

**Step 3:** Write `references/tflite-custom-models.md` — model quantisation pipeline, Interpreter setup, input/output processing, GPU delegate, benchmark tooling.

**Step 4:** Write `references/gemini-nano-on-device.md` — availability check, `GenerativeModel` setup, streaming coroutine pattern, Compose UI streaming text display, graceful cloud fallback when Nano unavailable.

**Step 5:** Validate and commit.
```bash
python -X utf8 skill-writing/scripts/quick_validate.py android-ai-ml
git add android-ai-ml/
git commit -m "feat: add android-ai-ml skill (ML Kit, TFLite, MediaPipe, Gemini Nano)"
```

---

## Task 2: Create `pwa-offline-first` skill

**Files:**
- Create: `pwa-offline-first/SKILL.md`
- Create: `pwa-offline-first/references/workbox-strategies.md`
- Create: `pwa-offline-first/references/indexeddb-dexie.md`
- Create: `pwa-offline-first/references/background-sync.md`

**Step 1:** Write `pwa-offline-first/SKILL.md` covering:

- Why offline-first for East Africa: typical connectivity patterns, 2G/3G latency, intermittent drops, user expectations
- PWA manifest: `name`, `short_name`, `icons` (192px + 512px), `start_url`, `display: standalone`, `theme_color`, `background_color`
- Service Worker registration: `navigator.serviceWorker.register()`, scope, update lifecycle, `skipWaiting()` + `clients.claim()`
- Workbox strategies: CacheFirst (static assets), StaleWhileRevalidate (API GET), NetworkFirst (user data), NetworkOnly (payments — never cache)
- Cache versioning: `CACHE_NAME` with version suffix, `activate` event cleanup of old caches
- IndexedDB via Dexie.js: schema definition, CRUD, indexes, transactions, sync queue table
- Background Sync: `SyncManager.register()`, `sync` event in service worker, retry with exponential backoff
- Offline UI: `navigator.onLine`, custom `offline` event listener, toast notification, queued action count badge
- Install prompt: `beforeinstallprompt` event, deferred prompt, custom install button

Anti-Patterns: caching POST requests without idempotency, not cleaning old caches on activation, showing stale prices/inventory from cache without staleness indicator, caching authentication tokens in Cache API (use secure storage instead).

**Step 2:** Write `references/workbox-strategies.md` — Workbox config for a Next.js SaaS app: asset precaching, API route strategies, cache name conventions, Workbox window for update notifications.

**Step 3:** Write `references/indexeddb-dexie.md` — Dexie schema for offline SaaS: `outbox` table (queued mutations), `cache` table (read-through), conflict resolution strategy (last-write-wins vs. server-authoritative).

**Step 4:** Write `references/background-sync.md` — full sync queue implementation: action serialisation, dequeue on connectivity restore, duplicate detection with idempotency keys, failure escalation to user notification.

**Step 5:** Validate and commit.
```bash
python -X utf8 skill-writing/scripts/quick_validate.py pwa-offline-first
git add pwa-offline-first/
git commit -m "feat: add pwa-offline-first skill (Workbox, IndexedDB, background sync, East Africa patterns)"
```

---

## Task 3: Enhance `ios-ai-ml`

**Files:**
- Modify: `ios-ai-ml/SKILL.md`
- Create: `ios-ai-ml/references/apple-intelligence-apis.md`

**Step 1:** Read `ios-ai-ml/SKILL.md` in full before editing.

**Step 2:** Add **Apple Intelligence (iOS 18+)** section to SKILL.md:
- Writing Tools: `UITextView` integration, custom actions via `UITextSelectionDisplayInteraction`
- Image Playground: `ImagePlaygroundViewController`, generating images in SwiftUI
- Siri integration: App Intents framework, `AppIntent` protocol, parameter resolution
- On-device LLM (Foundation Models framework, where available): availability check, privacy guarantee, streaming in SwiftUI
- Privacy model: what runs on-device vs. Private Cloud Compute, how to communicate to users

**Step 3:** Write `references/apple-intelligence-apis.md` — SwiftUI code examples for each API with iOS 18 availability guards and graceful fallback for iOS 17 and below.

**Step 4:** Validate and commit.
```bash
python -X utf8 skill-writing/scripts/quick_validate.py ios-ai-ml
git add ios-ai-ml/
git commit -m "feat: enhance ios-ai-ml — Apple Intelligence APIs (iOS 18), on-device LLM, Siri intents"
```

---

## Success Gate

- [ ] `android-ai-ml` passes validator, ≤ 500 lines, portable metadata present — achieves parity with `ios-ai-ml`
- [ ] `pwa-offline-first` passes validator, ≤ 500 lines, portable metadata present
- [ ] `ios-ai-ml` still passes validator after enhancement
- [ ] PWA skill explicitly addresses low-bandwidth East Africa patterns

---

## Reading Material

| Priority | Resource | Format | Cost | Unlocks |
|----------|----------|--------|------|---------|
| 1 | Android ML Kit guide | Free (developers.google.com/ml-kit) | Free | `android-ai-ml` ML Kit sections |
| 2 | TensorFlow Lite Android guide | Free (tensorflow.org/lite/android) | Free | TFLite inference patterns |
| 3 | MediaPipe documentation | Free (developers.google.com/mediapipe) | Free | Real-time vision tasks |
| 4 | Android AICore / Gemini Nano docs | Free (developer.android.com/ai/aicore) | Free | On-device generative AI |
| 5 | Workbox documentation | Free (developer.chrome.com/docs/workbox) | Free | `pwa-offline-first` caching strategies |
| 6 | Dexie.js documentation | Free (dexie.org/docs) | Free | IndexedDB ORM patterns |
| 7 | *Building Progressive Web Apps* — Tal Ater | Book | ~$40 | PWA concepts and offline patterns |
| 8 | Apple Intelligence documentation | Free (developer.apple.com) | Free | `ios-ai-ml` Apple Intelligence extension |

**Read first:** Android ML Kit guide (comprehensive, free) then Workbox docs. Buy *Building Progressive Web Apps* for the PWA conceptual foundation.

---

*Next → `phase-07-library-maintenance.md`*
