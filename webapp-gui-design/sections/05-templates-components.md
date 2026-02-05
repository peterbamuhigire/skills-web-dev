## Page Template

**ALWAYS clone `skeleton.php` for new pages in SaaS Seeder Template.**

```php
<?php
require_once __DIR__ . '/../src/config/auth.php';
requireAuth(); // Automatic auth check + session prefix system

// Set page metadata
$pageTitle = 'Students';
$panel = 'admin'; // or 'member' depending on panel

// Get franchise context (uses session prefix system)
$franchiseId = getSession('franchise_id');
$userType = getSession('user_type');
?>
<!doctype html>
<html lang="en">
<head>
    <?php include __DIR__ . "/includes/head.php"; ?>
</head>
<body>
    <script src="/assets/tabler/js/tabler.min.js"></script>

    <div class="page">
        <div class="sticky-top">
            <?php include __DIR__ . "/includes/topbar.php"; ?>
        </div>
        <div class="page-wrapper">
            <div class="page-header d-print-none">
                <div class="container-xl">
                    <div class="row g-2 align-items-center">
                        <div class="col">
                            <div class="page-pretitle">Student Management</div>
                            <h2 class="page-title">Students</h2>
                        </div>
                        <div class="col-auto">
                            <button class="btn btn-primary" onclick="showAddModal()">
                                <i class="bi bi-plus me-1"></i> Add Student
                            </button>
                        </div>
                    </div>
                </div>
            </div>
            <div class="page-body">
                <div class="container-xl">
                    <div class="card">
                        <div class="card-body">
                            <!-- Content -->
                            <table id="studentsTable" class="table table-striped" style="width:100%">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Name</th>
                                        <th>Email</th>
                                        <th>Status</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
            <footer class="footer footer-transparent d-print-none">
                <?php include __DIR__ . '/includes/footer.php'; ?>
            </footer>
        </div>
    </div>

    <?php include __DIR__ . "/includes/foot.php"; ?>
    <script src="./assets/js/pages/students.js"></script>
</body>
</html>
```

**Key Points:**

- Use `__DIR__` for all paths (works in any panel)
- Call `requireAuth()` (automatic session check with prefix system)
- Set `$pageTitle` and `$panel` variables for includes
- Use `getSession('franchise_id')` to get franchise context
- All database queries MUST filter by `franchise_id`

## SweetAlert2 (Mandatory)

**Never use alert/confirm/prompt.**

```javascript
// Success
Swal.fire({ icon: "success", title: "Saved!", timer: 2000 });

// Confirm
const result = await Swal.fire({
  icon: "warning",
  title: "Delete?",
  showCancelButton: true,
  confirmButtonText: "Delete",
  confirmButtonColor: "#d63939",
});
if (result.isConfirmed) {
  await deleteItem(id);
}

// Loading
Swal.fire({ title: "Processing...", didOpen: () => Swal.showLoading() });
Swal.close(); // When done

// Input
const { value } = await Swal.fire({
  title: "Name",
  input: "text",
  inputValidator: (v) => (!v ? "Required" : null),
});
```

## DataTables

**Always paginate** with a default of **25 rows per page**. Use server-side pagination for large datasets.
**Default ordering:** disable client-side sorting unless explicitly required. Keep ordering from the API/query.
**Reports with money or dates:** disable DataTables ordering to avoid string-based sorting errors (e.g., 85,000 as text). Preserve server order (largest arrears first when required).
**Number formatting:** display numeric values with thousands separators (e.g., 254,150.35).

```javascript
$("#myTable").DataTables({
  ajax: { url: "./api/items.php", dataSrc: "data" },
  columns: [
    { data: "id", visible: false },
    { data: "code", title: "Code" },
    {
      data: null,
      render: (d) => `
                <div class="d-flex align-items-center">
                    <span class="avatar me-2" style="background-image:url('${d.photo_url}')"></span>
                    <div>
                        <div>${escapeHtml(d.name)}</div>
                        <small class="text-muted">${d.category}</small>
                    </div>
                </div>
            `,
    },
    {
      data: "status",
      render: (d) => `<span class="badge bg-${getStatusColor(d)}">${d}</span>`,
    },
    {
      data: null,
      orderable: false,
      render: (d) => `
                <button class="btn btn-sm btn-primary btn-edit" data-id="${d.id}"><i class="bi bi-pencil"></i></button>
                <button class="btn btn-sm btn-danger btn-delete" data-id="${d.id}"><i class="bi bi-trash"></i></button>
            `,
    },
  ],
  ordering: false,
  pageLength: 25,
  responsive: true,
});

$("#myTable").on("click", ".btn-edit", function () {
  editItem($(this).data("id"));
});
```

**HTML:**

```html
<table id="myTable" class="table table-striped" style="width:100%">
  <thead>
    <tr>
      <th>ID</th>
      <th>Code</th>
      <th>Name</th>
      <th>Status</th>
      <th>Actions</th>
    </tr>
  </thead>
</table>
```

## Forms

```html
<form id="itemForm">
  <input type="hidden" id="itemId" />
  <div class="row">
    <div class="col-md-6 mb-3">
      <label class="form-label required">Code</label>
      <input type="text" class="form-control" id="code" required />
    </div>
    <div class="col-md-6 mb-3">
      <label class="form-label required">Name</label>
      <input type="text" class="form-control" id="name" required />
    </div>
  </div>
  <div class="mb-3">
    <label class="form-label">Description</label>
    <textarea class="form-control" id="description" rows="3"></textarea>
  </div>
  <div class="row">
    <div class="col-md-6 mb-3">
      <label class="form-label">Category</label>
      <select class="form-select" id="categoryId">
        <option value="">Select...</option>
      </select>
    </div>
    <div class="col-md-6 mb-3">
      <label class="form-label">Date</label>
      <input type="date" class="form-control" id="date" />
    </div>
  </div>
</form>
```

**Required CSS:**

```css
.form-label.required::after {
  content: " *";
  color: #d63939;
}
```

## Modals

```html
<div class="modal fade" id="itemModal" tabindex="-1">
  <div class="modal-dialog modal-lg">
    <div class="modal-content">
      <div class="modal-header">
        <h5 id="modalTitle">Add Item</h5>
        <button
          type="button"
          class="btn-close"
          data-bs-dismiss="modal"
        ></button>
      </div>
      <div class="modal-body"><!-- Form --></div>
      <div class="modal-footer">
        <button class="btn btn-secondary" data-bs-dismiss="modal">
          Cancel
        </button>
        <button class="btn btn-primary" id="saveBtn">
          <i class="bi bi-check me-1"></i> Save
        </button>
      </div>
    </div>
  </div>
</div>
```

```javascript
const modal = new bootstrap.Modal($("#itemModal")[0]);
$("#itemModal").on("hidden.bs.modal", resetForm);

function showAddModal() {
  resetForm();
  $("#modalTitle").text("Add Item");
  modal.show();
}
```

## Icons (Bootstrap Icons Only)

```html
<i class="bi bi-plus"></i>
<!-- Add -->
<i class="bi bi-pencil"></i>
<!-- Edit -->
<i class="bi bi-trash"></i>
<!-- Delete -->
<i class="bi bi-eye"></i>
<!-- View -->
<i class="bi bi-search"></i>
<!-- Search -->
<i class="bi bi-download"></i>
<!-- Export -->

<button class="btn btn-primary"><i class="bi bi-plus me-1"></i> Add</button>
```
