# Integration Guide

```javascript
// /public/js/main-gis-integration.js
class GISApplication {
  constructor() {
    this.map = null;
    this.components = {};
    this.init();
  }

  async init() {
    this.map = L.map("map").setView([40.7128, -74.006], 13);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution: "© OpenStreetMap contributors",
    }).addTo(this.map);

    await this.loadLibraries();
    this.initializeComponents();
  }

  async loadLibraries() {
    const libraries = [
      "https://unpkg.com/leaflet@1.9.4/dist/leaflet.css",
      "https://unpkg.com/leaflet@1.9.4/dist/leaflet.js",
      "https://unpkg.com/leaflet.markercluster@1.5.3/dist/leaflet.markercluster.js",
      "https://unpkg.com/leaflet.draw@1.0.4/dist/leaflet.draw.js",
      "https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.js",
      "https://unpkg.com/@turf/turf@6.5.0/turf.min.js",
      "https://unpkg.com/html2canvas@1.4.1/dist/html2canvas.min.js",
      "https://unpkg.com/jspdf@2.5.1/dist/jspdf.umd.min.js",
    ];

    for (const lib of libraries) {
      await this.loadScript(lib);
    }
  }

  loadScript(url) {
    return new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = url;
      script.onload = resolve;
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }

  initializeComponents() {
    this.components = {
      geocoding: new Geocoder(this.map),
      routing: new RoutingService(this.map),
      drawing: new DrawingTools(this.map),
      measurement: new MeasurementTools(this.map),
      clustering: new SmartClustering(this.map),
      spatialAnalysis: new SpatialAnalysis(this.map),
      timeSeries: new TimeSeriesAnalysis(this.map),
      export: new ExportPrinting(this.map),
      heatmap: new HeatmapLayer(this.map),
    };
  }
}

document.addEventListener("DOMContentLoaded", () => {
  window.gisApp = new GISApplication();
});
```
