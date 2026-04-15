# PDF Generation with WeasyPrint

Render HTML + CSS to PDF. Use when your report is essentially a web page, when designers supply HTML, or when you want print styles that mirror your web dashboard.

## Philosophy

WeasyPrint takes HTML5 and CSS 3 (including Paged Media, `@page`, `@media print`) and produces PDF. The mental model is "print stylesheet", not "programmatic canvas". If a designer can produce it in the browser, WeasyPrint can usually produce it as PDF.

Trade-offs vs ReportLab:

- Wins: designer-ready pipeline (same HTML/CSS as the web dashboard), CSS variables per tenant, flexbox/grid layouts, `@font-face` web fonts, easy branding.
- Loses: paginated data-dense tables (breaks, repeat headers, orphan control) are harder to tune than ReportLab's `repeatRows`. Performance on 1000+ page reports is poorer. Requires Cairo/Pango system libraries.

## When to pick WeasyPrint over ReportLab

```text
Marketing / brand-heavy layouts                  -> WeasyPrint
Designer delivers HTML/CSS                       -> WeasyPrint
Reuse existing web dashboard CSS                 -> WeasyPrint
Certificates, proposals, cover letters           -> WeasyPrint
Paginated financial tables (100+ pages)          -> ReportLab
Audit trails, statements, invoices               -> ReportLab
No system package install allowed                -> ReportLab
```

## System dependencies (Debian/Ubuntu)

```bash
apt-get install -y \
    python3-pip \
    libpango-1.0-0 libpangoft2-1.0-0 \
    libcairo2 libgdk-pixbuf-2.0-0 libffi-dev \
    libjpeg-dev libxml2 libxslt1.1 \
    shared-mime-info fonts-liberation
pip install weasyprint==62.3 pydyf==0.10.0
```

macOS dev: `brew install pango cairo gdk-pixbuf libffi`.
Docker: base on `python:3.12-slim-bookworm` and install the list above. Alpine is possible but fights musl — do not use Alpine for WeasyPrint unless you have to.

## Minimal render

```python
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

def render_pdf(html_str: str, css_paths: list[Path], output_path: Path):
    font_config = FontConfiguration()
    html = HTML(string=html_str, base_url=str(TEMPLATE_ROOT))
    stylesheets = [CSS(filename=str(p), font_config=font_config) for p in css_paths]
    html.write_pdf(
        target=str(output_path),
        stylesheets=stylesheets,
        font_config=font_config,
        optimize_images=True,
        jpeg_quality=85,
        presentational_hints=False,
    )
```

`base_url` is essential. Without it, relative `<img>` and `url(...)` references fail silently.

## Print-specific CSS

The heart of WeasyPrint work is the stylesheet.

```css
/* report.css */
:root {
  --brand-primary: #0B5FFF;
  --brand-text:    #111827;
  --brand-muted:   #6B7280;
  --brand-font:    "Inter", sans-serif;
}

@font-face {
  font-family: "Inter";
  src: url("fonts/Inter-Regular.ttf") format("truetype");
  font-weight: 400;
}
@font-face {
  font-family: "Inter";
  src: url("fonts/Inter-Bold.ttf") format("truetype");
  font-weight: 700;
}

@page {
  size: A4;
  margin: 25mm 18mm 20mm 18mm;

  @top-left  { content: element(running-logo); }
  @top-right { content: element(running-tenant); font-size: 9pt; color: var(--brand-muted); }
  @bottom-left  { content: "Confidential"; font-size: 8pt; color: var(--brand-muted); }
  @bottom-right { content: "Page " counter(page) " of " counter(pages);
                  font-size: 8pt; color: var(--brand-muted); }
}

@page :first {
  margin: 0;
  @top-left  { content: none; }
  @top-right { content: none; }
  @bottom-left  { content: none; }
  @bottom-right { content: none; }
}

/* Running elements: rendered once, repeated on every page. */
.running-logo    { position: running(running-logo);  }
.running-tenant  { position: running(running-tenant); }

body {
  font-family: var(--brand-font);
  color: var(--brand-text);
  font-size: 10pt;
  line-height: 1.45;
}

h1 { color: var(--brand-primary); font-size: 22pt; margin: 0 0 6pt; }
h2 { color: var(--brand-primary); font-size: 14pt; margin: 18pt 0 6pt;
     page-break-after: avoid; }

table.data { width: 100%; border-collapse: collapse; font-size: 9pt; }
table.data thead { display: table-header-group; }   /* repeat header across pages */
table.data tr    { page-break-inside: avoid; }
table.data th    { background: var(--brand-primary); color: #fff;
                   text-align: left; padding: 6pt 8pt; }
table.data td    { padding: 5pt 8pt; border-bottom: 0.5pt solid #E5E7EB; }
table.data tbody tr:nth-child(even) td { background: #F9FAFB; }

figure { page-break-inside: avoid; }
figure img { max-width: 100%; }
figcaption { font-size: 8pt; color: var(--brand-muted); margin-top: 3pt; }

.page-break { page-break-before: always; }

.toc a::after {
  content: leader(".") " " target-counter(attr(href), page);
}
```

