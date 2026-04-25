# Android Form Components (Jetpack Compose + Material 3)

## 1. Text Input Fields

**Primary composable** used across all forms. OutlinedTextField is the default; filled TextField is for dense layouts only.

```kotlin
@Composable
fun FormTextField(
    value: String, onValueChange: (String) -> Unit, label: String,
    modifier: Modifier = Modifier, placeholder: String = "",
    supportingText: String? = null, isError: Boolean = false,
    leadingIcon: @Composable (() -> Unit)? = null,
    trailingIcon: @Composable (() -> Unit)? = null,
    keyboardOptions: KeyboardOptions = KeyboardOptions.Default,
    keyboardActions: KeyboardActions = KeyboardActions.Default,
    singleLine: Boolean = true, maxLines: Int = if (singleLine) 1 else Int.MAX_VALUE
) {
    OutlinedTextField(
        value = value, onValueChange = onValueChange,
        label = { Text(label) },
        placeholder = if (placeholder.isNotEmpty()) {{ Text(placeholder) }} else null,
        supportingText = supportingText?.let {{ Text(it, color = if (isError) MaterialTheme.colorScheme.error else Color.Unspecified) }},
        isError = isError, leadingIcon = leadingIcon, trailingIcon = trailingIcon,
        keyboardOptions = keyboardOptions, keyboardActions = keyboardActions,
        singleLine = singleLine, maxLines = maxLines,
        shape = RoundedCornerShape(8.dp), modifier = modifier.fillMaxWidth()
    )
}
```

**Password with visibility toggle:**

```kotlin
@Composable
fun PasswordField(
    value: String, onValueChange: (String) -> Unit, label: String = "Password",
    modifier: Modifier = Modifier, isError: Boolean = false, supportingText: String? = null
) {
    var visible by rememberSaveable { mutableStateOf(false) }
    OutlinedTextField(
        value = value, onValueChange = onValueChange, label = { Text(label) },
        isError = isError, supportingText = supportingText?.let {{ Text(it) }}, singleLine = true,
        visualTransformation = if (visible) VisualTransformation.None else PasswordVisualTransformation(),
        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
        trailingIcon = { IconButton(onClick = { visible = !visible }) {
            Icon(painterResource(if (visible) R.drawable.ic_visibility_off else R.drawable.ic_visibility),
                if (visible) "Hide password" else "Show password")
        }},
        shape = RoundedCornerShape(8.dp), modifier = modifier.fillMaxWidth()
    )
}
```

**Typed fields** -- use `keyboardOptions` with `KeyboardType.Email`, `.Phone`, `.Decimal`, or `.Number`. Set `imeAction = ImeAction.Next` to advance focus, `ImeAction.Done` on the last field.

**Multi-line with character counter:**

```kotlin
@Composable
fun TextAreaField(
    value: String, onValueChange: (String) -> Unit, label: String,
    modifier: Modifier = Modifier, maxChars: Int = 500, minLines: Int = 3
) {
    val remaining = maxChars - value.length
    OutlinedTextField(
        value = value, onValueChange = { if (it.length <= maxChars) onValueChange(it) },
        label = { Text(label) }, minLines = minLines, maxLines = 6,
        supportingText = { Text("$remaining chars left", Modifier.fillMaxWidth(), textAlign = TextAlign.End,
            color = if (remaining < 20) MaterialTheme.colorScheme.error else MaterialTheme.colorScheme.onSurfaceVariant) },
        shape = RoundedCornerShape(8.dp), modifier = modifier.fillMaxWidth()
    )
}
```

**Search field:** Use `OutlinedTextField` with `RoundedCornerShape(24.dp)`, `leadingIcon` = search icon, `trailingIcon` = clear button (visible when query is non-empty), `imeAction = ImeAction.Search`.

## 2. Dropdown / Exposed Menu

