---
name: ios-pdf-export
description: Native iOS PDF export system using UIGraphicsPDFRenderer (zero dependencies).
  Reusable drawing-based generator with branded letterheads, data tables, summary
  cards, and share via UIActivityViewController. Use when adding PDF export to any
  iOS app...
metadata:
  portable: true
  compatible_with:
  - claude-code
  - codex
---

## Platform Notes

- Optional helper plugins may help in some environments, but they must not be treated as required for this skill.

# iOS PDF Export (Native UIGraphicsPDFRenderer)
Acknowledgement: Shared by Peter Bamuhigire, techguypeter.com, +256 784 464178.

<!-- dual-compat-start -->
## Use When

- Native iOS PDF export system using UIGraphicsPDFRenderer (zero dependencies). Reusable drawing-based generator with branded letterheads, data tables, summary cards, and share via UIActivityViewController. Use when adding PDF export to any iOS app...
- The task needs reusable judgment, domain constraints, or a proven workflow rather than ad hoc advice.

## Do Not Use When

- The task is unrelated to `ios-pdf-export` or would be better handled by a more specific companion skill.
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

## Evidence Produced

| Category | Artifact | Format | Example |
|----------|----------|--------|---------|
| Correctness | PDF export test plan | Markdown doc covering page layout, paginated content, fonts, and image rendering | `docs/ios/pdf-export-tests.md` |

## References

- Use the links and companion skills already referenced in this file when deeper context is needed.
<!-- dual-compat-end -->
Generate professional branded PDF documents from any iOS screen using the built-in `UIGraphicsPDFRenderer` API. Zero external dependencies — pure Core Graphics drawing. Supports A4 portrait/landscape, multi-page pagination, letterheads, tables, summary cards, info sections, status badges, and sharing.

## Overview

**Library choice:** Native `UIGraphicsPDFRenderer` (0 KB added to bundle). Alternatives like TPPDF (third-party dependency), PDFKit (viewer-only, not for generation), and libHaru (C library, complex bridging) were rejected.

**Architecture:** A core `PDFGenerator` class provides reusable drawing primitives. Per-module exporters compose these primitives for each screen. `PDFShareHelper` handles temporary file storage and sharing via `UIActivityViewController`.

```
Core/PDF/
  PDFGenerator.swift           — Drawing primitives (letterhead, tables, cards, footer)
  PDFShareHelper.swift         — Save to temp + share via UIActivityViewController
Core/UI/Components/
  PDFExportButton.swift        — Reusable toolbar button (icon + "PDF" label)
Per-module exporters (one struct per feature):
  SalesReportPDFExporter.swift, InventoryPDFExporter.swift, NetworkPDFExporter.swift
```

## Dependencies

**None.** Uses only Apple SDK classes: `UIGraphicsPDFRenderer`, `CGContext`, `NSAttributedString`, `UIFont`, `UIColor`, `UIActivityViewController`, `FileManager`.

## Step 1: PDFGenerator — Constants & Types

