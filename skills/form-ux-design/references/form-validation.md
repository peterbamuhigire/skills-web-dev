# Form Validation Reference

Complete validation patterns for **web** (Bootstrap 5/Tabler + PHP) and **Android** (Jetpack Compose + Material 3).

## 1. Validation Timing Strategy

Never show errors while the user is still typing. Choose the trigger based on field type.

| Trigger | When | Use For |
|---------|------|---------|
| **On blur** | User leaves field | All fields -- primary trigger |
| **On submit** | User clicks submit | Full-form sweep, error count summary, scroll to first error |
| **On input (debounced)** | 500ms after last keystroke | Async checks only (email uniqueness, username availability) |
| **On focus** | User returns to field | Clear error state so they can fix it |
| **On keystroke** | Never | Never -- creates anxiety while typing |

### Timing by Field Type

| Field Type | On Blur | On Submit | Debounced Input | On Focus |
|------------|---------|-----------|-----------------|----------|
| Required text | Validate | Validate | No | Clear error |
| Email | Format check | Validate | Uniqueness check | Clear error |
| Password | Length/complexity | Validate | Strength meter only | Clear error |
| Phone | Format check | Validate | No | Clear error |
| Date | Range check | Validate | No | Clear error |
| File upload | Type/size on select | Validate | No | Clear error |
| Select/dropdown | No (always valid) | Required check | No | No |

## 2. Client-Side Validation Rules

### Required / Email / Phone

```javascript
// Web
function isRequired(value) { return value !== null && value !== undefined && String(value).trim() !== ''; }
function isValidEmail(value) { return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim()); }
function isValidPhone(value) {
    const digits = value.replace(/[\s\-\(\)\+]/g, '');
    return /^\d{7,15}$/.test(digits);
}
```

```kotlin
// Android
fun isRequired(value: String): Boolean = value.trim().isNotEmpty()
fun isValidEmail(value: String): Boolean = Patterns.EMAIL_ADDRESS.matcher(value.trim()).matches()
fun isValidPhone(value: String): Boolean {
    val digits = value.replace(Regex("[\\s\\-()+ ]"), "")
    return digits.matches(Regex("^\\d{7,15}$"))
}
```

### Number (min/max/integer)

```javascript
// Web
function isValidNumber(value, { min, max, integer = false } = {}) {
    const num = Number(value);
    if (isNaN(num)) return false;
    if (integer && !Number.isInteger(num)) return false;
    if (min !== undefined && num < min) return false;
    return !(max !== undefined && num > max);
}
```

```kotlin
// Android
fun isValidNumber(value: String, min: Double? = null, max: Double? = null, integer: Boolean = false): Boolean {
    val num = value.toDoubleOrNull() ?: return false
    if (integer && num != num.toLong().toDouble()) return false
    if (min != null && num < min) return false
    return !(max != null && num > max)
}
```

### Password

```javascript
// Web -- returns array of error strings (empty = valid)
function validatePassword(value) {
    const errors = [];
    if (value.length < 8) errors.push('Must be at least 8 characters');
    if (!/[A-Z]/.test(value)) errors.push('Must include an uppercase letter');
    if (!/[a-z]/.test(value)) errors.push('Must include a lowercase letter');
    if (!/\d/.test(value)) errors.push('Must include a number');
    return errors;
}
```

```kotlin
// Android
fun validatePassword(value: String): List<String> = buildList {
    if (value.length < 8) add("Must be at least 8 characters")
    if (!value.any { it.isUpperCase() }) add("Must include an uppercase letter")
    if (!value.any { it.isLowerCase() }) add("Must include a lowercase letter")
    if (!value.any { it.isDigit() }) add("Must include a number")
}
```

### Date / File

```javascript
// Web
function isValidDate(value, { min, max } = {}) {
    const date = new Date(value);
    if (isNaN(date.getTime())) return false;
    if (min && date < new Date(min)) return false;
    return !(max && date > new Date(max));
}
function isValidFile(file, { maxSizeMB = 5, allowedTypes = [] } = {}) {
    if (file.size > maxSizeMB * 1024 * 1024) return 'File exceeds ' + maxSizeMB + 'MB limit';
    if (allowedTypes.length && !allowedTypes.includes(file.type)) return 'File type not allowed';
    return null; // null = valid
}
```

## 3. Server-Side Validation and Error Mapping

Server returns field-level errors: `{ "success": false, "errors": { "email": "Already registered", "phone": "Invalid format" } }`

