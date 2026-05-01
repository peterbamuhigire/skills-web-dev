---
name: android-ai-ml
description: Use when adding on-device AI/ML to an Android app — ML Kit (vision, NLP, GenAI), LiteRT (formerly TensorFlow Lite) custom-model inference via the CompiledModel API, MediaPipe Tasks, AICore + Gemini Nano, or streaming LLM tokens into Jetpack Compose; covers the bundled-vs-Play-Services delivery trade-off, CPU/GPU/NPU acceleration, on-device vs cloud routing, and Compose lifecycle-safe token streaming.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Android AI/ML (ML Kit, LiteRT, MediaPipe, Gemini Nano)

Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Adding on-device AI features to an Android app (OCR, face, barcode, language, pose, gestures, summarisation).
- Bundling a custom `.tflite`/LiteRT model and running inference with CPU/GPU/NPU acceleration.
- Wiring a MediaPipe Tasks vision solution (e.g. hand landmarker) into a CameraX preview.
- Calling ML Kit GenAI APIs (Summarization, Proofreading, Rewriting, Image Description, Speech Recognition, Prompt) on AICore-capable devices.
- Streaming LLM tokens into a Jetpack Compose UI with lifecycle-safe cancellation.

## Do Not Use When

- The model must run cloud-side only — load `ai-llm-integration`.
- You need iOS Core ML / Vision / NaturalLanguage parity — out of scope for this cohort.
- You need to train a model — this skill is inference-only.

## Required Inputs

Target API level (ML Kit 21+, LiteRT 23+, AICore 14+), accuracy vs latency budget, supported devices, model ownership (Google-hosted ML Kit vs BYOM LiteRT), privacy constraints, APK-size budget (drives bundled vs Play Services delivery), connectivity assumptions (offline-first?).

## Workflow

1. Pick the lowest-effort stack that solves the problem (decision rule in §1).
2. Choose the delivery model — bundled if on the critical path of first use, Play Services if optional and APK size matters (§1, §2).
3. For custom models, convert to LiteRT, quantise, and run via the CompiledModel API with the right `Accelerator` (§3).
4. For real-time video, plug a MediaPipe Tasks result listener into a CameraX `ImageAnalysis` use case (§4).
5. For on-device GenAI on Pixel/Samsung flagships, gate on AICore feature availability and fall back to cloud otherwise (§5).
6. Stream tokens into Compose with `LaunchedEffect` keyed on the prompt so cancellation is automatic (§6).
7. Apply the on-device-vs-cloud routing matrix per feature (§7).
8. Benchmark on a mid-tier target device (e.g. Pixel 6a) — never your flagship.

## Quality Standards

- Inference runs off the main thread (`Dispatchers.Default` or a `CoroutineWorker`).
- Detectors, interpreters, and MediaPipe tasks are singletons — never instantiated per frame.
- Every AI feature has a graceful fallback when the device cannot run it.
- Cloud LLM calls are cancellable and time out at <= 15 s.
- Compose token streams cancel when the composable leaves the composition (rely on `LaunchedEffect`, not raw `GlobalScope`).
- Releases include a benchmark report per target device tier.

## Anti-Patterns

Instantiating ML Kit clients per analyse call; running inference on the UI thread; shipping unquantised custom models (8x bigger APK); enabling full-landmark face mode on low-end devices; mixing GPU and NNAPI without benchmarking; appending streaming tokens into a `mutableStateListOf` without `derivedStateOf`; launching streams from `rememberCoroutineScope` when `LaunchedEffect` would auto-cancel; assuming Gemini Nano is available without `getFeatureAvailability()`.

## Outputs

ML Kit analyser + CameraX pipeline; LiteRT `CompiledModel` wrapper with accelerator selection; MediaPipe Tasks runner for video; AICore availability check + cloud fallback; Compose streaming composable; on-device-vs-cloud routing matrix; per-device benchmark report.

## Evidence Produced

| Category | Artifact | Format | Example |
|---|---|---|---|
| Correctness | Android on-device ML test plan | Markdown covering ML Kit, LiteRT, MediaPipe, and AICore inference paths | `docs/android/ml-tests.md` |
| Performance | On-device inference latency budget | Markdown — per-model latency, memory, battery budgets | `docs/android/ml-perf-budget.md` |
| Release evidence | ML analyser + CameraX pipeline | Kotlin sources | `feature/scan/BarcodeAnalyzer.kt`, `feature/scan/CameraScreen.kt` |
| Release evidence | LiteRT CompiledModel wrapper | Kotlin source + bundled model asset | `ml/Classifier.kt`, `assets/model_int8.tflite` |
| Release evidence | Compose streaming composable | Kotlin source using `LaunchedEffect` keyed on prompt | `ui/StreamedAnswer.kt` |
| Operability | Device benchmark report | Markdown — latency and memory per target device | `docs/ml/benchmarks-2026-04-16.md` |
| Correctness | Golden-output unit tests | Kotlin tests verifying inference against known inputs | `src/test/.../ClassifierTest.kt` |

