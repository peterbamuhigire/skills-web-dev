# Document Parsing Toolkit — PDFs + EPUBs

The full set of Python libraries (and their system-level dependencies) for reading, extracting, and converting PDF and EPUB documents. Use this when ingesting user-uploaded files, parsing books / manuals / reports, or building OCR pipelines.

Complements `ocr-tesseract.md` and `pdf-extraction.md` (PDF-specific recipes).

## System dependencies

Several Python libraries are thin wrappers over native binaries. Missing binaries is the #1 reason a "pdf reader" fails silently. Install these first.

### Debian / Ubuntu

```bash
sudo apt install -y poppler-utils tesseract-ocr tesseract-ocr-eng ghostscript libreoffice default-jre
# Optional extra Tesseract language packs:
sudo apt install -y tesseract-ocr-swa tesseract-ocr-fra
```

### macOS (Homebrew)

```bash
brew install poppler tesseract tesseract-lang ghostscript openjdk
```

### Windows (Chocolatey)

```powershell
choco install poppler          # provides pdftoppm, pdftotext, pdfinfo
choco install tesseract        # OCR engine
choco install ghostscript
choco install openjdk          # for tabula-py only
```

After install, confirm each is on `PATH`:

```bash
pdftoppm -v && pdftotext -v && tesseract --version && gs --version
```

## Python libraries — by purpose

### PDF: text and layout

```bash
uv pip install pymupdf pdfplumber pypdf pdfminer.six
```

- **PyMuPDF (`fitz`)** — fastest, most capable. Text, images, metadata, rendering, annotations, redaction. AGPL licence; commercial licence available.
- **pdfplumber** — default for born-digital PDFs. Text with bounding boxes, simple table extraction, visual debugging. MIT.
- **pypdf** (formerly PyPDF2) — pure-Python, good for split/merge/rotate/metadata. BSD.
- **pdfminer.six** — low-level text extraction; reach for this only when the output of others is unusable. MIT.

### PDF: tables

```bash
uv pip install "camelot-py[cv]"
uv pip install tabula-py      # needs Java
```

- **camelot-py** — two strategies: `lattice` for ruled tables, `stream` for whitespace-separated. Requires ghostscript + opencv. MIT.
- **tabula-py** — wraps the Java Tabula tool. Often different results to camelot; try both when one disappoints. MIT.

### PDF: pages to images

```bash
uv pip install pdf2image
```

- **pdf2image** — wraps `pdftoppm` from poppler. Returns PIL Images you can save as PNG/JPG/WebP. Required when you need to run custom OCR or image processing on each page. MIT.

### PDF: scanned-document OCR

```bash
uv pip install ocrmypdf pytesseract
```

- **ocrmypdf** — takes a scanned PDF and returns a searchable PDF with a hidden text layer. Wraps Tesseract, ghostscript, pikepdf. Idempotent (`--skip-text`). MIT.
- **pytesseract** — direct Python wrapper for Tesseract. Use when you want finer control (PSM mode, language, per-page processing).

### EPUB

```bash
uv pip install ebooklib beautifulsoup4 lxml html5lib
```

- **ebooklib** — de facto standard. Reads EPUB 2 + 3, exposes items, metadata, TOC, spine. MIT.
- **beautifulsoup4 + lxml** — parse the XHTML inside EPUB items. (html5lib is a more forgiving parser fallback.)

### Universal / cross-format

```bash
uv pip install "unstructured[pdf,epub,docx]" pypandoc
```

- **unstructured** — one API for PDFs, EPUBs, DOCX, HTML, images. Returns document elements (titles, paragraphs, tables) ready for indexing or RAG. Heavyweight; pulls many deps. Apache-2.
- **pypandoc** — Python binding for Pandoc. Converts EPUB / DOCX / HTML / LaTeX between any pair. Needs the `pandoc` binary installed.

## Decision matrix — which tool for which job

