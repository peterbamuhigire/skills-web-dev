# MediaPipe Tasks + CameraX

Companion to `SKILL.md` §4.

## Pose Landmarker

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

33 body landmarks with x/y/z + visibility. Normalise to image size for screen overlay. Use the `_lite` model on low-end; `_full` on flagships. Cap to 15 fps unless interaction demands 30 — battery cost roughly doubles at 30 fps.

## Hand Tracking & Gesture Recognition

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

Built-in gestures: Thumb_Up, Thumb_Down, Open_Palm, Closed_Fist, Pointing_Up, Victory, ILoveYou. Train a custom set with MediaPipe Model Maker. 21 hand landmarks render comfortably in a Compose `Canvas` overlay within an 8 ms frame budget.

## CameraX wiring

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

`STRATEGY_KEEP_ONLY_LATEST` drops backlogged frames — the right default for ML Kit and MediaPipe. Set the analyser executor explicitly; CameraX's default is the main thread.

## Forwarding to Compose

Push results into a `MutableStateFlow<Landmarks?>` on the analyser thread and collect with `collectAsStateWithLifecycle()` in the composable. Render with `Canvas { drawCircle(...) }` over the preview.

## Verification

For the canonical Android sample, check github.com/google-ai-edge/mediapipe-samples at integration time.