## References

- Companion skills: `android-development`, `jetpack-compose-ui`, `ai-llm-integration`.
- Deep-dives in this skill:
  - `references/ml-kit-catalogue.md` — full ML Kit API list and bundled-vs-Play-Services notes.
  - `references/litert-inference.md` — CompiledModel, Accelerator selection, quantisation.
  - `references/mediapipe-camerax.md` — MediaPipe Tasks wired to CameraX.
  - `references/aicore-gemini-nano.md` — AICore surface, privacy contract, device gating.
  - `references/compose-streaming.md` — token streaming patterns and pitfalls.
  - `references/on-device-vs-cloud.md` — full decision matrix and routing rules.
- Canonical sources (fetched 2026-05-01):
  - ML Kit — https://developers.google.com/ml-kit
  - ML Kit Text Recognition v2 (Android) — https://developers.google.com/ml-kit/vision/text-recognition/v2/android
  - LiteRT for Android — https://ai.google.dev/edge/litert/android
  - MediaPipe Solutions guide — https://ai.google.dev/edge/mediapipe/solutions/guide
  - AICore — https://developer.android.com/ai/aicore
  - Compose side-effects — https://developer.android.com/develop/ui/compose/side-effects
<!-- dual-compat-end -->

## Overview

Android exposes four on-device AI stacks. Pick the lowest-effort stack that solves the problem — dropping down is expensive; climbing up is cheap.

Cardinal rule: the model is a singleton, inference is off-main-thread, and every AI feature has a fallback.

---

## 1. ML Kit overview — catalogue and delivery models

ML Kit groups on-device APIs into three families.

- Vision: Barcode scanning, Face detection, Face mesh detection, Text recognition v2, Image labeling, Object detection and tracking, Digital ink recognition, Pose detection, Selfie segmentation, Subject segmentation, Document scanner.
- Natural language: Language identification, Translation, Smart reply, Entity extraction.
- GenAI (backed by Gemini Nano via AICore): Summarization, Proofreading, Rewriting, Image description, Speech recognition, Prompt.

Source: developers.google.com/ml-kit (fetched 2026-05-01).

Each vision API has two delivery models:

| Stack | Best For | Model Management | APK Impact |
|---|---|---|---|
| ML Kit (bundled) | On the critical path of first use; offline-from-install | Model ships in the APK | ~4 MB per script architecture (Text Recognition v2) |
| ML Kit (Play Services / unbundled) | Optional or rarely-invoked features; APK size matters | Downloaded on demand by Google Play Services | ~260 KB stub; full model fetched at first use |
| LiteRT | Custom models, strict privacy, offline-only | You ship the `.tflite` | + model size (often 2–20 MB after INT8) |
| MediaPipe Tasks | Real-time video pipelines (pose, hands, face mesh, gestures) | Bundled `.task` graphs or downloaded | 5–50 MB per pipeline |
| AICore + Gemini Nano | On-device text/image GenAI on Pixel 8 Pro+ / S24+ / Android 14+ | Provided by AICore system service | 0 MB |

Decision heuristic: *Does ML Kit solve it? Ship ML Kit. Otherwise LiteRT. Otherwise MediaPipe. Otherwise cloud via `ai-llm-integration`.*

Decision rule for delivery: bundle when the feature is on the critical path of first use; use Play Services when the feature is optional or rarely invoked and APK size matters.

Full per-API table with bundled/Play-Services tags lives in `references/ml-kit-catalogue.md`.

---

## 2. ML Kit integration — Gradle, runtime download, error handling

Gradle dependencies for Text Recognition v2 (verbatim from the official docs):

```gradle
// Bundled — model ships in the APK
implementation 'com.google.mlkit:text-recognition:16.0.1'

// Unbundled — model fetched via Google Play Services
implementation 'com.google.android.gms:play-services-mlkit-text-recognition:19.0.1'
```

(developers.google.com/ml-kit/vision/text-recognition/v2/android, fetched 2026-05-01.)

Recogniser construction:

```kotlin
val recognizer = TextRecognition.getClient(TextRecognizerOptions.DEFAULT_OPTIONS)

class TextAnalyzer(private val onResult: (Text) -> Unit) : ImageAnalysis.Analyzer {
  @OptIn(ExperimentalGetImage::class)
  override fun analyze(proxy: ImageProxy) {
    val image = proxy.image ?: return proxy.close()
    val input = InputImage.fromMediaImage(image, proxy.imageInfo.rotationDegrees)
    recognizer.process(input)
      .addOnSuccessListener(onResult)
      .addOnCompleteListener { proxy.close() }
  }
}
```

