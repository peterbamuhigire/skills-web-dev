# Phase 10: Frontier & Thought Leadership

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Extend the engine into the next generation of interface paradigms and scale patterns — edge computing, advanced cross-platform mobile, accessibility, and spatial/AR interfaces — so the skills library remains the reference point for world-class software development through the 2030s and into the 2040s.

**Architecture:** Four new skill directories (`edge-computing`, `react-native-advanced`, `accessibility-wcag`, `ar-vr-interfaces`) plus a sustained library governance practice. This phase is open-ended by design — the frontier evolves. Each skill in this phase should be reviewed and updated as the underlying platforms mature.

**Tech Stack:** Cloudflare Workers, Vercel Edge, D1 (SQLite at edge), React Native New Architecture (JSI/Fabric), Expo EAS, WCAG 2.2 AA, ARIA, ARKit, ARCore, Apple Vision Pro (visionOS), WebXR.

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

## Task 1: Create `edge-computing` skill

**Files:**
- Create: `edge-computing/SKILL.md`
- Create: `edge-computing/references/cloudflare-workers.md`
- Create: `edge-computing/references/edge-data-patterns.md`

**Step 1:** Write `edge-computing/SKILL.md` covering:

- Edge vs. origin: what runs at the edge (auth token validation, A/B routing, personalisation headers, geo-routing, rate limiting), what stays at origin (database writes, complex business logic, payments)
- Cloudflare Workers: V8 isolate model, `fetch` handler, `scheduled` handler (cron), KV store, R2 object storage, Durable Objects (stateful edge)
- Vercel Edge Functions: `export const config = { runtime: 'edge' }`, middleware, geolocation headers, A/B split at edge
- D1 (SQLite at edge): schema, query, transaction — when D1 is appropriate (read-heavy, eventual consistency acceptable) vs. when it is not (financial transactions, strong consistency required)
- Edge AI inference: Cloudflare Workers AI — hosted models (LLaMA, Mistral, Whisper) running at edge with no cold start; use cases (content classification, language detection, spam filter)
- Latency patterns: cache-first, stale-while-revalidate, edge cache invalidation on origin data change

Anti-Patterns: putting database writes in edge functions (consistency nightmare), using Durable Objects for simple stateless tasks, not setting appropriate cache TTLs, running heavy LLM inference at edge (use streaming from origin instead).

**Step 2:** Write `references/cloudflare-workers.md` — complete Worker examples: JWT validation at edge, geo-routing (redirect East African users to regional origin), rate limiting with KV, Durable Object counter.

**Step 3:** Write `references/edge-data-patterns.md` — cache invalidation patterns, D1 + origin database sync, R2 for large file serving with presigned URLs, KV for feature flags and A/B experiments.

**Step 4:** Validate and commit.
```bash
python -X utf8 skill-writing/scripts/quick_validate.py edge-computing
git add edge-computing/
git commit -m "feat: add edge-computing skill (Cloudflare Workers, Vercel Edge, D1, edge AI)"
```

---

## Task 2: Create `react-native-advanced` skill

**Files:**
- Create: `react-native-advanced/SKILL.md`
- Create: `react-native-advanced/references/new-architecture.md`
- Create: `react-native-advanced/references/expo-eas.md`
- Create: `react-native-advanced/references/performance-profiling.md`

**Step 1:** Write `react-native-advanced/SKILL.md` covering:

- New Architecture (RN 0.71+): JSI (JavaScript Interface) replacing the bridge, Fabric renderer for synchronous layout, TurboModules for lazy native module loading — performance implications for each
- Expo EAS: EAS Build (cloud builds for iOS + Android), EAS Submit (automated App Store + Play Store submission), EAS Update (OTA updates without app store review), EAS Secrets
- Native modules: creating a TurboModule in Kotlin/Swift, JSI direct memory access, Codegen for type-safe native bindings
- Performance profiling: Hermes bytecode, Flipper performance plugin, JS thread vs. UI thread vs. native thread attribution, `InteractionManager.runAfterInteractions()`, `useCallback`/`useMemo` — when they help vs. when they add noise
- Animation: `react-native-reanimated` (runs on UI thread, no bridge), `react-native-gesture-handler`, shared element transitions
- Large list performance: `FlashList` (Shopify, 10× faster than FlatList for large datasets), cell recycling, `getItemType` optimisation

Anti-Patterns: running heavy computation on the JS thread, animating with `setState` (use `Animated.Value` or Reanimated), using FlatList for lists > 100 items without optimisation, not using Hermes engine.

**Step 2:** Write `references/new-architecture.md` — JSI architecture diagram, TurboModule vs. legacy module decision, Codegen schema setup, migration path from bridge-based module.

**Step 3:** Write `references/expo-eas.md` — EAS Build config (`eas.json`), iOS signing with EAS (no local Xcode required), Android keystore management, EAS Update workflow for bug fixes without store submission.

**Step 4:** Write `references/performance-profiling.md` — Flipper setup, JS thread profiling, Hermes sampling profiler, identifying render bottlenecks, FlashList migration from FlatList.

