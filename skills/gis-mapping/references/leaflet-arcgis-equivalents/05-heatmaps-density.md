# 5) Heatmaps & Density

```javascript
class HeatmapLayer {
  constructor(map, options = {}) {
    this.map = map;
    this.options = {
      radius: 25,
      blur: 15,
      maxZoom: 17,
      minOpacity: 0.1,
      max: 1.0,
      gradient: {
        0.4: "blue",
        0.6: "cyan",
        0.7: "lime",
        0.8: "yellow",
        1.0: "red",
      },
      ...options,
    };

    this.heatLayer = null;
    this.data = [];
    this.filteredData = [];

    this.init();
  }

  init() {
    if (typeof L.heatLayer === "undefined") {
      this.loadHeatmapPlugin().then(() => {
        this.createHeatLayer();
      });
    } else {
      this.createHeatLayer();
    }
  }

  loadHeatmapPlugin() {
    return new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = "https://unpkg.com/leaflet.heat@0.2.0/dist/leaflet-heat.js";
      script.onload = resolve;
      script.onerror = reject;
      document.head.appendChild(script);
    });
  }

  createHeatLayer() {
    this.heatLayer = L.heatLayer([], this.options);
    this.heatLayer.addTo(this.map);
  }

  setData(points) {
    this.data = points.map((point) => [
      point.lat,
      point.lng,
      point.intensity || 1,
    ]);

    this.filteredData = [...this.data];
    this.updateHeatmap();
  }

  updateHeatmap() {
    if (!this.heatLayer) return;

    this.heatLayer.setLatLngs(this.filteredData);

    if (this.filteredData.length > 0) {
      const maxIntensity = Math.max(...this.filteredData.map((d) => d[2]));
      this.heatLayer.setOptions({ max: maxIntensity });
    }
  }

  filterData(filters) {
    this.filteredData = this.data.filter(() => true);
    this.updateHeatmap();
    return this.filteredData.length;
  }

  setRadius(radius) {
    this.options.radius = radius;
    this.heatLayer.setOptions({ radius: radius });
  }

  setBlur(blur) {
    this.options.blur = blur;
    this.heatLayer.setOptions({ blur: blur });
  }

  setGradient(gradient) {
    this.options.gradient = gradient;
    this.heatLayer.setOptions({ gradient: gradient });
  }
}
```
