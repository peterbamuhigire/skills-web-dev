## AJAX

```javascript
// GET
async function loadItems() {
  try {
    const res = await fetch("./api/items.php?action=list");
    const data = await res.json();
    return data.success ? data.data : [];
  } catch (error) {
    Swal.fire("Error", error.message, "error");
    return [];
  }
}

// POST
async function saveItem(itemData) {
  try {
    const res = await fetch("./api/items.php", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(itemData),
    });
    const data = await res.json();
    if (data.success) {
      Swal.fire("Success!", "", "success");
      return data;
    }
    throw new Error(data.message);
  } catch (error) {
    Swal.fire("Error", error.message, "error");
    return null;
  }
}

// DELETE
async function deleteItem(id) {
  const result = await Swal.fire({
    icon: "warning",
    title: "Delete?",
    showCancelButton: true,
    confirmButtonText: "Delete",
    confirmButtonColor: "#d63939",
  });
  if (!result.isConfirmed) return;

  const res = await fetch(`./api/items.php?id=${id}`, { method: "DELETE" });
  const data = await res.json();
  if (data.success) {
    Swal.fire("Deleted!", "", "success");
    dataTable.ajax.reload();
  }
}
```

## Utilities

```javascript
function formatCurrency(amount, currency = "USD") {
  return new Intl.NumberFormat("en-US", { style: "currency", currency }).format(
    amount || 0,
  );
}

function formatDate(dateString) {
  if (!dateString) return "N/A";
  return new Date(dateString).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function escapeHtml(text) {
  if (!text) return "";
  const map = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  };
  return String(text).replace(/[&<>"']/g, (m) => map[m]);
}

function debounce(func, wait) {
  let timeout;
  return (...args) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

function getStatusColor(status) {
  const colors = {
    active: "success",
    inactive: "secondary",
    pending: "warning",
    deleted: "danger",
  };
  return colors[status?.toLowerCase()] || "secondary";
}
```
