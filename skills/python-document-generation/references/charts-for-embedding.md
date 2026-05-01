# Charts for Embedding

Charts in downloadable artefacts must render identically on any server (no GUI), at print quality, with a consistent brand palette, and without leaking memory after thousands of jobs.

## Rules

1. Always `matplotlib.use("Agg")` before importing `pyplot`. Headless backend.
2. Always create explicit `fig, ax = plt.subplots(...)`. Never use the pyplot stateful API in a worker.
3. Always `plt.close(fig)` (or `matplotlib.pyplot.close("all")`). Matplotlib leaks figure memory — workers OOM after a few hundred charts.
4. Set DPI based on destination: 100 for screen, 150 for Word/PDF body, 200 for cover pages or large prints.
5. Size figures in inches at the DPI you intend. A 1600 x 800 px chart for a Word document at `dpi=200` is `figsize=(8, 4)`.
6. Use a palette derived from the tenant's `Brand`. No default matplotlib rainbow.

## Safe bootstrap

```python
import os
os.environ.setdefault("MPLBACKEND", "Agg")   # belt-and-braces before any import

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
```

Put this in a single `charts/bootstrap.py` module imported at worker startup.

## Brand-aware palette

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class ChartPalette:
    primary: str
    secondary: str
    accent: str
    muted: str
    grid: str = "#E5E7EB"
    text: str = "#111827"
    sequence: tuple = ()

    @classmethod
    def from_brand(cls, brand):
        return cls(
            primary=brand.primary,
            secondary=brand.secondary,
            accent=getattr(brand, "accent", "#F59E0B"),
            muted=brand.muted,
            sequence=(
                brand.primary,
                brand.secondary,
                getattr(brand, "accent", "#F59E0B"),
                "#10B981",
                "#8B5CF6",
                "#EC4899",
            ),
        )
```

Apply once per figure:

```python
def apply_chart_style(ax, palette: ChartPalette, brand_font: str):
    ax.set_prop_cycle(color=list(palette.sequence))
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(palette.grid)
    ax.spines["bottom"].set_color(palette.grid)
    ax.tick_params(colors=palette.muted, labelsize=9)
    ax.grid(True, axis="y", color=palette.grid, linewidth=0.6)
    ax.set_axisbelow(True)
    for label in ax.get_xticklabels() + ax.get_yticklabels():
        label.set_fontname(brand_font)
```

## DPI presets

```python
DPI_EXCEL_EMBED = 110     # xlsxwriter insert_image at x_scale ~1.0
DPI_WORD_BODY   = 200     # python-docx add_picture width Mm(160)
DPI_PDF_BODY    = 200     # reportlab Image() at computed size
DPI_COVER       = 240     # full-page hero charts
```

## Size presets by destination

```python
FIG_EXCEL_EMBED = (6.5, 3.25)   # fits under a KPI block, ~625 x 325 px @ 100 dpi
FIG_WORD_BODY   = (7.5, 3.5)    # full column width in A4 portrait
FIG_PDF_HALF    = (5.5, 3.0)    # half-page
FIG_PDF_FULL    = (7.8, 4.2)
FIG_COVER_HERO  = (8.5, 3.2)
```

## Canonical line-chart recipe

```python
def render_trend_line(df, value_col, title, out_path, brand, palette,
                      size=FIG_WORD_BODY, dpi=DPI_WORD_BODY):
    fig, ax = plt.subplots(figsize=size, dpi=dpi)
    apply_chart_style(ax, palette, brand.font_family)

    ax.plot(df.index, df[value_col],
            color=palette.primary, linewidth=2.0,
            marker="o", markersize=3.5, markerfacecolor=palette.primary)

    ax.fill_between(df.index, df[value_col], alpha=0.08, color=palette.primary)

    ax.set_title(title, fontsize=12, fontweight="bold",
                 color=palette.text, loc="left", pad=10,
                 fontname=brand.font_family)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:,.0f}"))
    ax.margins(x=0.01)

    fig.tight_layout()
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close(fig)
```

## Bar chart with annotations

```python
def render_bar(df, category_col, value_col, title, out_path, brand, palette,
               size=FIG_PDF_HALF, dpi=DPI_PDF_BODY):
    fig, ax = plt.subplots(figsize=size, dpi=dpi)
    apply_chart_style(ax, palette, brand.font_family)

    bars = ax.bar(df[category_col], df[value_col],
                  color=palette.primary, width=0.65, linewidth=0)

    for bar in bars:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2, h,
                f"{h:,.0f}", ha="center", va="bottom",
                fontsize=8, color=palette.text,
                fontname=brand.font_family)

    ax.set_title(title, fontsize=12, fontweight="bold", loc="left", pad=10)
    ax.set_ylim(0, max(df[value_col]) * 1.15)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:,.0f}"))

    fig.tight_layout()
    fig.savefig(out_path, dpi=dpi, bbox_inches="tight", facecolor="white")
    plt.close(fig)
