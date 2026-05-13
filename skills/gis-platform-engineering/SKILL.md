---
name: gis-platform-engineering
description: Use when implementing GIS maps, spatial data services, maps integrations, geocoding, spatial APIs, or PostGIS-backed geospatial platforms. Load absorbed GIS mapping, maps integration, and PostGIS backend references as needed.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

# GIS Platform Engineering
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

Use this parent skill as the active GIS implementation entrypoint. Keep enterprise concepts in `gis-enterprise-domain`; use this skill for build, integration, and platform engineering.

<!-- dual-compat-start -->
## Use When

- Building GIS map interfaces, layers, spatial search, geocoding flows, route displays, or geospatial APIs.
- Integrating third-party map providers, tile services, location capture, or spatial analytics.
- Designing PostGIS-backed storage, indexes, queries, and backend services for geospatial products.

## Do Not Use When

- The task is unrelated to this parent skill or is better handled by a narrower active parent named in the workflow.
- The request only needs a trivial answer and no reference module needs to be loaded.

## Required Inputs

- Gather the concrete system, repository, environment, constraints, and deliverable before loading references.
- Identify which absorbed reference file is needed; do not load every migrated reference by default.
## Workflow

1. Load `gis-enterprise-domain` for domain boundaries, organisational concepts, and GIS vocabulary.
2. Load the needed implementation reference:
   - `references/gis-mapping.md` for map UI, layers, markers, controls, and interaction.
   - `references/gis-maps-integration.md` for map providers, geocoding, routing, and external integrations.
   - `references/gis-postgis-backend.md` for PostGIS schema, indexing, spatial SQL, and backend patterns.
3. Pair with `database-design-engineering`, `postgresql-engineering`, `api-design-first`, and frontend skills when the GIS work crosses those boundaries.

## Quality Standards

- Treat coordinate reference systems, precision, privacy, and offline/low-bandwidth constraints as first-class design inputs.
- Make spatial indexes, query shape, geometry validity, and API payload size explicit for backend work.
- Keep map UI usable for inspection, comparison, filtering, and task completion, not only visual display.

## Anti-Patterns

- Treating absorbed reference files as active skills or separate routing entrypoints.
- Loading every migrated child reference instead of the one that matches the task.
- Producing generic advice without constraints, evidence, or next verification steps.
## Outputs

- GIS implementation plan, map UI spec, spatial API/schema, integration notes, or PostGIS review.

## References

- Load only the eferences/<old-skill>.md files named in the workflow when their depth is required.
<!-- dual-compat-end -->
