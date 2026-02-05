## Responsive

```css
/* Mobile first */
@media (max-width: 575.98px) {
}
@media (max-width: 767px) {
}
@media (max-width: 991.98px) {
}

/* Mobile nav */
@media (max-width: 767px) {
  .navbar-nav .nav-link {
    font-size: 1.5rem !important;
    padding: 1.2rem 1.35rem !important;
  }
  .page-header .btn-list .btn {
    flex: 1 1 100%;
  }
}

/* Responsive tables */
@media (max-width: 768px) {
  .priority-2,
  .priority-3 {
    display: none;
  }
}
```

## Photo Cards (Lists)

Use consistent visual patterns for card lists with photos:

- **People entities** (staff, customers, patients): social-style cards with circular avatar and banner background.jpg.
- **Non-people entities** (products, assets, vehicles): banner cards using a random photo; fallback to default.jpg.
- Always use `object-fit: cover` and fixed heights to prevent layout shift.
- Keep actions compact (view/edit) and align to the right.
- Avoid clipping avatar overlaps: set card `overflow: visible` or absolutely position the avatar within the banner.
- Overlap **only the avatar** (not the name/role text) by applying negative margin on the avatar itself.

## Flatpickr

Auto-applied to `<input type="date">` with `Y-m-d` value, `d F Y` display.

```javascript
// Manual
flatpickr("#date", { dateFormat: "Y-m-d", altInput: true, altFormat: "d M Y" });

// DateTime
flatpickr("#datetime", { enableTime: true, dateFormat: "Y-m-d H:i" });

// Range
flatpickr("#range", { mode: "range", dateFormat: "Y-m-d" });
```
