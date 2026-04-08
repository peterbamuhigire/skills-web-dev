---
name: form-ux-design
description: Cross-platform form UX/UI patterns for web (Bootstrap 5/Tabler), Android (Jetpack Compose), and iOS (SwiftUI). Covers field anatomy, validation, error states, multi-step wizards, accessibility, touch-friendly inputs, and submission workflows. Use...
---

## Required Plugins

**Superpowers plugin:** MUST be active for all work using this skill. Use throughout the entire build pipeline — design decisions, code generation, debugging, quality checks, and any task where it offers enhanced capabilities. If superpowers provides a better way to accomplish something, prefer it over the default approach.

**Frontend Design plugin:** Required for all UI generation from this skill. Use for form layout decisions, component styling, spacing, color selection for states, responsive form behavior, and visual QA of form elements.

# Form UX/UI Design

Cross-cutting form design patterns for **web** (Bootstrap 5 / Tabler + PHP), **Android** (Jetpack Compose + Material 3), and **iOS** (SwiftUI). Apply this skill whenever you build, review, or refactor any form.

## Quick Reference

| Topic | Reference File | Scope |
|-------|---------------|-------|
| Web form components | `references/web-form-components.md` | Bootstrap/Tabler inputs, selects, checkboxes, radios, switches, textareas, file uploads |
| Android form components | `references/android-form-components.md` | Compose TextField, ExposedDropdownMenu, Checkbox, RadioButton, Switch, Slider |
| iOS form components | `references/ios-form-components.md` | SwiftUI TextField, Picker, Toggle, DatePicker, Stepper |
| Validation patterns | `references/form-validation.md` | Validation logic, error states, async validation, submission workflows (all platforms) |
| Accessibility | `references/form-accessibility.md` | WCAG form requirements, ARIA, screen readers, keyboard nav, touch targets (all platforms) |

---

## 1. Form Design Philosophy

Five rules that govern every form decision:

**Three dimensions of every form** (most to least influential):
1. **Words** — what you say and how you say it. Users can work around bad layout; they cannot work around bad wording.
2. **Layout** — how things are visually presented
3. **Flow** — how the user moves through the form

**A form is a conversation.** Order, tone, appropriateness, and effort all matter to humans. Design accordingly.

**"Start with nothing. Then only add what's needed to communicate with the user."** — Every pixel must serve a purpose. Be ruthless.

**Collect only what you need.** Every additional question reduces completion rate and data quality. Never add questions "just in case."

### Rule 1 — Labels Above Inputs (ALWAYS)

Labels above inputs on ALL screen sizes. NEVER use placeholder text as the label — it disappears on focus, makes fields look pre-filled, is not reliably announced by screen readers, and corrupts data when left in the field. NEVER use float labels — they have all the same problems as placeholder-as-label plus broken animation on long labels.

Mark **optional** fields with "(optional)" appended to the label. Do NOT mark required fields with red asterisks — they are abstract, visually noisy, inaccessible, and often labelled with jargon like "mandatory."

### Rule 2 -- Single Column by Default

One column for forms. Two-column layout only for naturally paired fields (first name / last name, city / state). Mobile is always single column regardless.

### Rule 3 -- Progressive Disclosure

Show only what is needed now. Reveal advanced fields conditionally (toggles, dependency rules). Break long forms (more than 7 fields) into logical steps.

### Rule 4 -- Instant Feedback

Validate on blur (not on keystroke). Show errors inline below the field. Display success indicators (green border or checkmark) for completed fields that passed validation.

**Error message must do three things** (Enders):
1. Convey that an error has occurred
2. State exactly what the error is and where
3. Tell the user how to fix it — in plain, non-accusatory language

Never use vague messages ("Invalid input"). Never use the word "error" alone — be specific. For long forms: provide an error summary at the top of the page with anchor links to each error. Pair all error colours with an icon — never rely on colour alone.

### Rule 5 -- Minimal Friction

