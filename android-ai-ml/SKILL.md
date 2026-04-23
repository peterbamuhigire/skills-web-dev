---
name: android-ai-ml
description: On-device AI/ML for Android using Google's stack — ML Kit (text, face, barcode,
  language, entity), TensorFlow Lite (.tflite inference, custom models, quantisation),
  MediaPipe (pose + hand tracking), Gemini Nano via AICore, streaming Claude/GPT into
  Compose UI, CameraX integration, GPU/NNAPI delegates, battery profiling, and testing.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# Android AI/ML (ML Kit, TFLite, MediaPipe, Gemini Nano)
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Adding on-device AI features to an Android app (OCR, face, barcode, language, pose, gestures)
- Shipping a custom TFLite model inside the APK for offline inference
- Using Gemini Nano on Pixel 8 Pro+ / Android 14+ for summarisation or rewriting
- Streaming cloud LLM tokens (Claude/GPT) into a Jetpack Compose UI

## Do Not Use When

- The model needs to run cloud-side only — load `ai-llm-integration` instead
- Vision task is simple detection over static images — a plain `ImageAnalysis` may suffice
- iOS parity — load `ios-ai-ml` for CoreML/Vision/NaturalLanguage equivalents

## Required Inputs

Target API level (ML Kit 21+, Gemini Nano 34+), accuracy vs latency budget, supported devices, model ownership (Google-hosted ML Kit vs BYOM TFLite), privacy constraints (on-device only yes/no).

## Workflow

1. Prefer ML Kit for standard vision/text tasks — zero model management.
2. Drop to TFLite when you need a custom model or stricter privacy.
3. Reach for MediaPipe for real-time video pipelines (pose, hands, face mesh).
4. Use Gemini Nano for on-device summarisation on supported devices, cloud otherwise.
5. Wire CameraX once; fan out to ML Kit / MediaPipe analysers.
6. Benchmark on a mid-tier device (e.g. Pixel 6a) — not your flagship.

## Quality Standards

- Every inference call runs off the main thread (`Dispatchers.Default` or a WorkManager worker).
- Every model loader is a singleton — never instantiate per frame.
- Every AI feature has a graceful fallback when the device cannot run it.
- Every network call (cloud LLM) is cancellable and timeouts at ≤ 15 s.

## Anti-Patterns

Instantiating ML Kit clients per analyse call; running inference on the UI thread; shipping unquantised models (8× bigger APK); ignoring `FaceDetectorOptions` defaults (full landmark mode is 10× slower); mixing GPU + NNAPI delegates without benchmarking; streaming LLM tokens into a mutable `SnapshotStateList` without `derivedStateOf`.

## Outputs

ML Kit analyser + CameraX pipeline; TFLite model loader + Interpreter wrapper; MediaPipe graph runner for video; Gemini Nano availability check + fallback to cloud; Compose streaming composable; benchmark report per target device.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Correctness | Android on-device ML test plan | Markdown doc covering ML Kit (text/face/barcode/language/entity), TensorFlow Lite model load, and inference path tests | `docs/android/ml-tests.md` |
| Performance | On-device inference latency budget | Markdown doc covering per-model latency, memory, and battery-impact budgets | `docs/android/ml-perf-budget.md` |
| Release evidence | ML analyser + CameraX pipeline | Kotlin source files implementing ML Kit analyser and CameraX capture pipeline | `feature/scan/BarcodeAnalyzer.kt`, `feature/scan/CameraScreen.kt` |
| Release evidence | TFLite Interpreter wrapper | Kotlin source and bundled TFLite model asset | `ml/ClassifierInterpreter.kt`, `assets/model_int8.tflite` |
| Operability | Device benchmark report | Markdown doc capturing latency and memory per target device | `docs/ml/benchmarks-2026-04-16.md` |
| Correctness | Golden-output unit tests | Kotlin test files verifying classifier output against known inputs | `src/test/.../ClassifierInterpreterTest.kt` |

## References