Runtime model download (Play Services variant): the model is fetched lazily on first use. For features on the critical path, pre-download via `ModuleInstallClient` so users don't see a delay when they first invoke the feature. Confirm the current `ModuleInstallClient` sample on developers.google.com/android/guides/setup at implementation time.

Error-handling shape: every detector returns a `Task<T>` — attach `addOnSuccessListener`, `addOnFailureListener`, and resource release in `addOnCompleteListener`. A `suspendCoroutine` wrapper makes ML Kit play well with `Flow` and structured concurrency. Worked example for Face Detection, Barcode, Language ID, and Entity Extraction lives in `references/ml-kit-catalogue.md`.

---

## 3. LiteRT for custom models — CompiledModel, accelerators, quantisation

LiteRT is the rebrand of TensorFlow Lite. The Android docs describe two APIs: "the modern CompiledModel API for high-performance inference, streamlining hardware acceleration across CPU/GPU/NPU" and "the legacy Interpreter API maintained for backward compatibility" (ai.google.dev/edge/litert/android, fetched 2026-05-01).

Gradle dependency (verbatim):

```gradle
implementation 'com.google.ai.edge.litert:litert:2.1.0'
```

Version 2.1.0 supports API level 23 (Android 6 Marshmallow) and above (same source).

CompiledModel API (verbatim Kotlin sample):

```kotlin
val compiledModel = CompiledModel.create(
    "/path/to/mymodel.tflite",
    CompiledModel.Options(Accelerator.CPU))

val inputBuffers = compiledModel.createInputBuffers()
val outputBuffers = compiledModel.createOutputBuffers()

inputBuffers.get(0).writeFloat(input0)
compiledModel.run(inputBuffers, outputBuffers)
val output = outputBuffers.get(0).readFloat()
```

(ai.google.dev/edge/litert/android, fetched 2026-05-01.)

`CompiledModel.Options` takes the `Accelerator` directly — `CPU`, `GPU`, or `NPU` — eliminating the separate `Delegate` construction step that the legacy `Interpreter` API required. Pick per-device via a microbench at first run; cache the choice.

Quantisation: ship INT8 unless your model is accuracy-sensitive; INT8 is typically 4x smaller and 2–4x faster with <1% accuracy loss on vision tasks. Float16 is the milder fallback. The full conversion + quantisation walkthrough (Keras → TFLite → INT8 + representative dataset) and the legacy `Interpreter` wrapper are in `references/litert-inference.md`.

---

## 4. MediaPipe Tasks — categories and Android wiring

MediaPipe Solutions is "a comprehensive framework that enables developers to quickly apply artificial intelligence (AI) and machine learning (ML) techniques in your applications" (ai.google.dev/edge/mediapipe/solutions/guide, fetched 2026-05-01).

Tasks categories (verbatim names from the Solutions guide):

1. Vision Tasks — hand landmark detection, pose landmark detection, image segmentation, object detection, face detection, and gesture recognition.
2. Text Tasks — text classification, text embedding, and language detection.
3. Audio Tasks — audio classification.
4. Generative AI Tasks — LLM inference, retrieval augmented generation (RAG), function calling, and image generation.

Customisation is available through MediaPipe Model Maker for object detection, image classification, gesture recognition, and text classification.

Android wiring pattern: plug a Tasks `ResultListener` into a CameraX `ImageAnalysis` use case (`STRATEGY_KEEP_ONLY_LATEST`, `Dispatchers.Default.asExecutor()`) and forward landmarks to Compose state via a `MutableStateFlow`. Cap the frame rate to 15 fps for landmark tasks unless interaction demands 30 — battery cost roughly doubles at 30 fps. Full PoseLandmarker and GestureRecognizer wiring + Compose `Canvas` overlay live in `references/mediapipe-camerax.md`.

Verify the canonical CameraX sample on github.com/google-ai-edge/mediapipe-samples at implementation time.

---

## 5. Gemini Nano via AICore — surface and limits

AICore is "an Android system service that enables on-device execution of GenAI foundation models" and serves as "the interface between your app and the Gemini Nano model, managing model updates and safety while leveraging on-device hardware" (developer.android.com/ai/aicore, fetched 2026-05-01).

Apps access AICore "through a series of APIs in order to run inference on-device" — the public surface is ML Kit's GenAI APIs: Prompt, Summarization, Proofreading, Rewriting, Image Description, and Speech Recognition.

Privacy contract (verbatim): AICore "is built to isolate each request and doesn't store any record of the input data or the resulting outputs after processing them to protect user privacy".

Latency contract (verbatim): "While this removes network latency, inference speed depends on device hardware".

