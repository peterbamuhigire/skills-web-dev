# PDF Extraction

PDFs come in two flavours: born-digital (text layer present) and scanned (image only). Pick the tool accordingly.

## Detect text vs scanned

Always detect first. A wrong choice wastes seconds per page and produces garbage.

```python
import pdfplumber

def classify_pdf(path: str) -> str:
    """Return 'text', 'scanned', or 'mixed'."""
    with pdfplumber.open(path) as pdf:
        text_pages = 0
        total = len(pdf.pages)
        for page in pdf.pages:
            t = (page.extract_text() or "").strip()
            if len(t) >= 40:
                text_pages += 1
    if text_pages == total:
        return "text"
    if text_pages == 0:
        return "scanned"
    return "mixed"
```

Threshold of 40 characters catches pages that contain only a page number or a stamp.

## pdfplumber — text PDFs

Use for born-digital PDFs. Fast, no external binaries.

```python
import pdfplumber

def extract_text(path: str) -> list[str]:
    pages = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            pages.append(page.extract_text(x_tolerance=2, y_tolerance=2) or "")
    return pages
```

`x_tolerance` / `y_tolerance` control how characters are grouped. Default is fine for most documents; raise when columns bleed together, lower when letters are squashed.

### Tables

```python
def extract_tables(path: str) -> list[list[list[str]]]:
    tables = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            found = page.extract_tables(table_settings={
                "vertical_strategy": "lines",      # use actual drawn lines
                "horizontal_strategy": "lines",
                "snap_tolerance": 3,
                "join_tolerance": 3,
                "edge_min_length": 10,
                "intersection_y_tolerance": 3,
            })
            tables.extend(found)
    return tables
```

Strategy options:

- `"lines"` — the PDF has visible gridlines. Most reliable.
- `"text"` — no gridlines, infer columns from text alignment. Works for well-aligned tables.
- `"explicit"` — you supply the edges.

If the table has no visible lines, start with `"text"`. If it breaks, switch to camelot.

## camelot — complex tables

`camelot` is better than pdfplumber for dense financial tables, multi-line cells, and tables without full borders. It needs Ghostscript (`apt-get install ghostscript`).

```python
import camelot

# "lattice" = tables with visible lines; "stream" = tables with whitespace
tables = camelot.read_pdf(path, pages="all", flavor="lattice")
for t in tables:
    df = t.df            # pandas DataFrame
    accuracy = t.parsing_report["accuracy"]   # 0–100
```

Decision:

- Gridlines present → `flavor="lattice"`.
- No gridlines, aligned whitespace columns → `flavor="stream"`.
- Try both, pick the one with higher `accuracy` in `parsing_report`.

### When to reach for camelot vs pdfplumber

| Scenario | Tool |
|---|---|
| Simple tables with gridlines | pdfplumber (lines) |
| Bank statements with tight rows and borders | camelot lattice |
| Rate cards / price lists with no lines | camelot stream |
| Multi-page table with repeated header | camelot with `row_tol` |
| Tables with merged cells | camelot lattice, then post-process |

## ocrmypdf — scanned PDFs

Wraps Tesseract. Produces a searchable PDF with a text layer over the original image. Then extract with pdfplumber.

```bash
# System deps
sudo apt-get install -y ocrmypdf
```

```python
import subprocess
from pathlib import Path

def make_searchable(src: Path, dst: Path, lang: str = "eng") -> None:
    subprocess.run(
        [
            "ocrmypdf",
            "--language", lang,
            "--rotate-pages",
            "--deskew",
            "--clean",               # uses unpaper to clean up
            "--skip-text",           # if pages already have text, skip them (cheap no-op for mixed PDFs)
            "--optimize", "1",
            "--jobs", "2",
            str(src),
            str(dst),
        ],
        check=True,
        timeout=300,
    )
```

Rules:

- `--skip-text` is essential for mixed PDFs — prevents double-OCR of pages that already have a text layer.
- `--rotate-pages` + `--deskew` handle scanner orientation issues.
- Cap with `timeout=` — runaway OCR on a huge document can tie up a worker.
- Set `--jobs` to CPU count per worker, not total CPU count.

