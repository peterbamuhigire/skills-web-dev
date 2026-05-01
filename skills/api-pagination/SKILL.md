---
name: api-pagination
description: Offset pagination pattern for PHP REST APIs and mobile clients (Android
  Jetpack Compose + iOS SwiftUI). Covers backend response format, client DTOs, repository,
  ViewModel state, and infinite-scroll UI. Use when adding pagination to any list
  endpoint.
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

## Platform Notes

- Optional helper plugins may help in some environments, but they must not be treated as required for this skill.

# API Pagination Skill
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Offset pagination pattern for PHP REST APIs and mobile clients (Android Jetpack Compose + iOS SwiftUI). Covers backend response format, client DTOs, repository, ViewModel state, and infinite-scroll UI. Use when adding pagination to any list endpoint.
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `api-pagination` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve; load `references` only as needed.
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

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Correctness | Pagination test plan | Markdown doc covering offset, limit, edge cases (empty, last page, oversized), and stable sort | `docs/api/pagination-tests.md` |

## References

- Use the `references/` directory for deep detail after reading the core workflow below.
<!-- dual-compat-end -->
## Overview

Standard offset-based pagination pattern used across the Maduuka platform. Applies to the PHP backend (REST API) and mobile clients (Android Kotlin + Compose, iOS SwiftUI).

**Pattern:** Backend returns `data.items[]` + `data.pagination{}`. Mobile clients append items on scroll, track page/totalPages in ViewModel state.

**Deployment:** Backend runs on Windows dev (MySQL 8.4.7), Ubuntu staging (MySQL 8.x), Debian production (MySQL 8.x). Pagination queries must use `utf8mb4_unicode_ci` collation and work identically on all platforms.

## PHP Backend Pattern

### Response Format (MANDATORY)

Every paginated list endpoint MUST return this structure:

```json
{
  "success": true,
  "data": {
    "items": [ ... ],
    "pagination": {
      "page": 1,
      "per_page": 30,
      "total": 142,
      "total_pages": 5
    }
  }
}
```

### PHP Implementation Template

```php
<?php
declare(strict_types=1);
require_once __DIR__ . '/../middleware.php';

require_method('GET');
$auth = require_auth();
$db   = get_db();

$franchiseId = (int)$auth['franchise_id'];
$page        = max(1, (int)($_GET['page'] ?? 1));
$perPage     = min(100, max(1, (int)($_GET['per_page'] ?? 30)));
// Optional filters
$status      = isset($_GET['status']) ? trim((string)$_GET['status']) : '';

try {
    $where  = 't.franchise_id = :fid';
    $params = ['fid' => $franchiseId];

    if ($status !== '') {
        $where .= ' AND t.status = :status';
        $params['status'] = $status;
    }

    // 1. Count total
    $countSql = "SELECT COUNT(*) FROM tbl_example t WHERE {$where}";
    $countStmt = $db->prepare($countSql);
    $countStmt->execute($params);
    $total = (int)$countStmt->fetchColumn();
    $countStmt->closeCursor();   // IMPORTANT for PDO

    $totalPages = $total > 0 ? (int)ceil($total / $perPage) : 1;
    $offset = ($page - 1) * $perPage;

    // 2. Fetch page
    $sql = "SELECT t.* FROM tbl_example t WHERE {$where}
            ORDER BY t.created_at DESC
            LIMIT :lim OFFSET :off";

    $queryParams = $params;
    $queryParams['lim'] = $perPage;
    $queryParams['off'] = $offset;

    $stmt = $db->prepare($sql);
    foreach ($queryParams as $key => $value) {
        if ($key === 'lim' || $key === 'off') {
            $stmt->bindValue($key, $value, PDO::PARAM_INT);
        } else {
            $stmt->bindValue($key, $value);
        }
    }
    $stmt->execute();
    $rows = $stmt->fetchAll(PDO::FETCH_ASSOC);

    // 3. Return with pagination metadata
    json_response(200, [
        'success' => true,
        'data'    => [
            'items'      => $rows,
            'pagination' => [
                'page'        => $page,
                'per_page'    => $perPage,
                'total'       => $total,
                'total_pages' => $totalPages,
            ],
        ],
    ]);
} catch (Throwable $e) {
    json_response(500, [
        'success' => false,
        'message' => 'Failed to load items',
        'error'   => $e->getMessage(),
    ]);
}
```

### Key PHP Rules

1. **Always `closeCursor()`** after the COUNT query before running the main query (PDO requirement).
2. **Bind LIMIT/OFFSET as `PDO::PARAM_INT`** — string binding causes MySQL errors.
3. **Cap `per_page`** at 100 to prevent abuse: `min(100, max(1, ...))`.
4. **Default `per_page`** is 30 for list screens, 50 for stock-level screens.
5. **Response shape** is `data.items` + `data.pagination` — NEVER return a flat array in `data`.

## Additional Guidance

Extended guidance for `api-pagination` was moved to [references/skill-deep-dive.md](references/skill-deep-dive.md) to keep this entrypoint compact and fast to load.

Use that deep dive for:
- `Android Client Pattern`
- `Key Compose Imports for Pagination`
- `iOS Client Pattern`
- `Important Rules`
- `Existing Implementations`