```kotlin
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun <T> DropdownField(
    selected: T?, options: List<T>, onSelect: (T) -> Unit,
    label: String, displayText: (T) -> String,
    modifier: Modifier = Modifier, isError: Boolean = false, supportingText: String? = null
) {
    var expanded by remember { mutableStateOf(false) }
    ExposedDropdownMenuBox(expanded = expanded, onExpandedChange = { expanded = it }, modifier = modifier) {
        OutlinedTextField(
            value = selected?.let { displayText(it) } ?: "", onValueChange = {}, readOnly = true,
            label = { Text(label) }, isError = isError,
            supportingText = supportingText?.let {{ Text(it) }},
            trailingIcon = { ExposedDropdownMenuDefaults.TrailingIcon(expanded) },
            colors = ExposedDropdownMenuDefaults.outlinedTextFieldColors(),
            shape = RoundedCornerShape(8.dp),
            modifier = Modifier.menuAnchor(MenuAnchorType.PrimaryNotEditable).fillMaxWidth()
        )
        ExposedDropdownMenu(expanded = expanded, onDismissRequest = { expanded = false }) {
            options.forEach { option ->
                DropdownMenuItem(text = { Text(displayText(option)) },
                    onClick = { onSelect(option); expanded = false },
                    contentPadding = ExposedDropdownMenuDefaults.ItemContentPadding)
            }
        }
    }
}
```

**Searchable variant:** Use `MenuAnchorType.PrimaryEditable`, track `filterText` state, filter `options` with `remember(options, filterText)`, show "No results" when `filtered.isEmpty()`. Reset `filterText` on dismiss and selection.

**Grouped options:** Insert non-clickable `DropdownMenuItem` headers with `enabled = false` between option groups.

| Criteria | Dropdown | RadioButton |
|---|---|---|
| Options | 5+ items | 2-4 items |
| Space | Compact (collapsed) | All visible |
| Speed | Tap to open, then select | One-tap |
| Best for | Country, category, status | Gender, priority, yes/no |

## 3. Selection Controls

All selection controls use full-row tap targets with `Modifier.semantics { role = Role.Checkbox }` (or `.RadioButton`, `.Switch`). Pass `onCheckedChange = null` to the control itself; the Row handles the click.

```kotlin
@Composable
fun LabeledCheckbox(
    checked: Boolean, onCheckedChange: (Boolean) -> Unit, label: String, modifier: Modifier = Modifier
) {
    Row(verticalAlignment = Alignment.CenterVertically,
        modifier = modifier.fillMaxWidth().clip(RoundedCornerShape(8.dp))
            .clickable { onCheckedChange(!checked) }
            .padding(vertical = 8.dp, horizontal = 4.dp).semantics { role = Role.Checkbox }
    ) {
        Checkbox(checked = checked, onCheckedChange = null)
        Spacer(Modifier.width(12.dp))
        Text(label, style = MaterialTheme.typography.bodyLarge)
    }
}

@Composable
fun <T> CheckboxGroup(
    items: List<T>, selectedItems: Set<T>, onSelectionChange: (Set<T>) -> Unit, label: (T) -> String,
    modifier: Modifier = Modifier
) {
    Column(modifier = modifier) { items.forEach { item ->
        LabeledCheckbox(checked = item in selectedItems, label = label(item),
            onCheckedChange = { checked -> onSelectionChange(if (checked) selectedItems + item else selectedItems - item) })
    }}
}
```

**RadioButton group:** Wrap Column in `Modifier.selectableGroup()`. Use `Modifier.selectable(selected, onClick, role = Role.RadioButton)` on each Row. Pass `onClick = null` to RadioButton.

**Switch with label:** Row with `Text` (weight 1f) + optional description below + `Switch(onCheckedChange = null)` on the right. Entire row is clickable.

## 4. Date and Time Pickers

