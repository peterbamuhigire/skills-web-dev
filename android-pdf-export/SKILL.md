---
name: android-pdf-export
description: Native Android PDF export system using PdfDocument API (zero dependencies).
  Reusable Canvas-based generator with branded letterheads, data tables, summary cards,
  and share-via-Intent. Use when adding PDF export to any Android app screen —...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---


## Platform Notes

- Claude Code: use Superpowers or similar helpers when they are available and materially useful.
- Codex: apply this skill normally; do not treat optional plugins as a prerequisite.

# Android PDF Export (Native PdfDocument)

<!-- dual-compat-start -->
## Use When

- Native Android PDF export system using PdfDocument API (zero dependencies). Reusable Canvas-based generator with branded letterheads, data tables, summary cards, and share-via-Intent. Use when adding PDF export to any Android app screen —...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `android-pdf-export` or would be better handled by a more specific companion skill.
- The request only needs a trivial answer and none of this skill's constraints or references materially help.

## Required Inputs

- Gather relevant project context, constraints, and the concrete problem to solve.
- Confirm the desired deliverable: design, code, review, migration plan, audit, or documentation.

## Workflow

- Read this `SKILL.md` first, then load only the referenced deep-dive files that are necessary for the task.
- Apply the ordered guidance, checklists, and decision rules in this skill instead of cherry-picking isolated snippets.
- Produce the deliverable with assumptions, risks, and follow-up work made explicit when they matter.

## Quality Standards

- Keep outputs execution-oriented, concise, and aligned with the repository's baseline engineering standards.
- Preserve compatibility with existing project conventions unless the skill explicitly requires a stronger standard.
- Prefer deterministic, reviewable steps over vague advice or tool-specific magic.

## Anti-Patterns

- Treating examples as copy-paste truth without checking fit, constraints, or failure modes.
- Loading every reference file by default instead of using progressive disclosure.

## Outputs

- A concrete result that fits the task: implementation guidance, review findings, architecture decisions, templates, or generated artifacts.
- Clear assumptions, tradeoffs, or unresolved gaps when the task cannot be completed from available context alone.
- References used, companion skills, or follow-up actions when they materially improve execution.

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
Generate professional branded PDF documents from any Android screen using the built-in `android.graphics.pdf.PdfDocument` API. Zero external dependencies — pure Canvas drawing. Supports A4 portrait/landscape, multi-page pagination, letterheads, tables, summary cards, info sections, status badges, and charts.

## Overview

**Library choice:** Native `android.graphics.pdf.PdfDocument` (0 KB added to APK). Alternatives like iText (AGPL license), PDFBox-Android (stale since 2023), and OpenPDF (requires java.awt hack) were rejected.

**Architecture:** A core `DmsPdfGenerator` object provides reusable drawing primitives. Per-module exporters (Sales, Inventory, Network) compose these primitives for each screen. `PdfExportHelper` handles file I/O and sharing via `FileProvider`.

```
core/pdf/
  DmsPdfGenerator.kt         — Reusable drawing primitives (letterhead, tables, cards, footer)
  PdfExportHelper.kt          — Save to cache + share via FileProvider Intent

core/ui/components/
  PdfExportButton.kt          — Reusable TopAppBar button (icon + "PDF" label)

Per-module exporters (one object per feature module):
  SalesReportPdfExporter.kt   — Sales reports + invoice list
  InventoryPdfExporter.kt     — Stock levels, PO/transfer/adjustment details + lists
  NetworkPdfExporter.kt       — Distributor list/detail, genealogy
```

## Dependencies

**None.** Uses only Android SDK classes:
- `android.graphics.pdf.PdfDocument`
- `android.graphics.Canvas`, `Paint`, `TextPaint`, `Typeface`, `Color`
- `android.text.StaticLayout`, `android.text.TextUtils`
- `androidx.core.content.FileProvider` (already in most projects)

## Step 1: FileProvider Setup

### AndroidManifest.xml

```xml
<provider
    android:name="androidx.core.content.FileProvider"
    android:authorities="${applicationId}.fileprovider"
    android:exported="false"
    android:grantUriPermissions="true">
    <meta-data
        android:name="android.support.FILE_PROVIDER_PATHS"
        android:resource="@xml/file_paths" />
</provider>
```