## Running headers with logo

```html
<body>
  <div class="running-logo">
    <img src="logo.png" style="height: 10mm;">
  </div>
  <div class="running-tenant">{{ tenant.name }}</div>

  <section class="cover">
    <img src="logo.png" style="height: 25mm;">
    <h1>{{ title }}</h1>
    <p class="muted">{{ period }}</p>
  </section>

  <div class="page-break"></div>

  <h2>Executive Summary</h2>
  <p>...</p>
</body>
```

CSS `position: running(name)` + `@top-left { content: element(name) }` is how WeasyPrint does page-level repeating chrome. It beats fiddling with HTML-per-page tricks.

## Page counters and cross-references

```css
.toc-entry a::after {
  content: leader('.') " " target-counter(attr(href), page);
}
```

```html
<ul class="toc">
  <li class="toc-entry"><a href="#exec">Executive Summary</a></li>
  <li class="toc-entry"><a href="#fin">Financials</a></li>
</ul>
...
<section id="exec"><h2>Executive Summary</h2>...</section>
<section id="fin"><h2>Financials</h2>...</section>
```

WeasyPrint resolves `target-counter` at render time. You get a real ToC with page numbers, no manual counting.

## Jinja2 template pattern

```python
from jinja2 import Environment, FileSystemLoader, select_autoescape

def render_html(template_name: str, context: dict) -> str:
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_ROOT),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["money"] = lambda v: f"{v:,.2f}"
    env.filters["pct"] = lambda v: f"{v:.1%}"
    env.filters["date"] = lambda d, fmt="%d %b %Y": d.strftime(fmt)
    return env.get_template(template_name).render(**context)
```

Keep HTML and CSS in `templates/` and `static/`; base_url points at the project root so `<img src="static/logo.png">` resolves.

## Images and DPI

WeasyPrint treats CSS pixels as 96 DPI by default. For print, render raster images at 2x the display size and let CSS width handle scaling.

```html
<img src="chart.png" style="width: 160mm;">
<!-- chart.png should be 1260 px wide (160 mm * 2 * 96/25.4) for 192 DPI effective print -->
```

For charts, render matplotlib at `dpi=200` and scale in CSS. See `charts-for-embedding.md`.

## Per-tenant branding via CSS variables

```python
def tenant_css(brand) -> str:
    return f"""
    :root {{
      --brand-primary: {brand.primary};
      --brand-secondary: {brand.secondary};
      --brand-text: {brand.text};
      --brand-muted: {brand.muted};
      --brand-font: "{brand.font_family}", sans-serif;
    }}
    """

stylesheets = [
    CSS(filename=BASE_CSS),
    CSS(string=tenant_css(brand), font_config=font_config),
]
```

One base stylesheet, a small per-tenant override injected at render time. No template forks.

## Page break control

```css
h2 { page-break-after: avoid; }            /* don't orphan a heading */
.kpi-block, figure, blockquote { page-break-inside: avoid; }
.chapter { page-break-before: always; }
.widow-guard p { orphans: 3; widows: 3; }  /* prevents 1-line orphans */
```

## Anti-patterns

- Using `<canvas>` or JS-driven layouts — WeasyPrint does not run JavaScript.
- Assuming `@media print` from the web dashboard will just work — test and adjust.
- Leaving `base_url` unset and wondering why images are missing.
- Installing WeasyPrint on Alpine without patched musl — spurious glyph crashes.
- Rendering 500+ page reports with WeasyPrint — memory and time blow up; use ReportLab.
- Using `display: flex` in nested tables — WeasyPrint's flex support is solid in modern versions but nesting with `<table>` is still fragile.
- Forgetting to pin `weasyprint` and `pydyf` versions — minor releases break layout subtly.
