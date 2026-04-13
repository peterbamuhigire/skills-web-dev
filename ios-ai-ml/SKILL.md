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

- Gather relevant project context, constraints, and the concrete problem to solve.
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

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
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

## Section 2: Vision Framework

### Required Utility Extensions

Add these to every Vision project — they handle the UIImage/CGImage orientation mismatch that causes silent bugs:

```swift
extension VNImageRequestHandler {
    convenience init?(uiImage: UIImage) {
        guard let cgImage = uiImage.cgImage else { return nil }
        self.init(cgImage: cgImage, orientation: uiImage.cgImageOrientation)
    }
}

extension VNRequest {
    func queueFor(image: UIImage, completion: @escaping ([Any]?) -> ()) {
        DispatchQueue.global().async {
            if let handler = VNImageRequestHandler(uiImage: image) {
                try? handler.perform([self])
                completion(self.results)
            } else { completion(nil) }
        }
    }
}

extension UIImage {
    var cgImageOrientation: CGImagePropertyOrientation {
        switch imageOrientation {
        case .up: return .up; case .down: return .down
        case .left: return .left; case .right: return .right
        case .upMirrored: return .upMirrored; case .downMirrored: return .downMirrored
        case .leftMirrored: return .leftMirrored; case .rightMirrored: return .rightMirrored
        @unknown default: return .up
        }
    }
}
```

### Face Detection

```swift
extension UIImage {
    func detectFaces(completion: @escaping ([VNFaceObservation]?) -> ()) {
        guard let cgImage = self.cgImage else { return completion(nil) }
        let request = VNDetectFaceRectanglesRequest()
        DispatchQueue.global().async {
            let handler = VNImageRequestHandler(
                cgImage: cgImage, orientation: self.cgImageOrientation)
            try? handler.perform([request])
            completion(request.results as? [VNFaceObservation])
        }
    }
}
// Convert normalized bounding box:
// VNImageRectForNormalizedRect(observation.boundingBox, imageWidth, imageHeight)
```

### Face Landmarks (Emoji Overlay, AR Filters)

```swift
let request = VNDetectFaceLandmarksRequest()
// VNFaceLandmarks2D properties:
// leftEye, rightEye, leftPupil, rightPupil
// outerLips, innerLips, leftEyebrow, rightEyebrow
// nose, allPoints
// Each is VNFaceLandmarkRegion2D
// Call .pointsInImage(imageSize:) -> [CGPoint]
```

### Image Classification with Custom CoreML Model

```swift
class VisionClassifier {
    private let model: VNCoreMLModel
    private lazy var requests: [VNCoreMLRequest] = {
        let request = VNCoreMLRequest(model: model) { [weak self] req, _ in
            self?.handleResults(for: req)
        }
        request.imageCropAndScaleOption = .centerCrop  // critical for accuracy
        return [request]
    }()

    init?(mlmodel: MLModel) {
        guard let model = try? VNCoreMLModel(for: mlmodel) else { return nil }
        self.model = model
    }

    func classify(_ image: UIImage) {
        DispatchQueue.global(qos: .userInitiated).async {  // never on main thread
            guard let handler = VNImageRequestHandler(uiImage: image) else { return }
            try? handler.perform(self.requests)
        }
    }

    private func handleResults(for request: VNRequest) {
        DispatchQueue.main.async {
            guard let results = request.results as? [VNClassificationObservation],
                  let top = results.first, top.confidence >= 0.6 else { return }
            print("\(top.identifier) (\(Int(top.confidence * 100))%)")
        }
    }
}
```

### Barcode Detection

```swift
extension UIImage {
    func detectBarcodes(types: [VNBarcodeSymbology] = [.qr],
                        completion: @escaping ([VNBarcodeObservation]) -> ()) {
        let request = VNDetectBarcodesRequest()
        request.symbologies = types
        request.queueFor(image: self) { result in
            completion(result as? [VNBarcodeObservation] ?? [])
        }
    }
}
// VNBarcodeObservation.payloadStringValue — the decoded barcode data
```

### Saliency Detection

```swift
extension UIImage {
    func detectSalientRegions(completion: @escaping (CGRect?) -> ()) {
        let request = VNGenerateAttentionBasedSaliencyImageRequest()
        // Swap for VNGenerateObjectnessBasedSaliencyImageRequest() for object-based
        request.queueFor(image: self) { results in
            guard let obs = results?.first as? VNSaliencyImageObservation,
                  let objects = obs.salientObjects else { return completion(nil) }
            let merged = objects.reduce(CGRect.zero) { $0.union($1.boundingBox) }
            completion(merged)
        }
    }
}
```