### res/xml/file_paths.xml (NEW)

```xml
<?xml version="1.0" encoding="utf-8"?>
<paths>
    <cache-path name="pdf_exports" path="pdf_exports/" />
</paths>
```

## Step 2: PdfExportHelper

Saves the PdfDocument to the app's cache directory and launches a share sheet or PDF viewer.

```kotlin
object PdfExportHelper {

    fun exportAndShare(context: Context, document: PdfDocument, filename: String, title: String) {
        try {
            val file = savePdfToCache(context, document, filename)
            sharePdf(context, file, title)
            Toast.makeText(context, context.getString(R.string.pdf_export_success), Toast.LENGTH_SHORT).show()
        } catch (e: Exception) {
            Toast.makeText(context, context.getString(R.string.pdf_export_error), Toast.LENGTH_SHORT).show()
        } finally {
            document.close()
        }
    }

    private fun savePdfToCache(context: Context, document: PdfDocument, filename: String): File {
        val dir = File(context.cacheDir, "pdf_exports").apply { mkdirs() }
        val sanitized = filename.replace(Regex("[^a-zA-Z0-9._-]"), "_")
        val file = File(dir, "$sanitized.pdf")
        file.outputStream().use { document.writeTo(it) }
        return file
    }

    private fun sharePdf(context: Context, file: File, title: String) {
        val uri = FileProvider.getUriForFile(context, "${context.packageName}.fileprovider", file)
        val intent = Intent(Intent.ACTION_SEND).apply {
            type = "application/pdf"
            putExtra(Intent.EXTRA_STREAM, uri)
            putExtra(Intent.EXTRA_SUBJECT, title)
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        }
        context.startActivity(Intent.createChooser(intent, context.getString(R.string.pdf_share)))
    }
}
```

## Step 3: Core PDF Generator

The `DmsPdfGenerator` object provides all reusable drawing functions. Every function takes a `Canvas`, a current Y position, draws content, and returns the new Y position.

### Constants & Types

```kotlin
object DmsPdfGenerator {
    // A4 dimensions in PostScript points
    const val A4_WIDTH = 595
    const val A4_HEIGHT = 842
    const val A4_LAND_WIDTH = 842
    const val A4_LAND_HEIGHT = 595
    const val MARGIN = 40f

    // Brand colors (customize per project)
    val BRAND_RED = Color.rgb(198, 40, 40)        // #C62828
    val HEADER_BG = Color.rgb(176, 228, 252)       // #B0E4FC (table headers)
    val ALT_ROW = Color.rgb(248, 249, 250)         // #F8F9FA (alternating rows)
    val SUMMARY_BG = Color.rgb(240, 244, 248)      // Summary card background
    val ACCENT_BLUE = Color.rgb(32, 107, 196)      // #206BC4 (KPI values)
    val TEXT_BLACK = Color.rgb(33, 37, 41)
    val TEXT_GRAY = Color.rgb(108, 117, 125)
    val DIVIDER_GRAY = Color.rgb(200, 200, 200)

    data class FranchiseInfo(
        val name: String,
        val address: String?,
        val phone: String?,
        val email: String?,
        val taxId: String?,
        val currency: String
    )

    data class TableColumn(
        val header: String,
        val widthWeight: Float,
        val alignment: Paint.Align = Paint.Align.LEFT
    )
}
```

### Page Management

```kotlin
fun createDocument(): PdfDocument = PdfDocument()

fun startPage(doc: PdfDocument, pageNum: Int, landscape: Boolean = false): PdfDocument.Page {
    val w = if (landscape) A4_LAND_WIDTH else A4_WIDTH
    val h = if (landscape) A4_LAND_HEIGHT else A4_HEIGHT
    val pageInfo = PdfDocument.PageInfo.Builder(w, h, pageNum).create()
    return doc.startPage(pageInfo)
}

fun newPageIfNeeded(
    doc: PdfDocument, currentPage: PdfDocument.Page,
    y: Float, pageNum: Int, landscape: Boolean,
    footerUser: String
): Triple<PdfDocument.Page, Float, Int> {
    val ph = if (landscape) A4_LAND_HEIGHT else A4_HEIGHT
    if (y < ph - 50f - MARGIN) return Triple(currentPage, y, pageNum)
    // Finish current page with footer
    drawFooter(currentPage.canvas, pageNum, -1, footerUser,
        if (landscape) A4_LAND_WIDTH else A4_WIDTH, ph)
    doc.finishPage(currentPage)
    // Start new page
    val newNum = pageNum + 1
    val newPage = startPage(doc, newNum, landscape)
    return Triple(newPage, MARGIN + 10f, newNum)
}
```

