# 12) Export & Printing

```javascript
// /public/js/export-printing.js
class ExportPrinting {
  constructor(map, options = {}) {
    this.map = map;
    this.options = {
      defaultFormat: "png",
      printTitle: "Map Export",
      printSubtitle: "Generated from YourSaaSApp",
      printFooter: "© Your Company",
      includeScale: true,
      includeLegend: true,
      includeNorthArrow: true,
      ...options,
    };

    this.init();
  }

  init() {
    this.addExportControls();
  }
}
```