**Step 5:** Validate and commit.
```bash
python -X utf8 skill-writing/scripts/quick_validate.py react-native-advanced
git add react-native-advanced/
git commit -m "feat: add react-native-advanced skill (New Architecture, EAS, TurboModules, performance)"
```

---

## Task 3: Create `accessibility-wcag` skill

**Files:**
- Create: `accessibility-wcag/SKILL.md`
- Create: `accessibility-wcag/references/semantic-html-aria.md`
- Create: `accessibility-wcag/references/testing-accessibility.md`

**Step 1:** Write `accessibility-wcag/SKILL.md` covering:

- WCAG 2.2 AA — the compliance target for most SaaS, public sector, and healthcare projects: 4 principles (Perceivable, Operable, Understandable, Robust), new criteria in 2.2 (Focus Appearance, Dragging Movements, Target Size)
- Semantic HTML: use the right element (`<button>` not `<div onclick>`, `<nav>`, `<main>`, `<article>`, landmark roles)
- ARIA: when to use (custom widgets), when not to use (native HTML suffices), `aria-label`, `aria-describedby`, `aria-live` for dynamic content, `aria-expanded` for disclosure widgets
- Keyboard navigation: focus order must follow reading order, focus visible at all times, no keyboard traps, skip navigation link
- Colour contrast: AA = 4.5:1 for normal text, 3:1 for large text; tools: Colour Contrast Analyser, Figma contrast plugin
- Motion and animation: `prefers-reduced-motion` media query, all animation must be suppressible
- Forms: `<label>` for every input, error messages linked to field with `aria-describedby`, no colour-only error indication
- React/Next.js specifics: `eslint-plugin-jsx-a11y`, focus management on route change (`document.title` update, focus reset), modal focus trap

Anti-Patterns: `<div>` buttons, placeholder-as-label, colour-only error state, `outline: none` without focus-visible replacement, dynamic content updates not announced to screen reader.

**Step 2:** Write `references/semantic-html-aria.md` — component-by-component ARIA pattern library: modal dialog, disclosure widget, tabs, autocomplete combobox, toast notification, data table with sort.

**Step 3:** Write `references/testing-accessibility.md` — automated: `axe-core` + `@axe-core/playwright` in E2E suite (catches ~30% of issues). Manual: NVDA + Chrome, VoiceOver + Safari, keyboard-only navigation checklist, WCAG 2.2 AA audit checklist.

**Step 4:** Validate and commit.
```bash
python -X utf8 skill-writing/scripts/quick_validate.py accessibility-wcag
git add accessibility-wcag/
git commit -m "feat: add accessibility-wcag skill (WCAG 2.2 AA, ARIA, keyboard, contrast, React patterns)"
```

---

## Task 4: Create `ar-vr-interfaces` skill

**Files:**
- Create: `ar-vr-interfaces/SKILL.md`
- Create: `ar-vr-interfaces/references/arkit-arcore-patterns.md`
- Create: `ar-vr-interfaces/references/visionos-spatial-ui.md`

**Note:** This skill targets 2028+. Write it as a foundation — patterns will need updating as platforms mature. Flag time-sensitive content clearly.

**Step 1:** Write `ar-vr-interfaces/SKILL.md` covering:

- Platform landscape (as of 2026): ARKit (iOS), ARCore (Android), Apple Vision Pro (visionOS), Meta Quest (WebXR / Unity), web AR via WebXR API
- Use cases that justify AR/VR today: field service (overlay repair instructions on equipment), healthcare (anatomy visualisation, surgical planning), retail (virtual try-on), education (3D models), real estate (space visualisation)
- ARKit fundamentals: `ARSession`, `ARWorldTrackingConfiguration`, plane detection, object placement, `RealityKit` for rendering, `Reality Composer Pro` for scene authoring
- ARCore fundamentals: `ArSession`, plane detection, anchor placement, Sceneform (Kotlin), Cloud Anchors for shared AR
- visionOS / Vision Pro: `WindowGroup`, `ImmersiveSpace`, `RealityView`, hand tracking, eye tracking, spatial audio, ornaments — the SwiftUI-first development model
- WebXR: `navigator.xr`, immersive-ar and immersive-vr sessions, hit testing, Three.js / Babylon.js integration — widest reach but lowest capability
- When to choose native vs. WebXR: precision and performance (native) vs. no-install, cross-platform (WebXR)

Anti-Patterns: forcing AR for tasks better done in 2D, not designing for variable lighting conditions (AR tracking degrades), no fallback for devices without AR support, ignoring motion sickness in VR (maintain 90+ fps, minimise acceleration).

**Step 2:** Write `references/arkit-arcore-patterns.md` — ARKit RealityKit scene placement example (iOS), ARCore Kotlin object anchor example, shared Cloud Anchor pattern for collaborative AR.

**Step 3:** Write `references/visionos-spatial-ui.md` — visionOS app structure, `WindowGroup` for 2D windows, `ImmersiveSpace` for full immersion, `RealityView` for 3D content, hand gesture recognition, spatial audio attachment.