```kotlin
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DatePickerField(
    selectedDateMillis: Long?, onDateSelected: (Long?) -> Unit, label: String, modifier: Modifier = Modifier
) {
    var showPicker by rememberSaveable { mutableStateOf(false) }
    val dateText = selectedDateMillis?.let {
        SimpleDateFormat("MMM dd, yyyy", Locale.getDefault()).format(Date(it))
    } ?: ""
    OutlinedTextField(
        value = dateText, onValueChange = {}, readOnly = true, label = { Text(label) },
        trailingIcon = { IconButton(onClick = { showPicker = true }) {
            Icon(painterResource(R.drawable.ic_calendar), "Select date") }},
        shape = RoundedCornerShape(8.dp),
        modifier = modifier.fillMaxWidth().clickable { showPicker = true }
    )
    if (showPicker) {
        val state = rememberDatePickerState(initialSelectedDateMillis = selectedDateMillis)
        DatePickerDialog(
            onDismissRequest = { showPicker = false },
            confirmButton = { TextButton(onClick = { onDateSelected(state.selectedDateMillis); showPicker = false }) { Text("OK") } },
            dismissButton = { TextButton(onClick = { showPicker = false }) { Text("Cancel") } }
        ) { DatePicker(state = state) }
    }
}
```

**TimePicker:** Same pattern -- `rememberTimePickerState(initialHour, initialMinute)`, show in `AlertDialog` with `TimePicker(state = state)` as the `text` content.

**DateRangePicker:** Use `rememberDateRangePickerState`, display in `DatePickerDialog` with `DateRangePicker(state, Modifier.height(500.dp))`. Format both start/end millis for the text field display.

## 5. Sliders and Steppers

```kotlin
@Composable
fun LabeledSlider(
    value: Float, onValueChange: (Float) -> Unit, label: String, modifier: Modifier = Modifier,
    valueRange: ClosedFloatingPointRange<Float> = 0f..100f, steps: Int = 0,
    valueFormat: (Float) -> String = { "%.0f".format(it) }
) {
    Column(modifier = modifier.fillMaxWidth()) {
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
            Text(label, style = MaterialTheme.typography.bodyMedium)
            Text(valueFormat(value), style = MaterialTheme.typography.labelLarge, color = MaterialTheme.colorScheme.primary)
        }
        Slider(value = value, onValueChange = onValueChange, valueRange = valueRange, steps = steps)
    }
}
```

**RangeSlider:** Same layout, use `RangeSlider(value = range, onValueChange = onRangeChange, valueRange = valueRange)` and display `"${format(start)} - ${format(end)}"`.

**Stepper:** Row with label (weight 1f) + `FilledIconButton` (minus, 36.dp) + value Text (widthIn 48.dp, centered) + `FilledIconButton` (plus, 36.dp). Guard bounds with `enabled = value > minValue` / `value < maxValue`.

## 6. File and Image Upload

```kotlin
@Composable
fun DocumentPickerField(
    selectedUri: Uri?, onDocumentSelected: (Uri) -> Unit, label: String,
    modifier: Modifier = Modifier, mimeTypes: Array<String> = arrayOf("application/pdf", "image/*")
) {
    val launcher = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        uri?.let { onDocumentSelected(it) }
    }
    OutlinedTextField(
        value = selectedUri?.lastPathSegment ?: "", onValueChange = {}, readOnly = true,
        label = { Text(label) },
        trailingIcon = { IconButton(onClick = { launcher.launch(mimeTypes) }) {
            Icon(painterResource(R.drawable.ic_attach), "Select file") }},
        shape = RoundedCornerShape(8.dp),
        modifier = modifier.fillMaxWidth().clickable { launcher.launch(mimeTypes) }
    )
}

@Composable
fun ImagePickerField(imageUri: Uri?, onImageSelected: (Uri) -> Unit, modifier: Modifier = Modifier) {
    val launcher = rememberLauncherForActivityResult(ActivityResultContracts.PickVisualMedia()) { uri ->
        uri?.let { onImageSelected(it) }
    }
    Column(modifier = modifier) {
        if (imageUri != null) {
            AsyncImage(model = imageUri, contentDescription = "Selected image", contentScale = ContentScale.Crop,
                modifier = Modifier.fillMaxWidth().height(200.dp).clip(RoundedCornerShape(12.dp)))
            Spacer(Modifier.height(8.dp))
        }
        OutlinedButton(onClick = { launcher.launch(PickVisualMediaRequest(ActivityResultContracts.PickVisualMedia.ImageOnly)) },
            modifier = Modifier.fillMaxWidth()) {
            Icon(painterResource(R.drawable.ic_camera), null); Spacer(Modifier.width(8.dp))
            Text(if (imageUri != null) "Change Image" else "Select Image")
        }
    }
}
```