- Companion skills: `ios-ai-ml` (CoreML parity), `android-development`, `jetpack-compose-ui`, `ai-llm-integration`, `kmp-development` (shared AI code).
- Free: ML Kit (`developers.google.com/ml-kit`), TFLite Android (`tensorflow.org/lite/android`), MediaPipe (`developers.google.com/mediapipe`), Gemini Nano / AICore (`developer.android.com/ai/gemini-nano`), CameraX (`developer.android.com/training/camerax`).
<!-- dual-compat-end -->

## Overview

Android has four on-device AI stacks, each with a different trade-off between ease and flexibility. Pick the lowest-effort stack that solves the problem — dropping down is expensive, climbing up is cheap.

**Cardinal rule:** the model is a singleton, inference is off-main-thread, and every AI feature has a fallback.

---

## 1. Android AI/ML Landscape

| Stack | Best For | Model Management | APK Impact |
|-------|----------|------------------|-----------|
| **ML Kit** | Standard vision, text, language — zero code | Google-hosted, auto-download | ~0 MB (Play downloads) |
| **TFLite** | Custom models, strict privacy, offline-only | You ship the `.tflite` | + model size (often 2–20 MB) |
| **MediaPipe** | Real-time video pipelines (pose, hands, face mesh) | Bundled or downloaded graphs | 5–50 MB per pipeline |
| **Gemini Nano** | On-device text tasks (summarise, rewrite, safety) on Pixel 8 Pro+/Android 14+ | Provided by AICore system service | 0 MB |

Decision heuristic: *Does ML Kit solve it? Ship ML Kit. Otherwise TFLite. Otherwise MediaPipe. Otherwise cloud with `ai-llm-integration`.*

---

## 2. ML Kit — Text Recognition

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

Use `TextRecognizerOptions.Builder().setExecutor(Dispatchers.Default.asExecutor())` to keep the ML Kit internal threadpool off the main thread. Parse `Text` block → line → element for bounding boxes.

---

## 3. ML Kit — Face Detection

```kotlin
val options = FaceDetectorOptions.Builder()
  .setPerformanceMode(FaceDetectorOptions.PERFORMANCE_MODE_FAST)
  .setLandmarkMode(FaceDetectorOptions.LANDMARK_MODE_NONE)
  .setClassificationMode(FaceDetectorOptions.CLASSIFICATION_MODE_ALL) // smile + eyes open
  .setMinFaceSize(0.15f)
  .build()
val detector = FaceDetection.getClient(options)
```

Face mesh is a separate client (`FaceMeshDetection`) — 468 landmarks for filters/AR. Liveness: prompt a blink; watch `smilingProbability` + `leftEyeOpenProbability` deltas over ~1 s. Never ship full-landmark mode on low-end devices — use `FAST` + classification.

---

## 4. ML Kit — Barcode Scanning

```kotlin
val scanner = BarcodeScanning.getClient(
  BarcodeScannerOptions.Builder()
    .setBarcodeFormats(Barcode.FORMAT_QR_CODE, Barcode.FORMAT_EAN_13, Barcode.FORMAT_CODE_128)
    .build()
)
// In CameraX ImageAnalysis:
scanner.process(input)
  .addOnSuccessListener { barcodes -> barcodes.firstOrNull()?.rawValue?.let(onResult) }
  .addOnCompleteListener { proxy.close() }
```

Set format flags explicitly — scanning for all formats is 3–5× slower. Throttle result emission (`distinctUntilChanged` in a Flow) so the UI doesn't flicker.

---

## 5. ML Kit — Language Detection

```kotlin
val identifier = LanguageIdentification.getClient(
  LanguageIdentificationOptions.Builder().setConfidenceThreshold(0.6f).build()
)
identifier.identifyLanguage(text)
  .addOnSuccessListener { tag -> if (tag != "und") detectedLang = tag }
```

For translation, pair with `Translator` — first use downloads the language pack (~30 MB) — gate the download on Wi-Fi with `DownloadConditions`. For heavy multilingual workloads use cloud translation via `ai-llm-integration`.

---

## 6. ML Kit — Entity Extraction

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

Supported entity types include phone, email, URL, address, flight number, date/time, tracking numbers. Great for rendering tap-to-action chips under a chat message. Pack size ~1.5 MB per language.

