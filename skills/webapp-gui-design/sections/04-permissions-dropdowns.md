## Permissions (Required)

- Apply **page-level permissions** for sensitive screens (e.g., admin settings, financial configuration).
- Apply **action-level permissions** for sensitive buttons (create/edit/delete/export), so users only see actions they are allowed to perform.
- **Do not add new permissions** for features that are available to all users. Use existing roles/permissions and keep access simple unless a business rule requires restriction.
- When in doubt: protect destructive actions, keep read-only views available to broader roles.

## Searchable Dropdowns (Required)

- Any dropdown that can exceed **30 items in production** must be a searchable Select2 (or equivalent).
- Configure search to match **at least two attributes** where possible:
  - Students: name + registration number
  - Clients/customers: name + phone
  - Diseases: disease name + ICD number
  - Medicines: brand name + generic name + item code
  - Stock items/products: name + code

### Dropdown Testing (MANDATORY Before Marking Features Complete)

**CRITICAL:** Never mark a feature as "production ready" or "fully implemented" without testing dropdowns i.e the logic that loads them must return data, test these.

**Testing Requirements:**

✅ **Test in Browser** - Load the page and verify:

- Dropdown populates with data (not empty)
- Search functionality works
- API calls succeed (check Network tab)
- Console shows no errors

✅ **Add Console Logging** - For dynamic dropdowns:

```javascript
async function loadGroups() {
  console.log("Loading customer groups...");
  const result = await apiGet(`${apiBase}/customer-groups.php`, false);

  if (!result || !result.success) {
    console.error("❌ Failed to load customer groups:", result?.message);
    return;
  }

  const groups = result?.data?.groups || [];
  console.log("✅ Customer groups loaded:", groups.length, "items");
  // ... populate dropdown
}
```

✅ **Error Handling** - API calls for dropdowns should:

- Not show SweetAlert errors on page load (use `showErrors = false` parameter)
- Log errors to console with clear ❌ prefix
- Show user-friendly warning only if critical data fails
- Handle empty arrays gracefully

❌ **Common Mistakes:**

- Marking feature complete without browser testing
- API returning empty array but no error logged
- Silent failures (dropdown stays empty, no console error)
- Using wrong API endpoint path
- API response structure doesn't match expected format

**Example Error Handling:**

```javascript
async function apiGet(url, showErrors = true) {
  try {
    console.log("API GET:", url);
    const resp = await fetch(url, {
      method: "GET",
      credentials: "same-origin",
    });

    const json = await resp.json().catch((e) => {
      console.error("JSON parse error:", e);
      return null;
    });

    if (!json) {
      if (showErrors)
        await Swal.fire("Error", "Invalid server response", "error");
      return null;
    }

    return json;
  } catch (error) {
    console.error("❌ API GET exception:", error);
    if (showErrors) await Swal.fire("Error", "Network error occurred", "error");
    return null;
  }
}
```

### Select2 Visual Styling (Standard)

**Make searchable dropdowns visually distinct with a cream background:**

This helps users immediately identify which dropdowns are searchable vs. static.

```css
/* Custom styling for Select2 searchable dropdowns */
.select2-container--bootstrap-5 .select2-selection {
  background-color: #faf9f5 !important;
  border: 1px solid #d4c5a9 !important;
  transition: all 0.2s ease;
}

.select2-container--bootstrap-5 .select2-selection:hover {
  background-color: #f5f3ed !important;
  border-color: #c4b599 !important;
}

.select2-container--bootstrap-5.select2-container--focus .select2-selection,
.select2-container--bootstrap-5.select2-container--open .select2-selection {
  background-color: #ffffff !important;
  border-color: #0d6efd !important;
  box-shadow: 0 0 0 0.25rem rgba(13, 110, 253, 0.15);
}

/* Add a small search icon indicator */
.select2-container--bootstrap-5 .select2-selection--single::before {
  content: "\f52a";
  font-family: "bootstrap-icons";
  position: absolute;
  right: 30px;
  top: 50%;
  transform: translateY(-50%);
  color: #6c757d;
  font-size: 0.875rem;
  pointer-events: none;
}

/* Dropdown results styling */
.select2-container--bootstrap-5 .select2-dropdown {
  border-color: #d4c5a9;
}

.select2-container--bootstrap-5
  .select2-search--dropdown
  .select2-search__field {
  background-color: #faf9f5;
  border-color: #d4c5a9;
}

.select2-container--bootstrap-5
  .select2-search--dropdown
  .select2-search__field:focus {
  background-color: #ffffff;
  border-color: #0d6efd;
}
```

**Visual States:**

- **Default (closed):** Cream background (`#faf9f5`), tan border, search icon visible
- **Hover:** Slightly darker cream (`#f5f3ed`), darker tan border
- **Focus/Open:** White background, blue border with glow (standard focus state)
- **Dropdown search:** Cream background matching main input

**Why This Works:**

✅ **Visual affordance** - Users immediately see which dropdowns are searchable
✅ **Subtle distinction** - Cream color is noticeable but not jarring
✅ **Progressive enhancement** - Regular dropdowns remain standard white
✅ **Accessibility** - Maintains proper contrast ratios
✅ **Consistency** - All searchable dropdowns have same styling

**Usage Example:**

```javascript
// Initialize Select2 with Bootstrap 5 theme (required for styling)
$("#filterAgent").select2({
  placeholder: "Search agents...",
  allowClear: true,
  width: "100%",
  theme: "bootstrap-5", // Required for cream styling
});
```

**Note:** The `theme: 'bootstrap-5'` parameter is required for the cream styling to apply correctly.
