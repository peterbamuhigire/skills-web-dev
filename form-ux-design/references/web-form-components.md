# Web Form Components Reference

Bootstrap 5 + Tabler + PHP. Follows webapp-gui-design conventions.

## 1. Text Input Fields

Standard input with label, placeholder, helper text, error state, required CSS:

```html
<div class="mb-3">
  <label class="form-label required" for="fullName">Full Name</label>
  <input type="text" class="form-control" id="fullName" placeholder="John Doe" required>
  <small class="form-hint">Enter your legal name as shown on your ID.</small>
</div>
<!-- Error state: add is-invalid + invalid-feedback -->
<input type="text" class="form-control is-invalid" id="fullName" required>
<div class="invalid-feedback">Full name is required.</div>
```

```css
.form-label.required::after { content: " *"; color: #d63939; }
```

**Email / Password / URL / Number:**
```html
<input type="email" class="form-control" id="email" placeholder="user@example.com">
<input type="url" class="form-control" id="website" placeholder="https://example.com">
<input type="number" class="form-control" id="quantity" min="1" max="999" step="1">
<!-- Password with show/hide toggle -->
<div class="input-group">
  <input type="password" class="form-control" id="password" required>
  <button class="btn btn-outline-secondary" type="button" id="togglePwd"><i class="bi bi-eye"></i></button>
</div>
<script>
document.getElementById('togglePwd').addEventListener('click', function() {
  const p = document.getElementById('password'), hidden = p.type === 'password';
  p.type = hidden ? 'text' : 'password';
  this.querySelector('i').className = hidden ? 'bi bi-eye-slash' : 'bi bi-eye';
});
</script>
```

**Phone (auto-format) / Currency (prefix) / Search (debounce) / Textarea (counter + auto-resize):**
```html
<!-- Phone -->
<input type="tel" class="form-control" id="phone" placeholder="(555) 123-4567">
<!-- Currency -->
<div class="input-group">
  <span class="input-group-text">$</span>
  <input type="text" class="form-control" id="amount" placeholder="0.00" inputmode="decimal">
</div>
<!-- Search with clear -->
<div class="input-icon mb-3">
  <span class="input-icon-addon"><i class="bi bi-search"></i></span>
  <input type="text" class="form-control" id="searchInput" placeholder="Search...">
  <button class="btn btn-link input-icon-addon end-0" id="clearSearch" style="display:none;z-index:5;border:none;"><i class="bi bi-x-lg"></i></button>
</div>
<!-- Textarea with counter -->
<div class="mb-3">
  <label class="form-label" for="notes">Notes</label>
  <textarea class="form-control" id="notes" rows="3" maxlength="500"></textarea>
  <small class="form-hint text-end d-block"><span id="notesCount">0</span>/500</small>
</div>
```

