# Print Stylesheet Template

Copy-paste `@media print` block for finance UI repos. Project-specific selectors marked `/* TODO */`.

```css
@media print {
  @page {
    size: A4;
    margin: 15mm 18mm;
  }

  html, body {
    background: #fff !important;
    color: #000 !important;
    font-family: var(--font-sans);
    font-size: 11pt;
    line-height: 1.35;
  }

  /* Hide app chrome */
  .app-shell, .top-bar, .side-nav, .bottom-nav,
  .toast, .toolbar-actions, .filters, .skip-print {
    display: none !important;
  }

  /* Reveal print-only content */
  .print-only { display: block !important; }

  /* Headers / footers on every page */
  .print-header,
  .print-footer {
    position: running(header);
  }
  .print-footer { position: running(footer); }

  @page {
    @top-left   { content: element(header-left); }
    @top-right  { content: element(header-right); }
    @bottom-left { content: element(footer-left); }
    @bottom-right { content: "Page " counter(page) " of " counter(pages); }
  }

  .print-header-left  { position: running(header-left); }
  .print-header-right { position: running(header-right); }
  .print-footer-left  { position: running(footer-left); }

  /* Money cells */
  .money {
    font-variant-numeric: tabular-nums;
    font-feature-settings: "tnum" 1;
    text-align: right;
    white-space: nowrap;
  }

  /* Tables — repeat headers on each page; avoid orphan totals */
  table.ledger {
    width: 100%;
    border-collapse: collapse;
    page-break-inside: auto;
  }
  table.ledger thead { display: table-header-group; }
  table.ledger tfoot { display: table-footer-group; }
  table.ledger tr    { page-break-inside: avoid; page-break-after: auto; }
  table.ledger th, table.ledger td {
    border-bottom: 0.25pt solid #000;
    padding: 4pt 6pt;
  }

  /* Status chips — must remain readable in monochrome */
  .chip {
    border: 0.5pt solid #000;
    padding: 1pt 6pt;
    border-radius: 9999px;
    background: #fff !important;
    color: #000 !important;
  }
  .chip::after { content: ""; }

  /* Charts: pattern overlay so monochrome remains readable */
  .chart svg [data-series] {
    fill: url(#hatch-1) #ddd !important;
    stroke: #000 !important;
  }

  /* Sign-off block (last page) */
  .sign-off {
    page-break-before: always;
    page-break-inside: avoid;
    margin-top: 12mm;
  }
  .sign-off .box {
    display: inline-block;
    width: 50mm;
    height: 22mm;
    border: 0.5pt solid #000;
    vertical-align: top;
    margin-right: 4mm;
    padding: 2mm;
  }
  .sign-off .box .label {
    font-size: 9pt;
    text-transform: uppercase;
    letter-spacing: 0.5pt;
  }

  /* Watermark when draft */
  body[data-status="draft"]::before {
    content: "DRAFT";
    position: fixed;
    top: 40%;
    left: 50%;
    transform: translate(-50%, -50%) rotate(-30deg);
    font-size: 110pt;
    color: rgba(0,0,0,0.06);
    z-index: 0;
    pointer-events: none;
  }

  /* Links: keep readable, show URL where useful */
  a[href]::after { content: ""; }
  a.print-show-href[href]::after {
    content: " (" attr(href) ")";
    font-size: 9pt;
    color: #333;
  }
}
```

## Mandatory elements per printed page

Every printable page contains:

```html
<div class="print-header-left">
  <strong>{{entity_name}}</strong><br>
  TIN: {{tin}} · {{address_line}}
</div>
<div class="print-header-right">
  {{report_title}} · {{period}}<br>
  Framework: {{framework}} · Generated {{generated_at}}
</div>
<div class="print-footer-left">
  Prepared by: {{preparer}} on {{prepared_at}}<br>
  Reviewed by: {{reviewer}} on {{reviewed_at}}
</div>
```

## Sign-off block on the last page

```html
<section class="sign-off">
  <div class="box">
    <div class="label">Preparer</div>
    <div>Name: ____________________</div>
    <div>Signature: _______________</div>
    <div>Date: ___________________</div>
  </div>
  <div class="box">
    <div class="label">Reviewer</div>
    <div>Name: ____________________</div>
    <div>Signature: _______________</div>
    <div>Date: ___________________</div>
  </div>
  <div class="box">
    <div class="label">Approver</div>
    <div>Name: ____________________</div>
    <div>Signature: _______________</div>
    <div>Date: ___________________</div>
  </div>
  <div class="box" style="border-style:dashed;">
    <div class="label">Stamp</div>
  </div>
</section>
```

Last reviewed: 2026-05-12. Next review due: 2026-11-12.