### Web: Map Server Errors to Fields

```javascript
function mapServerErrors(errors) {
    document.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
    Object.entries(errors).forEach(([field, message]) => {
        const input = document.querySelector(`[name="${field}"]`);
        if (!input) return;
        input.classList.add('is-invalid');
        const feedback = input.parentElement.querySelector('.invalid-feedback');
        if (feedback) feedback.textContent = message;
    });
    const firstError = document.querySelector('.is-invalid');
    if (firstError) firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
}
```

### Android: Map Server Errors to Fields

```kotlin
// ViewModel
data class FormState(val fieldErrors: Map<String, String> = emptyMap(), val isSubmitting: Boolean = false)

fun handleServerErrors(errorBody: String) {
    val json = JSONObject(errorBody)
    val errors = json.optJSONObject("errors") ?: return
    val fieldErrors = mutableMapOf<String, String>()
    errors.keys().forEach { key -> fieldErrors[key] = errors.getString(key) }
    _uiState.update { it.copy(fieldErrors = fieldErrors) }
}
```

```kotlin
// Composable -- read error per field
val emailError = uiState.fieldErrors["email"]
OutlinedTextField(
    value = email, onValueChange = { email = it }, label = { Text("Email") },
    isError = emailError != null,
    supportingText = { emailError?.let { Text(it) } },
    modifier = Modifier.fillMaxWidth()
)
```

## 4. Error Message Guidelines

**Rules:** Be specific (what is wrong), be helpful (how to fix), be polite (never blame user). Position below field, left-aligned. Color: red `#DC2626` text + red border. Optional `x-circle` icon before message.

| Field | Bad | Good |
|-------|-----|------|
| Email | "Invalid email" | "Email must include @ and a domain (e.g. name@company.com)" |
| Password | "Too short" | "Password must be at least 8 characters" |
| Phone | "Invalid input" | "Please enter a valid phone number (7-15 digits)" |
| Name | "Error" | "Name is required" |
| Date | "Invalid date" | "Date must be between Jan 1, 2020 and today" |
| Amount | "Bad value" | "Amount must be a positive number" |
| File | "Wrong file" | "Please upload a PNG, JPG, or PDF file (max 5MB)" |
| URL | "Invalid" | "URL must start with https://" |
| Username | "Taken" | "This username is already in use. Try adding numbers." |
| Confirm pwd | "Mismatch" | "Passwords do not match" |

## 5. Error Display Patterns

**Inline error (primary):** Below field, replaces helper text. Default for all field-level validation.

```html
<!-- Web: is-invalid class shows invalid-feedback -->
<input type="email" class="form-control is-invalid" name="email" value="bad@">
<div class="invalid-feedback">Email must include @ and a domain</div>
```

```kotlin
// Android: isError + supportingText
OutlinedTextField(value = email, onValueChange = { email = it }, isError = true,
    supportingText = { Text("Email must include @ and a domain") }, modifier = Modifier.fillMaxWidth())
```

**Error summary banner (on submit, 3+ errors):** Top-of-form alert listing all errors with anchor links (web: `alert alert-danger` with `<ul>` of `<a href="#field">` links; Android: `Card` with `errorContainer` color listing errors).

**Toast / Snackbar:** For network, server, timeout failures only -- not field validation.

```javascript
// Web (SweetAlert2)
Swal.fire({ icon: 'error', title: 'Connection Lost', text: 'Please check your internet and try again.' });
```

```kotlin
// Android
snackbarHostState.showSnackbar(message = "Network error. Please try again.", actionLabel = "Retry")
```

## 6. Success / Confirmation Patterns

**Field-level:** Green checkmark after valid async check (email available). Use sparingly.

```html
<input type="email" class="form-control is-valid" value="john@example.com">
<div class="valid-feedback">Email is available</div>
```

**Form-level:** Success toast/modal then redirect.

```javascript
// Web (SweetAlert2)
Swal.fire({ icon: 'success', title: 'Saved!', text: 'Customer record created.',
    timer: 2000, showConfirmButton: false }).then(() => { window.location.href = '/customers'; });
```

```kotlin
// Android -- collect one-shot events
LaunchedEffect(Unit) {
    viewModel.events.collect { event -> when (event) {
        is FormEvent.Success -> { snackbarHostState.showSnackbar(event.message); navController.popBackStack() }
        is FormEvent.Error -> snackbarHostState.showSnackbar(event.message)
    }}
}
```

## 7. Async Validation

