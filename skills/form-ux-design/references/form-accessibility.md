# Form Accessibility Reference

Cross-platform accessibility patterns for **web** (Bootstrap 5 / Tabler) and **Android** (Jetpack Compose + Material 3). Every form built with `form-ux-design` MUST meet these standards.

---

## 1. Label Requirements

Every input MUST have a visible label. Never use placeholder-only inputs.

### Web: Correct vs Incorrect

```html
<!-- CORRECT: label linked via for/id -->
<div class="mb-3">
  <label class="form-label" for="full-name">Full Name <span aria-hidden="true">*</span></label>
  <input type="text" class="form-control" id="full-name" name="full_name"
         required aria-required="true" placeholder="e.g. Jane Doe">
</div>

<!-- INCORRECT: placeholder-only, no visible label -->
<input type="text" class="form-control" placeholder="Full Name">
```

### Android: Correct vs Incorrect

```kotlin
// CORRECT: label parameter provides visible + accessible label
OutlinedTextField(
    value = name, onValueChange = { name = it },
    label = { Text("Full Name *") },
    placeholder = { Text("e.g. Jane Doe") },
    modifier = Modifier.fillMaxWidth()
)

// INCORRECT: no label, placeholder only (disappears on focus)
OutlinedTextField(
    value = name, onValueChange = { name = it },
    placeholder = { Text("Full Name") },
    modifier = Modifier.fillMaxWidth()
)
```

### Label Rules

- Position: always above the input (stacked layout)
- Required indicator: asterisk `*` in label text
- Web: also add `aria-required="true"` and `required` attribute
- Android: include `*` in label string; use `semantics { stateDescription = "Required" }`
- Label must remain visible when focused and when filled

---

## 2. ARIA Attributes for Forms (Web)

| Attribute | Purpose | When to Apply |
|-----------|---------|---------------|
| `aria-describedby` | Link helper text and error messages | Every field with helper or error text |
| `aria-invalid="true"` | Mark field as having a validation error | When validation fails |
| `aria-required="true"` | Mark field as required | All required fields |
| `aria-live="polite"` | Announce dynamic content changes | Error message containers |
| `role="alert"` | Immediate announcement | Error summary banner on submit |
| `aria-errormessage` | Link specific error message element | Fields with dedicated error elements |
| `aria-labelledby` | Complex label associations | Compound labels or fieldset alternatives |

### Complete ARIA Pattern

```html
<div class="mb-3">
  <label class="form-label required" for="email">Email Address</label>
  <input type="email" class="form-control" id="email" name="email"
         required aria-required="true"
         aria-describedby="email-help email-error"
         aria-errormessage="email-error"
         placeholder="you@company.com" autocomplete="email">
  <div id="email-help" class="form-text">We will never share your email.</div>
  <div id="email-error" class="invalid-feedback" aria-live="polite" role="alert">
    Please enter a valid email address.
  </div>
</div>
```

### Toggling Invalid State

```javascript
function markFieldInvalid(input, errorMsg) {
    input.classList.add('is-invalid');
    input.setAttribute('aria-invalid', 'true');
    const errorEl = document.getElementById(input.getAttribute('aria-errormessage'));
    if (errorEl) errorEl.textContent = errorMsg;
}
function markFieldValid(input) {
    input.classList.remove('is-invalid');
    input.removeAttribute('aria-invalid');
}
```

### Error Summary Banner

```html
<div id="form-errors" role="alert" class="alert alert-danger d-none">
  <strong>Please fix the following errors:</strong>
  <ul id="error-list"></ul>
</div>
```

---

## 3. Compose Semantics for Forms (Android)

| Property | Purpose | Usage |
|----------|---------|-------|
| `contentDescription` | Label for icon-only buttons | `semantics { contentDescription = "Clear field" }` |
| `error()` | Announce validation errors | `semantics { if (hasError) error(msg) }` |
| `stateDescription` | Field state info | `semantics { stateDescription = "Required" }` |
| `liveRegion` | Dynamic content updates | `semantics { liveRegion = LiveRegionMode.Polite }` |
| `role` | Explicit role assignment | `semantics { role = Role.TextField }` |

### Accessible TextField Composable