Use smart defaults, autocomplete attributes, and auto-formatting (phone, currency). Reduce keystrokes. Never ask for information you already have or can derive.

---

## 2. Field Anatomy

Universal structure across all platforms:

```
+---------------------------------+
| Label *                         |  <- Always visible, * for required
+---------------------------------+
| [Icon] Placeholder text...      |  <- Input with optional leading icon
+---------------------------------+
| Helper text or character count  |  <- Below input, muted color
| Error: This field is required   |  <- Red, replaces helper on error
+---------------------------------+
```

**Rules:**
- Label is always above the input, never floating inside
- Required indicator is an asterisk `*` after the label text (not red color)
- Helper text and error text occupy the same space; error replaces helper when active
- Leading icons are optional; use them for fields where context helps (email, phone, search)
- Character count appears right-aligned in the helper text area for limited fields

---

## 3. Field States

| State | Web (Bootstrap 5) | Android (Compose) | Visual Cue |
|---------|---------------------|----------------------|-------------|
| Default | `form-control` | `OutlinedTextField` | Gray border |
| Focus | `:focus` blue border | `focusedBorderColor` | Blue/primary border + label color change |
| Filled | Value present | Value present | Default border, value displayed |
| Error | `is-invalid` class | `isError = true` | Red border + error message below |
| Success | `is-valid` class | Custom green indicator | Green border + checkmark icon |
| Disabled | `disabled` attribute | `enabled = false` | Gray background, reduced opacity |
| Loading | Spinner inside field | `CircularProgressIndicator` as trailing icon | Spinner replacing action icon |
| Read-only | `readonly` attribute | `readOnly = true` | No border, plain text appearance |

---

## 4. Essential Code Examples

### Web: Standard Form Field with Validation

```html
<div class="mb-3">
  <label class="form-label required" for="email">Email Address</label>
  <input type="email" class="form-control" id="email" name="email"
         placeholder="john@example.com" required autocomplete="email"
         aria-describedby="email-help email-error">
  <div id="email-help" class="form-text">We'll never share your email.</div>
  <div id="email-error" class="invalid-feedback">Please enter a valid email.</div>
</div>
```

**Key points:**
- `required` class on label shows the asterisk (Tabler CSS convention)
- `aria-describedby` links both helper and error text for screen readers
- `autocomplete="email"` enables browser autofill
- `invalid-feedback` is hidden by default, shown when `is-invalid` is on the input

### Web: Blur Validation with JavaScript

```javascript
document.querySelectorAll('.form-control[required]').forEach(input => {
    input.addEventListener('blur', function () {
        if (!this.checkValidity()) {
            this.classList.add('is-invalid');
            this.classList.remove('is-valid');
        } else {
            this.classList.remove('is-invalid');
            this.classList.add('is-valid');
        }
    });
});
```

### Android: Standard Form Field with Validation

```kotlin
@Composable
fun ValidatedTextField(
    value: String,
    onValueChange: (String) -> Unit,
    label: String,
    error: String? = null,
    helperText: String? = null,
    leadingIcon: @Composable (() -> Unit)? = null,
    keyboardOptions: KeyboardOptions = KeyboardOptions.Default,
    modifier: Modifier = Modifier
) {
    Column(modifier = modifier) {
        OutlinedTextField(
            value = value,
            onValueChange = onValueChange,
            label = { Text(label) },
            leadingIcon = leadingIcon,
            isError = error != null,
            keyboardOptions = keyboardOptions,
            supportingText = {
                Text(
                    text = error ?: helperText ?: "",
                    color = if (error != null) MaterialTheme.colorScheme.error
                            else MaterialTheme.colorScheme.onSurfaceVariant
                )
            },
            modifier = Modifier.fillMaxWidth()
        )
    }
}
```

### Android: Blur-Equivalent Validation (Focus Change)