### Image Similarity (Feature Print Distance)

```swift
extension UIImage {
    func similarity(to other: UIImage) -> Float? {
        guard let first = featurePrint(), let second = other.featurePrint() else { return nil }
        var distance: Float = 0
        try? second.computeDistance(&distance, to: first)
        return distance  // lower = more similar
    }

    private func featurePrint() -> VNFeaturePrintObservation? {
        guard let cgImage = self.cgImage else { return nil }
        let handler = VNImageRequestHandler(cgImage: cgImage, orientation: cgImageOrientation)
        let request = VNGenerateImageFeaturePrintRequest()
        try? handler.perform([request])
        return request.results?.first as? VNFeaturePrintObservation
    }
}
```

### Real-Time Camera Classification

```swift
class CameraClassifier: NSObject, AVCaptureVideoDataOutputSampleBufferDelegate {
    private var isProcessing = false  // skip frames while busy

    private lazy var requests: [VNCoreMLRequest] = {
        let model = try! VNCoreMLModel(for: MyClassifier().model)
        let request = VNCoreMLRequest(model: model) { [weak self] req, _ in
            self?.isProcessing = false
            DispatchQueue.main.async {
                let results = req.results as? [VNClassificationObservation]
                self?.processResults(results)
            }
        }
        request.imageCropAndScaleOption = .centerCrop
        return [request]
    }()

    func captureOutput(_ output: AVCaptureOutput,
                       didOutput sampleBuffer: CMSampleBuffer,
                       from connection: AVCaptureConnection) {
        guard !isProcessing,
              let pixelBuffer = CMSampleBufferGetImageBuffer(sampleBuffer) else { return }
        isProcessing = true
        let handler = VNImageRequestHandler(cvPixelBuffer: pixelBuffer, orientation: .up)
        DispatchQueue.global(qos: .userInitiated).async {
            try? handler.perform(self.requests)
        }
    }
}
```

---

## Section 3: Natural Language Framework

### Language Identification

```swift
extension String {
    func dominantLanguage() -> String? {
        let recognizer = NLLanguageRecognizer()
        recognizer.processString(self)
        return recognizer.dominantLanguage?.rawValue
    }
}
```

### Named Entity Recognition

```swift
extension String {
    func namedEntities() -> [(String, NLTag)] {
        var entities: [(String, NLTag)] = []
        let tagger = NLTagger(tagSchemes: [.nameType])
        tagger.string = self
        tagger.enumerateTags(in: startIndex..<endIndex, unit: .word,
                             scheme: .nameType,
                             options: [.omitPunctuation, .omitWhitespace, .joinNames]) { tag, range in
            if let tag = tag,
               [.personalName, .placeName, .organizationName].contains(tag) {
                entities.append((String(self[range]), tag))
            }
            return true
        }
        return entities
    }
}
```

### Parts of Speech / Lemmatization

```swift
let tagger = NLTagger(tagSchemes: [.lexicalClass, .lemma])
tagger.string = text
tagger.enumerateTags(in: text.startIndex..<text.endIndex, unit: .word,
                     scheme: .lexicalClass,
                     options: [.omitPunctuation, .omitWhitespace]) { tag, range in
    let lemmaTag = tagger.tag(at: range.lowerBound, unit: .word, scheme: .lemma)
    print("\(text[range]) → \(tag?.rawValue ?? "") (lemma: \(lemmaTag?.rawValue ?? ""))")
    return true
}
```

### Sentiment Analysis with Custom NLModel

```swift
// After training MLTextClassifier and exporting .mlmodel:
private lazy var sentimentModel: NLModel? = {
    try? NLModel(mlModel: SentimentClassifier().model)
}()

extension String {
    func sentiment(model: NLModel) -> String {
        guard !isEmpty else { return "neutral" }
        return model.predictedLabel(for: self) ?? "neutral"
    }
}
```

---

## Section 4: CreateML Training Workflow

### Image Classifier (Xcode App)

1. Xcode menu → Open Developer Tool → CreateML
2. Select "Image Classifier" template
3. Drop training folder (subfolders named by label) into Training Data
4. Press Play — auto 80/20 train/validation split
5. Drag `.mlmodel` from Output into Xcode project

### Text Classifier (Swift Script/Playground)

```swift
import CreateML

let data = try MLDataTable(contentsOf: URL(fileURLWithPath: "/path/data.csv"))
let (train, test) = data.randomSplit(by: 0.8, seed: 42)

let classifier = try MLTextClassifier(
    trainingData: train, textColumn: "text", labelColumn: "label"
)
let accuracy = (1.0 - classifier.evaluation(
    on: test, textColumn: "text", labelColumn: "label").classificationError) * 100

let metadata = MLModelMetadata(
    author: "Author", shortDescription: "Desc", version: "1.0")
try classifier.write(
    to: URL(fileURLWithPath: "/output/Model.mlmodel"), metadata: metadata)
```