```text
Born-digital PDF, extract plain text        -> pdfplumber OR PyMuPDF
Born-digital PDF, extract tables (ruled)    -> camelot-py (lattice mode)
Born-digital PDF, extract tables (no borders)-> camelot-py (stream) OR tabula-py
Born-digital PDF, extract images            -> PyMuPDF
Scanned PDF, need searchable text           -> ocrmypdf (then pdfplumber/PyMuPDF)
Scanned PDF, need per-page image processing -> pdf2image + opencv + pytesseract
PDF metadata / merge / split / rotate       -> pypdf
Redact / annotate PDF                       -> PyMuPDF
EPUB: read items + metadata                 -> ebooklib
EPUB: extract clean text                    -> ebooklib + BeautifulSoup
EPUB: convert to Markdown / plain text      -> pypandoc
One API for PDF + EPUB + DOCX (RAG-ready)   -> unstructured
Ugly PDF where nothing works                -> pdfminer.six (low-level) or render + OCR
```

## Minimal recipes

### Extract text from a PDF (pdfplumber)

```python
import pdfplumber

with pdfplumber.open(path) as pdf:
    for page in pdf.pages:
        text = page.extract_text() or ""
        print(f"--- page {page.page_number} ---")
        print(text)
```

### Extract text from a PDF (PyMuPDF, fastest)

```python
import pymupdf  # pip install pymupdf

doc = pymupdf.open(path)
for page in doc:
    print(page.get_text())
doc.close()
```

### Extract a table (camelot)

```python
import camelot

tables = camelot.read_pdf(str(path), pages="1-end", flavor="lattice")
for t in tables:
    df = t.df   # pandas DataFrame
```

### OCR a scanned PDF in place (ocrmypdf)

```bash
ocrmypdf --skip-text --language eng --output-type pdfa input.pdf output.pdf
```

### Render PDF pages to images (pdf2image)

```python
from pdf2image import convert_from_path

images = convert_from_path(path, dpi=200)
for i, img in enumerate(images, start=1):
    img.save(f"page-{i}.webp", "WEBP", quality=85)
```

### Read an EPUB (ebooklib + BeautifulSoup)

```python
from ebooklib import epub, ITEM_DOCUMENT
from bs4 import BeautifulSoup

book = epub.read_epub(path)
print("Title:", book.get_metadata("DC", "title"))
for item in book.get_items_of_type(ITEM_DOCUMENT):
    soup = BeautifulSoup(item.get_content(), "lxml")
    text = soup.get_text(separator="\n", strip=True)
    print(text[:500])
```

### Convert EPUB to Markdown (pypandoc)

```python
import pypandoc

pypandoc.convert_file("book.epub", "markdown", outputfile="book.md")
```

### Unified parsing (unstructured)

```python
from unstructured.partition.auto import partition

elements = partition(filename=path)
for el in elements:
    print(type(el).__name__, "-", str(el)[:200])
```

## Licensing notes

- **PyMuPDF** is AGPL — if you ship a SaaS that embeds PyMuPDF, either open-source the service or buy a commercial licence from Artifex.
- **Most others** (pdfplumber, pypdf, pdfminer.six, ebooklib, camelot, tabula, ocrmypdf, pdf2image, unstructured) are permissive (MIT / BSD / Apache-2 / GPL for some wrapped tools).
- **Check the Tesseract model licences** you ship (most are Apache-2).

## Common pitfalls

- **`pdftoppm not found`** — poppler isn't installed or not on PATH. Fix with the OS installs above.
- **`TesseractNotFoundError`** — Tesseract binary missing. Install + ensure `tesseract` is on PATH.
- **camelot returns empty** — try the other flavor (`lattice` vs `stream`); try `flavor="stream", strip_text="\n"`.
- **EPUB "encrypted"** — some publisher EPUBs use Adobe DRM; these require legal removal before extraction.
- **Garbled PDF text** — scanned PDF masquerading as digital; route it through ocrmypdf first.
- **Memory spike on huge PDFs** — page-by-page iteration (PyMuPDF or pdfplumber) rather than loading everything.
- **Unicode issues** — pdfminer sometimes fails on non-Latin scripts; switch to PyMuPDF.

## Read next

- `references/pdf-extraction.md` — production PDF extraction patterns.
- `references/ocr-tesseract.md` — OCR pipeline with preprocessing.
- `references/image-processing-pillow.md` — image preprocessing before OCR.
- `python-document-generation` (sister skill) — *writing* PDFs/Word/Excel, not reading them.
