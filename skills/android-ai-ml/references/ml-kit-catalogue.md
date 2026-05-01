# ML Kit Catalogue & Worked Examples

Companion to `SKILL.md` §1–§2.

## Full API list (developers.google.com/ml-kit, fetched 2026-05-01)

### Vision (each has bundled and Play Services delivery models)

| API | Bundled artifact (illustrative) | Play Services artifact (illustrative) |
|---|---|---|
| Barcode scanning | `com.google.mlkit:barcode-scanning` | `com.google.android.gms:play-services-mlkit-barcode-scanning` |
| Face detection | `com.google.mlkit:face-detection` | `com.google.android.gms:play-services-mlkit-face-detection` |
| Face mesh detection | `com.google.mlkit:face-mesh-detection` (beta) | n/a |
| Text recognition v2 | `com.google.mlkit:text-recognition:16.0.1` | `com.google.android.gms:play-services-mlkit-text-recognition:19.0.1` |
| Image labeling | `com.google.mlkit:image-labeling` | `com.google.android.gms:play-services-mlkit-image-labeling` |
| Object detection and tracking | `com.google.mlkit:object-detection` | `com.google.android.gms:play-services-mlkit-object-detection` |
| Digital ink recognition | `com.google.mlkit:digital-ink-recognition` | n/a |
| Pose detection | `com.google.mlkit:pose-detection` / `pose-detection-accurate` | n/a |
| Selfie segmentation | `com.google.mlkit:segmentation-selfie` | n/a |
| Subject segmentation | `com.google.mlkit:segmentation-subject` | n/a |
| Document scanner | n/a | `com.google.android.gms:play-services-mlkit-document-scanner` |

Always pin versions to the published Maven coordinates at the time of integration; the values above are representative.

### Natural language

- Language identification — `com.google.mlkit:language-id`.
- Translation — `com.google.mlkit:translate` (downloads ~30 MB packs on demand).
- Smart reply — `com.google.mlkit:smart-reply`.
- Entity extraction — `com.google.mlkit:entity-extraction` (~1.5 MB per language).

### GenAI (backed by AICore / Gemini Nano — see §5)

Summarization, Proofreading, Rewriting, Image description, Speech recognition, Prompt.

## Delivery model trade-off (Text Recognition v2 docs, fetched 2026-05-01)

- Bundled: ~4 MB per script architecture; available immediately.
- Play Services: ~260 KB stub; the model "must be downloaded before use".

Decision rule: bundle for critical-path features; Play Services for optional/rare ones.

## Worked examples

### Face Detection

```kotlin
val options = FaceDetectorOptions.Builder()
  .setPerformanceMode(FaceDetectorOptions.PERFORMANCE_MODE_FAST)
  .setLandmarkMode(FaceDetectorOptions.LANDMARK_MODE_NONE)
  .setClassificationMode(FaceDetectorOptions.CLASSIFICATION_MODE_ALL)
  .setMinFaceSize(0.15f)
  .build()
val detector = FaceDetection.getClient(options)
```

Face mesh is a separate client (`FaceMeshDetection`) — 468 landmarks for filters/AR. Liveness: prompt a blink; watch `smilingProbability` + `leftEyeOpenProbability` deltas over ~1 s. Never ship full-landmark mode on low-end devices.

### Barcode Scanning

```kotlin
val scanner = BarcodeScanning.getClient(
  BarcodeScannerOptions.Builder()
    .setBarcodeFormats(Barcode.FORMAT_QR_CODE, Barcode.FORMAT_EAN_13, Barcode.FORMAT_CODE_128)
    .build()
)
scanner.process(input)
  .addOnSuccessListener { barcodes -> barcodes.firstOrNull()?.rawValue?.let(onResult) }
  .addOnCompleteListener { proxy.close() }
```

Set format flags explicitly — scanning all formats is 3–5x slower. Throttle emission with `distinctUntilChanged` so the UI doesn't flicker.

### Language Identification + Translation

```kotlin
val identifier = LanguageIdentification.getClient(
  LanguageIdentificationOptions.Builder().setConfidenceThreshold(0.6f).build()
)
identifier.identifyLanguage(text)
  .addOnSuccessListener { tag -> if (tag != "und") detectedLang = tag }
```

Pair with `Translator`; first use downloads the language pack (~30 MB) — gate on Wi-Fi via `DownloadConditions`. For heavy multilingual workloads use cloud translation.

### Entity Extraction

```kotlin
val extractor = EntityExtraction.getClient(
  EntityExtractorOptions.Builder(EntityExtractorOptions.ENGLISH).build()
)
extractor.downloadModelIfNeeded()
  .onSuccessTask { extractor.annotate(text) }
  .addOnSuccessListener { annotations ->
    annotations.forEach { a ->
      a.entities.forEach { e -> println("${e.type}: ${text.substring(a.start, a.end)}") }
    }
  }
```

Supported types: phone, email, URL, address, flight number, date/time, tracking numbers. Great for tap-to-action chips under a chat message.

## Suspend wrapper for `Task<T>`

```kotlin
suspend fun <T> Task<T>.await(): T = suspendCancellableCoroutine { cont ->
  addOnSuccessListener { cont.resume(it) }
  addOnFailureListener { cont.resumeWithException(it) }
}
```

Use this from any coroutine to bridge ML Kit `Task<T>` into structured concurrency and `Flow`.

## Pre-downloading Play Services modules

Use `ModuleInstallClient` to pre-fetch Play Services models for critical-path features. Verify the current sample on developers.google.com/android/guides/setup at implementation time.
