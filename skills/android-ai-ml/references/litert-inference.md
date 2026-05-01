# LiteRT (TensorFlow Lite) — Inference, Accelerators, Quantisation

Companion to `SKILL.md` §3.

## CompiledModel API (current, ai.google.dev/edge/litert/android, fetched 2026-05-01)

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

`Accelerator.CPU | GPU | NPU` is passed directly via `CompiledModel.Options` — no separate `Delegate` construction.

### Picking the accelerator

1. At first launch, run a tiny microbench against CPU, GPU, and (where available) NPU.
2. Store the winner in DataStore keyed by `Build.SOC_MODEL` + model file hash.
3. Re-bench when the model file changes.
4. Beware GPU first-call warm-up (~1 s); pre-warm during splash if the model runs on the critical path.

## Legacy Interpreter API (still supported)

```kotlin
class ClassifierInterpreter(context: Context) {
  private val interpreter: Interpreter
  init {
    val model = FileUtil.loadMappedFile(context, "model_int8.tflite")
    val opts = Interpreter.Options().apply { numThreads = 4; useNNAPI = true }
    interpreter = Interpreter(model, opts)
  }
  fun classify(bitmap: Bitmap): FloatArray {
    val input = TensorImage.fromBitmap(bitmap)
    val output = TensorBuffer.createFixedSize(intArrayOf(1, 10), DataType.FLOAT32)
    interpreter.run(input.buffer, output.buffer)
    return output.floatArray
  }
}
```

Hold as a singleton — initialisation is 200–500 ms. Close in `onCleared()` only; never per-call.

## Quantisation — Keras → TFLite → INT8

```python
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.representative_dataset = gen  # 100–500 sample inputs
converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
converter.inference_input_type = tf.int8
converter.inference_output_type = tf.int8
open("model_int8.tflite", "wb").write(converter.convert())
```

INT8 is typically 4x smaller and 2–4x faster with <1% accuracy loss on vision tasks. Float16 is the milder fallback. Ship the `representative_dataset` script in the repo so reproducibility is preserved. The full quantisation guidance (post-training dynamic-range, full-integer, float16) lives at ai.google.dev/edge/litert under model conversion — verify the current page at integration time.

## Gradle

```gradle
implementation 'com.google.ai.edge.litert:litert:2.1.0'
```

API 23+.

## Testing

```kotlin
class ClassifierInterpreterTest {
  @Test fun `returns top-1 class for golden image`() {
    val bitmap = assetBitmap("golden/cat.png")
    val scores = classifier.classify(bitmap)
    assertEquals("cat", labels[scores.indices.maxBy { scores[it] }])
  }
}
```

Benchmark with `androidx.benchmark`; fail CI if p95 inference regresses by >15%.