```javascript
// Phone auto-format
document.getElementById('phone').addEventListener('input', function(e) {
  let v = e.target.value.replace(/\D/g, '').substring(0, 10);
  if (v.length >= 7) v = `(${v.slice(0,3)}) ${v.slice(3,6)}-${v.slice(6)}`;
  else if (v.length >= 4) v = `(${v.slice(0,3)}) ${v.slice(3)}`;
  else if (v.length > 0) v = `(${v}`;
  e.target.value = v;
});
// Currency format on blur
document.getElementById('amount').addEventListener('blur', function() {
  const n = parseFloat(this.value.replace(/[^0-9.]/g, ''));
  if (!isNaN(n)) this.value = n.toFixed(2);
});
// Search with debounce (350ms) + clear
const searchInput = document.getElementById('searchInput'), clearBtn = document.getElementById('clearSearch');
function debounce(fn, ms) { let t; return (...a) => { clearTimeout(t); t = setTimeout(() => fn(...a), ms); }; }
const doSearch = debounce(async (q) => {
  const res = await fetch(`./api/search.php?q=${encodeURIComponent(q)}`);
  const data = await res.json(); /* render results */
}, 350);
searchInput.addEventListener('input', function() {
  clearBtn.style.display = this.value ? 'block' : 'none';
  if (this.value.length >= 2) doSearch(this.value);
});
clearBtn.addEventListener('click', () => { searchInput.value = ''; clearBtn.style.display = 'none'; searchInput.focus(); });
// Textarea counter + auto-resize
const notes = document.getElementById('notes');
notes.addEventListener('input', function() {
  document.getElementById('notesCount').textContent = this.value.length;
  this.style.height = 'auto'; this.style.height = this.scrollHeight + 'px';
});
```

## 2. Select / Dropdown Fields
```html
<!-- Standard select (5+ options) -->
<select class="form-select" id="category">
  <option value="">Select...</option>
  <option value="1">Electronics</option>
</select>
<!-- Grouped options -->
<select class="form-select" id="location">
  <option value="">Select location...</option>
  <optgroup label="East Africa"><option value="UG">Uganda</option><option value="KE">Kenya</option></optgroup>
  <optgroup label="West Africa"><option value="NG">Nigeria</option><option value="GH">Ghana</option></optgroup>
</select>
<!-- Searchable select (Tom Select) - use for 10+ options -->
<select class="form-select" id="customerId"></select>
<!-- Multi-select (Tom Select) -->
<select class="form-select" id="tags" multiple></select>
```

```javascript
// Searchable select with remote data
new TomSelect('#customerId', {
  valueField: 'id', labelField: 'name', searchField: 'name', placeholder: 'Search customer...',
  load: function(query, callback) {
    fetch(`./api/customers.php?search=${encodeURIComponent(query)}`)
      .then(r => r.json()).then(d => callback(d.data)).catch(() => callback());
  }
});
// Multi-select with remove button
new TomSelect('#tags', { plugins: ['remove_button'], maxItems: 10 });
```

**When to use what:**
| Options | Single Choice     | Multiple Choice            |
|---------|-------------------|----------------------------|
| 2-5     | Radio buttons     | Checkbox group             |
| 6-9     | Standard select   | Checkbox group             |
| 10+     | Searchable select | Multi-select (Tom Select)  |
| Yes/No  | Toggle switch     | Single checkbox            |

## 3. Checkbox, Radio, Switch
```html
<!-- Single checkbox (terms/consent) -->
<label class="form-check">
  <input class="form-check-input" type="checkbox" id="agreeTerms" required>
  <span class="form-check-label">I agree to the <a href="/terms">Terms of Service</a></span>
</label>
<!-- Checkbox group (multi-select, vertical) -->
<div class="mb-3">
  <label class="form-label">Permissions</label>
  <label class="form-check"><input class="form-check-input" type="checkbox" name="perms[]" value="read"><span class="form-check-label">Read</span></label>
  <label class="form-check"><input class="form-check-input" type="checkbox" name="perms[]" value="write"><span class="form-check-label">Write</span></label>
  <label class="form-check"><input class="form-check-input" type="checkbox" name="perms[]" value="delete"><span class="form-check-label">Delete</span></label>
</div>
<!-- Radio group (2-5 options, vertical) -->
<div class="mb-3">
  <label class="form-label required">Payment Method</label>
  <label class="form-check"><input class="form-check-input" type="radio" name="payment" value="cash" required><span class="form-check-label">Cash</span></label>
  <label class="form-check"><input class="form-check-input" type="radio" name="payment" value="card"><span class="form-check-label">Card</span></label>
  <label class="form-check"><input class="form-check-input" type="radio" name="payment" value="mobile"><span class="form-check-label">Mobile Money</span></label>
</div>
<!-- Toggle switch (on/off settings) -->
<label class="form-check form-switch">
  <input class="form-check-input" type="checkbox" id="emailNotifications" checked>
  <span class="form-check-label">Email Notifications</span>
</label>
```

## 4. Date & Time Pickers (Flatpickr)

Storage: `Y-m-d`. Display: `d M Y` via `altInput`. Per webapp-gui-design conventions.

```javascript
// Date picker
flatpickr('#startDate', {
  dateFormat: 'Y-m-d', altInput: true, altFormat: 'd M Y',
  minDate: 'today', locale: { firstDayOfWeek: 1 }
});
// Time picker
flatpickr('#apptTime', {
  enableTime: true, noCalendar: true, dateFormat: 'H:i', time_24hr: true, minuteIncrement: 15
});
// Date range picker
flatpickr('#dateRange', {
  mode: 'range', dateFormat: 'Y-m-d', altInput: true, altFormat: 'd M Y',
  onClose: function(dates) {
    if (dates.length === 2) loadReport(dates[0].toISOString().slice(0,10), dates[1].toISOString().slice(0,10));
  }
});
// Max date + disabled dates (e.g., no Sundays)
flatpickr('#birthDate', {
  dateFormat: 'Y-m-d', altInput: true, altFormat: 'd M Y', maxDate: new Date(),
  disable: [ function(date) { return date.getDay() === 0; } ]
});
```

## 5. File Upload

**Single file with preview:**

```html
<input type="file" class="form-control" id="docUpload" accept=".pdf,.doc,.docx">
<div id="filePreview" class="mt-2"></div>
<script>
document.getElementById('docUpload').addEventListener('change', function() {
  const f = this.files[0]; if (!f) return;
  if (f.size > 5*1024*1024) { Swal.fire('Error','File must be under 5 MB','error'); this.value=''; return; }
  document.getElementById('filePreview').innerHTML = `<small class="text-muted"><i class="bi bi-file-earmark me-1"></i>${f.name} (${(f.size/1024).toFixed(1)} KB)</small>`;
});
</script>
```

**Multi-file with progress:**

```html
<input type="file" class="form-control" id="multiUpload" multiple accept="image/*,.pdf">
<div id="uploadProgress" class="mt-2"></div>
<script>
document.getElementById('multiUpload').addEventListener('change', async function() {
  const c = document.getElementById('uploadProgress'); c.innerHTML = '';
  for (const file of this.files) {
    const row = document.createElement('div'); row.className = 'mb-1';
    row.innerHTML = `<small>${file.name}</small><div class="progress"><div class="progress-bar" style="width:0%"></div></div>`;
    c.appendChild(row);
    const fd = new FormData(); fd.append('file', file);
    const xhr = new XMLHttpRequest();
    xhr.upload.onprogress = (e) => { if (e.lengthComputable) row.querySelector('.progress-bar').style.width = ((e.loaded/e.total)*100)+'%'; };
    xhr.onload = () => row.querySelector('.progress-bar').classList.add('bg-success');
    xhr.open('POST','./api/upload.php'); xhr.send(fd);
  }
});
</script>
```

**Drag-and-drop zone:**

```html
<div id="dropZone" class="border border-2 border-dashed rounded p-4 text-center text-muted" style="cursor:pointer;">
  <i class="bi bi-cloud-arrow-up fs-1 d-block mb-2"></i>
  Drag files here or <a href="#" onclick="document.getElementById('hiddenFile').click();return false;">browse</a>
  <input type="file" id="hiddenFile" class="d-none" multiple>
</div>
<script>
const dz = document.getElementById('dropZone');
['dragenter','dragover'].forEach(e => dz.addEventListener(e, ev => { ev.preventDefault(); dz.classList.add('border-primary'); }));
['dragleave','drop'].forEach(e => dz.addEventListener(e, () => dz.classList.remove('border-primary')));
dz.addEventListener('drop', e => { e.preventDefault(); handleFiles(e.dataTransfer.files); });
document.getElementById('hiddenFile').addEventListener('change', function() { handleFiles(this.files); });
</script>
```

**Image compression** (see `image-compression` skill) **+ validation:**

```javascript
async function uploadImage(file) {
  const compressed = await compressImage(file, { maxWidth: 1200, quality: 0.8 });
  const fd = new FormData(); fd.append('image', compressed, file.name);
  return (await fetch('./api/upload.php', { method:'POST', body:fd })).json();
}
const ALLOWED_TYPES = ['image/jpeg','image/png','image/webp','application/pdf'];
function validateFile(f) {
  if (!ALLOWED_TYPES.includes(f.type)) return 'File type not allowed';
  return f.size > 5*1024*1024 ? 'File exceeds 5 MB limit' : null;
}
```

## 6. Form Layout Patterns

```html
<!-- Single column (default) -->
<div class="card"><div class="card-body">
  <form id="profileForm"><div class="mb-3"><!-- field --></div><button type="submit" class="btn btn-primary">Save</button></form>
</div></div>

<!-- Two-column paired fields -->
<div class="row">
  <div class="col-md-6 mb-3"><label class="form-label required">First Name</label><input type="text" class="form-control" required></div>
  <div class="col-md-6 mb-3"><label class="form-label required">Last Name</label><input type="text" class="form-control" required></div>
</div>
<div class="row">
  <div class="col-md-8 mb-3"><label class="form-label">City</label><input type="text" class="form-control"></div>
  <div class="col-md-4 mb-3"><label class="form-label">State</label><select class="form-select"><option value="">Select...</option></select></div>
</div>

<!-- Inline form (search bar) -->
<form class="row g-2 align-items-end mb-3">
  <div class="col-auto flex-grow-1"><input type="text" class="form-control" placeholder="Search orders..."></div>
  <div class="col-auto"><button type="submit" class="btn btn-primary"><i class="bi bi-search"></i></button></div>
</form>

<!-- Horizontal form (settings pages only) -->
<div class="row mb-3 align-items-center">
  <label class="col-md-3 col-form-label">Company Name</label>
  <div class="col-md-9"><input type="text" class="form-control"></div>
</div>

<!-- Form in modal -->
<div class="modal fade" id="itemModal" tabindex="-1">
  <div class="modal-dialog modal-lg"><div class="modal-content">
    <div class="modal-header"><h5 id="modalTitle">Add Item</h5><button type="button" class="btn-close" data-bs-dismiss="modal"></button></div>
    <div class="modal-body"><form id="itemForm"><!-- fields --></form></div>
    <div class="modal-footer">
      <button class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
      <button class="btn btn-primary" id="saveBtn"><i class="bi bi-check me-1"></i>Save</button>
    </div>
  </div></div>
</div>

<!-- Form in card (standard CRUD) -->
<div class="card">
  <div class="card-header"><h3 class="card-title">Create Product</h3></div>
  <div class="card-body"><form id="productForm"><!-- fields --></form></div>
  <div class="card-footer text-end">
    <a href="products.php" class="btn btn-secondary me-2">Cancel</a>
    <button class="btn btn-primary" onclick="submitForm()">Save Product</button>
  </div>
</div>
```

## 7. Multi-Step Wizard

```html
<div class="card">
  <div class="card-header">
    <ul class="steps steps-counter" id="wizardSteps">
      <li class="step-item active">Personal Info</li>
      <li class="step-item">Address</li>
      <li class="step-item">Review</li>
    </ul>
  </div>
  <div class="card-body">
    <div class="wizard-step" data-step="0"><!-- Step 1 fields --></div>
    <div class="wizard-step d-none" data-step="1"><!-- Step 2 fields --></div>
    <div class="wizard-step d-none" data-step="2"><!-- Summary/review --></div>
  </div>
  <div class="card-footer d-flex justify-content-between">
    <button class="btn btn-secondary" id="prevBtn" style="display:none;">Back</button>
    <button class="btn btn-primary ms-auto" id="nextBtn">Next</button>
  </div>
</div>
```

```javascript
let currentStep = 0;
const steps = document.querySelectorAll('.wizard-step');
const stepItems = document.querySelectorAll('#wizardSteps .step-item');
const prevBtn = document.getElementById('prevBtn'), nextBtn = document.getElementById('nextBtn');

function showStep(idx) {
  steps.forEach((s, i) => s.classList.toggle('d-none', i !== idx));
  stepItems.forEach((s, i) => { s.classList.toggle('active', i === idx); s.classList.toggle('step-item--done', i < idx); });
  prevBtn.style.display = idx === 0 ? 'none' : '';
  nextBtn.textContent = idx === steps.length - 1 ? 'Submit' : 'Next';
  currentStep = idx;
}
function validateStep(idx) {
  let valid = true;
  steps[idx].querySelectorAll('[required]').forEach(f => {
    if (!f.value.trim()) { f.classList.add('is-invalid'); valid = false; } else f.classList.remove('is-invalid');
  });
  return valid;
}
nextBtn.addEventListener('click', () => {
  if (!validateStep(currentStep)) return;
  if (currentStep === steps.length - 1) { submitWizard(); return; }
  showStep(currentStep + 1);
});
prevBtn.addEventListener('click', () => showStep(currentStep - 1));
async function submitWizard() {
  nextBtn.disabled = true;
  nextBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Saving...';
  // collect all fields, POST, handle response
}
```

## 8. Form Submission Patterns

**CSRF token** (always include): `<input type="hidden" name="csrf_token" value="<?= $_SESSION['csrf_token'] ?>">`

**AJAX submit with loading + SweetAlert2 confirmation + error mapping:**

```javascript
// AJAX submit with loading state
document.getElementById('saveBtn').addEventListener('click', async function() {
  const btn = this; btn.disabled = true;
  btn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span>Saving...';
  try {
    const fd = new FormData(document.getElementById('itemForm'));
    fd.append('csrf_token', document.querySelector('[name=csrf_token]').value);
    const res = await fetch('./api/items.php', { method: 'POST', body: fd });
    const data = await res.json();
    if (!data.success) throw new Error(data.message || 'Save failed');
    if (data.errors) { mapServerErrors(data.errors); return; }
    Swal.fire({ icon:'success', title:'Saved!', timer:1500, showConfirmButton:false });
    bootstrap.Modal.getInstance(document.getElementById('itemModal'))?.hide();
    dataTable.ajax.reload();
  } catch (err) { Swal.fire('Error', err.message, 'error'); }
  finally { btn.disabled = false; btn.innerHTML = '<i class="bi bi-check me-1"></i>Save'; }
});
// SweetAlert2 confirmation before destructive action
async function deleteItem(id) {
  const r = await Swal.fire({ icon:'warning', title:'Delete this item?', text:'This action cannot be undone.',
    showCancelButton:true, confirmButtonText:'Delete', confirmButtonColor:'#d63939' });
  if (!r.isConfirmed) return;
  const data = await (await fetch(`./api/items.php?id=${id}`, { method:'DELETE' })).json();
  if (data.success) { Swal.fire('Deleted!','','success'); dataTable.ajax.reload(); }
  else Swal.fire('Error', data.message, 'error');
}
// Map server validation errors to fields
function mapServerErrors(errors) {
  document.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
  document.querySelectorAll('.invalid-feedback').forEach(el => el.remove());
  for (const [field, msg] of Object.entries(errors)) {
    const input = document.getElementById(field); if (!input) continue;
    input.classList.add('is-invalid');
    const fb = document.createElement('div'); fb.className = 'invalid-feedback'; fb.textContent = msg;
    input.parentNode.appendChild(fb);
  }
}
```

## 9. Inline Editing

```html
<span class="editable" data-field="name" data-id="42">John Doe</span>
```

```javascript
// Click-to-edit: save on blur/Enter, cancel on Escape
document.querySelectorAll('.editable').forEach(span => {
  span.style.cursor = 'pointer'; span.title = 'Click to edit';
  span.addEventListener('click', function() {
    if (this.querySelector('input')) return;
    const original = this.textContent;
    const input = document.createElement('input');
    input.type = 'text'; input.className = 'form-control form-control-sm'; input.value = original;
    this.textContent = ''; this.appendChild(input); input.focus();
    const save = async () => {
      const val = input.value.trim();
      if (val === original) { span.textContent = original; return; }
      const data = await (await fetch('./api/items.php', {
        method:'PATCH', headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ id: span.dataset.id, [span.dataset.field]: val })
      })).json();
      span.textContent = data.success ? val : original;
    };
    input.addEventListener('blur', save);
    input.addEventListener('keydown', e => {
      if (e.key === 'Enter') { e.preventDefault(); input.blur(); }
      if (e.key === 'Escape') span.textContent = original;
    });
  });
});
// Inline edit in DataTable cell
$('#myTable').on('click', 'td.editable-cell', function() {
  const cell = $(this); if (cell.find('input').length) return;
  const original = cell.text().trim();
  const input = $('<input class="form-control form-control-sm">').val(original);
  cell.html(input); input.focus();
  input.on('blur', async function() {
    const val = $(this).val().trim();
    if (val !== original) await fetch('./api/items.php', { method:'PATCH',
      headers:{'Content-Type':'application/json'},
      body: JSON.stringify({ id: cell.closest('tr').data('id'), [cell.data('field')]: val }) });
    cell.text(val || original);
  });
  input.on('keydown', function(e) { if (e.key==='Enter') $(this).blur(); if (e.key==='Escape') cell.text(original); });
});
```

## 10. Responsive Form Rules

| Rule | Breakpoint | Implementation |
|------|-----------|----------------|
| Single column | Below 768px | `col-md-6` collapses to full width |
| Labels stacked | Below 768px | Never use horizontal form on mobile |
| Full-width buttons | Below 576px | See CSS below |
| Touch-friendly | All mobile | `min-height: 44px` on inputs/buttons |
| Native date picker | Mobile only | Fall back to `type="date"` |

```css
@media (max-width: 575.98px) {
  .card-footer .btn { width: 100%; margin-bottom: 0.5rem; }
  .form-control, .form-select { min-height: 44px; font-size: 16px; /* prevent iOS zoom */ }
  .modal-dialog { margin: 0.5rem; }
}
```

```javascript
// Mobile: native date input; Desktop: Flatpickr
function initDatePicker(sel, opts) {
  if (/iPhone|iPad|Android/i.test(navigator.userAgent))
    document.querySelectorAll(sel).forEach(el => el.type = 'date');
  else flatpickr(sel, { dateFormat:'Y-m-d', altInput:true, altFormat:'d M Y', ...opts });
}
```

**Cross-references:** webapp-gui-design (templates, AJAX, Flatpickr), image-compression (file upload), vibe-security-skill (CSRF, XSS).
