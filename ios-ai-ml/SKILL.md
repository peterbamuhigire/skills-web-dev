---
name: ios-ai-ml
description: On-device AI/ML for iOS using Apple's stack — CoreML model integration
  (generated wrappers, batch prediction, dynamic model loading), Vision framework
  (face detection, landmarks, barcode, saliency, image similarity, real-time camera...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# iOS AI/ML — On-Device Intelligence with Apple's Stack

<!-- dual-compat-start -->
## Use When

- On-device AI/ML for iOS using Apple's stack — CoreML model integration (generated wrappers, batch prediction, dynamic model loading), Vision framework (face detection, landmarks, barcode, saliency, image similarity, real-time camera...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `ios-ai-ml` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve; load `references` only as needed.
- Confirm the desired deliverable: design, code, review, migration plan, audit, or documentation.

## Workflow

- Read this `SKILL.md` first, then load only the referenced deep-dive files that are necessary for the task.
- Apply the ordered guidance, checklists, and decision rules in this skill instead of cherry-picking isolated snippets.
- Produce the deliverable with assumptions, risks, and follow-up work made explicit when they matter.

## Quality Standards

- Keep outputs execution-oriented, concise, and aligned with the repository's baseline engineering standards.
- Preserve compatibility with existing project conventions unless the skill explicitly requires a stronger standard.
- Prefer deterministic, reviewable steps over vague advice or tool-specific magic.

## Anti-Patterns

- Treating examples as copy-paste truth without checking fit, constraints, or failure modes.
- Loading every reference file by default instead of using progressive disclosure.

## Outputs

- A concrete result that fits the task: implementation guidance, review findings, architecture decisions, templates, or generated artifacts.
- Clear assumptions, tradeoffs, or unresolved gaps when the task cannot be completed from available context alone.
- References used, companion skills, or follow-up actions when they materially improve execution.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Correctness | Core ML inference test plan | Markdown doc covering model load, batch prediction, and dynamic model swap scenarios | `docs/ios/coreml-tests.md` |
| Performance | On-device inference latency budget | Markdown doc covering per-model latency and memory budgets | `docs/ios/coreml-perf-budget.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
## The Apple AI Stack

```
CoreML            ← inference engine (all platforms, on-device)
   ↑
Vision            ← image analysis (wraps CoreML)
NaturalLanguage   ← text/language (wraps CoreML)
Speech            ← audio→text
SoundAnalysis     ← audio classification
   ↑
CreateML          ← training (macOS only, Swift + Xcode app)
Turi Create       ← training (Python, open source, Apple-maintained)
CoreML Tools      ← model conversion from Keras/TF/Caffe → CoreML (Python)
```

CoreML runs entirely on-device — no network required for inference. Selects optimal compute unit automatically: Neural Engine → GPU → CPU.

---

## Section 1: CoreML Model Integration

### Standard 4-Step Workflow

```swift
// Step 1: Add .mlmodel to Xcode project
// Step 2: Xcode auto-generates typed wrapper classes

// Step 3: Create input, call prediction()
let mobileNet = MobileNet()
let input = MobileNetInput(image: pixelBuffer)  // typed input
let output = try mobileNet.prediction(input: input)

// Step 4: Read typed output properties
print(output.classLabel)           // String
print(output.classLabelProbs)      // [String: Double]
```

### Batch Prediction

```swift
let inputs: [MobileNetInput] = [input1, input2, input3]
let batchIn = MLArrayBatchProvider(array: inputs)
let batchOut = try mobileNet.model.predictions(from: batchIn)
```

### Dynamic Model Loading (Downloaded Models)

```swift
// Compile downloaded model on-device
let compiledUrl = try MLModel.compileModel(at: downloadedModelUrl)

// Move from temp to permanent location
let appSupportDir = FileManager.default.urls(
    for: .applicationSupportDirectory, in: .userDomainMask).first!
let permanentUrl = appSupportDir.appendingPathComponent("MyModel.mlmodelc")
try FileManager.default.moveItem(at: compiledUrl, to: permanentUrl)

let model = try MLModel(contentsOf: permanentUrl)
```

### Low-Level CoreML (Custom/Unusual Models)

```swift
let input = try MLDictionaryFeatureProvider(dictionary: [
    "image": MLFeatureValue(pixelBuffer: pixelBuffer)
])
let output = try model.prediction(from: input)
let classLabel = output.featureValue(for: "classLabel")?.stringValue
```

### MLMultiArray for Numeric Inputs

```swift
let multiArray = try MLMultiArray(shape: [1, 3, 224, 224], dataType: .float32)
// Fill array values...
let input = MLFeatureValue(multiArray: multiArray)
```

### Compute Unit Configuration

```swift
let config = MLModelConfiguration()
config.computeUnits = .cpuOnly  // .all | .cpuAndGPU | .cpuOnly
let model = try MobileNet(configuration: config)
// Use .cpuOnly for debugging/testing; .all in production
```

---

## Additional Guidance

Extended guidance for `ios-ai-ml` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `Section 2: Vision Framework`
- `Section 3: Natural Language Framework`
- `Section 4: CreateML Training Workflow`
- `Section 5: On-Device Model Updates (Personalization)`
- `Section 6: Model Optimisation`
- `Section 7: On-Device vs Cloud AI`
- `Section 8: Privacy-Preserving Patterns`
- `Section 9: Anti-Patterns`