**Multi-file:** Use `ActivityResultContracts.OpenMultipleDocuments()`. **Upload progress:** `LinearProgressIndicator(progress = { progress })` with filename and percentage label. **Image optimization:** Apply `image-compression` skill patterns before upload.

## 7. Form Layout Patterns

```kotlin
// Single column (default) -- wrap form fields in LazyColumn
LazyColumn(contentPadding = PaddingValues(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
    item { /* form fields */ }
}

// Two-field row for paired inputs (first/last name, city/state)
Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(12.dp)) {
    Box(Modifier.weight(1f)) { FormTextField(value = first, onValueChange = onFirst, label = "First Name") }
    Box(Modifier.weight(1f)) { FormTextField(value = last, onValueChange = onLast, label = "Last Name") }
}

// Section header with divider
@Composable
fun FormSection(title: String, modifier: Modifier = Modifier, content: @Composable ColumnScope.() -> Unit) {
    Column(modifier = modifier.fillMaxWidth()) {
        Text(title, style = MaterialTheme.typography.titleMedium, color = MaterialTheme.colorScheme.primary)
        HorizontalDivider(Modifier.padding(vertical = 8.dp))
        Column(verticalArrangement = Arrangement.spacedBy(12.dp), content = content)
    }
}
```

**Other layouts:** Form in `BottomSheet` (use `ModalBottomSheet`), form in `Dialog`, full-screen form with `LargeTopAppBar` + `CollapsingToolbarLayout` equivalent via `TopAppBarScrollBehavior`.

## 8. Multi-Step Form / Wizard

```kotlin
@Composable
fun StepIndicator(totalSteps: Int, currentStep: Int, modifier: Modifier = Modifier) {
    Row(modifier = modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.Center) {
        repeat(totalSteps) { i ->
            val done = i < currentStep; val current = i == currentStep
            Box(Alignment.Center, Modifier.size(32.dp).clip(CircleShape).background(
                when { done -> MaterialTheme.colorScheme.primary; current -> MaterialTheme.colorScheme.primaryContainer
                    else -> MaterialTheme.colorScheme.surfaceVariant })) {
                if (done) Icon(painterResource(R.drawable.ic_check), null, tint = MaterialTheme.colorScheme.onPrimary, modifier = Modifier.size(16.dp))
                else Text("${i + 1}", style = MaterialTheme.typography.labelMedium)
            }
            if (i < totalSteps - 1) HorizontalDivider(Modifier.width(32.dp).padding(horizontal = 4.dp),
                color = if (done) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.surfaceVariant)
        }
    }
}

@OptIn(ExperimentalFoundationApi::class)
@Composable
fun FormWizard(
    steps: List<@Composable () -> Unit>, stepLabels: List<String>,
    isStepValid: (Int) -> Boolean, onSubmit: () -> Unit, modifier: Modifier = Modifier
) {
    val pagerState = rememberPagerState(pageCount = { steps.size })
    val scope = rememberCoroutineScope(); val page = pagerState.currentPage
    Column(modifier = modifier.fillMaxSize()) {
        StepIndicator(steps.size, page, Modifier.padding(16.dp))
        Text(stepLabels[page], style = MaterialTheme.typography.titleLarge, modifier = Modifier.padding(horizontal = 16.dp))
        HorizontalPager(state = pagerState, userScrollEnabled = false, modifier = Modifier.weight(1f)) { p ->
            Box(Modifier.fillMaxSize().padding(16.dp)) { steps[p]() } }
        Row(Modifier.fillMaxWidth().padding(16.dp), horizontalArrangement = Arrangement.SpaceBetween) {
            OutlinedButton(onClick = { scope.launch { pagerState.animateScrollToPage(page - 1) } }, enabled = page > 0) { Text("Back") }
            if (page < steps.size - 1) Button(onClick = { scope.launch { pagerState.animateScrollToPage(page + 1) } }, enabled = isStepValid(page)) { Text("Next") }
            else Button(onClick = onSubmit, enabled = isStepValid(page)) { Text("Submit") }
        }
    }
}
```

