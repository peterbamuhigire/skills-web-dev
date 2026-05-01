# TypeScript, Kubernetes, GIS, and Sales Skills — Design Spec

**Date:** 2026-04-15
**Author:** Peter Bamuhigire (with Claude Code, Opus 4.6)
**Status:** Approved — ready for scaffolding

## Purpose

Close three capability gaps and add one business skill so the repository can rival the engineering bar at Apple / Google for the stacks we actually use:

- **TypeScript:** extend beyond type system + GoF patterns into production idioms and full-stack type safety.
- **Kubernetes:** greenfield — from fundamentals to multi-tenant SaaS delivery.
- **GIS:** extend beyond Leaflet frontend into PostGIS backend, Google Maps / Mapbox integration, and enterprise/real-estate domain patterns.
- **SaaS Sales Organisation:** add business-side sales org design alongside existing metrics/pricing/billing skills.

## Existing coverage (what we build on)

- `typescript-mastery` — type system deep dive
- `typescript-design-patterns` — 23 GoF in TS
- `gis-mapping` — Leaflet frontend, geofencing validation
- `cloud-architecture` — AWS/GCP, Docker, single-host to multi-AZ
- `saas-business-metrics`, `subscription-billing`, `software-pricing-strategy`, `software-business-models` — monetisation side
- `cicd-pipelines`, `cicd-devsecops`, `cicd-jenkins-debian` — pipeline side
- `linux-security-hardening`, `network-security`, `vibe-security-skill` — security side

## Quality bar

- Concrete decision rules with thresholds, not vague advice.
- Production-grade patterns drawn from source books.
- Runnable code examples.
- Cross-references between skills in this set and existing skills.
- British English, plain markdown, no emojis.
- SKILL.md under 500 lines, depth in `references/`.

## Skill set (9 skills)

### 1. `typescript-effective`

**Purpose:** Production-grade TypeScript beyond the type system and GoF — idioms, clean code, migration, build performance, anti-patterns.

**Sources:** *Clean Code with TypeScript*, *Effective TypeScript*, *TypeScript Mini Reference*.