### Drawing Functions

Each function draws content at the given Y position and returns the new Y:

```kotlin
// ── Letterhead ──
fun drawLetterhead(canvas: Canvas, y: Float, logo: Bitmap?,
                   info: FranchiseInfo, pageWidth: Int): Float
// Logo (50x50), franchise name (bold 14pt red), address/phone/email (9pt gray), divider

// ── Report Title ──
fun drawReportTitle(canvas: Canvas, y: Float, title: String,
                    subtitle: String? = null, pageWidth: Int): Float
// Centered title (14pt bold uppercase), optional subtitle (10pt gray)

// ── Summary Cards ──
fun drawSummaryCards(canvas: Canvas, y: Float,
                     items: List<Pair<String, String>>, pageWidth: Int): Float
// Row of KPI boxes: label (9pt gray) + value (13pt bold accent blue)

// ── Data Table ──
fun drawTable(canvas: Canvas, y: Float, columns: List<TableColumn>,
              rows: List<List<String>>, pageWidth: Int,
              totalsRow: List<String>? = null): Float
// Header row (light blue bg), data rows (alternating), optional totals footer
// Supports multi-line cells via \n (first line normal, second line smaller gray)

// ── Info Section ──
fun drawInfoSection(canvas: Canvas, y: Float, title: String?,
                    items: List<Pair<String, String>>, pageWidth: Int): Float
// Key-value pairs for detail screens (label: value format)

// ── Status Badge ──
fun drawStatusBadge(canvas: Canvas, y: Float, status: String,
                    bgColor: Int, pageWidth: Int): Float
// Centered colored rounded rect with white text

// ── Chart Bitmap ──
fun drawChartBitmap(canvas: Canvas, y: Float, bitmap: Bitmap,
                    pageWidth: Int): Float
// Scaled bitmap centered on page, max 250pt height

// ── Footer ──
fun drawFooter(canvas: Canvas, pageNumber: Int, totalPages: Int,
               generatedBy: String, pageWidth: Int, pageHeight: Int)
// "Generated by X on DATE" (left) + "Page N of M" (right) at bottom
```

### Table Implementation (Key Details)

The table is the most complex component. Key features:

```kotlin
fun drawTable(
    canvas: Canvas, y: Float,
    columns: List<TableColumn>,
    rows: List<List<String>>,
    pageWidth: Int,
    totalsRow: List<String>? = null
): Float {
    val contentWidth = pageWidth - 2 * MARGIN
    val totalWeight = columns.sumOf { it.widthWeight.toDouble() }.toFloat()
    val rowHeight = 18f
    val cellPadding = 4f

    // Calculate column positions from weights
    val colPositions = mutableListOf<Float>()
    var xPos = MARGIN
    columns.forEach { col ->
        colPositions.add(xPos)
        xPos += (col.widthWeight / totalWeight) * contentWidth
    }

    // Header row (light blue background, bold white text)
    // ...

    // Data rows (alternating background, multi-line support)
    rows.forEachIndexed { rowIdx, row ->
        val hasMultiLine = row.any { it.contains('\n') }
        val thisRowHeight = if (hasMultiLine) rowHeight + 10f else rowHeight

        if (rowIdx % 2 == 1) drawAltBackground(...)

        row.forEachIndexed { colIdx, value ->
            if (value.contains('\n')) {
                // Multi-line: first line normal 8pt, second line 7pt gray
                val lines = value.split('\n', limit = 2)
                canvas.drawText(lines[0], textX, currentY + 11f, bodyPaint)
                canvas.drawText(lines[1], textX, currentY + 21f, subPaint)
            } else {
                canvas.drawText(value, textX, currentY + 11f, bodyPaint)
            }
        }
        currentY += thisRowHeight
    }

    // Optional totals row (same bg as header)
    // ...
}
```

## Step 4: Per-Module Exporters

Each exporter is an `object` with one function per screen. Every function follows the same pattern:

```kotlin
object SalesReportPdfExporter {

    private val formatter = NumberFormat.getNumberInstance(Locale.US).apply {
        minimumFractionDigits = 2; maximumFractionDigits = 2
    }
    private fun cfmt(c: String, v: Double) = "$c ${formatter.format(v)}"

    fun exportTopSellers(
        context: Context,
        authManager: AuthManager,
        report: TopSellersReport,
        currency: String,
        startDate: String,
        endDate: String,
        dpcName: String?
    ) {
        val pdf = DmsPdfGenerator
        val doc = pdf.createDocument()
        val landscape = true
        val pw = if (landscape) DmsPdfGenerator.A4_LAND_WIDTH else DmsPdfGenerator.A4_WIDTH
        val ph = if (landscape) DmsPdfGenerator.A4_LAND_HEIGHT else DmsPdfGenerator.A4_HEIGHT

        try {
            var page = pdf.startPage(doc, 1, landscape)
            var canvas = page.canvas
            var y = DmsPdfGenerator.MARGIN

            // 1. Letterhead
            val logo = getBrandLogo(context)
            val info = franchiseInfo(authManager)
            y = pdf.drawLetterhead(canvas, y, logo, info, pw)

            // 2. Title + subtitle (date range, filters)
            y = pdf.drawReportTitle(canvas, y, "TOP SELLERS REPORT",
                buildSubtitle(context, startDate, endDate, dpcName), pw)

            // 3. Summary cards
            val s = report.summary
            y = pdf.drawSummaryCards(canvas, y, listOf(
                "Sellers" to s.totalDistributors.toString(),
                "Invoices" to s.totalInvoices.toString(),
                "Revenue" to cfmt(currency, s.totalAmount),
                "BV" to formatter.format(s.totalBv)
            ), pw)

            // 4. Data table
            val columns = listOf(
                DmsPdfGenerator.TableColumn("#", 0.3f, Paint.Align.CENTER),
                DmsPdfGenerator.TableColumn("Name", 2f),
                DmsPdfGenerator.TableColumn("DPC", 0.8f),
                DmsPdfGenerator.TableColumn("Invoices", 0.6f, Paint.Align.RIGHT),
                DmsPdfGenerator.TableColumn("BV", 0.8f, Paint.Align.RIGHT),
                DmsPdfGenerator.TableColumn("Amount", 1f, Paint.Align.RIGHT)
            )
            val rows = report.rows.mapIndexed { idx, r ->
                listOf((idx+1).toString(), r.fullName ?: "-", r.dpcName ?: "-",
                    r.totalInvoices.toString(), formatter.format(r.totalBv),
                    cfmt(currency, r.totalAmount))
            }
            y = pdf.drawTable(canvas, y, columns, rows, pw, listOf(
                "", "TOTALS", "", s.totalInvoices.toString(),
                formatter.format(s.totalBv), cfmt(currency, s.totalAmount)
            ))

            // 5. Footer
            pdf.drawFooter(canvas, 1, 1, authManager.getUsername() ?: "", pw, ph)
            doc.finishPage(page)

            // 6. Save + share
            PdfExportHelper.exportAndShare(context, doc,
                "top_sellers_${startDate}_$endDate", "Top Sellers Report")
        } catch (e: Exception) {
            doc.close()
            Toast.makeText(context, context.getString(R.string.pdf_export_error),
                Toast.LENGTH_SHORT).show()
        }
    }

    // Helper: build franchise info from AuthManager
    private fun franchiseInfo(am: AuthManager) = DmsPdfGenerator.FranchiseInfo(
        name = am.getFranchiseName() ?: "",
        address = am.getFranchiseAddress(),
        phone = am.getFranchisePhone(),
        email = am.getFranchiseEmail(),
        taxId = am.getFranchiseTaxId(),
        currency = am.getFranchiseCurrency() ?: ""
    )
}
```

## Step 5: PdfExportButton Component

A reusable TopAppBar action button — more visible than a plain icon.