**Summary step:** The last step should display a review using `Card` composables for each section, with an "Edit" button per section that navigates back to the corresponding step.

## 9. Form State Management

```kotlin
data class FormState(
    val name: String = "", val email: String = "", val phone: String = "",
    val category: String? = null, val notes: String = "",
    val isSubmitting: Boolean = false, val fieldErrors: Map<String, String> = emptyMap()
) { val isValid: Boolean get() = fieldErrors.isEmpty() && name.isNotBlank() && email.isNotBlank() }

@HiltViewModel
class FormViewModel @Inject constructor(private val repo: Repository) : ViewModel() {
    private val _state = MutableStateFlow(FormState())
    val state: StateFlow<FormState> = _state.asStateFlow()
    private val _events = MutableSharedFlow<FormEvent>()
    val events: SharedFlow<FormEvent> = _events.asSharedFlow()

    fun onNameChange(v: String) { _state.update { it.copy(name = v, fieldErrors = it.fieldErrors - "name") } }
    fun onEmailChange(v: String) { _state.update { it.copy(email = v, fieldErrors = it.fieldErrors - "email") } }

    fun validate(): Boolean {
        val errs = mutableMapOf<String, String>()
        val s = _state.value
        if (s.name.isBlank()) errs["name"] = "Name is required"
        if (s.email.isBlank()) errs["email"] = "Email is required"
        else if (!Patterns.EMAIL_ADDRESS.matcher(s.email).matches()) errs["email"] = "Invalid email"
        _state.update { it.copy(fieldErrors = errs) }; return errs.isEmpty()
    }
    // submit() -- see section 10
}
```

**Focus management:** Use `FocusRequester.createRefs()` for field refs. Set `keyboardActions = KeyboardActions(onNext = { nextFocus.requestFocus() })` and `imeAction = ImeAction.Next` on each field. Last field uses `ImeAction.Done`.

## 10. Form Submission

```kotlin
// In FormViewModel
fun submit() {
    if (!validate()) return
    _state.update { it.copy(isSubmitting = true) }
    viewModelScope.launch {
        repo.submitForm(state.value.toRequest())
            .onSuccess { _state.update { it.copy(isSubmitting = false) }; _events.emit(FormEvent.Success("Saved")) }
            .onFailure { error -> _state.update { it.copy(isSubmitting = false) }; when (error) {
                is ValidationException -> { _state.update { it.copy(fieldErrors = error.fieldErrors) }; _events.emit(FormEvent.ScrollToFirstError) }
                is NetworkException -> _events.emit(FormEvent.NetworkError("Check connection"))
                else -> _events.emit(FormEvent.Error(error.message ?: "Unexpected error"))
            }}
    }
}
sealed interface FormEvent {
    data class Success(val msg: String) : FormEvent; data class Error(val msg: String) : FormEvent
    data class NetworkError(val msg: String) : FormEvent; data object ScrollToFirstError : FormEvent
}
```

**Submit button with loading state:**

```kotlin
@Composable
fun SubmitButton(text: String, onClick: () -> Unit, modifier: Modifier = Modifier,
    isLoading: Boolean = false, enabled: Boolean = true) {
    Button(onClick = onClick, enabled = enabled && !isLoading, modifier = modifier.fillMaxWidth().height(48.dp)) {
        if (isLoading) { CircularProgressIndicator(Modifier.size(20.dp), strokeWidth = 2.dp, color = MaterialTheme.colorScheme.onPrimary); Spacer(Modifier.width(8.dp)) }
        Text(if (isLoading) "Submitting..." else text)
    }
}
```

**Screen event handling:** Collect `viewModel.events` in `LaunchedEffect(Unit)`. On `Success`, show Snackbar and navigate. On `ScrollToFirstError`, call `listState.animateScrollToItem(0)`. On `NetworkError`, show Snackbar with "Retry" action that calls `viewModel.submit()`.