```kotlin
@Composable
fun AccessibleTextField(
    value: String, onValueChange: (String) -> Unit,
    label: String, isRequired: Boolean = false,
    error: String? = null, helperText: String? = null,
    modifier: Modifier = Modifier
) {
    OutlinedTextField(
        value = value, onValueChange = onValueChange,
        label = { Text(if (isRequired) "$label *" else label) },
        isError = error != null,
        supportingText = {
            Text(
                text = error ?: helperText ?: "",
                color = if (error != null) MaterialTheme.colorScheme.error
                        else MaterialTheme.colorScheme.onSurfaceVariant
            )
        },
        modifier = modifier.fillMaxWidth().semantics {
            if (isRequired) stateDescription = "Required"
            if (error != null) { error(error); liveRegion = LiveRegionMode.Polite }
        }
    )
}
```

### Icon-Only Button and Compound Field

```kotlin
// Icon button: set contentDescription on parent, null on Icon
IconButton(
    onClick = onClear,
    modifier = Modifier.semantics { contentDescription = "Clear search field" }
) { Icon(Icons.Default.Close, contentDescription = null) }

// Compound field: merge descendants for single announcement
Row(modifier = Modifier.semantics(mergeDescendants = true) {
    contentDescription = "Phone number with country code"
}) {
    CountryCodeDropdown(selected = code, onSelect = { code = it })
    OutlinedTextField(value = phone, onValueChange = { phone = it }, label = { Text("Phone") })
}
```

---

## 4. Keyboard Navigation (Web)

### Tab Order Rules

- Tab order MUST follow visual order -- never use `tabindex` greater than 0
- `tabindex="0"`: custom interactive elements not natively focusable
- `tabindex="-1"`: programmatically focusable only, not in tab order

### Expected Keyboard Behavior

| Key | Behavior |
|-----|----------|
| Tab / Shift+Tab | Move focus forward / backward |
| Enter | Submit form (unless in `<textarea>`) |
| Escape | Close dropdown, modal, or popover |
| Arrow Up/Down | Navigate radio groups and select options |
| Space | Toggle checkbox, activate button, select radio |

### Skip Link and Focus Trap

```html
<!-- Skip link for long forms -->
<a href="#form-actions" class="visually-hidden-focusable">Skip to form actions</a>
```

```javascript
// Focus trap for modals containing forms
function trapFocus(modal) {
    const focusable = modal.querySelectorAll('input, select, textarea, button, [tabindex="0"]');
    const first = focusable[0], last = focusable[focusable.length - 1];
    modal.addEventListener('keydown', (e) => {
        if (e.key !== 'Tab') return;
        if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
        else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    });
    first.focus();
}
```

---

## 5. Keyboard and IME Actions (Android)

### IME Action Chain

```kotlin
@Composable
fun MultiFieldForm(onSubmit: () -> Unit) {
    val focusManager = LocalFocusManager.current

    OutlinedTextField(
        value = firstName, onValueChange = { firstName = it },
        label = { Text("First Name *") },
        keyboardOptions = KeyboardOptions(imeAction = ImeAction.Next),
        keyboardActions = KeyboardActions(onNext = { focusManager.moveFocus(FocusDirection.Down) }),
        modifier = Modifier.fillMaxWidth()
    )
    OutlinedTextField(
        value = email, onValueChange = { email = it },
        label = { Text("Email *") },
        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email, imeAction = ImeAction.Done),
        keyboardActions = KeyboardActions(onDone = { focusManager.clearFocus(); onSubmit() }),
        modifier = Modifier.fillMaxWidth()
    )
}
```

### Programmatic Focus with FocusRequester

```kotlin
val firstFieldFocus = remember { FocusRequester() }
LaunchedEffect(Unit) { firstFieldFocus.requestFocus() } // auto-focus on load

OutlinedTextField(
    value = name, onValueChange = { name = it },
    label = { Text("Name *") },
    modifier = Modifier.fillMaxWidth().focusRequester(firstFieldFocus)
)
```

---

## 6. Focus Management

### Auto-Focus First Field

**Web:**
```javascript
document.addEventListener('DOMContentLoaded', () => {
    const first = document.querySelector('form input:not([type="hidden"])');
    if (first) first.focus();
});
```

