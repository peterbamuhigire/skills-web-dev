# Mobile OpenTelemetry Bootstrap

Reference snippets for `SKILL.md` §9 (Instrumentation across the stack). Pair with Sentry mobile SDKs (§8) for crash capture; OTel handles RUM and distributed traces.

## iOS — OpenTelemetry Swift

SPM: add `https://github.com/open-telemetry/opentelemetry-swift` (verify the latest stable line at integration time — alpha tags ship frequently).

```swift
import OpenTelemetryApi
import OpenTelemetrySdk
import OpenTelemetryProtocolExporterHttp
import URLSessionInstrumentation

func bootstrapOtel() {
    let resource = Resource(attributes: [
        "service.name": .string("ios-app"),
        "deployment.environment": .string("prod")
    ])
    let exporter = OtlpHttpTraceExporter(endpoint: URL(string: "https://otel.acme.io/v1/traces")!)
    let provider = TracerProviderBuilder()
        .add(spanProcessor: BatchSpanProcessor(spanExporter: exporter))
        .with(resource: resource).build()
    OpenTelemetry.registerTracerProvider(tracerProvider: provider)
    URLSessionInstrumentation(configuration: URLSessionInstrumentationConfiguration())
}

struct TracedScreen<Content: View>: View {
    let name: String
    @Environment(\.scenePhase) private var phase
    @ViewBuilder let content: () -> Content
    @State private var span: Span?
    var body: some View {
        content()
            .onAppear {
                span = OpenTelemetry.instance.tracerProvider
                    .get(instrumentationName: "ui")
                    .spanBuilder(spanName: "screen.\(name)").startSpan()
            }
            .onDisappear { span?.end() }
            .onChange(of: phase) { if $0 == .background { span?.end(); span = nil } }
    }
}
```

Initialize on the main thread as early as `application:didFinishLaunchingWithOptions:` so startup spans are captured.

## Android — OpenTelemetry Android Agent

The `opentelemetry-android` agent initializes the OpenTelemetry Java SDK and provides RUM auto-instrumentation, including offline buffering of telemetry via disk persistence.

```kotlin
// build.gradle.kts
dependencies {
    api(platform("io.opentelemetry.android:opentelemetry-android-bom:1.3.0-alpha"))
    implementation("io.opentelemetry.android:android-agent")
}

class MyApp : Application() {
    lateinit var rum: OpenTelemetryRum
    override fun onCreate() {
        super.onCreate()
        rum = OpenTelemetryRum.builder(this, OtelRumConfig())
            .setEndpoint("https://otel.acme.io")
            .addInstrumentation(AnrInstrumentation())
            .addInstrumentation(CrashReporterInstrumentation())
            .build()
    }
}
```

The ANR detector correlates frozen frames with the active `trace_id` so a Grafana jank spike resolves to the Compose frame that blocked the main thread.

Verify the latest stable BOM line at publish time — the Android agent is on an alpha track.
