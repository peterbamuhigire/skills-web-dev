---
name: csharp-dotnet-development
description: Use when building, reviewing, modernising, or debugging C# and .NET applications, including ASP.NET Core, EF Core, background services, concurrency, .NET MAUI, testing, packaging, and AI integration.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# C# And .NET Development
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Building or reviewing C#/.NET code, services, APIs, workers, desktop/mobile apps, or libraries.
- Choosing .NET target frameworks, SDK versions, project layout, dependency boundaries, or deployment shape.
- Implementing ASP.NET Core endpoints, EF Core repositories, background jobs, async/parallel code, MAUI UI, Azure services, or .NET AI features.
- Modernizing older .NET Framework, Web Forms, WPF, WinForms, or early .NET Core code to current .NET.

## Do Not Use When

- The work is only Avalonia UI; use `avalonia-desktop-development` for AXAML, Avalonia MVVM, styling, and packaging.
- The work is only generic architecture, data modelling, security, or CI/CD with no .NET-specific decisions; use the specialist skill first and return here for implementation details.

## Required Inputs

| Artefact | Required? | Purpose |
|---|---|---|
| Target framework, SDK, hosting model, and deployment target | yes | Fix runtime and compatibility boundaries |
| Solution, failures, logs, and tests | yes | Ground work in repository evidence |
| Integrations, security model, and scale assumptions | conditional | Shape operational decisions |

## Workflow

1. Identify the application shape: library, CLI, ASP.NET Core, worker, MAUI, desktop, Azure function, microservice, or AI-enabled service.
2. Verify the target framework and SDK. Prefer current LTS for production unless the project is explicitly pinned or compatibility requires otherwise.
3. Inspect project boundaries. Keep domain logic outside controllers, pages, XAML code-behind, EF `DbContext`, hosted services, and framework glue.
4. Apply C# idioms from `references/csharp-language-and-runtime.md` before adding abstractions.
5. Load only the relevant deep reference:
   - APIs/services: `references/aspnet-core-and-services.md`
   - EF Core/data: `references/ef-core-data-access.md`
   - MAUI UI: `references/dotnet-maui-cross-platform-ui.md`
   - Async/parallel work: `references/concurrency-and-parallelism.md`
   - Testing/release: `references/testing-packaging-and-operations.md`
   - AI integration: `references/ai-in-dotnet.md`
   - Source synthesis: `references/source-study-notes.md`
6. Implement or review with security, cancellation, structured logging, observability, performance, and testability as first-class concerns.
7. Validate with `dotnet restore`, `dotnet build`, `dotnet test`, analyzers, formatters, and a realistic runtime smoke test when a project is available.

## Quality Standards

- Treat nullable reference types, analyzers, warnings, and source-generated validation as quality gates, not optional polish.
- Use dependency injection and options binding deliberately; keep service lifetimes correct and avoid service locator patterns.
- Make all I/O async and cancellation-aware. Do not block on `Task.Result`, `.Wait()`, or `.GetAwaiter().GetResult()` in app code.
- Validate every boundary: HTTP, CLI args, config, queues, files, webhooks, external API responses, and AI/tool outputs.
- Prefer records/immutable value objects for data transfer and domain values; use classes for behaviour and identity.
- Keep EF Core queries explicit, measured, and projection-focused; avoid lazy-loading surprises on request paths.
- Add logging scopes, correlation IDs, health checks, metrics, and actionable errors before calling a service production-ready.
- Use platform-specific UI only behind thin adapters; keep MAUI view models and domain services testable without device APIs.

## Anti-Patterns

- Fat controllers, fat pages, fat hosted services, or XAML code-behind containing domain rules.
- `async void` outside UI event handlers, fire-and-forget tasks without supervised queues, or ignored `CancellationToken`.
- Returning EF entities directly from public APIs when contracts, privacy, or versioning matter.
- Global static state for clocks, configuration, database access, HTTP clients, or current user context.
- Swallowing exceptions, logging without context, or exposing raw exception details to users.
- Hand-written cryptography, custom authentication/session systems, or direct secret reads from source files.
- Treating `.NET Framework`, `.NET`, `.NET Core`, ASP.NET, ASP.NET Core, MAUI, WPF, and Avalonia as interchangeable.