```swift
final class PDFGenerator {
    static let a4Width: CGFloat = 595.0    // A4 in points (72 dpi)
    static let a4Height: CGFloat = 842.0
    static let a4LandWidth: CGFloat = 842.0
    static let a4LandHeight: CGFloat = 595.0
    static let margin: CGFloat = 40.0

    // Brand colours (customise per project)
    static let brandRed = UIColor(red: 198/255, green: 40/255, blue: 40/255, alpha: 1)
    static let headerBG = UIColor(red: 176/255, green: 228/255, blue: 252/255, alpha: 1)
    static let altRow = UIColor(red: 248/255, green: 249/255, blue: 250/255, alpha: 1)
    static let summaryBG = UIColor(red: 240/255, green: 244/255, blue: 248/255, alpha: 1)
    static let accentBlue = UIColor(red: 32/255, green: 107/255, blue: 196/255, alpha: 1)
    static let textBlack = UIColor(red: 33/255, green: 37/255, blue: 41/255, alpha: 1)
    static let textGray = UIColor(red: 108/255, green: 117/255, blue: 125/255, alpha: 1)

    struct FranchiseInfo {
        let name: String; let address: String?; let phone: String?
        let email: String?; let taxId: String?; let currency: String
    }

    struct TableColumn {
        let header: String; let widthWeight: CGFloat; let alignment: NSTextAlignment
        init(header: String, widthWeight: CGFloat, alignment: NSTextAlignment = .left) {
            self.header = header; self.widthWeight = widthWeight; self.alignment = alignment
        }
    }

    let pageWidth: CGFloat; let pageHeight: CGFloat; let landscape: Bool
    var pageBounds: CGRect { CGRect(x: 0, y: 0, width: pageWidth, height: pageHeight) }
    var contentWidth: CGFloat { pageWidth - (Self.margin * 2) }

    init(landscape: Bool = false) {
        self.landscape = landscape
        self.pageWidth = landscape ? Self.a4LandWidth : Self.a4Width
        self.pageHeight = landscape ? Self.a4LandHeight : Self.a4Height
    }

    func needsNewPage(y: CGFloat) -> Bool { y > pageHeight - 50 - Self.margin }

    func beginNewPage(context: UIGraphicsPDFRendererContext) -> CGFloat {
        context.beginPage(); return Self.margin + 10
    }
}
```

## Step 2: Drawing Functions

Each function draws at the given Y position and returns the new Y. All use `NSAttributedString.draw(in:)` for text and `UIBezierPath`/`UIRectFill` for shapes.

```swift
extension PDFGenerator {
    // ── Letterhead: logo (50x50 centred) + name (14pt bold red) + address/phone/email (9pt gray) + divider
    func drawLetterhead(y: CGFloat, logo: UIImage?, info: FranchiseInfo) -> CGFloat

    // ── Report Title: centred title (14pt bold uppercase) + optional subtitle (10pt gray)
    func drawReportTitle(y: CGFloat, title: String, subtitle: String? = nil) -> CGFloat

    // ── Summary Cards: row of KPI boxes — label (9pt gray) + value (13pt bold accent blue)
    func drawSummaryCards(y: CGFloat, items: [(label: String, value: String)]) -> CGFloat

    // ── Info Section: key-value pairs for detail screens (label: value format)
    func drawInfoSection(y: CGFloat, title: String?, items: [(label: String, value: String)]) -> CGFloat

    // ── Status Badge: centred coloured rounded rect with white text
    func drawStatusBadge(y: CGFloat, status: String, bgColor: UIColor) -> CGFloat

    // ── Chart Image: scaled bitmap centred on page, max 250pt height
    func drawChartImage(y: CGFloat, image: UIImage) -> CGFloat

    // ── Footer: "Generated by X on DATE" (left) + "Page N of M" (right) at bottom
    func drawFooter(pageNumber: Int, totalPages: Int, generatedBy: String)

    // ── Divider: thin gray horizontal line
    func drawDivider(y: CGFloat) -> CGFloat

    // ── Data Table (see full implementation below)
    func drawTable(y: CGFloat, context: UIGraphicsPDFRendererContext,
                   columns: [TableColumn], rows: [[String]],
                   totalsRow: [String]?, pageNumber: inout Int,
                   footerUser: String) -> CGFloat
}
```

### Table Implementation (Key Details)

The table is the most complex component — weight-based columns, alternating rows, multi-line cells, auto page breaks with header redraw.