```kotlin
@Composable
fun PdfExportButton(
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    TextButton(
        onClick = onClick,
        modifier = modifier.padding(end = 4.dp),
        shape = RoundedCornerShape(8.dp),
        colors = ButtonDefaults.textButtonColors(
            contentColor = MaterialTheme.colorScheme.onPrimary
        )
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Icon(Icons.Default.PictureAsPdf, contentDescription = stringResource(R.string.pdf_export),
                modifier = Modifier.size(18.dp))
            Spacer(Modifier.width(4.dp))
            Text(text = "PDF", style = MaterialTheme.typography.labelMedium)
        }
    }
}
```

## Step 6: Screen Integration

Each screen adds the PDF button in its TopAppBar and calls the exporter. ViewModel's `authManager` must be `internal` (not `private`) so the screen can pass it.

```kotlin
// ViewModel: expose authManager
@HiltViewModel
class TopSellersViewModel @Inject constructor(
    private val repository: PosRepository,
    internal val authManager: AuthManager  // internal, not private
) : ViewModel() { ... }

// Screen: add PdfExportButton in TopAppBar actions
TopAppBar(
    title = { Text(stringResource(R.string.report_top_sellers_title)) },
    actions = {
        if (uiState.report != null) {
            PdfExportButton(onClick = {
                SalesReportPdfExporter.exportTopSellers(
                    context, viewModel.authManager, uiState.report!!,
                    uiState.currency, uiState.startDate, uiState.endDate,
                    uiState.selectedDpc?.name
                )
            })
        }
    },
    colors = TopAppBarDefaults.topAppBarColors(
        containerColor = MaterialTheme.colorScheme.primary,
        titleContentColor = MaterialTheme.colorScheme.onPrimary,
        actionIconContentColor = MaterialTheme.colorScheme.onPrimary
    )
)
```

## Step 7: String Resources

```xml
<!-- PDF Export (16 strings, translate all) -->
<string name="pdf_export">Export PDF</string>
<string name="pdf_generating">Generating PDF\u2026</string>
<string name="pdf_export_success">PDF exported successfully</string>
<string name="pdf_export_error">Failed to export PDF</string>
<string name="pdf_share">Share PDF</string>
<string name="pdf_generated_by">Generated by %1$s</string>
<string name="pdf_generated_on">Generated on %1$s</string>
<string name="pdf_page_of">Page %1$d of %2$d</string>
<string name="pdf_report_period">Period: %1$s to %2$s</string>
<string name="pdf_report_filter_dpc">DPC: %1$s</string>
<string name="pdf_report_filter_warehouse">Warehouse: %1$s</string>
<string name="pdf_report_summary">Report Summary</string>
<string name="pdf_invoice_title">INVOICE</string>
<string name="pdf_invoice_bill_to">Bill To</string>
<string name="pdf_thank_you">Thank you for your business!</string>
```

## Step 8: Franchise Info for Letterheads

The login API should return franchise contact info. Store in AuthManager:

```kotlin
// AuthManager keys
KEY_FRANCHISE_ADDRESS = "franchise_address"
KEY_FRANCHISE_PHONE = "franchise_phone"
KEY_FRANCHISE_EMAIL = "franchise_email"
KEY_FRANCHISE_TAX_ID = "franchise_tax_id"

// Getters
fun getFranchiseAddress(): String? = securePreferences.getString(KEY_FRANCHISE_ADDRESS)
fun getFranchisePhone(): String? = securePreferences.getString(KEY_FRANCHISE_PHONE)
fun getFranchiseEmail(): String? = securePreferences.getString(KEY_FRANCHISE_EMAIL)
fun getFranchiseTaxId(): String? = securePreferences.getString(KEY_FRANCHISE_TAX_ID)
```

Populate during login in `saveUserInfo()` from the franchise DTO.

## PDF Design Specification

### Letterhead
```
          [Logo 50x50]
       FRANCHISE NAME                 ← 14pt bold red, uppercase
    123 Main Street, City             ← 9pt gray
    Tel: +1 234 567 · info@co.com     ← 9pt gray
  ─────────────────────────────────   ← divider
```

### Summary Cards
```
┌──────────┬──────────┬──────────┬──────────┐
│ Label    │ Label    │ Label    │ Label    │  ← 9pt gray
│ Value    │ Value    │ Value    │ Value    │  ← 13pt bold blue
└──────────┴──────────┴──────────┴──────────┘
```

---
> **Note:** Content trimmed to 500-line standard. Move overflow content to `references/` for on-demand loading.