**Android:** Use `FocusRequester` + `LaunchedEffect(Unit)` as shown in Section 5.

### Focus First Error Field

**Web:**
```javascript
function focusFirstError(form) {
    const el = form.querySelector('.is-invalid');
    if (el) { el.focus(); el.scrollIntoView({ behavior: 'smooth', block: 'center' }); }
}
```

**Android:**
```kotlin
val focusRequesters = remember { List(fieldCount) { FocusRequester() } }
fun focusFirstError(errors: Map<Int, String>) {
    errors.keys.minOrNull()?.let { idx ->
        coroutineScope.launch { focusRequesters[idx].requestFocus() }
    }
}
```

### Wizard Step Transitions and Modal Focus Return

**Web:**
```javascript
// Step change: focus first input in new step
function showStep(idx) {
    document.querySelectorAll('.step-panel').forEach(p => p.classList.add('d-none'));
    const panel = document.getElementById(`step-${idx}`);
    panel.classList.remove('d-none');
    panel.querySelector('input, select, textarea')?.focus();
}

// Modal: return focus to trigger on close
let trigger = null;
function openModal(modal, btn) { trigger = btn; modal.classList.add('show'); trapFocus(modal); }
function closeModal(modal) { modal.classList.remove('show'); trigger?.focus(); }
```

**Android:**
```kotlin
LaunchedEffect(currentStep) { stepFocusRequesters[currentStep].requestFocus() }
```

---

## 7. Error Announcement

### Web: aria-live + Error Summary

Errors inside `aria-live="polite"` containers are announced when content changes.

```html
<div id="name-error" class="invalid-feedback" aria-live="polite"></div>

<div id="error-summary" role="alert" class="alert alert-danger d-none">
  <strong>3 errors found:</strong>
  <ul>
    <li><a href="#email">Email is required</a></li>
    <li><a href="#phone">Phone format is invalid</a></li>
  </ul>
</div>
```

```javascript
function showErrorSummary(errors) {
    const summary = document.getElementById('error-summary');
    const list = summary.querySelector('ul');
    list.innerHTML = errors.map(e => `<li><a href="#${e.fieldId}">${e.message}</a></li>`).join('');
    summary.querySelector('strong').textContent = `${errors.length} error(s) found:`;
    summary.classList.remove('d-none');
    summary.focus();
}
```

### Android: Semantics Error + Live Region

```kotlin
// Field-level error
OutlinedTextField(
    value = email, onValueChange = { email = it },
    label = { Text("Email *") }, isError = emailError != null,
    supportingText = { emailError?.let { Text(it, color = MaterialTheme.colorScheme.error) } },
    modifier = Modifier.fillMaxWidth().semantics {
        if (emailError != null) { error(emailError!!); liveRegion = LiveRegionMode.Polite }
    }
)

// Form-level error summary
if (formErrors.isNotEmpty()) {
    Card(
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.errorContainer),
        modifier = Modifier.fillMaxWidth().semantics {
            liveRegion = LiveRegionMode.Assertive
            contentDescription = "${formErrors.size} errors: ${formErrors.joinToString(". ")}"
        }
    ) {
        Column(Modifier.padding(16.dp)) {
            Text("${formErrors.size} error(s):", fontWeight = FontWeight.Bold)
            formErrors.forEach { Text("- ${it.message}", color = MaterialTheme.colorScheme.error) }
        }
    }
}
```

---

## 8. Touch Target Sizing

| Element | Web Minimum | Android Minimum | Recommended |
|---------|------------|-----------------|-------------|
| Text input height | 44px | 48dp | 48px / 56dp |
| Checkbox / Radio | 44 x 44px | 48 x 48dp | Entire row clickable |
| Button | 44px height | 48dp height | 48px / 48dp |
| Spacing between targets | 8px min | 8dp min | 12px / 12dp |

### Clickable Row for Checkbox/Radio

**Web:**
```html
<label class="form-check d-flex align-items-center gap-2 p-2" style="min-height: 44px; cursor: pointer;">
  <input type="checkbox" class="form-check-input" id="terms" name="terms">
  <span class="form-check-label">I accept the terms and conditions</span>
</label>
```