```swift
func drawTable(y: CGFloat, context: UIGraphicsPDFRendererContext,
               columns: [TableColumn], rows: [[String]],
               totalsRow: [String]? = nil, pageNumber: inout Int,
               footerUser: String) -> CGFloat {
    let totalWeight = columns.reduce(0) { $0 + $1.widthWeight }
    let rowHeight: CGFloat = 18; let cellPadding: CGFloat = 4
    var currentY = y

    // Calculate column positions from weights
    var colPositions: [CGFloat] = []; var colWidths: [CGFloat] = []
    var xPos = Self.margin
    for col in columns {
        colPositions.append(xPos)
        let w = (col.widthWeight / totalWeight) * contentWidth
        colWidths.append(w); xPos += w
    }

    // Header row (light blue bg, bold white text 8pt)
    Self.headerBG.setFill()
    UIRectFill(CGRect(x: Self.margin, y: currentY, width: contentWidth, height: rowHeight))
    let headerAttrs: [NSAttributedString.Key: Any] = [
        .font: UIFont.boldSystemFont(ofSize: 8), .foregroundColor: UIColor.white
    ]
    for (i, col) in columns.enumerated() {
        let rect = CGRect(x: colPositions[i] + cellPadding, y: currentY + 3,
                          width: colWidths[i] - cellPadding * 2, height: rowHeight - 6)
        NSAttributedString(string: col.header, attributes:
            attributesWithAlignment(headerAttrs, alignment: col.alignment)).draw(in: rect)
    }
    currentY += rowHeight

    // Data rows
    for (rowIdx, row) in rows.enumerated() {
        let hasMultiLine = row.contains { $0.contains("\n") }
        let thisRowHeight = hasMultiLine ? rowHeight + 10 : rowHeight

        // Page break: draw footer, start new page, redraw header
        if needsNewPage(y: currentY + thisRowHeight) {
            drawFooter(pageNumber: pageNumber, totalPages: -1, generatedBy: footerUser)
            pageNumber += 1; currentY = beginNewPage(context: context)
            // Redraw header on new page (same code as above)
            Self.headerBG.setFill()
            UIRectFill(CGRect(x: Self.margin, y: currentY, width: contentWidth, height: rowHeight))
            for (i, col) in columns.enumerated() {
                let rect = CGRect(x: colPositions[i] + cellPadding, y: currentY + 3,
                                  width: colWidths[i] - cellPadding * 2, height: rowHeight - 6)
                NSAttributedString(string: col.header, attributes:
                    attributesWithAlignment(headerAttrs, alignment: col.alignment)).draw(in: rect)
            }
            currentY += rowHeight
        }

        if rowIdx % 2 == 1 { Self.altRow.setFill()
            UIRectFill(CGRect(x: Self.margin, y: currentY, width: contentWidth, height: thisRowHeight)) }

        // Draw cell values (multi-line: first line 8pt, second line 7pt gray)
        for (colIdx, value) in row.enumerated() {
            guard colIdx < columns.count else { continue }
            let cellX = colPositions[colIdx] + cellPadding
            let cellW = colWidths[colIdx] - cellPadding * 2
            if value.contains("\n") {
                let lines = value.split(separator: "\n", maxSplits: 1).map(String.init)
                NSAttributedString(string: lines[0], attributes: bodyAttrs(columns[colIdx].alignment))
                    .draw(in: CGRect(x: cellX, y: currentY + 3, width: cellW, height: 12))
                if lines.count > 1 {
                    NSAttributedString(string: lines[1], attributes: subAttrs(columns[colIdx].alignment))
                        .draw(in: CGRect(x: cellX, y: currentY + 14, width: cellW, height: 10))
                }
            } else {
                NSAttributedString(string: value, attributes: bodyAttrs(columns[colIdx].alignment))
                    .draw(in: CGRect(x: cellX, y: currentY + 3, width: cellW, height: 12))
            }
        }
        currentY += thisRowHeight
    }

    // Totals row (same bg as header, bold white)
    if let totals = totalsRow { /* same pattern as header row with bold text */ }
    return currentY + 8
}

// Helper: returns attrs dict with given alignment + .byTruncatingTail
private func attributesWithAlignment(_ attrs: [NSAttributedString.Key: Any],
                                      alignment: NSTextAlignment) -> [NSAttributedString.Key: Any]
```

## Step 3: PDF Share Helper

```swift
struct PDFShareHelper {
    static func share(data: Data, filename: String,
                      from viewController: UIViewController, sourceView: UIView? = nil) {
        let sanitised = filename.replacingOccurrences(
            of: "[^a-zA-Z0-9._-]", with: "_", options: .regularExpression)
        let tempURL = FileManager.default.temporaryDirectory
            .appendingPathComponent("\(sanitised).pdf")
        try? data.write(to: tempURL)

        let activityVC = UIActivityViewController(activityItems: [tempURL],
                                                   applicationActivities: nil)
        // iPad REQUIRES popover — crashes without this
        if let popover = activityVC.popoverPresentationController {
            popover.sourceView = sourceView ?? viewController.view
            popover.sourceRect = sourceView?.bounds
                ?? CGRect(x: viewController.view.bounds.midX,
                          y: viewController.view.bounds.midY, width: 0, height: 0)
            popover.permittedArrowDirections = [.up, .down]
        }
        viewController.present(activityVC, animated: true)
    }
}
```