```kotlin
var emailTouched by remember { mutableStateOf(false) }
val emailError = if (emailTouched && !isValidEmail(email)) "Invalid email" else null

OutlinedTextField(
    value = email,
    onValueChange = { email = it },
    label = { Text("Email Address") },
    isError = emailError != null,
    supportingText = { emailError?.let { Text(it) } },
    modifier = Modifier
        .fillMaxWidth()
        .onFocusChanged { if (!it.isFocused) emailTouched = true }
)
```

---

## 5. Multi-Step Form Pattern (Wizard)

Use when a form exceeds 7 fields or spans logically distinct sections.

### Structure

```
Step 1          Step 2          Step 3          Review
[Personal] ---> [Address] ---> [Payment] ---> [Summary]
  (active)       (pending)      (pending)      (pending)
```

### Rules

- **Progress indicator:** Show step number + label. Mark completed steps with green checkmark.
- **Navigation:** Back and Next buttons. Save draft state on each step transition.
- **Validation:** Validate the current step completely before allowing progression to next.
- **Summary step:** Display all collected inputs in read-only form for review before final submit.
- **Persistence:** Store partial data in session (web) or ViewModel (Android) so refresh/rotation does not lose progress.

### Web Implementation

Use Tabler's steps component. Each step renders inside a card body. Hide/show steps with JS. Store step data in a hidden form or session storage.

```html
<div class="steps steps-counter steps-blue mb-4">
  <a href="#" class="step-item active">Personal Info</a>
  <a href="#" class="step-item">Address</a>
  <a href="#" class="step-item">Review</a>
</div>
<div class="card card-body" id="step-1">
  <!-- Step 1 fields here -->
</div>
```

### Android Implementation

Use `HorizontalPager` with a custom step indicator composable. Each page is a composable form section. State lives in the ViewModel.

```kotlin
@Composable
fun WizardForm(viewModel: WizardViewModel = hiltViewModel()) {
    val pagerState = rememberPagerState(pageCount = { viewModel.stepCount })

    Column {
        StepIndicator(
            currentStep = pagerState.currentPage,
            totalSteps = viewModel.stepCount,
            stepLabels = viewModel.stepLabels
        )
        HorizontalPager(state = pagerState, userScrollEnabled = false) { page ->
            when (page) {
                0 -> PersonalInfoStep(viewModel)
                1 -> AddressStep(viewModel)
                2 -> ReviewStep(viewModel)
            }
        }
        WizardNavButtons(
            onBack = { /* animate to previous */ },
            onNext = { if (viewModel.validateStep(pagerState.currentPage)) /* animate to next */ },
            isLastStep = pagerState.currentPage == viewModel.stepCount - 1
        )
    }
}
```

---

## 5b. Gateway Screen (Before Long Forms)

Required for any form that takes more than 5 minutes. The gateway screen should:
- Explain what and who the form is for
- Warn users of information they will need (passport, account number, bill)
- State average time to complete
- State whether save-and-resume is available
- Include privacy/terms summary with links
- Have a prominent CTA button

The gateway screen is NOT part of the progress indicator step count.

## 5c. Confirmation Screen (After Submission)

Must include:
- Confirmation that the form was submitted
- Reference/receipt number if applicable
- Whether a confirmation email was sent
- What happens next and when
- Any further actions required from the user
- A path to somewhere else (never a dead end)

Thank the user. Make them feel the submission was a success.

## 5d. Specific Field Rules (from Enders)

**Name:** Single text box. Accept all characters including apostrophes, diacritics, hyphens, spaces, non-Latin characters. Avoid splitting into "first" and "last" — culturally limited.

**Email:** Single text box. Use `type="email"` for mobile keyboard. Accept any string with one character before "@" and one after — do not over-validate format.

**Phone:** Single text box. Accept hyphens, dashes, spaces, parentheses. Use `type="tel"` for mobile. Specify which type (home, mobile, work).

