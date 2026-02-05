# Web App GUI Design

Build professional web UIs using commercial templates with established component patterns.

**Core Principle:** Start with templates, follow modular architecture, maintain consistency.

**API-First Rule (Required):** Frontend must never access the database directly. All reads/writes go through backend services exposed via APIs so future clients (Android, iOS, etc.) reuse the same logic.

## When to Use

✅ CRUD interfaces, admin panels, dashboards
✅ Data management UIs
✅ Need professional look fast

✅ When asked for polished frontend aesthetics inside a web app

❌ Marketing sites (not covered by this skill)
❌ Mobile-native apps

## Stack

- **Base:** Tabler (Bootstrap 5.3.0)
- **Icons:** Bootstrap Icons only (`bi-*`)
- **Alerts:** SweetAlert2 (NO native alert/confirm)
- **Tables:** DataTables + Bootstrap 5
- **Dates:** Flatpickr (auto-applied)
- **Selects:** Select2