## Step 4: Per-Module Exporters

Each exporter is a `struct` with `static` functions. Pattern:

```swift
struct SalesReportPDFExporter {
    static func exportTopSellers(
        report: TopSellersReport, franchiseInfo: PDFGenerator.FranchiseInfo,
        logo: UIImage?, currency: String, startDate: String, endDate: String,
        generatedBy: String, from viewController: UIViewController
    ) {
        let pdf = PDFGenerator(landscape: true)
        let renderer = UIGraphicsPDFRenderer(bounds: pdf.pageBounds)

        let data = renderer.pdfData { context in
            context.beginPage()
            var y = PDFGenerator.margin; var pageNum = 1

            y = pdf.drawLetterhead(y: y, logo: logo, info: franchiseInfo)
            y = pdf.drawReportTitle(y: y, title: "TOP SELLERS REPORT",
                subtitle: "Period: \(startDate) to \(endDate)")
            y = pdf.drawSummaryCards(y: y, items: [
                ("Sellers", "\(report.summary.totalDistributors)"),
                ("Invoices", "\(report.summary.totalInvoices)"),
                ("Revenue", "\(currency) \(report.summary.totalAmount)"),
            ])

            let columns: [PDFGenerator.TableColumn] = [
                .init(header: "#", widthWeight: 0.3, alignment: .center),
                .init(header: "Name", widthWeight: 2.0),
                .init(header: "Invoices", widthWeight: 0.6, alignment: .right),
                .init(header: "Amount", widthWeight: 1.0, alignment: .right)
            ]
            let rows = report.rows.enumerated().map { idx, r in
                ["\(idx + 1)", r.fullName ?? "-", "\(r.totalInvoices)", "\(currency) \(r.totalAmount)"]
            }
            y = pdf.drawTable(y: y, context: context, columns: columns, rows: rows,
                              totalsRow: nil, pageNumber: &pageNum, footerUser: generatedBy)
            pdf.drawFooter(pageNumber: pageNum, totalPages: pageNum, generatedBy: generatedBy)
        }

        PDFShareHelper.share(data: data, filename: "top_sellers_\(startDate)_\(endDate)",
                             from: viewController)
    }
}
```

## Step 5: PDFExportButton + SwiftUI Integration

```swift
// Reusable toolbar button
struct PDFExportButton: View {
    let action: () -> Void
    var body: some View {
        Button(action: action) {
            HStack(spacing: 4) {
                Image(systemName: "doc.richtext").font(.system(size: 14))
                Text("PDF").font(.caption).fontWeight(.medium)
            }
        }
    }
}

// Screen integration — get topmost VC for share sheet presentation
struct TopSellersReportView: View {
    @StateObject private var viewModel = TopSellersViewModel()

    var body: some View {
        List { /* report content */ }
            .navigationTitle("Top Sellers")
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    if viewModel.report != nil { PDFExportButton { exportPDF() } }
                }
            }
    }

    private func exportPDF() {
        guard let report = viewModel.report,
              let scene = UIApplication.shared.connectedScenes.first as? UIWindowScene,
              let rootVC = scene.windows.first?.rootViewController else { return }
        var topVC = rootVC
        while let presented = topVC.presentedViewController { topVC = presented }

        SalesReportPDFExporter.exportTopSellers(
            report: report, franchiseInfo: viewModel.franchiseInfo,
            logo: UIImage(named: "company_logo"), currency: viewModel.currency,
            startDate: viewModel.startDate, endDate: viewModel.endDate,
            generatedBy: viewModel.username, from: topVC)
    }
}
```

## Step 6: Localised Strings