```kotlin
val features = AICore.getFeatureAvailability(context)
if (features.isAvailable(Feature.SUMMARIZATION)) {
  val model = GenerativeModel(generationConfig { temperature = 0.2f })
  val summary = model.generateContent("Summarise: $longText").text
} else {
  // Fallback to cloud via ai-llm-integration
}
```

Always gate on `getFeatureAvailability()` — availability can be withdrawn by a system update. Device support moves with each Pixel/Samsung release; verify the current support list on developer.android.com/ai/aicore at publication time and re-verify on every flagship release that touches Gemini Nano. Worked GenAI examples (summarise, rewrite, proofread, image-describe) live in `references/aicore-gemini-nano.md`.

---

## 6. Streaming UI in Compose — `LaunchedEffect`, lifecycle, cancellation

`LaunchedEffect` runs a suspend block keyed to one or more values. Behaviour, verbatim: "Launches a coroutine when entering the Composition. Cancels the coroutine if LaunchedEffect leaves the Composition. If recomposed with different keys, cancels the existing coroutine and launches a new one" (developer.android.com/develop/ui/compose/side-effects, fetched 2026-05-01).

Signature: `LaunchedEffect(vararg keys: Any?, block: suspend () -> Unit)`.

Streaming pattern — collect a `Flow<String>` of LLM tokens inside a `LaunchedEffect` keyed on the prompt; cancellation is automatic when the user navigates away:

```kotlin
@Composable
fun StreamedAnswer(prompt: String, tokens: (String) -> Flow<String>) {
    var text by remember { mutableStateOf("") }
    LaunchedEffect(prompt) {
        text = ""
        tokens(prompt).collect { chunk -> text += chunk }
    }
    Text(text, modifier = Modifier.animateContentSize())
}
```

For event-handler-driven launches (e.g., a "Send" button), use `rememberCoroutineScope`:

```kotlin
@Composable
fun rememberCoroutineScope(factory: CoroutineContext = EmptyCoroutineContext): CoroutineScope
```

(developer.android.com/develop/ui/compose/side-effects, fetched 2026-05-01.)

For long streams, virtualise into `LazyColumn` with chunk messages instead of one growing `Text`; use `derivedStateOf` when accumulating into a list to avoid recomposing on every mutation. ViewModel-side streaming, backpressure, and integration with ML Kit GenAI / cloud SDKs are in `references/compose-streaming.md`.

---

## 7. On-device vs cloud trade-offs — decision matrix

| Dimension | On-device (ML Kit / LiteRT / Gemini Nano) | Cloud (Gemini API / Anthropic / OpenAI) |
|---|---|---|
| Latency | No network round trip; bounded by device hardware | Network-bound; tens of ms to seconds depending on region |
| Privacy | AICore "doesn't store any record of the input data or the resulting outputs" | Subject to provider data-retention terms |
| Cost | Zero per-call cost after the model is on device | Per-token / per-call cost |
| Model size & freshness | Bounded by device storage; updates ride OS or Play Services | Provider rolls model updates centrally |
| Capability ceiling | Smaller models (Gemini Nano, MobileBERT-class) | Frontier models |
| Offline | Works without connectivity | Fails without network |

Routing rule of thumb: route to on-device for short, latency-critical, privacy-sensitive interactions (barcode scanning, on-screen translation, message proofreading, OCR). Route to cloud for long-context reasoning, RAG over server-side corpora, or anything beyond Gemini Nano's capability ceiling. Hybrid: try on-device first with a 200 ms budget; fall back to cloud on `FeatureNotAvailable` or timeout. The full hybrid-routing checklist (signals, fallback ladder, telemetry) is in `references/on-device-vs-cloud.md`.

---

## Performance & Battery (cross-cutting)

- GPU vs NPU vs CPU: pick via microbench at first launch, cache the choice; warm-up cost is real (~1 s for GPU).
- Throttle video pipelines at 15–20 fps unless interaction demands more.
- Use `WorkManager` + `CoroutineWorker` with `Constraints` (charging, idle, unmetered) for batch inference — never run 10-minute jobs in `viewModelScope`.
- Profile with Android Studio Energy + CPU; watch for `binder/1` spikes from ML Kit Play Services IPC.

## Testing AI Features (cross-cutting)

- Unit: wrap inference behind an interface; stub returns fixed tensors.
- Integration: drive CameraX with pre-recorded `ImageProxy` fixtures from `androidx.camera.testing`.
- Golden outputs: store expected detection outputs per fixture; allow ±2 px tolerance; refresh in PR when upgrading a model.
- Benchmark via `androidx.benchmark`; fail CI if p95 inference regresses by >15%.

Detailed test recipes live alongside each section's reference file.