## Combining strategies — the real pipeline

```python
def extract_pdf(tenant_id: int, path: Path) -> ExtractResult:
    kind = classify_pdf(str(path))

    if kind == "text":
        text_pages = extract_text(str(path))
        tables = extract_tables(str(path))
        return ExtractResult(tenant_id, kind, text_pages, tables)

    if kind == "scanned":
        searchable = path.with_suffix(".searchable.pdf")
        make_searchable(path, searchable, lang="eng")
        text_pages = extract_text(str(searchable))
        return ExtractResult(tenant_id, kind, text_pages, tables=[])

    # mixed — OCR only where needed
    searchable = path.with_suffix(".searchable.pdf")
    make_searchable(path, searchable, lang="eng")     # --skip-text keeps it cheap
    text_pages = extract_text(str(searchable))
    tables = extract_tables(str(searchable))
    return ExtractResult(tenant_id, kind, text_pages, tables)
```

## Security — uploaded PDFs

Every tenant-uploaded PDF is untrusted input. Before extraction:

1. **Validate MIME by content, not by extension.** Use `python-magic`:

```python
import magic

def is_pdf(path: Path) -> bool:
    mime = magic.from_file(str(path), mime=True)
    return mime == "application/pdf"
```

2. **Enforce a size cap.** 25 MB per upload is a reasonable ceiling for receipts/invoices. Reject anything bigger at the API layer; never load a 500 MB PDF into memory.

3. **Cap page count.** Before full extraction, open and count pages. Refuse > 500 pages unless the tenant is on a tier that allows it.

```python
def page_count(path: str) -> int:
    with pdfplumber.open(path) as pdf:
        return len(pdf.pages)
```

4. **Sandbox the extraction.** Ghostscript and Tesseract are large C codebases with CVE history. Run the extraction process:

   - as a non-privileged user,
   - in a container or under AppArmor / seccomp,
   - with a CPU and memory cgroup limit (e.g. 2 CPU, 2 GB RAM),
   - with a wall-clock timeout (e.g. 5 minutes per document).

5. **Scan for malware.** Pass the upload through ClamAV before extraction. Cheap insurance:

```python
import subprocess

def clam_scan(path: Path) -> None:
    r = subprocess.run(["clamdscan", "--fdpass", str(path)], capture_output=True, timeout=30)
    if r.returncode != 0:
        raise MalwareDetected(r.stdout.decode())
```

6. **Strip JavaScript and embedded objects.** If you will serve the PDF back to users, use `qpdf --linearize --object-streams=disable --decrypt` first, or flatten with Ghostscript.

## Encrypted PDFs

```python
import pdfplumber

try:
    with pdfplumber.open(path, password="") as pdf:
        ...
except Exception as e:
    # decrypt with tenant-supplied password if available
    ...
```

Never store the decryption password in the same row as the document. If the tenant provides a password, use it once to strip encryption (via `qpdf`), store the decrypted PDF, and discard the password.

## Performance

- Text extraction: 100–300 pages/second on a modern server.
- OCR: 0.5–2s per page, CPU-bound.
- Table extraction (camelot lattice): 0.2–1s per page.

Run OCR and camelot in a process pool, not threads. Both hit the GIL effectively.

```python
from concurrent.futures import ProcessPoolExecutor

with ProcessPoolExecutor(max_workers=4) as pool:
    results = list(pool.map(ocr_and_extract, paths))
```

## Anti-patterns

- Extracting text with PyPDF2 / pypdf for complex layouts — pdfplumber is better.
- OCR-ing every PDF "to be safe" instead of detecting first.
- Accepting the uploaded filename's extension as proof of MIME type.
- No size cap on uploads.
- Running ocrmypdf in the web request — always background it, 30s+ timeouts are normal.
- Skipping `--skip-text` on mixed PDFs and double-OCR-ing good pages.
