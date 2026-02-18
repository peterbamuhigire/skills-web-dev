# Web App GUI Design

Build professional web UIs using commercial templates with established component patterns.

**Core Principle:** Start with templates, follow modular architecture, maintain consistency.

**API-First Rule (Required):** Frontend must never access the database directly. All reads/writes go through backend services exposed via APIs so future clients (Android, iOS, etc.) reuse the same logic.

**Cross-Platform:** Code deploys to Windows (dev), Ubuntu (staging), and Debian (production). Use forward slashes in PHP include paths. Match exact file/directory case (Linux is case-sensitive). Never hardcode Windows paths in application code.

## When to Use

✅ CRUD interfaces, admin panels, dashboards
✅ Data management UIs
✅ Need professional look fast

✅ When asked for polished frontend aesthetics inside a web app

❌ Marketing sites (not covered by this skill)
❌ Mobile-native apps

## Interface Design Checklist

Use this for dashboards, admin panels, SaaS apps, tools, settings pages, and data interfaces. Follow [skills/webapp-gui-design/sections/09-interface-design.md](skills/webapp-gui-design/sections/09-interface-design.md) before proposing UI direction or writing UI code:

1. Define human, verb, feel.
2. Produce Domain, Color world, Signature, Defaults.
3. Replace each default deliberately.
4. Run swap, squint, signature, token checks.

## Stack

- **Base:** Tabler (Bootstrap 5.3.0)
- **Icons:** Bootstrap Icons only (`bi-*`)
- **Alerts:** SweetAlert2 (NO native alert/confirm)
- **Tables:** DataTables + Bootstrap 5
- **Dates:** Flatpickr (auto-applied)
- **Selects:** Select2