For server-side uniqueness/availability checks. Trigger on blur with 500ms debounce.

### Web: Debounced Async Check

```javascript
function debounce(fn, ms) {
    let timer;
    return (...args) => { clearTimeout(timer); timer = setTimeout(() => fn(...args), ms); };
}
const checkEmail = debounce(async function (input) {
    const value = input.value.trim();
    if (!isValidEmail(value)) return;
    const spinner = input.parentElement.querySelector('.spinner-border');
    if (spinner) spinner.classList.remove('d-none');
    try {
        const res = await fetch(`/api/check-email?email=${encodeURIComponent(value)}`);
        const data = await res.json();
        input.classList.toggle('is-valid', data.available);
        input.classList.toggle('is-invalid', !data.available);
        if (!data.available)
            input.parentElement.querySelector('.invalid-feedback').textContent = 'Email already registered';
    } finally { if (spinner) spinner.classList.add('d-none'); }
}, 500);
document.getElementById('email').addEventListener('blur', function () { checkEmail(this); });
```

### Android: Debounced Async Check in ViewModel

```kotlin
private val emailFlow = MutableStateFlow("")
init {
    emailFlow.debounce(500)
        .filter { it.isNotBlank() && Patterns.EMAIL_ADDRESS.matcher(it).matches() }
        .distinctUntilChanged()
        .onEach { email ->
            _uiState.update { it.copy(emailChecking = true) }
            val result = repository.checkEmailAvailability(email)
            _uiState.update { it.copy(emailChecking = false,
                emailError = if (result.available) null else "Email already registered") }
        }.launchIn(viewModelScope)
}
fun onEmailChanged(value: String) { emailFlow.value = value }
```

```kotlin
// Composable -- loading indicator + result icon in trailingIcon
OutlinedTextField(
    value = email, onValueChange = { email = it; viewModel.onEmailChanged(it) },
    label = { Text("Email") }, isError = uiState.emailError != null,
    trailingIcon = { when {
        uiState.emailChecking -> CircularProgressIndicator(Modifier.size(20.dp), strokeWidth = 2.dp)
        uiState.emailError != null -> Icon(Icons.Default.Close, "Error", tint = MaterialTheme.colorScheme.error)
        email.isNotBlank() -> Icon(Icons.Default.Check, "Valid", tint = Color(0xFF16A34A))
    }},
    supportingText = { uiState.emailError?.let { Text(it) } },
    modifier = Modifier.fillMaxWidth()
)
```

## 8. Multi-Step Validation

**Rules:** Validate current step before "Next". Show step error count on failure. Skip future steps. Allow "Back" without validation. Final submit validates all steps.

```javascript
// Web
function validateStep(stepNumber) {
    const stepEl = document.getElementById(`step-${stepNumber}`);
    let valid = true;
    stepEl.querySelectorAll('[required], [data-validate]').forEach(input => {
        if (!input.checkValidity()) { input.classList.add('is-invalid'); valid = false; }
        else { input.classList.remove('is-invalid'); }
    });
    return valid;
}
function nextStep(currentStep) {
    if (!validateStep(currentStep)) {
        const n = document.querySelectorAll(`#step-${currentStep} .is-invalid`).length;
        Swal.fire('Fix Errors', `Please fix ${n} error(s) before continuing.`, 'warning');
        return;
    }
    showStep(currentStep + 1);
}
```

```kotlin
// Android ViewModel
fun validateStep(step: Int): Boolean {
    val errors = when (step) {
        0 -> validatePersonalInfo(); 1 -> validateAddress(); 2 -> validatePayment()
        else -> emptyMap()
    }
    _uiState.update { it.copy(fieldErrors = errors) }
    return errors.isEmpty()
}
fun validateAll(): Boolean {
    val all = validatePersonalInfo() + validateAddress() + validatePayment()
    _uiState.update { it.copy(fieldErrors = all) }
    return all.isEmpty()
}
```

## 9. Form Data Preservation

**Golden rule:** Never destroy user input. On any error, preserve all form data.

### Web: Draft Save to localStorage

```javascript
const DRAFT_KEY = 'form_draft_' + formId;
const saveDraft = debounce(() => {
    localStorage.setItem(DRAFT_KEY, JSON.stringify(Object.fromEntries(new FormData(form))));
}, 1000);
form.querySelectorAll('input, select, textarea').forEach(el => el.addEventListener('input', saveDraft));
function restoreDraft() {
    const saved = localStorage.getItem(DRAFT_KEY);
    if (!saved) return;
    Object.entries(JSON.parse(saved)).forEach(([name, value]) => {
        const input = form.querySelector(`[name="${name}"]`);
        if (input) input.value = value;
    });
}
function clearDraft() { localStorage.removeItem(DRAFT_KEY); }
```

### Android: Draft Save with SavedStateHandle

```kotlin
class FormViewModel @Inject constructor(
    private val savedStateHandle: SavedStateHandle, private val repository: FormRepository
) : ViewModel() {
    var name by mutableStateOf(savedStateHandle["name"] ?: ""); private set
    var email by mutableStateOf(savedStateHandle["email"] ?: ""); private set
    fun onNameChange(value: String) { name = value; savedStateHandle["name"] = value }
    fun onEmailChange(value: String) { email = value; savedStateHandle["email"] = value }
    fun clearDraft() { savedStateHandle.remove<String>("name"); savedStateHandle.remove<String>("email") }
}
```

### Preservation Rules

| Scenario | Action |
|----------|--------|
| Validation error | Keep all fields, highlight errors |
| Network error | Keep all fields, show retry button |
| Server error (500) | Keep all fields, show "try again later" |
| Session timeout (web) | Save to localStorage before redirect to login |
| Process death (Android) | SavedStateHandle auto-restores |
| Successful submit | Clear draft, redirect or reset form |

## 10. Security Validation

### CSRF Token (Web -- Every Form)

```html
<form method="POST" action="/api/customers">
  <input type="hidden" name="csrf_token" value="<?= $_SESSION['csrf_token'] ?>">