**SKILL.md sections:**
- When to use (code review, new projects, migrating JS, fixing "any" drift)
- TypeScript config for production (strict, noUncheckedIndexedAccess, exactOptionalPropertyTypes, noImplicitOverride)
- Core effective-TS items (avoid `any`, prefer union over enum for small sets, narrow before use, discriminated unions, exhaustive checks)
- Clean code in TS (small functions, names, comments, SOLID applied to TS)
- Error handling patterns (Result/Either, typed errors, never throw `any`)
- API boundaries (validate input with Zod, don't trust `unknown`)
- Migration strategies (`allowJs`, `checkJs`, JSDoc types, gradual strict)
- Build performance (project references, incremental, isolatedModules, transpile-only in dev)
- Testing patterns (vitest/jest, fixture typing, property-based with fast-check)
- Anti-patterns catalogue (type assertions, `!` non-null, `as unknown as`, enum pitfalls, `Function` type)

**references/:**
- `tsconfig-production.md`
- `effective-ts-items.md`
- `clean-code-ts.md`
- `error-handling-result.md`
- `zod-boundaries.md`
- `migration-js-to-ts.md`
- `build-performance.md`
- `testing-vitest.md`
- `anti-patterns.md`

### 2. `typescript-full-stack`

**Purpose:** End-to-end TypeScript stack with shared types FE↔BE, validated boundaries, monorepo patterns.

**Sources:** *Full-Stack Web Development with TypeScript 5*.

**SKILL.md sections:**
- When to use (new TS app greenfield, unifying FE+BE, refactoring an Express/JS backend)
- Architecture (Fastify or Express on backend, React/Next on frontend, shared types package, Zod schemas as source of truth)
- Monorepo with turborepo or nx (pnpm workspaces, shared packages, caching)
- tRPC for internal APIs (end-to-end types without OpenAPI)
- REST + OpenAPI when external clients exist (ts-rest, zod-to-openapi)
- Data layer (Prisma, Drizzle — decision rule)
- Validation at every boundary (Zod)
- Auth patterns (Lucia, better-auth, NextAuth)
- Testing the full stack (vitest + Playwright)
- Deployment (Docker, Node-slim, multi-stage, env handling)

**references/:**
- `monorepo-turborepo.md`
- `fastify-backend.md`
- `trpc-end-to-end.md`
- `rest-plus-openapi.md`
- `prisma-vs-drizzle.md`
- `zod-shared-schemas.md`
- `auth-patterns.md`
- `testing-full-stack.md`
- `docker-node-production.md`

### 3. `kubernetes-fundamentals`

**Purpose:** K8s core objects and mental model. When K8s is the right tool vs overkill.

**Sources:** *Kubernetes: A Comprehensive Step-by-Step Guide* (Annable), *KUBERNETES: A Simple Guide* (Docker), *Kubernetes Best Practices* (starter chapters).

**SKILL.md sections:**
- When to use K8s (vs systemd, vs Docker Compose, vs ECS/Fargate, vs PaaS)
- Core objects (Pod, Deployment, Service, Ingress, ConfigMap, Secret, Namespace, PersistentVolume)
- Manifests + kubectl workflow
- Declarative vs imperative
- Labels/selectors/annotations — the glue
- Probes (liveness, readiness, startup) and their semantics
- Service types (ClusterIP, NodePort, LoadBalancer) and Ingress controllers (nginx, Traefik)
- Cluster bootstrap options (kubeadm, kind for local, EKS, GKE) with decision rule
- Anti-patterns (hostPath volumes, latest tags, no resource requests/limits)

**references/:**
- `when-k8s-is-right.md`
- `core-objects.md`
- `kubectl-workflow.md`
- `probes-and-lifecycles.md`
- `ingress-controllers.md`
- `cluster-setup-eks-gke.md`
- `local-kind-minikube.md`
- `anti-patterns.md`

### 4. `kubernetes-production`

**Purpose:** Production operations on K8s — Helm, autoscaling, resource management, observability, security baseline.

**Sources:** *Kubernetes Best Practices*, *Comprehensive Guide* production chapters.

**SKILL.md sections:**
- Helm charts (templates, values, dependencies, versioning) vs Kustomize
- Resource requests + limits (how to size, CPU/memory units, OOMKilled prevention)
- HorizontalPodAutoscaler (CPU, memory, custom metrics via Prometheus Adapter)
- VerticalPodAutoscaler (when, when not)
- PodDisruptionBudget — protect against voluntary disruptions
- StatefulSets + PVCs for stateful workloads (databases, caches)
- ConfigMaps + Secrets (external-secrets operator for Vault/AWS Secrets Manager)
- Observability: Prometheus + Grafana + Loki + Alertmanager
- Security baseline: RBAC, Pod Security Standards, NetworkPolicies, image scanning (Trivy), admission control (OPA Gatekeeper or Kyverno)
- Backup + DR (Velero)
- Cost control (requests-vs-usage reports, cluster autoscaler, karpenter on AWS)

**references/:**
- `helm-vs-kustomize.md`
- `resource-management.md`
- `autoscaling-hpa-vpa.md`
- `stateful-workloads.md`
- `secrets-external-secrets.md`
- `observability-stack.md`
- `rbac-and-pod-security.md`
- `network-policies.md`
- `admission-control-opa-kyverno.md`
- `backup-velero.md`
- `cost-control.md`

### 5. `kubernetes-saas-delivery`

**Purpose:** Multi-tenant SaaS on Kubernetes + GitOps delivery + progressive delivery.

**Sources:** All 3 K8s books plus multi-tenant SaaS engineering knowledge.

**SKILL.md sections:**
- Multi-tenancy models on K8s (shared cluster + namespace per tenant, cluster per tenant, hybrid)
- Namespace isolation (ResourceQuotas, LimitRanges, NetworkPolicies per tenant)
- Tenant-aware deployment patterns (Helm values per tenant, ArgoCD ApplicationSets)
- GitOps with ArgoCD (or Flux) — App of Apps, sync waves, drift detection
- Progressive delivery (Argo Rollouts, Flagger) — canary, blue/green, analysis templates
- Secrets per tenant (namespaced external-secrets)
- Observability per tenant (Grafana folders, label-based isolation)
- Onboarding automation (create tenant = create namespace + quota + secrets + ingress)
- Offboarding + data deletion
- Cost allocation per tenant (kubecost, label-based)

**references/:**
- `multi-tenancy-models.md`
- `namespace-isolation.md`
- `gitops-argocd.md`
- `progressive-delivery.md`
- `tenant-onboarding-automation.md`
- `per-tenant-secrets.md`
- `tenant-observability.md`
- `cost-allocation.md`
- `offboarding-data-deletion.md`

### 6. `gis-postgis-backend`

**Purpose:** PostGIS as the spatial backbone — schemas, indexes, queries, tiling, performance.

**Sources:** *Mastering ArcGIS Enterprise* (server-side concepts), general PostGIS knowledge, *Real Estate and GIS* (use cases).

**SKILL.md sections:**
- When to use PostGIS vs MySQL spatial vs specialised stores
- Schema design (geometry vs geography, SRID 4326 vs 3857, picking for your region — EPSG:32636 for Uganda)
- Spatial indexes (GIST, BRIN for very large)
- Core spatial SQL (ST_Contains, ST_DWithin, ST_Distance, ST_Intersects, ST_Buffer, ST_Union, ST_ConvexHull)
- Performance patterns (clustering, partitioning large tables, index-only scans)
- Vector tile generation (MVT via ST_AsMVT, pg_tileserv)
- Geocoding (pgAdmin + geocoder extensions, or external API with cache)
- Integration with MySQL SaaS (hybrid: MySQL app DB + PostGIS spatial DB)
- Backup + migration (pg_dump with spatial ref, ogr2ogr for conversions)
- Security (RLS for tenant isolation, GRANT on spatial tables)

**references/:**
- `when-postgis.md`
- `schema-srid-choice.md`
- `spatial-indexes.md`
- `core-spatial-sql.md`
- `performance-patterns.md`
- `mvt-tiles.md`
- `geocoding.md`
- `hybrid-mysql-postgis.md`
- `backup-migration.md`
- `tenant-isolation-rls.md`

### 7. `gis-maps-integration`

**Purpose:** Google Maps JavaScript API + Mapbox GL as richer alternatives or supplements to Leaflet — including geocoding, routing, places.

**Sources:** *Google Maps JavaScript API Cookbook*, Mapbox docs knowledge.

**SKILL.md sections:**
- When to pick Leaflet vs Google Maps vs Mapbox (cost, features, licensing, offline, styling, 3D)
- Google Maps JS API setup (key restrictions, billing guardrails, loader pattern)
- Markers, InfoWindows, overlays, polylines
- Geocoding (forward + reverse), places autocomplete, distance matrix
- Directions + routes + turn-by-turn preview
- Google Maps styling (cloud-based styling vs JSON in code)
- Mapbox GL (WebGL, 3D, offline, vector styles, turn-by-turn)
- Integrating with existing `gis-mapping` Leaflet work (hybrid approach, choosing per feature)
- Cost control (API quotas, client-side caching, server-proxied calls to control keys)
- Accessibility (a11y on map interfaces, keyboard navigation)

**references/:**
- `leaflet-vs-google-vs-mapbox.md`
- `google-maps-setup-keys.md`
- `google-places-autocomplete.md`
- `google-routing-directions.md`
- `mapbox-gl-basics.md`
- `mapbox-offline.md`
- `styling-comparison.md`
- `cost-control-quotas.md`
- `a11y-maps.md`

### 8. `gis-enterprise-domain`

**Purpose:** Enterprise GIS administration patterns (ArcGIS Enterprise) + real-estate-specific GIS recipes.

**Sources:** *Mastering ArcGIS Enterprise administration*, *Real Estate and GIS*.

**SKILL.md sections:**
- When ArcGIS Enterprise beats open source (enterprise, governance, specific datasets)
- ArcGIS components (Portal, Server, Data Store, Web Adaptor) overview
- Publishing services (map, feature, image, geocoding) and versioning
- Security, roles, and groups (Portal + Server)
- Backup + disaster recovery for ArcGIS Enterprise
- Real estate GIS recipes:
  - Property search with spatial filters (within district, within school zone, walking distance to transit)
  - Neighbourhood analysis (comparables, amenities, walkability scores)
  - Service area / catchment (drive-time isochrones)
  - Boundary-aware listings (admin boundaries, custom tenant boundaries)
  - Market heatmaps (price density, demand heatmaps)
  - Route-based tours for agents
- Integrating real estate GIS with SaaS (MySQL listings + PostGIS spatial + map client)

**references/:**
- `when-arcgis-enterprise.md`
- `arcgis-components.md`
- `publishing-services.md`
- `arcgis-security-roles.md`
- `arcgis-backup-dr.md`
- `property-search-spatial.md`
- `neighbourhood-analysis.md`
- `catchment-isochrones.md`
- `market-heatmaps.md`
- `real-estate-saas-integration.md`

### 9. `saas-sales-organization`

**Purpose:** Business skill — design a SaaS sales organisation that matches product motion, segment, and deal size.

**Source:** *Blueprints for a SaaS Sales Organization* (van der Kooij, Pizarro).

**SKILL.md sections:**
- When to read this (founder-led sales → first hires; scaling from 1M to 10M ARR; designing sales ops for a new segment)
- Sales motions — picking the model (self-service, SMB transactional, mid-market, enterprise)
- Roles and specialisation (SDR/BDR, AE, CSM, SE, AM) and when to specialise
- Pipeline stages and stage definitions that stand up to scrutiny
- Lead-to-cash process (lead → MQL → SQL → opp → close → onboarding → renewal)
- Territory design (geographic, vertical, named-account, round-robin)
- Quota + commission design (OTE, accelerators, clawbacks, SPIFs)
- Sales org structure at scale (pods, geographies, inside vs field)
- Sales operations foundations (CRM hygiene, forecasting, pipeline reviews, QBRs)
- Onboarding + ramp + enablement
- Hiring rubric for each role

**references/:**
- `sales-motions-picker.md`
- `roles-specialisation.md`
- `pipeline-stages.md`
- `lead-to-cash.md`
- `territory-design.md`
- `quota-commission-design.md`
- `sales-ops-fundamentals.md`
- `forecasting-accuracy.md`
- `onboarding-ramp.md`
- `hiring-rubrics.md`

## Cross-references

- `typescript-effective` + `typescript-full-stack` reference `typescript-mastery`, `typescript-design-patterns`, `react-development`, `nextjs-app-router`.
- All K8s skills reference `cloud-architecture`, `observability-monitoring`, `cicd-pipeline-design`, `cicd-devsecops`, `deployment-release-engineering`, `multi-tenant-saas-architecture`.
- `gis-postgis-backend` references `postgresql-*` family and `database-design-engineering`.
- `gis-maps-integration` + `gis-enterprise-domain` reference `gis-mapping` (existing).
- `saas-sales-organization` references `saas-business-metrics`, `subscription-billing`, `software-pricing-strategy`, `product-strategy-vision`, `competitive-analysis-pm`.

## Validation

After scaffolding each skill:

```text
python -X utf8 skill-writing/scripts/quick_validate.py <skill-directory>
python -X utf8 skill-writing/scripts/upgrade_dual_compat.py <skill-directory>   # if needed
```

## Out of scope (non-goals)

- Deno or Bun specific runtime skills (we're on Node.js primarily).
- Cloud-specific managed K8s deep dives beyond setup (we cover EKS/GKE entry; specialised skills could follow later).
- ArcGIS Pro desktop / mobile SDK (we focus on Enterprise admin for SaaS integration).
- Sales enablement content writing or outbound copywriting (that is marketing).
- Revenue operations tooling reviews (CRM vendor picks live elsewhere).

## Sequencing

1. Scaffold all 9 skill directories with SKILL.md skeletons (this step).
2. Run dual-compat upgrader.
3. Validate each.
4. Dispatch 9 parallel agents, one per skill, to write all reference files.
5. Re-validate.
6. Update `README.md`, `CLAUDE.md`, `PROJECT_BRIEF.md`.

Skill build order (if serial): TS first (2), then K8s (3), then GIS (3), then sales (1). With parallel agents, all run concurrently.

## Update points for repository docs

- `README.md` — new TypeScript, Kubernetes, GIS, and Sales sections; bump count from 199 to 208.
- `CLAUDE.md` — add Kubernetes baseline, extend TypeScript baseline, extend GIS baseline, note the sales addition.
- `PROJECT_BRIEF.md` — add "Kubernetes, Full-Stack TypeScript, Enterprise GIS, and Sales Organisation" as capability additions.