**Date of birth:** Three separate text boxes (day, month, year) — fastest and most accurate. Use `type="date"` for mobile as optional input. Never three dropdowns.

**Credit card:** Single text box per element (card number, expiry, CVC). Determine card type computationally from first digits — never ask user to choose. Show accepted payment methods before the payment step.

**Sex/Gender:** Make optional. If sex: Female / Male / Another option / Prefer not to say (alphabetical). If gender identity: single free-text box — there is no universal list.

---

## 6. Form Submission Workflow

Standard sequence for both platforms:

```
1. Client-side validation (all fields)
       |
       v  (all valid?)
2. Disable submit button + show loading spinner
       |
       v
3. Send request
   - Web: POST with CSRF token, FormData or JSON
   - Android: API call via Repository/UseCase
       |
       v
4. Handle response
   +-- Success ----> Toast/Snackbar + redirect or form reset
   +-- Validation error --> Map server errors to individual fields
   +-- Network error ----> Show retry option, preserve form state
       |
       v
5. Re-enable submit button
```

### Web: Submit Handler

```javascript
form.addEventListener('submit', async function (e) {
    e.preventDefault();
    if (!validateAllFields()) return;

    const btn = form.querySelector('[type="submit"]');
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Saving...';

    try {
        const res = await fetch(form.action, {
            method: 'POST',
            body: new FormData(form),
            headers: { 'X-CSRF-TOKEN': csrfToken }
        });
        const data = await res.json();
        if (data.success) {
            Swal.fire('Saved!', data.message, 'success');
        } else {
            mapServerErrors(data.errors); // Set is-invalid on each field
        }
    } catch (err) {
        Swal.fire('Error', 'Network error. Please try again.', 'error');
    } finally {
        btn.disabled = false;
        btn.innerHTML = 'Save';
    }
});
```

### Android: Submit in ViewModel

```kotlin
fun submit() {
    if (!validateAll()) return
    _uiState.update { it.copy(isSubmitting = true) }
    viewModelScope.launch {
        repository.submitForm(formData)
            .onSuccess {
                _events.emit(FormEvent.Success("Saved successfully"))
            }
            .onFailure { error ->
                when (error) {
                    is ValidationException -> _uiState.update {
                        it.copy(fieldErrors = error.fieldErrors)
                    }
                    else -> _events.emit(FormEvent.Error("Network error. Retry?"))
                }
            }
        _uiState.update { it.copy(isSubmitting = false) }
    }
}
```

---

## 7. Touch Target and Spacing Rules

| Element | Min Size (Web) | Min Size (Android) | Gap Between Elements |
|---------|---------------|--------------------|-----------------------|
| Text input | 44px height | 56dp height | 16px / 16dp |
| Checkbox / Radio | 44 x 44px | 48 x 48dp | 12px / 12dp |
| Button | 44px height | 48dp height | 8px / 8dp |
| Switch | 44px clickable area | 48dp clickable area | 12px / 12dp |

**Additional spacing rules:**
- Form sections separated by 24px / 24dp with a subtle divider or heading
- Label to input gap: 4px / 4dp
- Input to helper/error text gap: 4px / 4dp
- Submit button gets 24px / 24dp top margin from last field

---

## 8. Form DOs and DON'Ts

### DO

- Use visible labels above every input (never placeholder-only)
- Validate on blur, not on keystroke
- Show total error count on submit when multiple errors exist
- Preserve all form data on validation failure
- Use `autocomplete` attributes: `name`, `email`, `tel`, `address-line1`, `cc-number`
- Group related fields with `<fieldset>` + `<legend>` (web) or section headers (Android)
- Support keyboard Enter to submit on the last field
- Auto-focus the first field on form load
- Show character count for fields with a max length
- Use `inputmode` (web) and `keyboardOptions` (Android) to show the correct keyboard

### DON'T

