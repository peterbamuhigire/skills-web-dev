# Gold Standard Example — User Profile Update

**Path:** `docs/plans/auth/user-profile-update.md`

---

# User Profile Update — Spec
**Status:** Draft

## User Story
As a **logged-in user**, I want to **update my profile details** so that **my account information stays accurate**.

## Acceptance Criteria (Definition of Done)
- [ ] User can update name, email, phone, and preferred language.
- [ ] Email uniqueness is enforced.
- [ ] Changes are audited with updated timestamp.
- [ ] Invalid input returns clear validation errors.
- [ ] Update is restricted to the user’s own profile.

## Technical Constraints
- Use existing auth session for user identity.
- Enforce validation server-side (email format, required fields).
- Use existing database migration mechanism for schema changes.

## Data Model
- **Tables:** `tbl_users`
- **Columns:**
  - `tbl_users.full_name` — VARCHAR(150) — display name
  - `tbl_users.phone` — VARCHAR(30) — contact number
  - `tbl_users.preferred_language` — ENUM('en','fr','ar','sw','es') — i18n preference
  - `tbl_users.updated_at` — TIMESTAMP — audit update time
- **Indexes/Constraints:**
  - UNIQUE(`email`)

## Execution Plan
1. Add/verify columns and constraints — `database/patches/XXX-user-profile-update.sql`
2. Implement service method for profile update — `src/Services/UserProfileService.php`
3. Add API endpoint for update — `api/user-profile.php`
4. Add UI form and client validation — `public/profile.php`
5. Add translations for labels/messages — `src/lang/en.php`, `src/lang/fr.php`, `src/lang/ar.php`, `src/lang/sw.php`, `src/lang/es.php`