</form>
```

```php
if (!hash_equals($_SESSION['csrf_token'], $_POST['csrf_token'] ?? '')) {
    http_response_code(403);
    echo json_encode(['success' => false, 'message' => 'Invalid security token. Please refresh.']);
    exit;
}
```

### XSS Prevention

```php
// PHP -- sanitize before display, never before storage
function sanitize($value) { return htmlspecialchars($value, ENT_QUOTES | ENT_HTML5, 'UTF-8'); }
```

```javascript
// JS -- sanitize before DOM insertion
function escapeHtml(str) { const d = document.createElement('div'); d.textContent = str; return d.innerHTML; }
```

### Server-Side File Validation (PHP)

```php
$finfo = new finfo(FILEINFO_MIME_TYPE);
$mimeType = $finfo->file($_FILES['document']['tmp_name']);
$allowed = ['image/jpeg', 'image/png', 'application/pdf'];
if (!in_array($mimeType, $allowed, true)) $errors['document'] = 'Upload JPG, PNG, or PDF only.';
if ($_FILES['document']['size'] > 5 * 1024 * 1024) $errors['document'] = 'File must be under 5MB.';
```

### Honeypot Field (Anti-Bot -- Better Than CAPTCHA)

```html
<div style="position: absolute; left: -9999px;" aria-hidden="true">
  <input type="text" name="website_url" tabindex="-1" autocomplete="off">
</div>
```

```php
if (!empty($_POST['website_url'])) {
    http_response_code(422);
    echo json_encode(['success' => false, 'message' => 'Submission rejected.']);
    exit;
}
```

### Rate Limiting (PHP)

```php
$ip = $_SERVER['REMOTE_ADDR'];
$key = "form_submit:{$ip}";
$count = (int) apcu_fetch($key);
if ($count >= 5) {
    http_response_code(429);
    echo json_encode(['success' => false, 'message' => 'Too many attempts. Wait a minute.']);
    exit;
}
apcu_store($key, $count + 1, 60);
```

### SQL Injection Prevention

```php
// Always parameterized -- never concatenate user input
$stmt = $pdo->prepare('INSERT INTO customers (name, email, phone) VALUES (?, ?, ?)');
$stmt->execute([$_POST['name'], $_POST['email'], $_POST['phone']]);
```

## Quick Checklist

Before shipping any form, verify:

- [ ] Every field validates on blur
- [ ] Submit validates all fields and shows error count
- [ ] Server errors map back to individual fields
- [ ] Error messages are specific and helpful
- [ ] Form data is preserved on any error
- [ ] CSRF token is present (web)
- [ ] Inputs are sanitized before display
- [ ] File uploads are validated server-side by MIME type
- [ ] Async checks use debounce (500ms minimum)
- [ ] Multi-step forms validate per step, not all at once
- [ ] Honeypot field is present instead of CAPTCHA
- [ ] Rate limiting is in place for public forms