---

## 7. TensorFlow Lite — Model Inference

```kotlin
class ClassifierInterpreter(context: Context) {
  private val interpreter: Interpreter
  init {
    val model = FileUtil.loadMappedFile(context, "model_int8.tflite")
    val opts = Interpreter.Options().apply { numThreads = 4; useNNAPI = true }
    interpreter = Interpreter(model, opts)
  }
  fun classify(bitmap: Bitmap): FloatArray {
    val input = TensorImage.fromBitmap(bitmap).apply { /* resize to model input */ }
    val output = TensorBuffer.createFixedSize(intArrayOf(1, 10), DataType.FLOAT32)
    interpreter.run(input.buffer, output.buffer)
    return output.floatArray
  }
}
```

Prefer `Interpreter` over the task-specific APIs when you control the model. Hold it as a `@Singleton` — initialisation cost is real (200–500 ms). Close it in `onCleared` / `Application.onTerminate` only; never per-call.

---

## 8. TensorFlow Lite — Custom Model Training & Quantisation

Workflow: Train in Python (Keras) → convert to TFLite → quantise to INT8 → ship in `assets/`.

```python
# Python side
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.representative_dataset = gen  # 100–500 sample inputs
converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
converter.inference_input_type = tf.int8
converter.inference_output_type = tf.int8
open("model_int8.tflite", "wb").write(converter.convert())
```

INT8 quantisation is typically 4× smaller and 2–4× faster with < 1 % accuracy loss on vision tasks. Float16 is a milder alternative when INT8 is lossy on your model. Ship the `representative_dataset` script in the repo so reproducibility is preserved.

---

## 9. MediaPipe — Pose Landmark Detection

```kotlin
val options = PoseLandmarkerOptions.builder()
  .setBaseOptions(BaseOptions.builder().setModelAssetPath("pose_landmarker_full.task").build())
  .setRunningMode(RunningMode.LIVE_STREAM)
  .setNumPoses(1)
  .setResultListener { result, _ -> renderLandmarks(result.landmarks()) }
  .setErrorListener { e -> Log.e("pose", e.message, e) }
  .build()
val poseLandmarker = PoseLandmarker.createFromOptions(context, options)
// Frame loop: poseLandmarker.detectAsync(mpImage, frameTimeMs)
```

33 body landmarks with x/y/z + visibility. Normalise to image size for screen overlay. Use the `_lite` model on low-end; `_full` on flagships. Battery cost is real — cap frame rate to 15 fps unless the task demands 30.

---

## 10. MediaPipe — Hand Tracking & Gesture Recognition

```kotlin
val gesture = GestureRecognizer.createFromOptions(
  context,
  GestureRecognizerOptions.builder()
    .setBaseOptions(BaseOptions.builder().setModelAssetPath("gesture_recognizer.task").build())
    .setRunningMode(RunningMode.LIVE_STREAM)
    .setNumHands(2)
    .setResultListener { res, _ -> res.gestures().firstOrNull()?.firstOrNull()?.categoryName()?.let(onGesture) }
    .build()
)
```

Built-in gestures: Thumb_Up, Thumb_Down, Open_Palm, Closed_Fist, Pointing_Up, Victory, ILoveYou. Train a custom gesture model with MediaPipe Model Maker when the built-ins aren't enough. Render 21 hand landmarks in a Compose `Canvas` overlay — 21 × 2 hands fits an 8-ms frame budget easily.

---

## 11. Gemini Nano via AICore (Android 14+)

```kotlin
// build.gradle: implementation "com.google.ai.edge.aicore:aicore:0.0.1-exp01"
val features = AICore.getFeatureAvailability(context)
if (features.isAvailable(Feature.SUMMARIZATION)) {
  val model = GenerativeModel(generationConfig { temperature = 0.2f })
  val response = model.generateContent("Summarise: $longText")
  val summary = response.text
} else {
  // Fallback to cloud via ai-llm-integration
}
```