## Outputs

- Code changes, review findings, architecture decisions, migration plans, test strategy, release checklist, or implementation guidance.
- Explicit assumptions about target framework, platform support, data stores, threading, deployment, and compatibility.
- Validation evidence: commands run, tests added or skipped with reason, runtime smoke checks, and residual risk.

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Correctness | .NET verification log | Markdown or terminal summary with restore/build/test/analyzer/runtime smoke results | `docs/dotnet/verification.md` |
| Correctness | Boundary map | Markdown table of projects, responsibilities, dependencies, and forbidden references | `docs/dotnet/project-boundaries.md` |
| Operability | Release readiness checklist | Markdown checklist for config, health, telemetry, packaging, rollback, and owner | `docs/dotnet/release-readiness.md` |

## References

- `references/csharp-language-and-runtime.md`: load for language idioms, C# 12/13/14 features, project files, nullability, records, spans, exceptions, and runtime choices.
- `references/aspnet-core-and-services.md`: load for APIs, minimal APIs, controllers, middleware, auth, OpenAPI, Blazor, SignalR, hosted services, and Azure functions.
- `references/ef-core-data-access.md`: load for EF Core modelling, migrations, query performance, transactions, concurrency, JSON/vector features, and repository boundaries.
- `references/dotnet-maui-cross-platform-ui.md`: load for .NET MAUI app structure, XAML, MVVM, platform services, device features, and packaging.
- `references/concurrency-and-parallelism.md`: load for async workflows, channels, task parallelism, dataflow, cancellation, locking, and CPU-bound work.
- `references/testing-packaging-and-operations.md`: load for test strategy, analyzers, CI, publishing, containers, NativeAOT, trimming, health checks, and observability.
- `references/ai-in-dotnet.md`: load for Semantic Kernel, Microsoft.Extensions.AI, embeddings, RAG, tool calling, safety, and telemetry.
- `references/source-study-notes.md`: load when you need the source-book map and synthesis boundaries used to prepare this skill.
<!-- dual-compat-end -->

## Project Defaults

Prefer this baseline unless the target project already has stronger conventions:

- `Directory.Build.props` with nullable enabled, implicit usings enabled, latest stable language version only when the SDK supports it, warnings treated seriously, and analyzers on.
- One solution with explicit projects: `Domain`, `Application`, `Infrastructure`, `Api`/`Worker`/`Maui`, and `Tests` for non-trivial systems.
- External dependencies behind interfaces or typed clients; contracts versioned separately from EF entities and UI models.
- `IOptions<T>` with validated configuration; secrets from environment, user secrets for local development, or managed secret stores.
- `TimeProvider`, `ILogger<T>`, `IHttpClientFactory`, `IHostedService`/`BackgroundService`, and `CancellationToken` instead of ad hoc infrastructure.
- `dotnet format`, analyzers, unit tests, integration tests, and smoke tests in CI.

## Review Checklist

- Does each project have a clear reason to exist, and are dependencies one-way?
- Are public contracts stable, documented, validated, and decoupled from persistence?
- Are async calls cancellation-aware and free from sync-over-async?
- Are secrets, auth, authorization, CORS, cookies, tokens, and data access scoped correctly?
- Are database queries projected, indexed, bounded, and observable?
- Are tests proving domain rules, API contracts, persistence behaviour, and critical failure paths?
- Can production operators diagnose startup, dependency failure, queue backlog, request latency, and release version quickly?

## Decision Rules

| Condition | Action |
|---|---|
| Supported target framework exists | Improve in place and preserve public contracts |
| Upgrade crosses compatibility boundaries | Stage migration with rollback points |
| Failure is runtime-specific | Reproduce against the pinned SDK first |

## Capability Contract

Read and search are required. Editing and execution require task authorisation; network access is optional for documentation and package verification.

## Degraded Mode

If execution is unavailable, return a code review and exact verification commands without claiming build or test success.
