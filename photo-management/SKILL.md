---
name: photo-management
description: Manage photo uploads, previews, storage, and deletion across the app.
  Use when building any photo upload UI or API, and always apply client-side compression
  via image-compression before upload.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---


## Platform Notes

- Optional helper plugins may help in some environments, but they must not be treated as required for this skill.

# Photo Management

<!-- dual-compat-start -->
## Use When

- Manage photo uploads, previews, storage, and deletion across the app. Use when building any photo upload UI or API, and always apply client-side compression via image-compression before upload.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `photo-management` or would be better handled by a more specific companion skill.
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
## Overview

Standardize photo upload UX, storage, and deletion patterns for all modules (DPC shops, assets, products, staff, etc.). Always compress images before upload using the Image Compression skill.

## Security Baseline (Required)

Always load and apply the **Vibe Security Skill** for upload flows (XSS, CSRF, file validation, path traversal, and access control are mandatory).

**Cross-Platform:** Upload code runs on Windows (dev) and Linux (staging/production). Use forward-slash paths in PHP. Check `is_dir()` before `mkdir()`. File permissions: use `0755` for directories, `0644` for files. Never hardcode Windows paths in upload logic.

## Entity Photo Rules (Mandatory)

### A) People / Individual Entities (1 photo max)

**Examples:** distributor, client, customer, employee, student, patient, member.

- **Limit:** 1 photo per individual.
- **Default image:** `uploads/<entity>/default.jpg` (always present).
- **Card list view:** Use a **social media-style card** (like `staff-list.php`) with:
  - Circular avatar.
  - Banner background: `uploads/<entity>/background.jpg`.
  - Status + quick actions.
- **Detail view:** Show the avatar prominently with edit/upload UI near it.

### B) Non‑People Entities (3 photos max)

**Examples:** products, farms, vehicles, animals, crops, stock items, buildings, assets, shops.

- **Limit:** 3 photos per entity.
- **Default image:** `uploads/<entity>/default.jpg`.
- **Card list view:** Use a **banner-style card** (like `dpcs.php`):
  - Banner image = random pick among the 3 photos.
  - If none, use default.jpg.
- **Detail view:** show minimal gallery (3-photo grid) above tabs (like `dpc-details.php`).

## Quick Reference

- **UI upload flow:** compress → preview → auto-upload → reload gallery
- **Storage:** per-module folders in `uploads/` with defaults
- **Deletion:** confirm → delete DB row → delete file
- **Limits:** hide upload UI when max count reached

## Core Instructions

1. **Always apply compression**
   - Load and use `image-compression` rules.
   - Use `window.prepareImageUpload()` for client-side compression.
2. **Validate on server**
   - Enforce file type and size limits.
   - Verify franchise ownership before write/delete.
3. **Keep UX minimal**
   - Auto-upload on file selection.
   - Use SweetAlert2 for errors and confirmations.
4. **Respect limits**
   - 1 photo for people; 3 photos for non-people entities.
   - Hide upload UI when limit reached.

## Minimalistic Detail Page Pattern (3‑Photo Entities)

Follow the `dpc-details.php` approach:

- **Photo section above tabs**, compact, 3 columns.
- **Auto-upload on file selection** (no explicit “Upload” button).
- **Upload UI hidden** when 3 photos exist.
- **Lightbox preview** on click.
- **Delete button** overlay only when permission is granted.

## Card List Pattern

### Non‑People Entities (banner cards)

- Banner image = random pick among the 3 photos.
- If none, fallback to default.jpg.
- Keep the card minimal: image + name + status + 1–2 meta lines.

### People Entities (social cards)

- Use `background.jpg` as banner.
- Circular avatar (photo or default.jpg).
- Name + role/position + 1–2 meta lines.
- Actions inline (view/edit) with compact buttons.
- Ensure the avatar overlap is visible (no clipping): set card `overflow: visible` or position avatar inside banner with `position: absolute` and higher `z-index`.
- Prefer overlapping **only the avatar** (not the text): apply negative margin to the avatar itself, keep header text flow normal.

## Key Patterns

### Upload (client)

- Input change → compress → size check → `FormData` → POST → reload gallery.

### Gallery (client)

- Render a grid with a max of 3 items.
- Hide uploader when full.
- Show delete button only for authorized users.

### API (server)

- **GET:** return photo list with URLs.
- **POST:** validate, store, insert DB row.
- **DELETE:** validate ownership, remove DB row and file.

## API Response Format (Align with Maduuka)

Use the standard JSON envelope used across the app:

- Success:
  - `success: true`, `message`, `data`, `timestamp`
- Validation error:
  - `success: false`, `message`, `errors`

Keep payloads lean: return only `id`, `file_name`, `file_path`, `created_at`.

## Database Schema Tips (Maduuka Best Practice)

- Store **relative** file path (e.g., `uploads/dpc-photos/abc.jpg`).
- Index `(franchise_id, entity_id)` for fast retrieval.
- Store `created_by`, `created_at` for auditability.
- Prefer soft delete only if required by audit rules; otherwise hard delete with file cleanup.

## Security & Efficiency

- Verify **franchise ownership** on every read/write/delete.
- Enforce allowed MIME types and extensions server-side.
- Use unique filenames (timestamp + random suffix), never trust original names.
- Cap size after compression; reject oversized images.
- Clean up orphaned files if DB insert fails.
- Use transactions for multi-step delete (DB + file).
- Return 404 for missing records and 403 for cross-franchise access.

## Tips & Tricks (Efficiency + UX)

- Use `object-fit: cover` for all thumbnails.
- Use consistent sizes (e.g., 3-column grid with fixed height) to avoid layout shift.
- Use `loading="lazy"` for card images in large lists.
- Cache the photo list per entity on load; only refresh after upload/delete.
- Use unique file names (timestamp + random suffix) to avoid collisions.
- Always store **relative file paths** in DB.
- Avoid re-uploading if the same file is selected twice; reset input after upload.
- Prefer CDN/local caching headers for read-heavy image endpoints where applicable.

## Reference Files

- Use `image-compression/SKILL.md` for compression defaults and rules.

## Common Pitfalls

- Skipping compression (breaks bandwidth/storage goals).
- Missing `franchise_id` filter on queries.
- Leaving upload UI visible when max photos already exist.
- Using native `alert()` instead of SweetAlert2.

## Examples

- DPC photo management: `api/dpc-photos.php` + client gallery pattern.
- Asset photo management: `api/asset-photos.php` + client gallery pattern.