**Step 4:** Validate and commit.
```bash
python -X utf8 skill-writing/scripts/quick_validate.py ar-vr-interfaces
git add ar-vr-interfaces/
git commit -m "feat: add ar-vr-interfaces skill (ARKit, ARCore, visionOS, WebXR — 2028+ foundation)"
```

---

## Task 5: Library Governance — Ongoing Practice

This task is not one-time. After completing the four new skills above, establish a quarterly governance practice:

**Quarterly Review Checklist:**
- [ ] Run `python -X utf8 skill-writing/scripts/quick_validate.py` across all skills — fix any regressions
- [ ] Check all skills for `metadata.portable: true` and `compatible_with: [claude-code, codex]`
- [ ] Identify skills approaching obsolescence (platform versions, deprecated APIs)
- [ ] Review `ar-vr-interfaces` and `edge-computing` for new platform capabilities
- [ ] Update reading material lists as new books publish
- [ ] Promote thin-coverage skills (< 200 lines) or deprecate if superseded
- [ ] Run `python -X utf8 skill-writing/scripts/upgrade_dual_compat.py` if new skills were added without the portable contract

**Commit the governance result:**
```bash
git commit -m "chore: quarterly skills library governance review — [quarter] [year]"
```

---

## Success Gate

- [ ] `edge-computing` passes validator, ≤ 500 lines, portable metadata present
- [ ] `react-native-advanced` passes validator, ≤ 500 lines, portable metadata present
- [ ] `accessibility-wcag` passes validator, ≤ 500 lines, portable metadata present — references `e2e-testing` axe-core integration
- [ ] `ar-vr-interfaces` passes validator, ≤ 500 lines, portable metadata present — time-sensitive content flagged
- [ ] Quarterly governance practice documented and scheduled

---

## Reading Material

| Priority | Resource | Format | Cost | Unlocks |
|----------|----------|--------|------|---------|
| 1 | Cloudflare Workers documentation | Free (developers.cloudflare.com/workers) | Free | `edge-computing` Workers patterns |
| 2 | Expo EAS documentation | Free (docs.expo.dev/eas) | Free | `react-native-advanced` EAS workflows |
| 3 | React Native New Architecture guide | Free (reactnative.dev/docs/the-new-architecture/landing-page) | Free | JSI, Fabric, TurboModules |
| 4 | WCAG 2.2 specification | Free (w3.org/TR/WCAG22) | Free | `accessibility-wcag` authoritative spec |
| 5 | Apple ARKit documentation | Free (developer.apple.com/arkit) | Free | ARKit + RealityKit patterns |
| 6 | visionOS documentation | Free (developer.apple.com/visionos) | Free | Spatial UI patterns |
| 7 | WebXR Device API specification | Free (w3.org/TR/webxr) | Free | WebXR API reference |
| 8 | *Designing for Spatial Computing* — (watch Apple WWDC sessions) | Free | Free | visionOS UX principles |

**Read first:** WCAG 2.2 spec and Cloudflare Workers docs — both free and immediately productive. Buy the Expo EAS subscription only when building React Native projects at scale.

---

## The Complete Engine — Final State

After Phase 10, the skills library will contain **200+ skills** across every domain required to build, ship, operate, and grow world-class software:

| Layer | Skills | Status |
|-------|--------|--------|
| Architecture & Design | system-architecture-design, database-design-engineering, distributed-systems-patterns, microservices-* | Complete |
| Infrastructure | cloud-architecture, kubernetes-platform, infrastructure-as-code, cicd-pipelines, cicd-devsecops | Phase 01+03 |
| Backend | nodejs-development, php-modern-standards, api-design-first, graphql-patterns, event-driven-architecture | Complete |
| Frontend | react-development, nextjs-app-router, typescript-mastery, tailwind-css, webapp-gui-design, pwa-offline-first | Phase 06+07 |
| Mobile | ios-development (23 skills), android-development (11 skills), kmp-development (3 skills), react-native-advanced | Phase 06+10 |
| AI/LLM | 28 AI skills + multimodal-ai | Phase 09+10 |
| Data | MySQL (7), PostgreSQL (6), database-internals, database-reliability | Complete |
| Security | 9 security skills + network security enhancement | Phase 07 |
| Observability | observability-platform + SRE enhancements | Phase 04 |
| Quality | e2e-testing, advanced-testing-strategy, android-tdd, ios-tdd, kmp-tdd | Phase 05 |
| Revenue | stripe-payments, subscription-billing, ai-saas-billing | Phase 02 |
| Growth | product-led-growth, saas-growth-metrics, saas-business-metrics | Phase 08 |
| UX/Design | 19 UI/UX skills + accessibility-wcag | Phase 10 |
| Frontier | edge-computing, ar-vr-interfaces | Phase 10 |
| Business | software-business-models, technology-grant-writing, engineering-management-system | Complete |

This is the engine. Every skill dual-compatible. Every skill validated. Every skill a self-contained execution contract — usable by Claude Code, Codex, or any future AI coding assistant that can read a SKILL.md.

---

*Return to index → `docs/plans/engine-phases/00-engine-roadmap-index.md`*