### Available CreateML Model Types

| Type | Use Case |
|---|---|
| `MLImageClassifier` | Image classification |
| `MLObjectDetector` | Object detection with bounding boxes |
| `MLTextClassifier` | Document/sentence classification |
| `MLWordTagger` | Word-level entity tagging |
| `MLSoundClassifier` | Audio classification |
| `MLActivityClassifier` | Motion/gesture (accelerometer data) |
| `MLRegressor` / `MLClassifier` | Tabular data |
| `MLRecommender` | Recommendation systems |

---

## Section 5: On-Device Model Updates (Personalization)

```swift
// Model must be marked updatable in .mlmodel
// Supported: neural networks (classifier/regressor), K-nearest neighbor
// Only updates: convolutional and fully connected layers

let handlers = MLUpdateProgressHandlers(
    forEvents: [.trainingBegin, .epochEnd],
    progressHandler: { context in
        if let epoch = context.metrics[.epochIndex] as? Int,
           let loss = context.metrics[.lossValue] as? Double {
            print("Epoch \(epoch), loss: \(loss)")
        }
    },
    completionHandler: { context in
        try? context.model.write(to: updatedModelURL)
    }
)

let updateTask = try MLUpdateTask(
    forModelAt: compiledModelURL,
    trainingData: trainingBatchProvider,  // MLBatchProvider
    configuration: nil,
    progressHandlers: handlers
)
updateTask.resume()
```

Real-world pattern: FaceID improves with each successful unlock via on-device personalization — no data leaves the device.

---

## Section 6: Model Optimisation

### Quantization (Python / CoreML Tools)

```python
import coremltools

model = coremltools.models.MLModel('MyModel.mlmodel')

# 16-bit quantization (~2x size reduction, minimal accuracy loss)
from coremltools.models.neural_network import quantization_utils
model_fp16 = quantization_utils.quantize_weights(
    model, nbits=16, quantization_mode='linear')

# 8-bit quantization (~4x size reduction)
model_int8 = quantization_utils.quantize_weights(
    model, nbits=8, quantization_mode='linear_symmetric')
model_int8.save('MyModel_quantized.mlmodel')
```

**Transfer learning:** CreateML reuses a pretrained CNN backbone and only retrains final classification layers. Training takes minutes, not weeks.

**Large model strategy:** Bundle small models; download large models on-demand and compile on-device using the dynamic loading pattern in Section 1.

---

## Section 7: On-Device vs Cloud AI

| Factor | CoreML (On-Device) | Cloud AI |
|---|---|---|
| Availability | Always, offline | Requires network |
| Privacy | Data never leaves device | Data leaves device |
| Latency | Near-zero | Network RTT |
| Model updates | Via MLUpdateTask or app update | Instant server-side |
| App size | Larger (embedded model) | Smaller |
| Infrastructure | None | Servers required |

Apple's stance: on-device advantages (privacy, availability, latency) outweigh the disadvantages for most use cases. The Neural Engine makes inference fast enough.

---

## Section 8: Privacy-Preserving Patterns

1. **Feature vectors instead of raw data** — `VNFeaturePrintObservation` gives a numeric representation; the original image is never needed for comparison
2. **On-device personalization** — model improves per user; data stays local via `MLUpdateTask`
3. **NSCache for sensitive intermediates** — auto-evicts under memory pressure before `didReceiveMemoryWarning`
4. **Never upload for inference** — if CoreML can do it on-device, it should
5. **Model metadata transparency** — use `MLModelMetadata` to embed licence and description; expose via `model.modelDescription.metadata[.license]`

---

## Section 9: Anti-Patterns

| Anti-Pattern | Consequence | Fix |
|---|---|---|
| Vision requests on main thread | Frozen UI | Always `DispatchQueue.global().async` |
| Missing `imageCropAndScaleOption` | Poor classifier accuracy | Set `.centerCrop` for classifiers |
| UIImage directly to Vision without orientation | Silent orientation bugs | Convert via `cgImageOrientation` extension |
| Processing every camera frame | CPU/GPU overload | Skip frames with `isProcessing` flag |
| Bundling very large models (>100 MB) | App Store size rejection | Download on-demand + compile on-device |
| Confidence threshold ignored | Noisy/wrong predictions | Gate on `confidence >= 0.6` minimum |
| Uploading data for cloud inference | Privacy violation | Use on-device CoreML |