As of 2026, Gemini Nano ships on Pixel 8 Pro / Pixel 9 / Samsung S24+ with Android 14+. Always check `getFeatureAvailability()` — availability can be withdrawn by a system update. Features available: summarisation, proofreading, rewrite, safety classification. No raw chat.

---

## 12. Streaming AI Responses in Compose

```kotlin
@Composable
fun StreamingMessage(flow: Flow<String>) {
  val tokens = remember { mutableStateListOf<String>() }
  LaunchedEffect(flow) { flow.collect { t -> tokens += t } }
  val text by remember { derivedStateOf { tokens.joinToString("") } }
  Text(text, modifier = Modifier.animateContentSize())
}

// ViewModel side
fun ask(prompt: String) = viewModelScope.launch {
  client.messages.stream(prompt).collect { chunk -> _stream.emit(chunk.deltaText) }
}
```

`derivedStateOf` avoids recomposing on every list mutation; `animateContentSize` hides the layout jump. For long streams, virtualise into `LazyColumn` with chunk messages instead of one growing `Text`. Cancel the job on screen leave with `viewModelScope`.

---

## 13. CameraX Integration Patterns

```kotlin
val cameraProvider = ProcessCameraProvider.getInstance(context).await()
val preview = Preview.Builder().build().also { it.surfaceProvider = previewView.surfaceProvider }
val analysis = ImageAnalysis.Builder()
  .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
  .setTargetResolution(Size(720, 1280))
  .build()
  .also { it.setAnalyzer(Dispatchers.Default.asExecutor(), BarcodeAnalyzer(::onDetect)) }
cameraProvider.unbindAll()
cameraProvider.bindToLifecycle(lifecycleOwner, CameraSelector.DEFAULT_BACK_CAMERA, preview, analysis)
```

`STRATEGY_KEEP_ONLY_LATEST` drops backlogged frames — the right default for ML Kit. Set the analyser executor explicitly; the CameraX default is the main thread. Add `ImageCapture` as a third use case when you also need still shots.

---

## 14. Performance & Battery

- **GPU delegate:** `Interpreter.Options().addDelegate(GpuDelegate())` — 2–4× speedup on supported ops, but first-call warm-up is ~1 s. Cache the interpreter.
- **NNAPI:** `options.setUseNNAPI(true)` — pick whichever is faster on the target device via microbench.
- **Throttle.** Cap video pipelines at 15–20 fps unless interaction demands more. Battery drain of 30-fps pose tracking is roughly 2×.
- **WorkManager for background inference:** schedule image classification jobs with `CoroutineWorker` + `Constraints` (charging, idle, unmetered) — never run 10-minute batch jobs in `viewModelScope`.
- **Profile.** Android Studio Profiler → Energy + CPU. Watch `binder/1` spikes from ML Kit Play service IPC.

---

## 15. Testing AI Features

**Unit:** wrap the Interpreter in an injected interface; test with a stub that returns fixed tensors.

```kotlin
class ClassifierInterpreterTest {
  @Test fun `returns top-1 class for golden image`() {
    val bitmap = assetBitmap("golden/cat.png")
    val scores = classifier.classify(bitmap)
    assertEquals("cat", labels[scores.indices.maxBy { scores[it] }])
  }
}
```

**Integration with CameraX:** use `FakeImageAnalyzer` driven by pre-recorded `ImageProxy` fixtures from `androidx.camera.testing`.

**Golden outputs:** store expected detection bounding boxes per fixture frame; allow ±2 px tolerance. Refresh goldens when upgrading a model; review the diff in PR.

**Benchmark test** via `androidx.benchmark`:

```kotlin
@get:Rule val rule = BenchmarkRule()
@Test fun classifyIsUnder30ms() = rule.measureRepeated { classifier.classify(bitmap) }
```

Fail CI if p95 inference regresses by > 15 %.

---

## iOS Parity Note

Every section above has a CoreML/Vision/NaturalLanguage counterpart in `ios-ai-ml`. When building the same feature on both platforms, design the domain-layer interfaces in a KMP `commonMain` module (see `kmp-development`) and implement `expect`/`actual` for the platform-specific runners.