**Android:**
```kotlin
Row(
    verticalAlignment = Alignment.CenterVertically,
    modifier = Modifier.fillMaxWidth().heightIn(min = 48.dp)
        .clickable { checked = !checked }.padding(horizontal = 16.dp, vertical = 8.dp)
) {
    Checkbox(checked = checked, onCheckedChange = null)
    Spacer(Modifier.width(12.dp))
    Text("I accept the terms and conditions")
}
```

---

## 9. Color and Contrast

| Element | Minimum Ratio | Standard |
|---------|--------------|----------|
| Body text on background | 4.5:1 | WCAG AA |
| Large text (18px+ / bold 14px+) | 3:1 | WCAG AA |
| Input borders against background | 3:1 | WCAG 1.4.11 |
| Placeholder text | 4.5:1 | WCAG AA |
| Icons conveying meaning | 3:1 | WCAG 1.4.11 |

### Error Indication: Never Color Alone

Always combine at least two indicators -- color + icon + text.

**Web:**
```html
<div class="mb-3">
  <label class="form-label" for="phone">Phone</label>
  <input type="tel" class="form-control is-invalid" id="phone" value="12345">
  <div class="invalid-feedback d-block">
    <i class="ti ti-alert-circle"></i> Phone must be at least 10 digits.
  </div>
</div>
```

**Android:**
```kotlin
OutlinedTextField(
    value = phone, onValueChange = { phone = it },
    label = { Text("Phone") }, isError = true,
    trailingIcon = { Icon(Icons.Default.Warning, "Error", tint = MaterialTheme.colorScheme.error) },
    supportingText = { Text("Phone must be at least 10 digits", color = MaterialTheme.colorScheme.error) },
    modifier = Modifier.fillMaxWidth()
)
```

### Disabled State

- Visually distinct (reduced opacity) but text remains readable
- Web: `opacity: 0.65` on disabled inputs (Bootstrap default)
- Android: `enabled = false` applies Material 3 disabled styling automatically

---

## 10. Screen Reader Testing Checklist

- [ ] Every field label read correctly on focus
- [ ] Required fields announced as required
- [ ] Helper text read when field receives focus
- [ ] Error messages announced when they appear
- [ ] Error messages associated with the correct field
- [ ] Disabled fields announced as disabled
- [ ] Submission result announced (success or error summary)
- [ ] Error summary banner announced on submission failure
- [ ] Error summary links navigate to corresponding field
- [ ] Step progress announced on change ("Step 2 of 4: Address")
- [ ] Focus moves to first field of new step
- [ ] Dropdown options navigable with arrow keys and announced
- [ ] Checkbox/radio state changes announced
- [ ] File upload status announced (selected, uploading, complete)
- [ ] Date picker values announced when selected

### Testing Tools

| Platform | Tool | Notes |
|----------|------|-------|
| Web | NVDA | Free, most common Windows screen reader |
| Web | VoiceOver | Built-in macOS, Cmd+F5 to toggle |
| Web | axe DevTools | Browser extension, automated WCAG checks |
| Android | TalkBack | Built-in, Settings > Accessibility |
| Android | Accessibility Scanner | Google Play, visual overlay of issues |

---

## Quick Reference: Web to Android Attribute Mapping

| Concept | Web | Android Compose |
|---------|-----|-----------------|
| Field label | `<label for="id">` | `label = { Text("...") }` |
| Required state | `aria-required="true"` + `required` | `semantics { stateDescription = "Required" }` |
| Error state | `aria-invalid="true"` + `is-invalid` | `isError = true` + `semantics { error("...") }` |
| Helper text link | `aria-describedby="id"` | `supportingText = { }` (automatic) |
| Error announcement | `aria-live="polite"` | `semantics { liveRegion = LiveRegionMode.Polite }` |
| Error message link | `aria-errormessage="id"` | `semantics { error("...") }` (automatic) |
| Disabled state | `disabled` attribute | `enabled = false` |
| Icon label | `aria-label` on button | `contentDescription` in semantics |
| Focus management | `element.focus()` | `FocusRequester.requestFocus()` |
| Tab/IME next | Natural tab order | `imeAction = ImeAction.Next` |
| Submit action | Enter key submits form | `imeAction = ImeAction.Done` |