- **Don't use placeholder text as the label** — it disappears, looks pre-filled, corrupts data, not accessible
- **Don't use float labels** — same problems as placeholder-as-label; space saved is illusory
- **Don't mark required fields with red asterisks** — mark optional fields with "(optional)" instead
- **Don't disable the submit button** until all fields are filled — leaves users confused about what is wrong
- **Don't use inline validation that fires while the user is still typing** — interrupting, confusing
- **Don't use colour alone to indicate errors** — always pair with an icon (4–10% of users are colour-blind)
- **Don't hide help text behind tooltips or hover states** — it won't be seen, doesn't work on touch
- **Don't use dropdowns for short lists** (fewer than 5 options) — use radio buttons instead
- **Don't use dropdowns for long lists** (more than 20 options) — use text box + auto-suggest instead
- **Don't use sliders for numeric input** — users cannot enter precise values; use a text box
- **Don't use three dropdowns for date entry** — use three text boxes (day, month, year) instead
- **Don't make date picker the only way to enter a date** — always allow text box entry as alternative
- **Don't auto-move cursor between split fields** (e.g., split card number boxes) — jarring, causes errors
- **Don't ask users to enter email or password twice** — users paste from the first field; use password reset instead
- **Don't ask double/multi-concept questions** — one concept per question
- **Don't ask questions that yield poor-quality data** (e.g., "How did you hear about us?" — recall is inaccurate)
- **Don't use accordion layouts for multi-step forms** — known usability issues
- **Don't use percentage-based progress indicators** — vague; use "Step X of Y" instead
- **Don't include site navigation or fat footers inside forms** — distracts users, adds no value
- **Don't give text fields a background colour** — makes them look like buttons
- **Don't use a reset/clear button** — users accidentally clear their work; remove entirely
- **Don't reset the form on validation error**
- **Don't use CAPTCHA unless absolutely necessary** — prefer honeypot fields
- **Don't split phone numbers or dates into multiple input fields**

---

## 9. Common Form Types -- Quick Patterns

| Form Type | Key Fields | Special Considerations |
|-----------|-----------|------------------------|
| Registration | Name, email, password, confirm | Password strength meter, terms checkbox |
| Login | Email/username, password | "Remember me" checkbox, "Forgot password" link |
| Search / Filter | Keyword, dropdowns, date range | Instant apply (no submit button), clear-all action |
| Data Entry (CRUD) | Dynamic per entity | Pre-fill on edit, confirm on delete, dirty-form warning |
| Settings / Profile | Grouped preferences | Auto-save toggle or explicit save, section navigation |
| Checkout / Payment | Address, card, billing | PCI considerations, address autocomplete, order summary |
| Clinical / Medical | Vitals, notes, medications | Unit validation, required-field enforcement, audit trail |

---

## 10. Integration with Existing Skills

```
form-ux-design (this skill)
    |
    +-- webapp-gui-design ---------> Web form components, Tabler template pages
    +-- jetpack-compose-ui --------> Android form composables, Material 3 theming
    +-- swiftui-design -----------> iOS form views (when available)
    +-- pos-sales-ui-design -------> POS forms: customer entry, payment, invoice
    +-- api-error-handling --------> Server validation error mapping to form fields
    +-- vibe-security-skill -------> CSRF tokens, XSS prevention, input sanitization
    +-- dual-auth-rbac ------------> Login/registration forms, role-based field visibility
    +-- image-compression ---------> File upload fields with client-side compression
    +-- mysql-best-practices ------> Backend storage for form data, safe queries
```

**Usage pattern:** Load `form-ux-design` alongside the primary skill for your platform:
- Web admin panel? Load `webapp-gui-design` + `form-ux-design`
- Android data entry app? Load `jetpack-compose-ui` + `form-ux-design`
- iOS data entry app? Load `swiftui-design` (when available) + `form-ux-design`
- POS forms? Load `pos-sales-ui-design` + `form-ux-design`

The form skill provides the UX rules and patterns; the platform skill provides the component library and architecture.