```

## Plotly static export (kaleido)

When the rest of the app is Plotly (web dashboard) and you want to reuse the exact same figure definition.

```python
import plotly.graph_objects as go

def render_plotly_png(fig: go.Figure, out_path, width=1600, height=800, scale=1.5):
    # scale=1.5 with width=1600 => effective 2400 px at render, 300 dpi at 8 inch width.
    fig.write_image(out_path, width=width, height=height, scale=scale, engine="kaleido")
```

Pin kaleido to a known version (`kaleido==0.2.1`). Later 1.x releases changed the engine. Install the matching Chromium binary the kaleido version ships with.

Trade-off: Kaleido spawns a Chromium process per export. Slower than matplotlib. For high-volume chart generation, stay on matplotlib. Use Plotly exports only when the parity with the web dashboard matters.

## Sizing for destination

### Excel embedding

xlsxwriter's `insert_image` expects image pixels, not inches. Render at display DPI to keep file size small:

```python
render_trend_line(..., size=FIG_EXCEL_EMBED, dpi=DPI_EXCEL_EMBED)
ws.insert_image("B18", png_path, {"x_scale": 1.0, "y_scale": 1.0})
```

Oversizing the raster produces huge `.xlsx` files.

### Word (python-docx)

```python
doc.add_picture(str(png_path), width=Mm(160))   # render at dpi=200 and the column width constraint handles final size
```

### ReportLab PDF

```python
from reportlab.lib.units import mm
img = Image(str(png_path), width=160*mm, height=80*mm)
```

Render matplotlib at a ratio that matches this aspect (2:1 here), then ReportLab does not distort.

### WeasyPrint PDF

Render at 2x display pixel count, set CSS `width: 160mm;`. Browser/WeasyPrint handles the DPI calculation.

## Memory hygiene

```python
try:
    render_trend_line(...)
    render_bar(...)
    render_stacked_area(...)
finally:
    plt.close("all")
    import gc
    gc.collect()
```

In a worker loop, call `plt.close("all")` at the end of each job. For long-lived worker processes, recycle the process every N jobs (`max_jobs_per_child` in your worker config) — matplotlib's font cache and backend state still grow slowly.

## Parallel chart generation

Threads do not help — matplotlib's internal state is not thread-safe for simultaneous figure building. Use process pools:

```python
from concurrent.futures import ProcessPoolExecutor

def build_charts_parallel(spec_list, out_dir, brand):
    with ProcessPoolExecutor(max_workers=4, initializer=_chart_worker_init) as pool:
        futures = [pool.submit(_render_one, spec, out_dir, brand) for spec in spec_list]
        for f in futures:
            f.result()

def _chart_worker_init():
    import matplotlib
    matplotlib.use("Agg")
```

Pass picklable spec dicts, not matplotlib objects. The worker rebuilds the figure from the spec. Always `max_workers = min(cpu_count, 4)` unless you have measured otherwise — chart rendering is CPU-bound and RAM-hungry.

## Anti-patterns

- Using `plt.plot(...)` without a `fig, ax` handle — pyplot stores figures in a global registry that grows forever in long-running workers.
- Forgetting to `plt.close(fig)` — visible only after 500+ jobs, by which point the worker has OOM'd and restarted mid-job.
- Setting chart colours per-call with hex strings scattered across the codebase — use `ChartPalette.from_brand(brand)`.
- Rendering charts inside a web request — put chart generation in the worker; return a signed URL to the final artefact.
- Relying on the default matplotlib font — it is DejaVu Sans; most reports look amateur next to a branded PDF cover. Register and use the brand font.
- Using `tight_layout()` and `bbox_inches="tight"` together with expectations of pixel-exact size — they fight each other. Pick one, usually `bbox_inches="tight"` for embedding.
