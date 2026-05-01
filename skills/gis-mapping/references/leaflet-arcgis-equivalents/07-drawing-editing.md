# 7) Drawing & Editing

```javascript
class DrawingTools {
  constructor(map, options = {}) {
    this.map = map;
    this.options = {
      editLayer: null,
      maxPoints: 1000,
      snapTolerance: 10,
      measurement: true,
      ...options,
    };

    this.drawnItems = new L.FeatureGroup();
    this.editLayer = this.options.editLayer || this.drawnItems;
    this.snapLayer = new L.FeatureGroup();

    this.currentTool = null;
    this.isDrawing = false;
    this.snapEnabled = true;

    this.init();
  }

  init() {
    this.map.addLayer(this.drawnItems);
    this.map.addLayer(this.snapLayer);

    this.drawControl = new L.Control.Draw({
      position: "topright",
      draw: {
        polygon: {
          allowIntersection: false,
          showArea: this.options.measurement,
        },
        polyline: { shapeOptions: { color: "#f357a1", weight: 4 } },
        rectangle: { showArea: this.options.measurement },
        circle: { showRadius: this.options.measurement },
        marker: true,
        circlemarker: false,
      },
      edit: { featureGroup: this.editLayer, remove: true },
    });

    this.map.addControl(this.drawControl);
  }
}
```