```
// Localizable.strings (translate all)
"pdf_export" = "Export PDF";
"pdf_generating" = "Generating PDF…";
"pdf_export_success" = "PDF exported successfully";
"pdf_export_error" = "Failed to export PDF";
"pdf_share" = "Share PDF";
"pdf_generated_by" = "Generated by %@";
"pdf_generated_on" = "Generated on %@";
"pdf_page_of" = "Page %d of %d";
"pdf_report_period" = "Period: %@ to %@";
"pdf_report_summary" = "Report Summary";
"pdf_invoice_title" = "INVOICE";
"pdf_invoice_bill_to" = "Bill To";
"pdf_thank_you" = "Thank you for your business!";
```

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

### Data Table
```
┌────┬──────────────┬────────┬──────────┐
│ #  │ Product      │ Qty    │ Amount   │  ← Light blue bg, bold white
├────┼──────────────┼────────┼──────────┤
│ 1  │ Widget A     │   120  │ USD 500  │  ← White
│ 2  │ Widget B     │    80  │ USD 320  │  ← Gray stripe
├────┼──────────────┼────────┼──────────┤
│    │ TOTALS       │   200  │ USD 820  │  ← Light blue bg
└────┴──────────────┴────────┴──────────┘
```

### Footer
```
Generated by admin on 17 February 2026, 2:30 PM     Page 1 of 3
```

## Portrait vs Landscape Decision

| Content Type | Orientation | Reason |
|-------------|-------------|--------|
| 4 columns or fewer | Portrait | Fits comfortably |
| 5+ wide columns | Landscape | Needs horizontal space |
| Invoice / detail view | Portrait | Standard document format |
| Lists with many columns | Landscape | Table readability |

## Patterns & Anti-Patterns

### DO
- Use `struct` with `static` functions for exporters (stateless, no DI needed)
- Pass `UIViewController` for share sheet presentation
- Use `NSTextAlignment` for column alignment (left, center, right)
- Use weight-based column sizing (proportional, adapts to page width)
- Truncate text with `.byTruncatingTail` line break mode
- Support multi-line cells via `\n` delimiter
- Always configure `popoverPresentationController` for iPad compatibility
- Use `FileManager.default.temporaryDirectory` (auto-cleaned, no permissions needed)
- Sanitise filenames (replace special chars with `_`)
- Use `UIGraphicsPDFRenderer` (modern, block-based, handles context lifecycle)

### DON'T
- Don't use third-party PDF libraries (TPPDF, libHaru — unnecessary dependency)
- Don't hardcode text — use `NSLocalizedString` for user-facing strings
- Don't skip the letterhead — branding matters for exported documents
- Don't forget the footer with page numbers and "generated by" attribution
- Don't screenshot SwiftUI views for PDF — draw everything with Core Graphics
- Don't forget iPad popover configuration — crashes without it on iPad
- Don't store PDFs permanently — use temporary directory, let OS manage cleanup
- Don't use deprecated `UIGraphicsBeginPDFContext` — use `UIGraphicsPDFRenderer`

## Integration with Other Skills

```
ios-pdf-export
  ├── android-pdf-export           (platform counterpart, same visual output)
  ├── dual-auth-rbac               (franchise info for letterheads)
  ├── report-print-pdf             (shared report layout concepts)
  └── webapp-gui-design            (design patterns for report screens)
```

## Checklist

- [ ] Create `PDFGenerator` with drawing primitives (letterhead, table, cards, footer)
- [ ] Create `PDFShareHelper` (save to temp + share via UIActivityViewController)
- [ ] Create `PDFExportButton` SwiftUI component for toolbar
- [ ] Ensure API returns franchise contact info (address, phone, email, tax_id)
- [ ] Store franchise info in user session/manager for letterhead access
- [ ] Create per-module exporter structs with one static function per screen
- [ ] Add PDF button to each screen's toolbar
- [ ] Configure `popoverPresentationController` for iPad share sheet
- [ ] Add localised strings (translate to all supported languages)
- [ ] Test: export → share sheet opens → PDF renders correctly in viewer
- [ ] Test on iPad: share sheet presents as popover without crash