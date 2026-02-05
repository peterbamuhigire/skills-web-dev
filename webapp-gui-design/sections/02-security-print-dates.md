## Security Baseline (Required)

Always load and apply the **Vibe Security Skill** for any web UI work. UI changes must align with secure data handling, CSRF protections, output encoding, and safe error display.

## Print/PDF Letterhead (Mandatory)

All report print and PDF outputs MUST include a full letterhead with:

- Organization name
- Physical address
- Phone number
- Email address
- Logo

Never ship a report print/PDF view without the complete letterhead. Print views must auto-trigger the browser print dialog on load.

## Date Formatting (UI Required)

- Never display raw SQL timestamps (e.g., `2026-01-25 00:00:00`).
- Display dates as `d M Y` (e.g., `27 Jan 2026`) or `d F Y` (e.g., `27 January 2026`) depending on context.
- Store and transmit dates as `YYYY-MM-DD`.
- Use a shared formatter for UI rendering to keep consistent output.

```javascript
function formatDisplayDate(value) {
  if (!value) return "-";
  const datePart = String(value).slice(0, 10);
  const parts = datePart.split("-");
  if (parts.length === 3) {
    const date = new Date(
      Number(parts[0]),
      Number(parts[1]) - 1,
      Number(parts[2]),
    );
    return date.toLocaleDateString("en-GB", {
      day: "2-digit",
      month: "short",
      year: "numeric",
    });
  }
  return value;
}
```
